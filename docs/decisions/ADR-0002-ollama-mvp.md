---
id: ollama-mvp-decision
title: ADR-0002 — Ollama as the Initial MVP Runtime
type: decision
status: proposed
authority: canonical
relations:
  - type: implements
    target: local-first-decision
  - type: depends-on
    target: model-comparison
  - type: informs
    target: system-overview
last_reviewed: 2026-07-15
---

# ADR-0002 — Ollama as the Initial MVP Runtime

## Context

The MVP needs a local runtime that is simple to install, exposes a localhost API,
supports model switching, and works on Apple Silicon. Candidates include Ollama,
llama.cpp server, MLX-based servers, and LM Studio.

## Proposed decision

Use Ollama for the first working backend while keeping a runtime-neutral backend
interface.

## Rationale

Ollama is expected to minimize prototype setup and simplify model comparison.
This expectation must be validated during Phase 1 rather than treated as a
completed benchmark.

## Consequences

- Prompt and validation logic must not depend on Ollama-specific response types.
- Runtime availability, timeout, model configuration, and errors need explicit
  handling.
- The decision should move to `accepted` only after model and latency evidence is
  recorded in [Local Model Comparison](../evaluation/model-comparison.md).
