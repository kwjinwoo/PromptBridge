---
id: roadmap-phase-2-preservation-validator
title: Phase 2 — Preservation Pipeline
type: roadmap-phase
status: completed
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
last_reviewed: 2026-07-17
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

Phase 2 is complete only when all of the following have repository evidence:

- One detector returns non-overlapping spans for inline code, fenced code, POSIX
  paths, HTTP(S) URLs, supported CLI commands, unambiguous identifiers, numbers,
  and versions in synthetic Korean developer prompts.
- Inline code, paths, URLs, supported commands, and unambiguous identifiers use
  source-collision-resistant placeholders. Fenced code, numbers, and versions
  remain visible for contextual transformation.
- Restoration requires every placeholder exactly once and in source order.
  Missing, duplicated, mutated, or reordered placeholders fail closed.
- Validation checks original occurrence counts for every required category.
  Fenced code therefore passes only when its complete fence, language tag,
  indentation, and content remain byte-for-byte identical.
- Findings identify the category, failure code, severity, and expected and
  observed counts without embedding the full prompt or protected values in their
  descriptions.
- A restoration or validation failure receives at most one retry with the failed
  categories. A second failure returns no transformed text and is not safe to
  apply. Runtime failures remain distinct and do not expose raw exception text.
- Focused preservation tests, the complete Python suite, documentation graph
  validation, and the repository pre-commit quality gate pass.

## Completion evidence

Completed on 2026-07-17. The deterministic
[implementation](../../src/promptbridge/preservation.py) and its synthetic
[unit and regression tests](../../tests/test_preservation.py) provide evidence
for detection, collision-resistant protection, exact restoration, category-level
validation, fail-closed results, and the bounded retry contract.

Regex-based detection intentionally covers only the unambiguous MVP syntax above.
Ambiguous identifiers, command grammars outside the supported patterns, semantic
requirement coverage, and Markdown AST or Tree-sitter analysis remain outside
this phase.
