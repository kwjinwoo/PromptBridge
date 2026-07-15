---
id: evaluation-methodology
title: Evaluation Methodology
type: evaluation
status: proposed
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
last_reviewed: 2026-07-15
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

## Decision boundary

Evaluation evidence informs model and prompt decisions. An LLM-based quality
judge may supplement human review, but deterministic preservation checks remain
authoritative for automatic application.
