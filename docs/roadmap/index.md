---
id: project-roadmap
title: Project Roadmap
type: roadmap
status: active
authority: canonical
relations:
  - type: depends-on
    target: product-invariants
  - type: defines
    target: roadmap-phase-1-quality-validation
  - type: defines
    target: roadmap-phase-2-preservation-validator
  - type: defines
    target: roadmap-phase-3-hotkey-prototype
  - type: defines
    target: roadmap-phase-4-macos-application
  - type: defines
    target: roadmap-phase-5-refine-mode
  - type: defines
    target: roadmap-phase-6-quality-improvements
last_reviewed: 2026-07-16
---

# Project Roadmap

The roadmap is organized around verifiable exit criteria rather than speculative
dates. [Project Status](../status.md) records the current repository state.

## Phase 0 — Foundation

Status: **Completed**

Establish canonical documentation, product invariants, the knowledge graph, and
documentation validation. Phase 0 is complete when the initial documents are
reviewed and automated graph checks pass.

The product overview and invariants were reviewed against their connected
transformation, architecture, failure, and privacy documents. The canonical
graph validator and the complete local pre-commit suite passed at Phase 0 exit.

## Delivery phases

| Phase | Goal | Status | Primary exit criterion |
|---|---|---|---|
| [Phase 1](phase-1-quality-validation.md) | Validate transformation quality | In progress | A baseline local model is selected from reproducible results |
| [Phase 2](phase-2-preservation-validator.md) | Build preservation pipeline | Not started | Required protected-element tests pass |
| [Phase 3](phase-3-hotkey-prototype.md) | Prove end-to-end replacement | Not started | Selection transforms safely in target apps |
| [Phase 4](phase-4-macos-application.md) | Deliver the MVP application | Not started | Menu-bar MVP satisfies product invariants |
| [Phase 5](phase-5-refine-mode.md) | Add explicit refinement | Deferred | Coverage and hallucination gates pass |
| [Phase 6](phase-6-quality-improvements.md) | Improve quality and breadth | Deferred | Regression and compatibility suites are established |

## Roadmap principles

- A phase is completed only when its exit criteria have repository evidence.
- Work may be explored early, but status reflects verified completion.
- Scope changes must update the relevant phase document and current status.
- Privacy and safe-replacement invariants apply to every phase.
