---
id: translate-mode
title: Translate Mode
type: transformation
status: proposed
authority: canonical
relations:
  - type: implements
    target: product-invariants
  - type: depends-on
    target: protected-elements
  - type: informs
    target: prompt-pipeline
last_reviewed: 2026-07-16
---

# Translate Mode

Translate Mode is the default transformation mode. It converts Korean developer
instructions into clear English while preserving intent, structure, and scope.

## Required behavior

- Translate Korean natural language into English.
- Preserve the task type, confidence, uncertainty, requirement order, and output
  format.
- Keep protected tokens unchanged.
- Preserve Markdown structure.
- Return only the transformed prompt.
- Do not answer the prompt.
- Do not add requirements, explanations, or recommendations.

## Example

Source:

```text
이 함수가 thread-safe한지 확인해줘.
```

Result:

```text
Check whether this function is thread-safe.
```

## Initial generation parameters

The Phase 1 baseline uses the versioned
[`translate-v1`](../../evaluation/prompts/translate-v1.txt) prompt with
`qwen3.5:4b` Q4_K_M, temperature 0, seed 42, a 4,096-token context, a
1,024-token output cap, and model thinking disabled. These are evaluation-backed
baseline values, not universal constants. Model-specific changes must use the
[evaluation methodology](../evaluation/methodology.md).

## Automatic application

Translate Mode may be automatically applied only after all required preservation
checks pass. Failure behavior is defined by the
[Failure Policy](../policies/failure-policy.md).
