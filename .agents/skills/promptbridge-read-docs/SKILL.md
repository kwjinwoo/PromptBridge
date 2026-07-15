---
name: promptbridge-read-docs
description: Build task-specific context from PromptBridge's docs-as-wiki before planning, implementing, diagnosing, reviewing, or answering repository questions. Use for substantive PromptBridge work that depends on product scope, invariants, architecture, policies, decisions, roadmap, status, evaluation, or development conventions; read index-first, follow typed relations, and distinguish planned behavior from repository evidence.
---

# Read PromptBridge Docs

Build the smallest sufficient context set from the repository's canonical
documentation before acting. Do not mutate documentation while using this skill.

## Workflow

1. Resolve the repository root and confirm that `docs/index.md` exists.
2. Read `docs/index.md` and `docs/status.md` completely.
3. Classify the task using the routing table below.
4. Read each selected canonical document completely.
5. Follow relevant frontmatter relations one hop. Follow a second hop only when
   the first hop exposes a dependency, constraint, decision, or conflict material
   to the task.
6. Compare documentation claims with source code, tests, configuration, and Git
   state when the task depends on current implementation status.
7. Form a compact task-context brief before planning or editing.

Use `docs/generated/document-index.json` to map stable document IDs to paths.
Use `docs/generated/graph.md` and `docs/generated/backlinks.md` for navigation
only; canonical document frontmatter and repository evidence take precedence.

## Task routing

| Task | Read in addition to index and status |
|---|---|
| Product behavior or scope | `product/overview.md`, `product/invariants.md`, relevant transformation and policy documents |
| Prompt transformation | Relevant files in `transformation/`, `architecture/prompt-pipeline.md`, `architecture/preservation-validator.md` |
| macOS or clipboard work | `architecture/system-overview.md`, `architecture/clipboard-state-machine.md`, relevant policies and macOS roadmap phase |
| Local runtime or model work | Relevant ADRs, evaluation methodology, model comparison, Phase 1 roadmap |
| Evaluation or compatibility | `evaluation/methodology.md`, the relevant evaluation document, connected roadmap phase |
| Roadmap or delivery status | `roadmap/index.md`, relevant phase, `status.md`, and repository evidence |
| Tooling or conventions | Relevant files in `development/`, plus configuration files named there |
| Documentation changes | Complete this workflow, then use `$promptbridge-maintain-docs` |

For implementation and review tasks that can affect user-visible or safety
behavior, always include `product/invariants.md` even when the task appears
localized.

## Context brief

Capture these points in working context:

- Current phase and subsystem status
- Canonical documents relevant to the task
- Product invariants and policies that constrain the change
- Accepted and proposed decisions that affect implementation
- Known gaps, blockers, and evaluation requirements
- Any mismatch between documentation and repository evidence

Do not present a `proposed`, `not-started`, or `deferred` document as implemented.
Do not treat a generated artifact as authoritative. Surface contradictions rather
than silently choosing the most convenient source.

## Reading discipline

- Start from indexes; do not load the entire `docs/` tree by default.
- Prefer stable IDs and typed relations over filename guesses.
- Read selected documents fully rather than relying on isolated search matches.
- Expand context only when it can change the plan, implementation, or review.
- Keep actual user prompts, clipboard contents, credentials, and private paths
  out of notes and outputs.
