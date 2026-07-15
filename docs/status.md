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
last_reviewed: 2026-07-15
---

# Project Status

## Current phase

Phase 0 — Project foundation and documentation knowledge graph.

## Overall status

| Area | State | Evidence |
|---|---|---|
| Product specification | In progress | [Product Overview](product/overview.md) |
| Documentation graph | In progress | [Documentation Index](index.md) |
| Pre-commit quality gates | Implemented and passing | [Pre-commit Conventions](development/pre-commit.md) |
| Development conventions | Active | [Commit Convention](development/commit-convention.md), [Code Style](development/code-style.md), [Testing Convention](development/testing.md) |
| Agent documentation workflow | Active | [Agent Skills](development/agent-skills.md) |
| Prompt engine | Not started | [Phase 1](roadmap/phase-1-quality-validation.md) |
| Preservation validator | Not started | [Phase 2](roadmap/phase-2-preservation-validator.md) |
| Hotkey prototype | Not started | [Phase 3](roadmap/phase-3-hotkey-prototype.md) |
| macOS application | Not started | [Phase 4](roadmap/phase-4-macos-application.md) |
| Evaluation dataset | Not started | [Evaluation Methodology](evaluation/methodology.md) |
| CI | Not configured | No workflow exists |

## Active work

- Establish the canonical docs-as-wiki structure.
- Convert the initial project brief into focused, interlinked documents.
- Integrate the local quality gates into the future CI workflow.

## Recently completed

- Defined the initial product scope and MVP boundary.
- Chose a docs-as-wiki model instead of a separate `.wiki/` directory.
- Defined typed frontmatter relations and document splitting rules.
- Added pre-commit checks for documentation, Python, and Swift conventions.
- Added a repository TDD convention and agent workflow.

## Blockers

None currently recorded.

## Next milestone

Complete Phase 0 by validating the documentation graph and reviewing the
canonical product invariants.

## Known gaps

- No prompt-engine implementation exists.
- No baseline evaluation dataset exists.
- Local model candidates have not been benchmarked.
- Clipboard behavior has not been prototyped against target applications.
- Documentation graph validation is available locally but not automated in CI.

## Repository health

| Check | Status |
|---|---|
| Build | Not configured |
| Unit tests | Not configured |
| Documentation graph | Local pre-commit validation passing |
| Continuous integration | Not configured |
