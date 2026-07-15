---
id: docs-index
title: PromptBridge Documentation
type: index
status: active
authority: canonical
relations:
  - type: defines
    target: product-overview
  - type: tracks
    target: project-status
  - type: related-to
    target: project-roadmap
  - type: related-to
    target: pre-commit-conventions
  - type: related-to
    target: commit-convention
  - type: related-to
    target: code-style-convention
  - type: related-to
    target: testing-convention
  - type: related-to
    target: agent-documentation-skills
last_reviewed: 2026-07-15
---

# PromptBridge Documentation

This directory is the canonical knowledge base for PromptBridge. Start with the
[current status](status.md), then use the sections below to navigate by intent.

## Project navigation

- [Current Status](status.md) — what is verifiably true now
- [Roadmap](roadmap/index.md) — planned phases and exit criteria
- [Product Overview](product/overview.md) — problem, scope, and user workflow
- [Product Invariants](product/invariants.md) — behavior that must not regress
- [System Overview](architecture/system-overview.md) — major components

## Knowledge areas

| Area | Entry point | Purpose |
|---|---|---|
| Product | [Overview](product/overview.md) | Goals, scope, and terminology |
| Transformation | [Translate Mode](transformation/translate-mode.md) | Translation and refinement behavior |
| Architecture | [System Overview](architecture/system-overview.md) | Runtime components and flows |
| Policies | [Failure Policy](policies/failure-policy.md) | Safety and privacy boundaries |
| Decisions | [ADR-0001](decisions/ADR-0001-local-first.md) | Accepted and proposed decisions |
| Evaluation | [Methodology](evaluation/methodology.md) | Quality, latency, and compatibility |
| Development | [Pre-commit](development/pre-commit.md) | Shared local quality gates |
| Commit convention | [Commit Convention](development/commit-convention.md) | Commitizen and Conventional Commits |
| Code documentation | [Code Style](development/code-style.md) | Python docstrings and Swift DocC comments |
| Testing | [Testing Convention](development/testing.md) | TDD cycles, test design, and verification evidence |
| Agent workflow | [Agent Skills](development/agent-skills.md) | Context loading, TDD, and docs maintenance |
| Roadmap | [Roadmap Index](roadmap/index.md) | Delivery phases |

## Generated navigation

- [Knowledge Graph](generated/graph.md)
- [Backlinks](generated/backlinks.md)
- [`document-index.json`](generated/document-index.json)

Generated navigation is derived from canonical frontmatter and does not define
product behavior.
