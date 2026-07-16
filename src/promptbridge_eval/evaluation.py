"""Dataset loading, deterministic scoring, and local runtime access."""

from __future__ import annotations

import json
import re
import statistics
import time
import urllib.error
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class EvaluationError(ValueError):
    """Raised when evaluation input violates the evaluation contract."""


@dataclass(frozen=True)
class Case:
    """One synthetic translation case and its deterministic scoring rules."""

    case_id: str
    category: str
    source: str
    protected_elements: tuple[str, ...]
    requirements: tuple[tuple[str, ...], ...]
    forbidden_additions: tuple[str, ...]


@dataclass(frozen=True)
class CaseScore:
    """Scores for one model output."""

    case_id: str
    preservation_accuracy: float
    requirement_coverage: float
    hallucinated_requirement_rate: float
    output_disciplined: bool

    @property
    def protected_passed(self) -> bool:
        """Return whether every protected element was reproduced exactly."""
        return self.preservation_accuracy == 1.0


@dataclass(frozen=True)
class ModelResponse:
    """One local model response and its measured end-to-end latency."""

    output: str
    latency_ms: float


def load_cases(path: Path) -> tuple[Case, ...]:
    """Load and validate a versioned synthetic evaluation dataset.

    Args:
        path: JSON dataset path.

    Returns:
        Validated immutable cases.

    Raises:
        EvaluationError: If the dataset is malformed or contains duplicate IDs.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvaluationError(f"cannot load dataset: {error}") from error

    if payload.get("schema_version") != 1 or not isinstance(payload.get("cases"), list):
        raise EvaluationError("dataset must use schema_version 1 and contain cases")

    cases: list[Case] = []
    seen: set[str] = set()
    for raw in payload["cases"]:
        if not isinstance(raw, dict):
            raise EvaluationError("each case must be an object")
        case_id = _required_string(raw, "id")
        if case_id in seen:
            raise EvaluationError(f"duplicate case id: {case_id}")
        seen.add(case_id)
        cases.append(
            Case(
                case_id=case_id,
                category=_required_string(raw, "category"),
                source=_required_string(raw, "source"),
                protected_elements=_string_tuple(raw, "protected_elements"),
                requirements=_requirements(raw),
                forbidden_additions=_string_tuple(raw, "forbidden_additions"),
            )
        )

    if not cases:
        raise EvaluationError("dataset must contain at least one case")
    return tuple(cases)


def score_output(case: Case, output: str) -> CaseScore:
    """Score a transformation with explicit deterministic rules.

    Args:
        case: Source case and scoring markers.
        output: Model-produced transformation.

    Returns:
        Scores for preservation, coverage, additions, and output discipline.
    """
    protected_matches = sum(element in output for element in case.protected_elements)
    preservation = _ratio(protected_matches, len(case.protected_elements))

    normalized = output.casefold()
    covered = sum(
        any(term.casefold() in normalized for term in group) for group in case.requirements
    )
    coverage = _ratio(covered, len(case.requirements))
    additions = sum(term.casefold() in normalized for term in case.forbidden_additions)
    hallucination_rate = _ratio(additions, len(case.forbidden_additions))

    stripped = output.strip()
    has_preamble = bool(
        re.match(
            r"^(?:here(?:'s| is)|okay[,!]?\s+here(?:'s| is)|sure[,!]|translation\s*:|translated prompt\s*:)",
            stripped,
            flags=re.IGNORECASE,
        )
    )
    has_korean_prose = bool(re.search(r"[가-힣]", stripped))
    disciplined = bool(stripped) and not has_preamble and not has_korean_prose

    return CaseScore(
        case_id=case.case_id,
        preservation_accuracy=preservation,
        requirement_coverage=coverage,
        hallucinated_requirement_rate=hallucination_rate,
        output_disciplined=disciplined,
    )


def aggregate_scores(
    scores: Iterable[CaseScore],
    latencies_ms: Iterable[float],
) -> dict[str, int | float]:
    """Aggregate case scores and warm latency into decision metrics."""
    score_rows = tuple(scores)
    latency_rows = tuple(latencies_ms)
    if not score_rows or len(score_rows) != len(latency_rows):
        raise EvaluationError("scores and latencies must be non-empty and aligned")

    return {
        "case_count": len(score_rows),
        "preservation_accuracy": statistics.fmean(
            score.preservation_accuracy for score in score_rows
        ),
        "protected_pass_rate": statistics.fmean(score.protected_passed for score in score_rows),
        "requirement_coverage": statistics.fmean(
            score.requirement_coverage for score in score_rows
        ),
        "hallucinated_requirement_rate": statistics.fmean(
            score.hallucinated_requirement_rate for score in score_rows
        ),
        "discipline_pass_rate": statistics.fmean(score.output_disciplined for score in score_rows),
        "warm_latency_median_ms": statistics.median(latency_rows),
        "warm_latency_p95_ms": _percentile(latency_rows, 0.95),
    }


class OllamaClient:
    """Minimal client boundary restricted to a loopback Ollama endpoint."""

    def __init__(self, endpoint: str) -> None:
        """Validate and retain a local-only endpoint."""
        parsed = urlparse(endpoint)
        if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise EvaluationError("Ollama endpoint must use HTTP on a loopback host")
        self.endpoint = endpoint.rstrip("/")

    def generate(
        self,
        model: str,
        system_prompt: str,
        source: str,
        options: dict[str, object],
    ) -> ModelResponse:
        """Generate one transformation through Ollama's local chat API."""
        body = json.dumps(
            {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": source},
                ],
                "options": options,
                "think": False,
                "stream": False,
                "keep_alive": "10m",
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.endpoint}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
            raise EvaluationError(f"local model request failed: {error}") from error
        latency_ms = (time.perf_counter() - started) * 1000
        try:
            output = payload["message"]["content"]
        except (KeyError, TypeError) as error:
            raise EvaluationError("local model response did not contain message.content") from error
        if not isinstance(output, str):
            raise EvaluationError("local model output must be text")
        return ModelResponse(output=output, latency_ms=latency_ms)

    def runtime_version(self) -> str:
        """Return the version reported by the local Ollama service."""
        payload = self._request_json("/api/version")
        version = payload.get("version")
        if not isinstance(version, str):
            raise EvaluationError("local runtime did not report a version")
        return version

    def model_metadata(self, model: str) -> dict[str, Any]:
        """Return reproducibility metadata for an installed model."""
        payload = self._request_json("/api/show", {"model": model})
        tags = self._request_json("/api/tags")
        details = payload.get("details", {})
        if not isinstance(details, dict):
            details = {}
        installed = next(
            (
                row
                for row in tags.get("models", [])
                if isinstance(row, dict) and row.get("name") == model
            ),
            {},
        )
        return {
            "family": details.get("family"),
            "parameter_size": details.get("parameter_size"),
            "quantization_level": details.get("quantization_level"),
            "digest": installed.get("digest"),
            "size_bytes": installed.get("size"),
            "modified_at": payload.get("modified_at"),
        }

    def _request_json(self, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            f"{self.endpoint}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST" if body is not None else "GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
            raise EvaluationError(f"local runtime metadata request failed: {error}") from error
        if not isinstance(payload, dict):
            raise EvaluationError("local runtime metadata must be an object")
        return payload


def evaluate_model(
    client: Any,
    model: str,
    system_prompt: str,
    cases: Iterable[Case],
    options: dict[str, object],
) -> dict[str, Any]:
    """Run and score identical cases for one local model."""
    records: list[dict[str, Any]] = []
    scores: list[CaseScore] = []
    latencies: list[float] = []
    for case in cases:
        response = client.generate(model, system_prompt, case.source, options)
        score = score_output(case, response.output)
        scores.append(score)
        latencies.append(response.latency_ms)
        records.append(
            {
                "case_id": case.case_id,
                "category": case.category,
                "output": response.output,
                "latency_ms": round(response.latency_ms, 3),
                "preservation_accuracy": score.preservation_accuracy,
                "requirement_coverage": score.requirement_coverage,
                "hallucinated_requirement_rate": score.hallucinated_requirement_rate,
                "output_disciplined": score.output_disciplined,
            }
        )
    return {"model": model, "summary": aggregate_scores(scores, latencies), "cases": records}


def select_baseline(
    model_results: Iterable[dict[str, Any]],
    gates: dict[str, float],
) -> dict[str, Any]:
    """Select the strongest model that satisfies every Phase 1 gate."""
    rows = tuple(model_results)
    eligibility: dict[str, dict[str, bool]] = {}
    eligible: list[dict[str, Any]] = []
    comparisons = (
        ("protected_pass_rate", "protected_pass_rate_min", lambda value, gate: value >= gate),
        ("requirement_coverage", "requirement_coverage_min", lambda value, gate: value >= gate),
        (
            "hallucinated_requirement_rate",
            "hallucinated_requirement_rate_max",
            lambda value, gate: value <= gate,
        ),
        ("discipline_pass_rate", "discipline_pass_rate_min", lambda value, gate: value >= gate),
        (
            "warm_latency_median_ms",
            "warm_latency_median_ms_max",
            lambda value, gate: value <= gate,
        ),
    )
    for row in rows:
        model = row["model"]
        summary = row["summary"]
        checks = {
            metric: comparator(float(summary[metric]), gates[gate_name])
            for metric, gate_name, comparator in comparisons
        }
        eligibility[model] = checks
        if all(checks.values()):
            eligible.append(row)

    eligible.sort(
        key=lambda row: (
            -float(row["summary"]["requirement_coverage"]),
            float(row["summary"]["hallucinated_requirement_rate"]),
            float(row["summary"]["warm_latency_median_ms"]),
            str(row["model"]),
        )
    )
    return {
        "selected_model": eligible[0]["model"] if eligible else None,
        "eligible_models": [row["model"] for row in eligible],
        "gate_results": eligibility,
    }


def _required_string(raw: dict[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value:
        raise EvaluationError(f"case field {key} must be a non-empty string")
    return value


def _string_tuple(raw: dict[str, Any], key: str) -> tuple[str, ...]:
    value = raw.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise EvaluationError(f"case field {key} must be a non-empty string list")
    return tuple(value)


def _requirements(raw: dict[str, Any]) -> tuple[tuple[str, ...], ...]:
    value = raw.get("requirements")
    if not isinstance(value, list) or not value:
        raise EvaluationError("case field requirements must be a non-empty list")
    groups: list[tuple[str, ...]] = []
    for group in value:
        if (
            not isinstance(group, list)
            or not group
            or not all(isinstance(item, str) for item in group)
        ):
            raise EvaluationError("each requirement must be a non-empty string list")
        groups.append(tuple(group))
    return tuple(groups)


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def _percentile(values: tuple[float, ...], quantile: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * quantile)))
    return ordered[index]
