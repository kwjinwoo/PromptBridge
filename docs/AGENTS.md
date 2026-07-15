# Documentation maintenance rules

These instructions apply to every file under `docs/`.

## Purpose

The `docs/` directory is PromptBridge's canonical, human-readable knowledge base.
It is maintained for both people and coding agents. Product requirements,
architecture, decisions, policies, evaluation results, roadmap, and current
status belong here rather than in a separate generated wiki.

Generated files summarize canonical documents but never override them.

## Required frontmatter

Every Markdown document except this file must start with YAML frontmatter and
contain at least these fields:

```yaml
---
id: globally-unique-document-id
title: Human-readable title
type: document-type
status: document-status
authority: canonical
relations: []
last_reviewed: YYYY-MM-DD
---
```

Use stable IDs in relations. Do not use file paths as relation targets because
documents may move.

Allowed document statuses are:

- `not-started`
- `proposed`
- `active`
- `in-progress`
- `blocked`
- `accepted`
- `implemented`
- `completed`
- `deferred`
- `deprecated`

Allowed relation types are:

- `defines`
- `implements`
- `depends-on`
- `constrains`
- `validates`
- `triggers`
- `informs`
- `supersedes`
- `conflicts-with`
- `related-to`
- `part-of`
- `tracks`

Write only the forward relation. Backlinks are derived automatically and must
not be duplicated as reverse relations.

## Canonical and generated content

- Documents outside `docs/generated/` are canonical unless their frontmatter
  explicitly says otherwise.
- Files under `docs/generated/` are derived navigation artifacts.
- Do not manually place product requirements or decisions only in a generated
  file.
- When generated content conflicts with a canonical document, the canonical
  document wins and the generated artifact must be rebuilt.
- Source code, tests, and accepted ADRs are evidence for implementation status.
  Documentation must not claim that a feature is implemented without evidence.

## Creating documents

Before creating a document:

1. Search existing IDs, titles, aliases, and headings.
2. Extend an existing document when the subject has the same responsibility.
3. Create a new document when the subject evolves or is reviewed independently.
4. Give the document a unique, stable ID.
5. Add at least one meaningful relation unless it is the root index.
6. Link it from a navigational or conceptual parent.
7. Do not create orphan documents.

## Document size and splitting

Keep each document focused on one primary concept.

Consider splitting a document when any of the following is true:

- It exceeds 300 lines or 20 KB.
- Its table of contents needs more than two nested heading levels.
- It contains more than one independently evolving concept.
- Different sections have different owners or review cycles.
- Other documents frequently link to a subsection instead of the document.

Split a document when any of the following is true:

- It exceeds 500 lines or 40 KB.
- It combines product requirements, architecture, and operational procedures.
- A section can be understood and maintained independently.
- Updating one topic repeatedly causes unrelated sections to be reviewed.
- The document cannot be summarized accurately with one title and one `type`.

When splitting a document:

1. Preserve the original ID for the primary concept.
2. Assign a new unique ID to every extracted document.
3. Move content without silently changing its meaning.
4. Add typed relations between the resulting documents.
5. Replace moved sections with concise summaries and links.
6. Update affected Markdown links and frontmatter relations.
7. Update `docs/index.md` when navigation changes.
8. Rebuild and validate generated graph artifacts.
9. Do not leave duplicate canonical content in multiple documents.

The original may become an index page when it still provides useful navigation.
An index summarizes child documents; it does not duplicate their full content.

## Status and roadmap maintenance

- `status.md` describes the repository's current, verifiable state.
- `roadmap/index.md` describes planned phases and their exit criteria.
- Update `status.md` when the active phase, blockers, or subsystem state changes.
- Update the relevant roadmap phase when its scope or exit criteria changes.
- Keep detailed task tracking out of `status.md`; link to a roadmap phase, issue,
  decision, evaluation, or implementation instead.
- Prefer exit criteria over speculative dates.
- Do not present planned or aspirational behavior as implemented behavior.
- Use repository-relative links for evidence.

## Linking and graph rules

- Use standard relative Markdown links in prose.
- Use typed frontmatter relations for machine-readable connections.
- Relation targets must resolve to an existing document ID.
- Keep the relation vocabulary small. Add a new relation type here before using
  it elsewhere.
- Architecture documents should connect to requirements or policies they
  implement and, once available, to relevant code and tests.
- Decision documents should state what they inform or supersede.
- Evaluation documents should state what they validate or inform.
- Policy documents should state what they constrain or trigger.

## Review checklist

After changing documentation:

1. Verify that all frontmatter is valid YAML.
2. Verify that IDs are unique.
3. Verify that relation targets exist.
4. Verify that relative Markdown links resolve.
5. Check that status claims have repository evidence.
6. Update `last_reviewed` only for documents actually reviewed.
7. Rebuild `docs/generated/` when graph structure changes.

## Sensitive data

Never add actual clipboard contents, user prompts, credentials, access tokens,
private local paths, or unredacted logs to the documentation graph. Examples
must be synthetic or explicitly sanitized.
