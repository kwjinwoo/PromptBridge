#!/usr/bin/env python3
"""Validate PromptBridge's docs-as-wiki knowledge graph."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX_PATH = DOCS / "generated" / "document-index.json"

REQUIRED_FIELDS = {
    "id",
    "title",
    "type",
    "status",
    "authority",
    "relations",
    "last_reviewed",
}

ALLOWED_STATUSES = {
    "not-started",
    "proposed",
    "active",
    "in-progress",
    "blocked",
    "accepted",
    "implemented",
    "completed",
    "deferred",
    "deprecated",
}

ALLOWED_AUTHORITIES = {"canonical", "derived"}

ALLOWED_RELATIONS = {
    "defines",
    "implements",
    "depends-on",
    "constrains",
    "validates",
    "triggers",
    "informs",
    "supersedes",
    "conflicts-with",
    "related-to",
    "part-of",
    "tracks",
}

FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---(?:\n|\Z)", re.DOTALL)
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:")


class ValidationError(Exception):
    """A documentation graph validation error."""


def relative(path: Path) -> str:
    """Return a repository-relative POSIX path.

    Args:
        path: Absolute path located inside the repository.

    Returns:
        The path relative to the repository root using POSIX separators.
    """
    return path.relative_to(ROOT).as_posix()


def load_document(path: Path) -> dict[str, Any]:
    """Load and validate one Markdown document's frontmatter.

    Args:
        path: Markdown document to load.

    Returns:
        Parsed frontmatter mapping.

    Raises:
        ValidationError: If frontmatter or document-level conventions are invalid.
    """
    content = path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(content)
    if match is None:
        raise ValidationError(f"{relative(path)}: missing YAML frontmatter")

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        raise ValidationError(f"{relative(path)}: invalid frontmatter: {error}") from error

    if not isinstance(data, dict):
        raise ValidationError(f"{relative(path)}: frontmatter must be a mapping")

    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        fields = ", ".join(sorted(missing))
        raise ValidationError(f"{relative(path)}: missing fields: {fields}")

    if data["status"] not in ALLOWED_STATUSES:
        raise ValidationError(f"{relative(path)}: invalid status: {data['status']}")

    if data["authority"] not in ALLOWED_AUTHORITIES:
        raise ValidationError(f"{relative(path)}: invalid authority: {data['authority']}")

    if not isinstance(data["relations"], list):
        raise ValidationError(f"{relative(path)}: relations must be a list")

    expected_authority = "derived" if "generated" in path.parts else "canonical"
    if data["authority"] != expected_authority:
        raise ValidationError(
            f"{relative(path)}: expected authority {expected_authority}, found {data['authority']}"
        )

    if path.stat().st_size > 40 * 1024 or content.count("\n") > 500:
        raise ValidationError(
            f"{relative(path)}: exceeds the required split limit of 500 lines or 40 KB"
        )

    return data


def validate_relations(documents: dict[str, tuple[Path, dict[str, Any]]]) -> None:
    """Validate typed edges between documentation nodes.

    Args:
        documents: Documents indexed by their stable IDs.

    Raises:
        ValidationError: If an edge has an invalid type, target, or duplicate.
    """
    for source_id, (path, document) in documents.items():
        seen: set[tuple[str, str]] = set()
        for relation in document["relations"]:
            if not isinstance(relation, dict):
                raise ValidationError(f"{relative(path)}: relation must be a mapping")

            relation_type = relation.get("type")
            target = relation.get("target")
            if relation_type not in ALLOWED_RELATIONS:
                raise ValidationError(f"{relative(path)}: invalid relation type: {relation_type}")
            if not isinstance(target, str) or not target:
                raise ValidationError(f"{relative(path)}: relation target must be an ID")
            if target not in documents:
                raise ValidationError(f"{relative(path)}: relation target does not exist: {target}")
            if target == source_id:
                raise ValidationError(f"{relative(path)}: document cannot relate to itself")

            edge = (relation_type, target)
            if edge in seen:
                raise ValidationError(
                    f"{relative(path)}: duplicate relation: {relation_type} -> {target}"
                )
            seen.add(edge)


def validate_links(paths: list[Path]) -> None:
    """Validate repository-local Markdown links.

    Args:
        paths: Markdown documents whose links should be checked.

    Raises:
        ValidationError: If a link escapes the repository or targets a missing file.
    """
    for path in paths:
        content = path.read_text(encoding="utf-8")
        for raw_link in MARKDOWN_LINK_PATTERN.findall(content):
            link = raw_link.strip().split(maxsplit=1)[0].strip("<>")
            if not link or link.startswith("#") or link.startswith(EXTERNAL_SCHEMES):
                continue

            local_path = unquote(link.split("#", 1)[0])
            if not local_path:
                continue

            target = (path.parent / local_path).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError as error:
                raise ValidationError(
                    f"{relative(path)}: link escapes the repository: {raw_link}"
                ) from error

            if not target.exists():
                raise ValidationError(f"{relative(path)}: broken local link: {raw_link}")


def validate_index(documents: dict[str, tuple[Path, dict[str, Any]]]) -> None:
    """Validate the generated document index against canonical frontmatter.

    Args:
        documents: Documents indexed by their stable IDs.

    Raises:
        ValidationError: If the generated index is missing, invalid, or stale.
    """
    try:
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationError(f"{relative(INDEX_PATH)}: invalid index: {error}") from error

    rows = index.get("documents")
    if not isinstance(rows, list):
        raise ValidationError(f"{relative(INDEX_PATH)}: documents must be a list")

    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValidationError(f"{relative(INDEX_PATH)}: invalid document entry")
        document_id = row["id"]
        if document_id in indexed:
            raise ValidationError(f"{relative(INDEX_PATH)}: duplicate ID: {document_id}")
        indexed[document_id] = row

    if indexed.keys() != documents.keys():
        missing = sorted(documents.keys() - indexed.keys())
        extra = sorted(indexed.keys() - documents.keys())
        raise ValidationError(
            f"{relative(INDEX_PATH)}: document set mismatch; missing={missing}, extra={extra}"
        )

    for document_id, (path, frontmatter) in documents.items():
        row = indexed[document_id]
        expected = {
            "id": document_id,
            "path": relative(path),
            "type": frontmatter["type"],
            "status": frontmatter["status"],
        }
        if row != expected:
            raise ValidationError(
                f"{relative(INDEX_PATH)}: stale entry for {document_id}; "
                f"expected={expected}, found={row}"
            )


def validate() -> None:
    """Validate the complete documentation knowledge graph.

    Raises:
        ValidationError: If any document, relation, link, or index entry is invalid.
    """
    paths = sorted(path for path in DOCS.rglob("*.md") if path.name != "AGENTS.md")
    documents: dict[str, tuple[Path, dict[str, Any]]] = {}

    for path in paths:
        document = load_document(path)
        document_id = document["id"]
        if not isinstance(document_id, str) or not document_id:
            raise ValidationError(f"{relative(path)}: id must be a non-empty string")
        if document_id in documents:
            other_path = documents[document_id][0]
            raise ValidationError(
                f"{relative(path)}: duplicate ID {document_id}; "
                f"already used by {relative(other_path)}"
            )
        documents[document_id] = (path, document)

    validate_relations(documents)
    validate_links(paths)
    validate_index(documents)
    print(
        f"docs graph valid: {len(documents)} documents, "
        f"{sum(len(item[1]['relations']) for item in documents.values())} relations"
    )


def main() -> int:
    """Run documentation validation and return a process exit code.

    Returns:
        Zero when the documentation graph is valid; otherwise one.
    """
    try:
        validate()
    except ValidationError as error:
        print(f"docs graph validation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
