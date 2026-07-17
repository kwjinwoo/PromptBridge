"""Standard-input/JSON bridge for the macOS Phase 3 prototype."""

from __future__ import annotations

import argparse
import json
import sys

from promptbridge.preservation import PipelineResult
from promptbridge.runtime import OllamaRuntime, RuntimeConfigurationError


def main(arguments: list[str] | None = None) -> int:
    """Transform stdin and write one structured JSON result to stdout.

    Args:
        arguments: Optional command-line arguments for tests and embedding.

    Returns:
        Zero for a safe result, two for a fail-closed result, or 64 for invalid
        local runtime configuration.
    """
    parser = argparse.ArgumentParser(description="Run the local PromptBridge pipeline.")
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="qwen3.5:4b")
    parser.add_argument("--timeout", type=float, default=10.0)
    options = parser.parse_args(arguments)
    try:
        runtime = OllamaRuntime(
            endpoint=options.endpoint,
            model=options.model,
            timeout=options.timeout,
        )
    except RuntimeConfigurationError:
        _write_configuration_failure()
        return 64

    result = runtime.run(sys.stdin.read())
    json.dump(_serialize(result), sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0 if result.safe_to_apply else 2


def _serialize(result: PipelineResult) -> dict[str, object]:
    return {
        "text": result.text,
        "safe_to_apply": result.safe_to_apply,
        "retry_count": result.retry_count,
        "failure_kind": result.failure_kind.value if result.failure_kind else None,
        "findings": [
            {
                "category": finding.category.value,
                "code": finding.code,
                "severity": finding.severity,
                "expected_count": finding.expected_count,
                "observed_count": finding.observed_count,
                "description": finding.description,
            }
            for finding in result.findings
        ],
        "message": result.message,
    }


def _write_configuration_failure() -> None:
    json.dump(
        {
            "text": None,
            "safe_to_apply": False,
            "retry_count": 0,
            "failure_kind": "runtime",
            "findings": [],
            "message": "The local runtime configuration is not allowed.",
        },
        sys.stdout,
        separators=(",", ":"),
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
