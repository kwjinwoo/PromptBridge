import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from promptbridge_eval.evaluation import (
    Case,
    EvaluationError,
    ModelResponse,
    OllamaClient,
    aggregate_scores,
    evaluate_model,
    load_cases,
    score_output,
    select_baseline,
)


class DatasetTests(unittest.TestCase):
    def test_phase1_dataset_covers_each_technical_category_twice(self) -> None:
        cases = load_cases(Path("evaluation/datasets/translate-v1.json"))
        categories = [case.category for case in cases]

        self.assertEqual(len(cases), 16)
        for category in ("C++", "Python", "CMake", "Metal", "MLIR", "LLVM", "Git", "Docker"):
            self.assertGreaterEqual(categories.count(category), 2)

    def test_load_cases_rejects_duplicate_ids(self) -> None:
        payload = {
            "schema_version": 1,
            "dataset_id": "synthetic-test-v1",
            "cases": [self._case("duplicate"), self._case("duplicate")],
        }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dataset.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(EvaluationError, "duplicate case id"):
                load_cases(path)

    @staticmethod
    def _case(case_id: str) -> dict[str, object]:
        return {
            "id": case_id,
            "category": "Python",
            "source": "`parse_item`이 Python 3.11에서 동작하는지 확인해줘.",
            "protected_elements": ["parse_item", "Python 3.11"],
            "requirements": [["check", "verify"], ["works", "runs"]],
            "forbidden_additions": ["rewrite", "benchmark"],
        }


class ScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = Case(
            case_id="python-verify",
            category="Python",
            source="`parse_item`이 Python 3.11에서 동작하는지 확인해줘.",
            protected_elements=("parse_item", "Python 3.11"),
            requirements=(("check", "verify"), ("works", "runs")),
            forbidden_additions=("rewrite", "benchmark"),
        )

    def test_score_output_accepts_a_disciplined_translation(self) -> None:
        score = score_output(
            self.case,
            "Check whether `parse_item` works in Python 3.11.",
        )

        self.assertEqual(score.preservation_accuracy, 1.0)
        self.assertEqual(score.requirement_coverage, 1.0)
        self.assertEqual(score.hallucinated_requirement_rate, 0.0)
        self.assertTrue(score.output_disciplined)

    def test_score_output_reports_each_failure_dimension(self) -> None:
        score = score_output(
            self.case,
            "Here is the translation: Rewrite parse_item and benchmark it.",
        )

        self.assertEqual(score.preservation_accuracy, 0.5)
        self.assertEqual(score.requirement_coverage, 0.0)
        self.assertEqual(score.hallucinated_requirement_rate, 1.0)
        self.assertFalse(score.output_disciplined)

    def test_score_output_rejects_untranslated_korean_prose(self) -> None:
        score = score_output(
            self.case,
            "Check whether `parse_item`이 works in Python 3.11.",
        )

        self.assertFalse(score.output_disciplined)

    def test_score_output_rejects_conversational_preamble(self) -> None:
        score = score_output(
            self.case,
            "Okay, here's the translation: Check whether parse_item works in Python 3.11.",
        )

        self.assertFalse(score.output_disciplined)

    def test_phase1_markers_recognize_valid_paraphrases(self) -> None:
        cases = {
            case.case_id: case for case in load_cases(Path("evaluation/datasets/translate-v1.json"))
        }
        outputs = {
            "python-pytest-failure": "Analyze why a `TypeError: expected str, got bytes` error occurs in pytest and propose only solutions without executing them.",
            "metal-threadgroup-reduction": "Review whether there is a race condition in the memory access of the `threadgroup` for the `reduce_sum` kernel, without modifying the code.",
            "mlir-lowering-failure": "Diagnose why `arith.addi` is not being transformed to `llvm.add`, and check the order of passes.",
            "llvm-gep-explanation": "Explain why the second type argument is required for `getelementptr` in opaque pointer mode.",
            "git-rebase-explanation": "Explain what commits `git rebase --onto main release feature` moves without using examples.",
        }

        for case_id, output in outputs.items():
            with self.subTest(case_id=case_id):
                self.assertEqual(score_output(cases[case_id], output).requirement_coverage, 1.0)

    def test_aggregate_scores_uses_request_level_pass_rates(self) -> None:
        passing = score_output(self.case, "Verify that parse_item runs in Python 3.11.")
        failing = score_output(self.case, "Here is the translation: Rewrite parse_item.")

        summary = aggregate_scores([passing, failing], latencies_ms=[800.0, 1200.0])

        self.assertEqual(summary["case_count"], 2)
        self.assertEqual(summary["protected_pass_rate"], 0.5)
        self.assertEqual(summary["discipline_pass_rate"], 0.5)
        self.assertEqual(summary["warm_latency_median_ms"], 1000.0)


class RuntimeBoundaryTests(unittest.TestCase):
    def test_ollama_client_rejects_non_loopback_endpoints(self) -> None:
        with self.assertRaisesRegex(EvaluationError, "loopback"):
            OllamaClient("https://example.com")

    def test_ollama_client_accepts_ipv4_and_ipv6_loopback(self) -> None:
        OllamaClient("http://127.0.0.1:11434")
        OllamaClient("http://[::1]:11434")

    def test_ollama_client_disables_model_thinking(self) -> None:
        response = _FakeHTTPResponse({"message": {"content": "Translated."}})

        with patch("urllib.request.urlopen", return_value=response) as urlopen:
            OllamaClient("http://127.0.0.1:11434").generate(
                "model", "system", "source", {"temperature": 0}
            )

        request = urlopen.call_args.args[0]
        body = json.loads(request.data)
        self.assertIs(body["think"], False)

    def test_model_metadata_includes_immutable_digest(self) -> None:
        client = OllamaClient("http://127.0.0.1:11434")
        with patch.object(
            client,
            "_request_json",
            side_effect=[
                {
                    "details": {
                        "family": "test",
                        "parameter_size": "4B",
                        "quantization_level": "Q4_K_M",
                    },
                    "modified_at": "2026-07-16T00:00:00Z",
                },
                {"models": [{"name": "test:4b", "digest": "sha256:abc123", "size": 42}]},
            ],
        ):
            metadata = client.model_metadata("test:4b")

        self.assertEqual(metadata["digest"], "sha256:abc123")
        self.assertEqual(metadata["size_bytes"], 42)

    def test_evaluate_model_scores_every_case_with_identical_options(self) -> None:
        cases = (
            Case(
                case_id="one",
                category="Python",
                source="첫 번째를 확인해줘.",
                protected_elements=("first_item",),
                requirements=(("check",),),
                forbidden_additions=("rewrite",),
            ),
            Case(
                case_id="two",
                category="Git",
                source="두 번째를 확인해줘.",
                protected_elements=("second_item",),
                requirements=(("check",),),
                forbidden_additions=("rewrite",),
            ),
        )
        client = _FakeClient(
            {
                "첫 번째를 확인해줘.": ModelResponse("Check first_item.", 700.0),
                "두 번째를 확인해줘.": ModelResponse("Check second_item.", 900.0),
            }
        )

        result = evaluate_model(
            client=client,
            model="test-model",
            system_prompt="Translate only.",
            cases=cases,
            options={"temperature": 0, "seed": 42},
        )

        self.assertEqual(result["summary"]["case_count"], 2)
        self.assertEqual(result["summary"]["protected_pass_rate"], 1.0)
        self.assertEqual(len(result["cases"]), 2)
        self.assertEqual(
            client.calls,
            [
                (
                    "test-model",
                    "Translate only.",
                    "첫 번째를 확인해줘.",
                    {"temperature": 0, "seed": 42},
                ),
                (
                    "test-model",
                    "Translate only.",
                    "두 번째를 확인해줘.",
                    {"temperature": 0, "seed": 42},
                ),
            ],
        )

    def test_select_baseline_requires_every_quality_gate(self) -> None:
        gates = {
            "protected_pass_rate_min": 1.0,
            "requirement_coverage_min": 0.9,
            "hallucinated_requirement_rate_max": 0.0,
            "discipline_pass_rate_min": 1.0,
            "warm_latency_median_ms_max": 2000.0,
        }
        fast_complete = _model_result("fast-complete", coverage=0.95, latency=900.0)
        faster_incomplete = _model_result("faster-incomplete", coverage=0.8, latency=600.0)

        decision = select_baseline([faster_incomplete, fast_complete], gates)

        self.assertEqual(decision["selected_model"], "fast-complete")
        self.assertEqual(decision["eligible_models"], ["fast-complete"])


def _model_result(model: str, coverage: float, latency: float) -> dict[str, object]:
    return {
        "model": model,
        "summary": {
            "protected_pass_rate": 1.0,
            "requirement_coverage": coverage,
            "hallucinated_requirement_rate": 0.0,
            "discipline_pass_rate": 1.0,
            "warm_latency_median_ms": latency,
        },
    }


class _FakeClient:
    def __init__(self, responses: dict[str, ModelResponse]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, str, str, dict[str, object]]] = []

    def generate(
        self,
        model: str,
        system_prompt: str,
        source: str,
        options: dict[str, object],
    ) -> ModelResponse:
        self.calls.append((model, system_prompt, source, options))
        return self.responses[source]


class _FakeHTTPResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self) -> "_FakeHTTPResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode()


if __name__ == "__main__":
    unittest.main()
