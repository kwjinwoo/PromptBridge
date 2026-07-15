---
id: roadmap-phase-5-refine-mode
title: Phase 5 — Refine Mode
type: roadmap-phase
status: deferred
authority: canonical
relations:
  - type: part-of
    target: project-roadmap
  - type: depends-on
    target: roadmap-phase-4-macos-application
  - type: implements
    target: refine-mode
  - type: depends-on
    target: preservation-validator
  - type: depends-on
    target: evaluation-methodology
last_reviewed: 2026-07-15
---

# Phase 5 — Refine Mode

## Objective

Add an explicitly selected mode that clarifies and structures prompts without
inventing requirements.

## Scope

- Mode-specific prompt and user interaction
- Requirement extraction and coverage evaluation
- Hallucinated-requirement detection
- Translate/Refine comparison preview
- Refine-specific evaluation dataset

## Exit criteria

- Multiple source requirements remain represented in the result.
- Added-requirement failures are measured and categorized.
- Refine Mode is clearly distinguishable from Translate Mode in the UI.
- Preview remains the default until an explicit decision approves otherwise.
