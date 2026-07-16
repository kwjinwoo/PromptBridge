---
id: roadmap-phase-1-quality-validation
title: Phase 1 — Transformation Quality Validation
type: roadmap-phase
status: completed
authority: canonical
relations:
  - type: part-of
    target: project-roadmap
  - type: depends-on
    target: translate-mode
  - type: informs
    target: model-comparison
  - type: informs
    target: ollama-mvp-decision
last_reviewed: 2026-07-16
---

# Phase 1 — Transformation Quality Validation

## Objective

Determine whether candidate local models can transform Korean developer prompts
with adequate intent preservation, technical preservation, latency, and output
discipline.

## Scope

- Create an initial synthetic evaluation dataset.
- Define the Translate Mode system prompt.
- Compare local model candidates through a consistent runtime.
- Measure preservation, requirement coverage, hallucinated requirements, and
  latency.
- Classify failure modes across C++, Python, CMake, Metal, MLIR, LLVM, Git, and
  Docker prompts.

## Deliverables

- Versioned dataset and evaluation configuration
- Reproducible evaluation runner
- Model comparison report
- Baseline model and prompt decision

## Exit criteria

Phase 1 is complete only when all of the following have repository evidence:

- A versioned, synthetic dataset contains at least 16 cases, with at least two
  cases for each of C++, Python, CMake, Metal, MLIR, LLVM, Git, and Docker.
- Dataset scoring rules deterministically measure exact protected-element
  preservation, requirement coverage, forbidden additions, and output
  discipline. Valid scoring paraphrases found during review have regression
  tests.
- A versioned Translate Mode prompt, evaluation configuration, and runner can
  reproduce the comparison through a localhost-only runtime.
- At least two local models run the identical dataset, prompt, generation
  parameters, runtime version, and hardware class.
- A baseline passes all decision gates: 100% request-level protected-element
  checks, at least 90% requirement coverage, 0% detected forbidden additions,
  100% output discipline, and warm median latency no greater than 2,000 ms.
- The comparison records model and quantization metadata, warm latency evidence,
  known failure classes, scoring limitations, and the baseline decision.

## Completion evidence

Completed on 2026-07-16. The versioned
[dataset](../../evaluation/datasets/translate-v1.json),
[prompt](../../evaluation/prompts/translate-v1.txt),
[configuration](../../evaluation/configs/phase1-v1.json),
[runner](../../scripts/run_evaluation.py), and
[Apple M5 result](../../evaluation/results/phase1-apple-m5-2026-07-16.json)
provide the reproducible evidence.

The comparison selected `qwen3.5:4b` Q4_K_M. It passed all 16 cases with 100%
protected-element preservation, 100% requirement coverage, 0% detected
forbidden additions, 100% output discipline, and 1,085 ms warm median latency.
The [model comparison](../evaluation/model-comparison.md) records the competing
result, failure classes, and evaluator limitations.
