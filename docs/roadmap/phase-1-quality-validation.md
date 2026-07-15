---
id: roadmap-phase-1-quality-validation
title: Phase 1 — Transformation Quality Validation
type: roadmap-phase
status: not-started
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
last_reviewed: 2026-07-15
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

- Dataset categories and scoring rules are documented.
- At least two viable local models are compared using identical cases.
- The selected baseline has recorded quality and latency evidence.
- Known failure classes and mitigation candidates are documented.
