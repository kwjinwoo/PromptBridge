"""Local runtime boundary for the production prompt pipeline."""

from __future__ import annotations

import ipaddress
import json
import re
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from promptbridge.preservation import ElementCategory, PipelineResult, PreservationPipeline

TRANSLATE_INSTRUCTIONS = """You are PromptBridge Translate Mode. Transform the Korean developer instruction into clear English.

Rules:
1. Return only the transformed prompt. Do not add a preamble, label, explanation, or answer.
2. Preserve the requested task type, scope, constraints, order, uncertainty, and output format.
3. Do not add any requirement, recommendation, implementation detail, or example absent from the source.
4. Copy every identifier, path, URL, command, version, numeric value, error message, and technical token exactly, including punctuation and capitalization.
5. Copy fenced code blocks byte-for-byte, including the fence language, whitespace, and line breaks.
6. Preserve Markdown structure and inline code delimiters.
7. Translate all Korean prose into English. Do not execute the instruction.
8. Copy every placeholder beginning with __PB_ exactly once and in source order. Do not add backticks or any other characters around a placeholder.
"""


class RuntimeConfigurationError(ValueError):
    """Raised when a runtime would cross the local-only privacy boundary."""


OpenRequest = Callable[[Request, float], Any]
PLACEHOLDER_PATTERN = re.compile(r"__PB_[A-Z_]+_[0-9a-f]{12}_\d+__")


class OllamaRuntime:
    """Invoke an Ollama-compatible runtime through its loopback API."""

    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:11434",
        model: str = "qwen3.5:4b",
        timeout: float = 10.0,
        open_request: OpenRequest = urlopen,
    ) -> None:
        """Configure a local runtime without storing prompt content.

        Args:
            endpoint: Loopback-only Ollama base URL.
            model: Locally installed model identifier.
            timeout: Request timeout in seconds.
            open_request: Injectable URL opener used at the network boundary.

        Raises:
            RuntimeConfigurationError: If the endpoint is not a loopback HTTP URL.
        """
        self._endpoint = _validated_endpoint(endpoint)
        self._model = model
        self._timeout = timeout
        self._open_request = open_request

    def transform(
        self,
        text: str,
        failed_categories: tuple[ElementCategory, ...],
    ) -> str:
        """Return prompt-only model output for protected input text.

        Args:
            text: Prompt text with eligible technical values protected.
            failed_categories: Categories that failed the first preservation attempt.

        Returns:
            The model's transformed prompt.

        Raises:
            RuntimeError: If the local runtime response is unavailable or malformed.
        """
        retry_instruction = ""
        if failed_categories:
            categories = ", ".join(category.value for category in failed_categories)
            retry_instruction = (
                "\nA previous attempt failed preservation for these categories: "
                f"{categories}. Copy their protected values exactly.\n"
            )
        placeholders = tuple(dict.fromkeys(PLACEHOLDER_PATTERN.findall(text)))
        required_placeholders = ""
        if placeholders:
            required_placeholders = f"\nRequired placeholders: {', '.join(placeholders)}\n"
        system_instructions = f"{TRANSLATE_INSTRUCTIONS}{retry_instruction}"
        prompt = f"{required_placeholders}\nSource prompt:\n{text}"
        body = json.dumps(
            {
                "model": self._model,
                "system": system_instructions,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0,
                    "seed": 42,
                    "num_ctx": 4096,
                    "num_predict": 1024,
                },
            }
        ).encode()
        request = Request(
            f"{self._endpoint}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._open_request(request, timeout=self._timeout) as response:
                payload = json.loads(response.read())
        except Exception as error:
            raise RuntimeError("The local transformation runtime failed.") from error
        result = payload.get("response") if isinstance(payload, dict) else None
        if not isinstance(result, str) or not result.strip():
            raise RuntimeError("The local transformation runtime returned an invalid response.")
        for placeholder in placeholders:
            result = result.replace(f"`{placeholder}`", placeholder)
        return result

    def run(self, source: str) -> PipelineResult:
        """Run transformation, restoration, validation, and one safe retry.

        Args:
            source: Selected source prompt held in memory for this request.

        Returns:
            A structured safe-to-apply result or sanitized failure.
        """
        return PreservationPipeline(self.transform).run(source)


def _validated_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username:
        raise RuntimeConfigurationError("The runtime endpoint must be a loopback HTTP URL.")
    try:
        is_loopback = ipaddress.ip_address(parsed.hostname).is_loopback
    except ValueError:
        is_loopback = parsed.hostname == "localhost"
    if not is_loopback or parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise RuntimeConfigurationError("The runtime endpoint must be a loopback HTTP URL.")
    return endpoint.rstrip("/")
