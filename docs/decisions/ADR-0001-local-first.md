---
id: local-first-decision
title: ADR-0001 — Local-First Prompt Processing
type: decision
status: accepted
authority: canonical
relations:
  - type: implements
    target: privacy-boundary
  - type: constrains
    target: system-overview
  - type: informs
    target: ollama-mvp-decision
last_reviewed: 2026-07-15
---

# ADR-0001 — Local-First Prompt Processing

## Context

Developer prompts may contain private source code, internal paths, logs, and
credentials. The product's initial value proposition includes avoiding an
external translation service.

## Decision

Prompt transformation is local-first. The MVP uses a local inference runtime,
does not require a cloud translation API, does not persist prompt contents by
default, and exposes any service endpoint on localhost only.

## Consequences

- Model quality and latency depend on local hardware and model selection.
- Runtime setup and health must be visible to the user.
- Evaluation must include practical Apple Silicon configurations.
- A future remote backend requires a separate ADR and explicit privacy design.
