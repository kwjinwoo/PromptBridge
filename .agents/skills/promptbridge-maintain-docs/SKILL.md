---
name: promptbridge-maintain-docs
description: Create, edit, split, and maintain PromptBridge's canonical docs-as-wiki and derived graph artifacts. Use whenever work changes documentation, product behavior, architecture, policies, ADRs, evaluation conclusions, roadmap or status, development conventions, frontmatter relations, backlinks, or document indexes; preserve canonical authority, follow docs/AGENTS.md, synchronize generated navigation, and validate the graph.
---

# Maintain PromptBridge Docs

Keep documentation accurate, connected, evidence-based, and useful to both
people and agents.

## Workflow

1. Complete the `$promptbridge-read-docs` workflow for the task.
2. Read `docs/AGENTS.md` completely before editing anything under `docs/`.
3. Inspect the relevant canonical documents, their forward relations, and their
   backlinks.
4. Update an existing document when it has the same responsibility. Create a new
   document only when the subject evolves or is reviewed independently.
5. Edit canonical documents first, then synchronize derived navigation.
6. Validate the graph and run applicable repository checks.
7. Report canonical changes, derived changes, validation, and unresolved gaps.

## Canonical changes

- Treat files outside `docs/generated/` as canonical unless frontmatter states
  otherwise.
- Preserve stable IDs when moving, renaming, or splitting documents.
- Add a unique ID and at least one meaningful typed relation to a new document.
- Write only forward relations; derive reverse backlinks.
- Use relative Markdown links for prose navigation.
- Follow the exact frontmatter vocabulary, authority rules, and split thresholds
  in `docs/AGENTS.md`.
- Update `last_reviewed` only for documents actually reviewed.
- Do not duplicate canonical requirements across multiple documents.

When a document becomes too broad, follow the split procedure in
`docs/AGENTS.md`. Leave a concise index or summary at the original location only
when it remains a useful navigation parent.

## Evidence and status

- Update `docs/status.md` when the active phase, blocker, subsystem state, or
  repository health changes.
- Update the relevant roadmap phase when scope or exit criteria change.
- Mark work completed or implemented only when source code, tests,
  configuration, or another repository artifact provides evidence.
- Record durable architectural choices as ADRs. Keep unvalidated choices
  `proposed`.
- Record evaluation conclusions only with reproducible context and results.
- Surface conflicts between docs and implementation instead of rewriting history
  to hide them.

## Derived navigation

After changing nodes, paths, types, statuses, or relations, synchronize:

- `docs/generated/document-index.json`
- `docs/generated/graph.md`
- `docs/generated/backlinks.md`

These files are derived and must not introduce claims absent from canonical
documents. The document index must contain every frontmatter document under
`docs/`, excluding `docs/AGENTS.md`, with matching ID, path, type, and status.

## Validation

Run the focused graph check first:

```shell
uv run python scripts/validate_docs.py
```

Then run the repository quality gates for changed files or the full tree when
appropriate:

```shell
uv run pre-commit run --all-files
```

Fix invalid YAML, duplicate IDs, unknown relation types, missing targets, broken
links, stale index entries, and Markdown lint errors before finishing. If a check
cannot run, state exactly what remains unverified.

## Safety

- Never add actual clipboard contents, user prompts, credentials, access tokens,
  private local paths, or unredacted logs.
- Use synthetic or explicitly sanitized examples.
- Preserve user-authored decisions and unrelated working-tree changes.
- Do not hand-edit generated artifacts without updating their canonical source.
