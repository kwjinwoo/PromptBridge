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
last_reviewed: 2026-07-16
---

# Project Status

## Current phase

Phase 1 — Transformation quality validation is completed. Phase 2 is next and
has not started.

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
| Production prompt engine | Not started | [Prompt Pipeline](architecture/prompt-pipeline.md) |
| Preservation validator | Not started | [Phase 2](roadmap/phase-2-preservation-validator.md) |
| Hotkey prototype | Not started | [Phase 3](roadmap/phase-3-hotkey-prototype.md) |
| macOS application | Not started | [Phase 4](roadmap/phase-4-macos-application.md) |
| Evaluation dataset | Implemented for Phase 1 | [Evaluation Methodology](evaluation/methodology.md) |
| Python unit tests | Implemented and passing | [Testing Convention](development/testing.md) |
| CI | Not configured | No workflow exists |

## Active work

- Begin Phase 2 with focused tests for protected-element extraction and exact
  restoration.
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

## Blockers

None currently recorded.

## Next milestone

Start the deterministic preservation pipeline required by
[Phase 2](roadmap/phase-2-preservation-validator.md).

## Known gaps

- No production prompt-engine implementation exists.
- The Phase 1 keyword-based coverage and addition scores are deterministic
  proxies, not complete semantic judgments.
- Clipboard behavior has not been prototyped against target applications.
- Documentation graph validation is available locally but not automated in CI.

## Repository health

| Check | Status |
|---|---|
| Build | Not configured |
| Unit tests | Python evaluation suite passing; Swift not configured |
| Documentation graph | Local pre-commit validation passing |
| Continuous integration | Not configured |
