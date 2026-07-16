---
id: evaluation-methodology
title: Evaluation Methodology
type: evaluation
status: active
authority: canonical
relations:
  - type: validates
    target: translate-mode
  - type: validates
    target: preservation-validator
  - type: informs
    target: model-comparison
  - type: informs
    target: application-compatibility
last_reviewed: 2026-07-16
---

# Evaluation Methodology

PromptBridge evaluates translation quality separately from technical
preservation and safe application.

## Metrics

### Preservation accuracy

The fraction of protected elements reproduced according to category rules. For
automatic application, the request-level target is all required checks passing,
not merely a high average.

### Requirement coverage

The fraction of source actions, constraints, and requested outputs represented
in the transformed prompt.

### Hallucinated requirement rate

The rate at which the result introduces a requirement absent from the source.
Translate Mode targets zero.

### Output discipline

Whether the model returns only the transformed prompt without answering,
explaining, adding a preamble, or changing requested formatting.

### Latency

Measure capture, preprocessing, inference, restoration, validation, and paste
separately. Record warm and cold runtime behavior.

## Dataset principles

- Use synthetic, licensed, or sanitized cases only.
- Version cases and expected protected elements.
- Cover C++, Python, CMake, Metal, MLIR, LLVM, Git, Docker, Markdown, mixed logs,
  and multi-requirement prompts.
- Preserve failing cases as regression fixtures.
- Record model, quantization, runtime, hardware class, prompt version, and
  generation parameters for reproducibility.

## Phase 1 deterministic scoring

The initial Translate Mode dataset is
[`promptbridge-translate-v1`](../../evaluation/datasets/translate-v1.json). Each
case declares exact protected elements, groups of acceptable English phrases for
source requirements, and phrases that would indicate an added requirement.

The Phase 1 runner computes:

- protected-element accuracy and the stricter request-level all-protected pass;
- requirement coverage as the fraction of expected phrase groups represented;
- detected forbidden-addition rate from case-specific prohibited phrases;
- output discipline from non-empty output, preamble rejection, and untranslated
  Korean prose rejection; and
- end-to-end warm latency measured around the localhost model request.

These phrase rules are a transparent deterministic proxy, not a complete
semantic judge. A human must review apparent misses before changing a rule.
Accepted paraphrases require a regression test, and the entire comparison must
be rerun after calibration. The runner and tests are in
[`scripts/run_evaluation.py`](../../scripts/run_evaluation.py) and
[`tests/test_evaluation.py`](../../tests/test_evaluation.py).

## Phase 1 decision gates

The baseline must achieve 100% request-level protected-element checks, at least
90% requirement coverage, 0% detected forbidden additions, 100% output
discipline, and warm median latency at or below 2,000 ms. The comparison records
warm p95 latency for context, but Phase 1 does not gate on it.

## Decision boundary

Evaluation evidence informs model and prompt decisions. An LLM-based quality
judge may supplement human review, but deterministic preservation checks remain
authoritative for automatic application.
