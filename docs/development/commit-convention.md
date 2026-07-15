---
id: commit-convention
title: Commit Convention
type: development
status: active
authority: canonical
relations:
  - type: part-of
    target: pre-commit-conventions
  - type: related-to
    target: code-style-convention
last_reviewed: 2026-07-15
---

# Commit Convention

PromptBridge uses Commitizen with the Conventional Commits convention. Commit
messages are written in English and validated by the `commit-msg` Git hook.

## Format

```text
<type>(<scope>): <description>

[optional body]

[optional footer]
```

The scope is optional. Use it when it makes the affected subsystem clearer.

## Types

| Type | Use |
|---|---|
| `feat` | User-visible capability |
| `fix` | Defect correction |
| `docs` | Documentation-only change |
| `style` | Formatting with no behavioral change |
| `refactor` | Internal restructuring without a feature or fix |
| `perf` | Performance improvement |
| `test` | Test or fixture change |
| `build` | Build system or dependency change |
| `ci` | Continuous integration change |
| `chore` | Repository maintenance not covered above |
| `revert` | Revert of a previous commit |

## Suggested scopes

- `macos`
- `prompt-engine`
- `transformation`
- `validation`
- `evaluation`
- `docs`
- `tooling`
- `deps`

Add a new scope only when it represents a stable subsystem. Do not use filenames
or issue numbers as scopes.

## Description

- Use the imperative mood: `add`, `fix`, `preserve`, `validate`.
- Start with lowercase unless the first word is a proper noun or identifier.
- Do not end with a period.
- Describe the outcome, not the editing activity.
- Keep the first line concise; use the body for rationale and tradeoffs.

## Breaking changes

Use `!` before the colon and add a `BREAKING CHANGE:` footer:

```text
feat(prompt-engine)!: change transformation response schema

BREAKING CHANGE: clients must read validation results from the checks array.
```

## Examples

```text
feat(macos): add safe clipboard restoration
fix(validation): preserve fenced code indentation
docs(roadmap): define phase two exit criteria
build(tooling): add Commitizen commit validation
```

Avoid vague messages such as `update files`, `fix issue`, or `work in progress`.
Commits should represent one coherent change and leave the repository in a
reviewable state.

## Commands

Create a message interactively:

```shell
uv run cz commit
```

Validate a message manually:

```shell
uv run cz check --message "docs(tooling): define commit convention"
```

The normal `git commit` flow is validated automatically after installing the
hooks described in [Pre-commit Conventions](pre-commit.md).
