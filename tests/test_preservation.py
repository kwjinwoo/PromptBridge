import unittest
from itertools import pairwise

from promptbridge.preservation import (
    ElementCategory,
    FailureKind,
    PreservationPipeline,
    protect,
    restore,
    validate,
)


class ProtectionTests(unittest.TestCase):
    def test_detects_every_phase_two_category_without_overlapping_spans(self) -> None:
        source = (
            "`parse_item`으로 https://example.test/api의 ./config/app.yaml을 확인하고 "
            "git rebase --onto main release feature를 실행해. "
            "std::span과 build_target을 Python 3.11에서 2번 확인해.\n\n"
            "```python\nprint('그대로')\n```"
        )

        result = protect(source)

        categories = {element.category for element in result.elements}
        self.assertEqual(
            categories,
            {
                ElementCategory.INLINE_CODE,
                ElementCategory.URL,
                ElementCategory.PATH,
                ElementCategory.COMMAND,
                ElementCategory.IDENTIFIER,
                ElementCategory.VERSION,
                ElementCategory.NUMBER,
                ElementCategory.FENCED_CODE,
            },
        )
        spans = sorted((element.start, element.end) for element in result.elements)
        self.assertTrue(
            all(left_end <= right_start for (_, left_end), (right_start, _) in pairwise(spans))
        )

    def test_protects_eligible_elements_but_keeps_code_numbers_and_versions_visible(self) -> None:
        source = (
            "`parse_item`과 /tmp/input.txt를 Python 3.11에서 확인해.\n```python\nprint('원문')\n```"
        )

        result = protect(source)

        self.assertNotIn("`parse_item`", result.text)
        self.assertNotIn("/tmp/input.txt", result.text)
        self.assertIn("Python 3.11", result.text)
        self.assertIn("```python\nprint('원문')\n```", result.text)
        self.assertTrue(
            all(result.text.count(element.placeholder) == 1 for element in result.protected)
        )

    def test_placeholders_do_not_collide_with_source_text(self) -> None:
        source = "기존 __PB_000000000000_0__와 `item`을 보존해."

        result = protect(source)

        self.assertNotIn(result.protected[0].placeholder, source)


class RestorationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.protection = protect("`parse_item`과 /tmp/input.txt를 확인해.")

    def test_restores_every_placeholder_exactly_once(self) -> None:
        transformed = self.protection.text.replace("확인해", "Check")

        result = restore(transformed, self.protection.protected)

        self.assertTrue(result.succeeded)
        self.assertEqual(result.text, "`parse_item`과 /tmp/input.txt를 Check.")
        self.assertEqual(result.findings, ())

    def test_reports_missing_and_duplicated_placeholders_without_prompt_values(self) -> None:
        first, second = self.protection.protected
        transformed = self.protection.text.replace(first.placeholder, "").replace(
            second.placeholder, second.placeholder + second.placeholder
        )

        result = restore(transformed, self.protection.protected)

        self.assertFalse(result.succeeded)
        self.assertIsNone(result.text)
        self.assertEqual(
            {finding.code for finding in result.findings},
            {"placeholder_missing", "placeholder_duplicated"},
        )
        for finding in result.findings:
            self.assertNotIn(first.original, finding.description)
            self.assertNotIn(second.original, finding.description)

    def test_rejects_reordered_placeholders(self) -> None:
        first, second = self.protection.protected
        transformed = (
            self.protection.text.replace(first.placeholder, "__SWAP__")
            .replace(second.placeholder, first.placeholder)
            .replace("__SWAP__", second.placeholder)
        )

        result = restore(transformed, self.protection.protected)

        self.assertFalse(result.succeeded)
        self.assertEqual({finding.code for finding in result.findings}, {"placeholder_reordered"})

    def test_rejects_mutated_placeholder_as_missing(self) -> None:
        first = self.protection.protected[0]
        transformed = self.protection.text.replace(first.placeholder, first.placeholder[:-1])

        result = restore(transformed, self.protection.protected)

        self.assertFalse(result.succeeded)
        self.assertIn("placeholder_missing", {finding.code for finding in result.findings})


class ValidationTests(unittest.TestCase):
    def test_validates_required_categories_and_byte_exact_fenced_code(self) -> None:
        source = (
            "`parse_item` /tmp/input.txt https://example.test git status "
            "std::span Python 3.11 2048\n"
            "```cpp\nint value = 1;\n```"
        )
        protection = protect(source)

        result = validate(protection.elements, source)

        self.assertTrue(result.succeeded)
        self.assertEqual(result.findings, ())

    def test_reports_each_changed_category_and_blocks_application(self) -> None:
        source = (
            "`parse_item` /tmp/input.txt https://example.test git status "
            "std::span Python 3.11 2048\n"
            "```cpp\nint value = 1;\n```"
        )
        protection = protect(source)
        changed = (
            "`parse_other` /tmp/output.txt https://invalid.test git log "
            "std::vector Python 3.12 4096\n"
            "```cpp\nint value = 2;\n```"
        )

        result = validate(protection.elements, changed)

        self.assertFalse(result.succeeded)
        self.assertEqual(
            {finding.category for finding in result.findings},
            {
                ElementCategory.INLINE_CODE,
                ElementCategory.PATH,
                ElementCategory.URL,
                ElementCategory.COMMAND,
                ElementCategory.IDENTIFIER,
                ElementCategory.VERSION,
                ElementCategory.NUMBER,
                ElementCategory.FENCED_CODE,
            },
        )


class PipelineTests(unittest.TestCase):
    def test_retries_one_preservation_failure_then_returns_safe_success(self) -> None:
        calls: list[tuple[str, tuple[ElementCategory, ...]]] = []

        def transform(text: str, failed_categories: tuple[ElementCategory, ...]) -> str:
            calls.append((text, failed_categories))
            token = protect("`item`을 번역해.").protected[0].placeholder
            if len(calls) == 1:
                return text.replace(token, "")
            return text.replace("번역해", "Translate")

        result = PreservationPipeline(transform).run("`item`을 번역해.")

        self.assertTrue(result.safe_to_apply)
        self.assertEqual(result.text, "`item`을 Translate.")
        self.assertEqual(result.retry_count, 1)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1][1], (ElementCategory.INLINE_CODE,))

    def test_retries_one_validation_failure_with_affected_category(self) -> None:
        calls: list[tuple[ElementCategory, ...]] = []

        def transform(text: str, failed_categories: tuple[ElementCategory, ...]) -> str:
            calls.append(failed_categories)
            if len(calls) == 1:
                return text.replace("2", "3")
            return text.replace("확인해", "Check")

        result = PreservationPipeline(transform).run("값 2를 확인해.")

        self.assertTrue(result.safe_to_apply)
        self.assertEqual(result.text, "값 2를 Check.")
        self.assertEqual(calls, [(), (ElementCategory.NUMBER,)])

    def test_second_failure_returns_structured_result_and_never_applies(self) -> None:
        call_count = 0

        def transform(text: str, failed_categories: tuple[ElementCategory, ...]) -> str:
            nonlocal call_count
            call_count += 1
            return "플레이스홀더 없음"

        result = PreservationPipeline(transform).run("`item`을 번역해.")

        self.assertFalse(result.safe_to_apply)
        self.assertIsNone(result.text)
        self.assertEqual(result.failure_kind, FailureKind.RESTORATION)
        self.assertEqual(result.retry_count, 1)
        self.assertEqual(call_count, 2)
        self.assertEqual(result.failed_categories, (ElementCategory.INLINE_CODE,))

    def test_runtime_failure_is_distinct_and_does_not_expose_exception_text(self) -> None:
        def transform(text: str, failed_categories: tuple[ElementCategory, ...]) -> str:
            raise RuntimeError("synthetic secret response")

        result = PreservationPipeline(transform).run("`item`을 번역해.")

        self.assertFalse(result.safe_to_apply)
        self.assertEqual(result.failure_kind, FailureKind.RUNTIME)
        self.assertNotIn("synthetic secret response", result.message)
        self.assertEqual(result.retry_count, 0)


if __name__ == "__main__":
    unittest.main()
