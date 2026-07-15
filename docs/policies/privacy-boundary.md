---
id: privacy-boundary
title: Privacy Boundary
type: policy
status: proposed
authority: canonical
relations:
  - type: implements
    target: product-invariants
  - type: constrains
    target: system-overview
  - type: constrains
    target: clipboard-state-machine
  - type: constrains
    target: evaluation-methodology
last_reviewed: 2026-07-15
---

# Privacy Boundary

PromptBridge processes developer prompts that may contain proprietary source
code, local paths, errors, credentials, or other sensitive information.

## Default boundary

- Transformation runs on the user's machine.
- Runtime servers listen only on localhost.
- Prompt source and transformed output are not persisted by default.
- Clipboard data is held only for the duration needed to complete or recover the
  active request.
- Telemetry is disabled unless a future explicit decision defines an opt-in,
  content-free design.

## Logs

Logs may contain request IDs, durations, mode, protected-element counts, failure
categories, and runtime status. They must not contain full prompts, code blocks,
clipboard contents, credentials, or private paths by default.

## Evaluation data

Committed evaluation fixtures must be synthetic, licensed for redistribution, or
explicitly sanitized. Real user prompts must not be promoted into the dataset as
part of normal operation.

## Future remote backends

A remote backend would cross the default privacy boundary and requires a new ADR,
clear UI disclosure, explicit user configuration, transport security, data
retention documentation, and separate evaluation.
