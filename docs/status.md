---
id: project-status
title: Project Status
type: status
status: in-progress
authority: canonical
relations:
  - type: tracks
    target: project-roadmap
  - type: depends-on
    target: product-overview
last_reviewed: 2026-07-17
---

# Project Status

## Current phase

Phase 4 — The menu-bar macOS application is next after Phase 3 completed the
hotkey-driven safe replacement prototype.

## Overall status

| Area | State | Evidence |
|---|---|---|
| Product specification | Active | [Product Overview](product/overview.md), [Product Invariants](product/invariants.md) |
| Documentation graph | Implemented and passing locally | [Documentation Index](index.md) |
| Pre-commit quality gates | Implemented and passing | [Pre-commit Conventions](development/pre-commit.md) |
| Development conventions | Active | [Commit Convention](development/commit-convention.md), [Code Style](development/code-style.md), [Testing Convention](development/testing.md) |
| Agent documentation workflow | Active | [Agent Skills](development/agent-skills.md) |
| Evaluation runner | Implemented and passing | [Phase 1](roadmap/phase-1-quality-validation.md), [Raw Result](../evaluation/results/phase1-apple-m5-2026-07-16.json) |
| Translate prompt | Validated for Phase 1 baseline | [Translate Mode](transformation/translate-mode.md), [Model Comparison](evaluation/model-comparison.md) |
| Production prompt engine | Implemented; real runtime verified | [Prompt Pipeline](architecture/prompt-pipeline.md), [`runtime.py`](../src/promptbridge/runtime.py) |
| Preservation validator | Implemented and passing | [Phase 2](roadmap/phase-2-preservation-validator.md), [`tests/test_preservation.py`](../tests/test_preservation.py) |
| Hotkey prototype | Phase 3 completed | [Phase 3](roadmap/phase-3-hotkey-prototype.md), [`main.swift`](../Sources/PromptBridgeHotkey/main.swift) |
| macOS application | Not started | [Phase 4](roadmap/phase-4-macos-application.md) |
| Evaluation dataset | Implemented for Phase 1 | [Evaluation Methodology](evaluation/methodology.md) |
| Python and Swift unit tests | Implemented and passing | [Testing Convention](development/testing.md) |
| CI | Not configured | No workflow exists |

## Active work

- Define the Phase 4 application boundary from the proven prototype without
  treating its subprocess bridge as the durable service design.
- Integrate the local quality gates into the future CI workflow.

## Recently completed

- Completed Phase 0 after reviewing the product overview and invariants against
  their connected transformation, architecture, failure, and privacy documents.
- Validated the canonical documentation graph and complete local pre-commit
  quality gate at Phase 0 exit.
- Defined the initial product scope and MVP boundary.
- Chose a docs-as-wiki model instead of a separate `.wiki/` directory.
- Defined typed frontmatter relations and document splitting rules.
- Added pre-commit checks for documentation, Python, and Swift conventions.
- Added a repository TDD convention and agent workflow.
- Completed Phase 1 with a versioned 16-case synthetic dataset, deterministic
  runner, two-model comparison, and regression-tested scoring calibration.
- Selected `qwen3.5:4b` Q4_K_M as the baseline after it passed every quality and
  latency gate; accepted Ollama as the initial MVP runtime.
- Completed Phase 2 with deterministic protected-element detection, placeholder
  restoration, category-level validation, fail-closed structured results, and a
  single bounded preservation retry.
- Completed Phase 3 with a global Command-Option-T prototype, local stdin/JSON
  runtime bridge, full clipboard representation recovery, fail-closed focus and
  ownership checks, and successful TextEdit plus conditional VS Code real-target
  workflows.

## Blockers

None for the completed Phase 3 scope.

## Next milestone

Define and begin the menu-bar MVP required by
[Phase 4](roadmap/phase-4-macos-application.md).

## Known gaps

- The production prompt-engine bridge completed real local requests. A
  diagnostic 16-case production-pipeline sweep allowed 12 safe results and
  rejected four placeholder-order or omission failures after the bounded retry.
- The Phase 1 keyword-based coverage and addition scores are deterministic
  proxies, not complete semantic judgments.
- TextEdit and VS Code with renderer accessibility are verified targets. Codex,
  Chrome, Safari, Terminal, and ordinary VS Code without an exposed focused
  Accessibility element are not supported claims and remain Phase 6 evaluation
  work.
- Documentation graph validation is available locally but not automated in CI.

## Repository health

| Check | Status |
|---|---|
| Build | Swift debug and release builds passing |
| Unit tests | Python and Swift suites passing |
| Documentation graph | Local pre-commit validation passing |
| Continuous integration | Not configured |
