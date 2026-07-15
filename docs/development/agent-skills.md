---
id: agent-documentation-skills
title: Agent Workflow Skills
type: development
status: active
authority: canonical
relations:
  - type: implements
    target: docs-index
  - type: depends-on
    target: pre-commit-conventions
  - type: depends-on
    target: testing-convention
  - type: related-to
    target: project-status
last_reviewed: 2026-07-15
---

# Agent Workflow Skills

PromptBridge provides repository-scoped Codex skills under `.agents/skills` so
documentation context and maintenance procedures travel with the repository.

## Skills

| Skill | Responsibility |
|---|---|
| `$promptbridge-read-docs` | Build a minimal task-specific context set from canonical docs and typed relations |
| `$promptbridge-maintain-docs` | Author and maintain canonical documents and derived graph artifacts |
| `$promptbridge-tdd` | Implement executable behavior through focused Red-Green-Refactor cycles |

The root `AGENTS.md` requires the read skill before substantive repository work
and the maintenance skill whenever work changes durable project knowledge. It
requires the TDD skill whenever implementation adds, changes, or fixes executable
behavior.

## Discovery

Codex discovers repository skills from `.agents/skills`. Each skill contains a
required `SKILL.md` plus `agents/openai.yaml` UI metadata. Skills use progressive
disclosure: descriptions support discovery, full instructions load when selected,
and repository documents are read only as the workflow requires them.

## Authority boundary

Skills define procedures, not product facts. Product knowledge remains canonical
under `docs/`. A skill must route agents to the relevant documents instead of
copying requirements that can become stale.

## Validation

Validate each skill folder after changing its structure or metadata:

```shell
uv run python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/promptbridge-read-docs
uv run python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/promptbridge-maintain-docs
uv run python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/promptbridge-tdd
```

Also run the docs graph validator and applicable pre-commit hooks. If the
skill-creator installation lives elsewhere, resolve its actual path rather than
assuming the example path.
