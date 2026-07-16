---
id: ollama-mvp-decision
title: ADR-0002 — Ollama as the Initial MVP Runtime
type: decision
status: accepted
authority: canonical
relations:
  - type: implements
    target: local-first-decision
  - type: depends-on
    target: model-comparison
  - type: informs
    target: system-overview
last_reviewed: 2026-07-16
---

# ADR-0002 — Ollama as the Initial MVP Runtime

## Context

The MVP needs a local runtime that is simple to install, exposes a localhost API,
supports model switching, and works on Apple Silicon. Candidates include Ollama,
llama.cpp server, MLX-based servers, and LM Studio.

## Decision

Use Ollama for the first working backend while keeping a runtime-neutral backend
interface.

## Rationale

The Phase 1 comparison ran two local models through Ollama 0.32.0 with identical
inputs and selected `qwen3.5:4b` from reproducible quality and latency evidence.
The localhost API supported model switching, deterministic generation settings,
runtime metadata, and warm inference without sending synthetic prompts to a
cloud service. See [Local Model Comparison](../evaluation/model-comparison.md).

## Consequences

- Prompt and validation logic must not depend on Ollama-specific response types.
- Runtime availability, timeout, model configuration, and errors need explicit
  handling.
- The application must disable cloud-backed models, bind the service to
  localhost, and avoid prompt history.
- Accepting Ollama does not accept an Ollama-specific prompt pipeline contract.
