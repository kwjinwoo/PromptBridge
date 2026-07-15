---
id: roadmap-phase-2-preservation-validator
title: Phase 2 — Preservation Pipeline
type: roadmap-phase
status: not-started
authority: canonical
relations:
  - type: part-of
    target: project-roadmap
  - type: depends-on
    target: roadmap-phase-1-quality-validation
  - type: implements
    target: protected-elements
  - type: implements
    target: preservation-validator
  - type: depends-on
    target: failure-policy
last_reviewed: 2026-07-15
---

# Phase 2 — Preservation Pipeline

## Objective

Extract, protect, restore, and validate technical elements deterministically.

## Scope

- Inline-code, fenced-code, path, URL, command, identifier, number, and version
  detection
- Placeholder assignment and restoration
- Category-level preservation validation
- Structured failure results and one safe retry
- Unit and regression tests

## Out of scope

- Tree-sitter-based analysis
- Full semantic requirement coverage
- Refine Mode

## Exit criteria

- Fenced code passes byte-level preservation tests.
- Every required placeholder is restored exactly once.
- Required identifiers, paths, commands, numbers, and versions are checked.
- Any required failure blocks automatic application.
- Failure findings identify the affected category without persisting prompt text.
