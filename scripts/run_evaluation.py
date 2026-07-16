#!/usr/bin/env python3
"""Run the versioned PromptBridge Phase 1 local-model evaluation."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from promptbridge_eval.evaluation import (  # noqa: E402
    EvaluationError,
    OllamaClient,
    evaluate_model,
    load_cases,
    select_baseline,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "evaluation/configs/phase1-v1.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    """Run the configured evaluation and write reproducible JSON evidence."""
    args = parse_args()
    config = load_config(args.config)
    client = OllamaClient(config["endpoint"])
    cases = load_cases(ROOT / config["dataset"])
    system_prompt = (ROOT / config["prompt"]).read_text(encoding="utf-8").strip()
    results: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {}

    for model in config["models"]:
        model_metadata = client.model_metadata(model)
        warmup = client.generate(
            model,
            system_prompt,
            "`warmup_value`를 변경하지 말고 이 요청을 영어로 번역해줘.",
            config["options"],
        )
        result = evaluate_model(client, model, system_prompt, cases, config["options"])
        result["warmup_latency_ms"] = round(warmup.latency_ms, 3)
        results.append(result)
        metadata[model] = model_metadata

    evidence = {
        "schema_version": 1,
        "evaluation_id": config["evaluation_id"],
        "run_at": datetime.now(UTC).isoformat(),
        "dataset": config["dataset"],
        "prompt": config["prompt"],
        "runtime": {"name": "Ollama", "version": client.runtime_version()},
        "hardware": hardware_context(),
        "options": config["options"],
        "gates": config["gates"],
        "model_metadata": metadata,
        "models": results,
        "decision": select_baseline(results, config["gates"]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(evidence["decision"], indent=2))
    return 0 if evidence["decision"]["selected_model"] else 2


def load_config(path: Path) -> dict[str, Any]:
    """Load a Phase 1 evaluation configuration."""
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvaluationError(f"cannot load evaluation config: {error}") from error
    required = {"evaluation_id", "dataset", "prompt", "models", "endpoint", "options", "gates"}
    if config.get("schema_version") != 1 or not required.issubset(config):
        raise EvaluationError("evaluation config is missing required schema_version 1 fields")
    if not isinstance(config["models"], list) or len(config["models"]) < 2:
        raise EvaluationError("evaluation config must contain at least two models")
    return config


def hardware_context() -> dict[str, str]:
    """Return a compact, non-sensitive local hardware class."""
    return {
        "system": platform.system(),
        "release": platform.mac_ver()[0],
        "architecture": platform.machine(),
        "chip": _sysctl("machdep.cpu.brand_string"),
        "memory_bytes": _sysctl("hw.memsize"),
    }


def _sysctl(key: str) -> str:
    result = subprocess.run(
        ["sysctl", "-n", key],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvaluationError as error:
        print(f"evaluation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
