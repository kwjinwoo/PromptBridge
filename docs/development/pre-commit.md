---
id: pre-commit-conventions
title: Pre-commit Conventions
type: development
status: active
authority: canonical
relations:
  - type: implements
    target: docs-index
  - type: validates
    target: generated-knowledge-graph
  - type: informs
    target: project-status
last_reviewed: 2026-07-15
---

# Pre-commit Conventions

PromptBridge uses pre-commit as the shared local quality gate for documentation,
Python, and Swift changes.

## Environment setup

The repository is a non-package uv project. Its development tools are declared
in the root `pyproject.toml`, and Python 3.11 is selected through
`.python-version`.

Create or synchronize the development environment with:

```shell
uv sync
```

The `dev` dependency group is synchronized by default. Commit the resulting
`uv.lock` so local and CI environments resolve the same tool versions.

Install the Git hook through the uv-managed environment:

```shell
uv run pre-commit install
```

This installs both `pre-commit` and `commit-msg` hook types. The latter validates
messages against the [Commit Convention](commit-convention.md).

## Running hooks

Run every pre-commit command through uv:

```shell
uv run pre-commit run
uv run pre-commit run --all-files
```

Do not use a globally installed `pre-commit` command or `uvx pre-commit` for
normal repository work. `uv run` ensures the version declared in
`pyproject.toml` and resolved in `uv.lock` is used.

## Hook policy

- Generic hooks normalize trailing whitespace, final newlines, byte-order marks,
  and line endings, and validate common file formats and accidental secrets.
- Markdown is checked with markdownlint-cli2.
- Python is formatted and linted with Ruff using the root `pyproject.toml`.
- Swift is formatted with SwiftFormat and linted with SwiftLint.
- Commit messages are validated with the uv-managed Commitizen.
- The local docs graph hook validates frontmatter, stable IDs, typed relations,
  relative links, document split limits, and the generated document index.
- Formatters may modify files. Review and stage their changes before committing.
- Linters and graph validation report failures without rewriting semantics.

## Configuration ownership

| Concern | Configuration |
|---|---|
| uv project and tool dependencies | `pyproject.toml` |
| Python selection | `.python-version` |
| Reproducible dependency resolution | `uv.lock` |
| Hook orchestration | `.pre-commit-config.yaml` |
| Markdown | `.markdownlint-cli2.yaml` |
| Python | `pyproject.toml` |
| Swift formatting | `.swiftformat` |
| Swift linting | `.swiftlint.yml` |
| Commit messages | `pyproject.toml` and `docs/development/commit-convention.md` |
| Docstrings and comments | `docs/development/code-style.md` |
| Test-driven development | `docs/development/testing.md` |
| Documentation graph | `scripts/validate_docs.py` |

The pre-commit runner is pinned in `pyproject.toml`; individual hook revisions
are pinned in `.pre-commit-config.yaml`. Update hook revisions intentionally
with:

```shell
uv run pre-commit autoupdate
```

Then review the diff, refresh `uv.lock` when Python dependencies change, and run
the complete hook suite before accepting an update.

## Initial language baseline

- Python targets Python 3.11 or newer for project source.
- Python and Swift use a 100-column formatting target.
- SwiftLint permits lines up to 120 columns only as an error boundary; new code
  should normally remain within 100 columns.
- Generated and build directories are excluded from source formatting.

These baselines can change through an explicit convention update once the first
Python package and Xcode project establish their deployment constraints.
