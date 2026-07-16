---
id: preservation-validator
title: Preservation Validator
type: architecture
status: implemented
authority: canonical
relations:
  - type: implements
    target: product-invariants
  - type: depends-on
    target: protected-elements
  - type: triggers
    target: failure-policy
  - type: validates
    target: prompt-pipeline
last_reviewed: 2026-07-17
---

# Preservation Validator

The Preservation Validator determines whether a transformed prompt is safe for
automatic application.

## MVP checks

| Check | Failure condition |
|---|---|
| Protected tokens | Missing, mutated, duplicated, or unrestored token |
| Identifiers | Required identifier absent or text changed |
| File paths | Slash, case, extension, or content changed |
| Commands | Command, option, order where significant, or value changed |
| Code blocks | Count, fence, language tag, indentation, or content changed |
| Numbers and versions | Required numeric or version token changed or missing |
| Markdown | Required structure is malformed or materially changed |

Any required check failure blocks automatic replacement.

## Requirement validation

Requirement coverage and hallucinated-requirement detection are important but
less deterministic. The MVP may combine rule-based extraction with an LLM judge,
but an LLM judge must not override a deterministic preservation failure.

## Result model

Validation returns category-level findings containing a failure code, expected
and observed counts, severity, and a safe user-facing description. Protected
values remain in the in-memory element records used for restoration, but are not
copied into finding descriptions. This supports retry prompts and debugging
without encouraging prompt content to enter logs or persisted results.

## Retry

One automatic retry may include the failed preservation categories. A second
failure returns control to the client, which follows the
[Failure Policy](../policies/failure-policy.md).

## Implementation status

The Phase 2 [preservation module](../../src/promptbridge/preservation.py) now
implements deterministic restoration, category-level validation, structured
runtime/restoration/validation failures, fail-closed results, and one bounded
retry for preservation failures. The complete model-backed processing pipeline
and macOS client integration remain planned work in the
[Prompt Pipeline](prompt-pipeline.md) and subsequent roadmap phases.
