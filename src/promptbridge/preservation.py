"""Detect, protect, restore, and validate technical prompt elements."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import StrEnum


class ElementCategory(StrEnum):
    """Technical element categories required by the preservation contract."""

    INLINE_CODE = "inline_code"
    FENCED_CODE = "fenced_code"
    PATH = "path"
    URL = "url"
    COMMAND = "command"
    IDENTIFIER = "identifier"
    NUMBER = "number"
    VERSION = "version"


class FailureKind(StrEnum):
    """Failure boundaries returned by the preservation pipeline."""

    RUNTIME = "runtime"
    RESTORATION = "restoration"
    VALIDATION = "validation"


@dataclass(frozen=True)
class ProtectedElement:
    """One non-overlapping technical span found in a source prompt."""

    category: ElementCategory
    original: str
    start: int
    end: int
    placeholder: str | None


@dataclass(frozen=True)
class ProtectionResult:
    """Protected model input and the source elements used to validate it."""

    text: str
    elements: tuple[ProtectedElement, ...]

    @property
    def protected(self) -> tuple[ProtectedElement, ...]:
        """Return elements represented by placeholders in model input."""
        return tuple(element for element in self.elements if element.placeholder is not None)


@dataclass(frozen=True)
class Finding:
    """A category-level finding that does not embed protected prompt values."""

    category: ElementCategory
    code: str
    severity: str
    expected_count: int
    observed_count: int
    description: str


@dataclass(frozen=True)
class RestorationResult:
    """Result of restoring every required placeholder exactly once."""

    text: str | None
    findings: tuple[Finding, ...]

    @property
    def succeeded(self) -> bool:
        """Return whether restoration produced safe text."""
        return self.text is not None and not self.findings


@dataclass(frozen=True)
class ValidationResult:
    """Deterministic preservation findings grouped by technical category."""

    findings: tuple[Finding, ...]

    @property
    def succeeded(self) -> bool:
        """Return whether every required preservation check passed."""
        return not self.findings


@dataclass(frozen=True)
class PipelineResult:
    """Safe-to-apply output or a structured, non-applying failure."""

    text: str | None
    safe_to_apply: bool
    retry_count: int
    failure_kind: FailureKind | None
    findings: tuple[Finding, ...]
    message: str

    @property
    def failed_categories(self) -> tuple[ElementCategory, ...]:
        """Return affected categories in stable contract order."""
        affected = {finding.category for finding in self.findings}
        return tuple(category for category in ElementCategory if category in affected)


Transform = Callable[[str, tuple[ElementCategory, ...]], str]


class PreservationPipeline:
    """Run deterministic protection around a transformation boundary."""

    def __init__(self, transform: Transform) -> None:
        """Create a pipeline using an injected local transformation callable."""
        self._transform = transform

    def run(self, source: str) -> PipelineResult:
        """Transform, restore, validate, and retry one preservation failure."""
        protection = protect(source)
        failed_categories: tuple[ElementCategory, ...] = ()
        for attempt in range(2):
            try:
                transformed = self._transform(protection.text, failed_categories)
            except Exception:
                return PipelineResult(
                    text=None,
                    safe_to_apply=False,
                    retry_count=attempt,
                    failure_kind=FailureKind.RUNTIME,
                    findings=(),
                    message="The local transformation runtime failed.",
                )

            restoration = restore(transformed, protection.protected)
            if not restoration.succeeded:
                failed_categories = _finding_categories(restoration.findings)
                if attempt == 0:
                    continue
                return _failed_pipeline_result(
                    FailureKind.RESTORATION, restoration.findings, attempt
                )

            validation = validate(protection.elements, restoration.text or "")
            if validation.succeeded:
                return PipelineResult(
                    text=restoration.text,
                    safe_to_apply=True,
                    retry_count=attempt,
                    failure_kind=None,
                    findings=(),
                    message="Preservation checks passed.",
                )

            failed_categories = _finding_categories(validation.findings)
            if attempt == 0:
                continue
            return _failed_pipeline_result(FailureKind.VALIDATION, validation.findings, attempt)

        raise AssertionError("preservation pipeline exceeded its fixed attempt limit")


@dataclass(frozen=True)
class _Pattern:
    category: ElementCategory
    regex: re.Pattern[str]
    protect: bool


_PATTERNS = (
    _Pattern(
        ElementCategory.FENCED_CODE,
        re.compile(
            r"^(?P<fence>`{3,}|~{3,})[^\n]*\n.*?^(?P=fence)[ \t]*$", re.MULTILINE | re.DOTALL
        ),
        False,
    ),
    _Pattern(ElementCategory.INLINE_CODE, re.compile(r"(?<!`)`[^`\n]+`(?!`)"), True),
    _Pattern(
        ElementCategory.URL,
        re.compile(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'*+,;=%-]+"),
        True,
    ),
    _Pattern(
        ElementCategory.COMMAND,
        re.compile(
            r"(?<![A-Za-z0-9_`])(?:"
            r"git\s+(?:rebase(?:\s+(?:--[A-Za-z0-9_-]+|[A-Za-z0-9_./-]+)){0,5}|status|diff|log)|"
            r"(?:uv\s+run|python3?|pytest|docker|cmake|ninja|swift|xcodebuild)"
            r"\s+(?:--?[A-Za-z0-9_-]+|[A-Za-z0-9_./:=+-]+)"
            r"(?:\s+(?:--?[A-Za-z0-9_-]+|[A-Za-z0-9_./:=+-]+)){0,5}"
            r")"
        ),
        True,
    ),
    _Pattern(
        ElementCategory.PATH,
        re.compile(r"(?<![A-Za-z0-9_:])(?:~/|\.{1,2}/|/)(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+"),
        True,
    ),
    _Pattern(
        ElementCategory.VERSION,
        re.compile(
            r"(?<![A-Za-z0-9_.])(?:[A-Za-z][A-Za-z0-9+.-]*[ \t]+)?"
            r"v?\d+\.\d+(?:\.\d+)*(?![A-Za-z0-9_.])"
        ),
        False,
    ),
    _Pattern(
        ElementCategory.IDENTIFIER,
        re.compile(
            r"(?<![A-Za-z0-9_])(?:[A-Za-z_][A-Za-z0-9_]*"
            r"(?:::[A-Za-z_][A-Za-z0-9_]*)+|[A-Za-z][A-Za-z0-9_]*_[A-Za-z0-9_]+)"
            r"(?![A-Za-z0-9_])"
        ),
        True,
    ),
    _Pattern(
        ElementCategory.NUMBER,
        re.compile(r"(?<![A-Za-z0-9_.])\d+(?![A-Za-z0-9_.])"),
        False,
    ),
)


def protect(source: str) -> ProtectionResult:
    """Detect non-overlapping elements and hide eligible values with placeholders."""
    candidates: list[tuple[int, int, ElementCategory, bool]] = []
    occupied: list[tuple[int, int]] = []
    for pattern in _PATTERNS:
        for match in pattern.regex.finditer(source):
            start, end = match.span()
            if any(start < used_end and used_start < end for used_start, used_end in occupied):
                continue
            candidates.append((start, end, pattern.category, pattern.protect))
            occupied.append((start, end))

    candidates.sort(key=lambda row: row[0])
    namespace = _placeholder_namespace(source)
    elements = tuple(
        ProtectedElement(
            category=category,
            original=source[start:end],
            start=start,
            end=end,
            placeholder=(
                f"__PB_{category.value.upper()}_{namespace}_{index}__" if should_protect else None
            ),
        )
        for index, (start, end, category, should_protect) in enumerate(candidates)
    )
    text = source
    for element in reversed(elements):
        if element.placeholder is not None:
            text = text[: element.start] + element.placeholder + text[element.end :]
    return ProtectionResult(text=text, elements=elements)


def restore(text: str, elements: Iterable[ProtectedElement]) -> RestorationResult:
    """Restore placeholders only when every token occurs exactly once."""
    protected = tuple(element for element in elements if element.placeholder is not None)
    findings: list[Finding] = []
    for element in protected:
        placeholder = element.placeholder or ""
        count = text.count(placeholder)
        if count != 1:
            code = "placeholder_missing" if count == 0 else "placeholder_duplicated"
            findings.append(
                Finding(
                    category=element.category,
                    code=code,
                    severity="error",
                    expected_count=1,
                    observed_count=count,
                    description=f"A required {element.category.value} placeholder was not restored exactly once.",
                )
            )
            continue
        position = text.index(placeholder)
        before = text[position - 1] if position > 0 else ""
        after_index = position + len(placeholder)
        after = text[after_index] if after_index < len(text) else ""
        if before == "`" or after == "`":
            findings.append(
                Finding(
                    category=element.category,
                    code="placeholder_wrapped",
                    severity="error",
                    expected_count=0,
                    observed_count=1,
                    description=(
                        f"A required {element.category.value} placeholder gained Markdown wrapping."
                    ),
                )
            )
    if findings:
        return RestorationResult(text=None, findings=tuple(findings))

    observed_order = tuple(
        sorted(protected, key=lambda element: text.index(element.placeholder or ""))
    )
    if observed_order != protected:
        for expected_index, element in enumerate(protected):
            if observed_order[expected_index] != element:
                findings.append(
                    Finding(
                        category=element.category,
                        code="placeholder_reordered",
                        severity="error",
                        expected_count=1,
                        observed_count=1,
                        description=(
                            f"A required {element.category.value} placeholder changed order."
                        ),
                    )
                )
        return RestorationResult(text=None, findings=tuple(findings))

    restored = text
    for element in protected:
        restored = restored.replace(element.placeholder or "", element.original, 1)
    return RestorationResult(text=restored, findings=())


def validate(
    elements: Iterable[ProtectedElement],
    output: str,
) -> ValidationResult:
    """Require the original occurrence count for every technical value."""
    expected = Counter((element.category, element.original) for element in elements)
    findings: list[Finding] = []
    for (category, original), expected_count in expected.items():
        observed_count = output.count(original)
        if observed_count != expected_count:
            findings.append(
                Finding(
                    category=category,
                    code="protected_value_changed",
                    severity="error",
                    expected_count=expected_count,
                    observed_count=observed_count,
                    description=f"Required {category.value} content changed or has the wrong count.",
                )
            )
    return ValidationResult(findings=tuple(findings))


def _placeholder_namespace(source: str) -> str:
    salt = 0
    while True:
        digest = hashlib.sha256(f"{salt}\0{source}".encode()).hexdigest()[:12]
        if digest not in source:
            return digest
        salt += 1


def _finding_categories(findings: Iterable[Finding]) -> tuple[ElementCategory, ...]:
    affected = {finding.category for finding in findings}
    return tuple(category for category in ElementCategory if category in affected)


def _failed_pipeline_result(
    kind: FailureKind,
    findings: tuple[Finding, ...],
    retry_count: int,
) -> PipelineResult:
    return PipelineResult(
        text=None,
        safe_to_apply=False,
        retry_count=retry_count,
        failure_kind=kind,
        findings=findings,
        message="Preservation checks failed; the source must remain unchanged.",
    )
