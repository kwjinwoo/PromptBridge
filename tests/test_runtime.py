import io
import json
import unittest
from unittest.mock import patch
from urllib.error import URLError

from promptbridge.cli import main
from promptbridge.runtime import OllamaRuntime, RuntimeConfigurationError


class _Response:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = json.dumps(payload).encode()

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


class OllamaRuntimeTests(unittest.TestCase):
    def test_rejects_non_loopback_runtime_endpoint(self) -> None:
        with self.assertRaises(RuntimeConfigurationError):
            OllamaRuntime(endpoint="https://models.example.test")

    def test_sends_evaluation_backed_options_and_returns_prompt_only_response(self) -> None:
        requests: list[object] = []

        def open_request(request: object, *, timeout: float) -> _Response:
            requests.append((request, timeout))
            return _Response({"response": "Check `parse_item`.", "done": True})

        runtime = OllamaRuntime(
            endpoint="http://127.0.0.1:11434",
            model="qwen3.5:4b",
            timeout=2.5,
            open_request=open_request,
        )

        result = runtime.transform("`parse_item`을 확인해.", ())

        self.assertEqual(result, "Check `parse_item`.")
        request, timeout = requests[0]
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, "http://127.0.0.1:11434/api/generate")
        self.assertEqual(timeout, 2.5)
        self.assertEqual(payload["model"], "qwen3.5:4b")
        self.assertFalse(payload["stream"])
        self.assertEqual(
            payload["options"],
            {"temperature": 0, "seed": 42, "num_ctx": 4096, "num_predict": 1024},
        )
        self.assertIn("Return only the transformed prompt", payload["system"])
        self.assertIn("Do not add backticks", payload["system"])
        self.assertNotIn("Return only the transformed prompt", payload["prompt"])

    def test_runtime_error_is_sanitized_by_preservation_pipeline(self) -> None:
        def unavailable(request: object, timeout: float) -> _Response:
            raise URLError("synthetic private runtime detail")

        runtime = OllamaRuntime(open_request=unavailable)

        result = runtime.run("`parse_item`을 확인해.")

        self.assertFalse(result.safe_to_apply)
        self.assertEqual(result.failure_kind.value, "runtime")
        self.assertNotIn("synthetic private runtime detail", result.message)

    def test_lists_every_required_placeholder_without_exposing_protected_values(self) -> None:
        requests: list[object] = []

        def open_request(request: object, *, timeout: float) -> _Response:
            requests.append(request)
            return _Response(
                {"response": "__PB_INLINE_CODE_0123456789ab_0__ __PB_PATH_0123456789ab_1__"}
            )

        runtime = OllamaRuntime(open_request=open_request)
        protected = "__PB_INLINE_CODE_0123456789ab_0__이 __PB_PATH_0123456789ab_1__를 확인해."

        runtime.transform(protected, ())

        payload = json.loads(requests[0].data)
        self.assertIn(
            "Required placeholders: __PB_INLINE_CODE_0123456789ab_0__, __PB_PATH_0123456789ab_1__",
            payload["prompt"],
        )

    def test_removes_only_model_added_backticks_around_intact_placeholders(self) -> None:
        token = "__PB_PATH_0123456789ab_0__"

        def open_request(request: object, *, timeout: float) -> _Response:
            return _Response({"response": f"Read `{token}`."})

        result = OllamaRuntime(open_request=open_request).transform(f"{token}를 읽어.", ())

        self.assertEqual(result, f"Read {token}.")


class CommandLineTests(unittest.TestCase):
    def test_reads_source_from_stdin_and_writes_structured_json(self) -> None:
        stdin = io.StringIO("`parse_item`을 확인해.")
        stdout = io.StringIO()

        with (
            patch("promptbridge.cli.sys.stdin", stdin),
            patch("promptbridge.cli.sys.stdout", stdout),
            patch(
                "promptbridge.cli.OllamaRuntime.transform",
                return_value="Check __PB_ignored_0__.",
            ),
        ):
            exit_code = main([])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertFalse(payload["safe_to_apply"])
        self.assertEqual(payload["failure_kind"], "restoration")
        self.assertNotIn("`parse_item`", payload["message"])


if __name__ == "__main__":
    unittest.main()
