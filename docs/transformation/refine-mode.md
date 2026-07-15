---
id: refine-mode
title: Refine Mode
type: transformation
status: deferred
authority: canonical
relations:
  - type: implements
    target: product-invariants
  - type: depends-on
    target: protected-elements
  - type: depends-on
    target: translate-mode
  - type: informs
    target: roadmap-phase-5-refine-mode
last_reviewed: 2026-07-15
---

# Refine Mode

Refine Mode transforms a Korean developer instruction into a clearer, more
actionable English prompt. It is explicitly selected by the user because it
permits limited interpretation beyond direct translation.

## Allowed refinement

- Make the requested task type explicit when reasonably clear.
- Organize multiple existing requirements.
- Replace vague phrasing with a clearer description that preserves the evident
  goal.
- Improve readability and instruction structure.

## Forbidden refinement

- Adding features or deliverables not requested by the user.
- Selecting a new technology without source support.
- Introducing performance, security, or compatibility goals absent from the
  source.
- Changing implementation permission into an analysis-only request or vice
  versa.
- Solving or answering the instruction.

## Preview behavior

Refine Mode should show a preview by default until requirement-coverage and
hallucinated-requirement evaluations demonstrate that automatic application is
safe.

Implementation is planned for [Phase 5](../roadmap/phase-5-refine-mode.md).
