---
id: preservation-validator
title: Preservation Validator
type: architecture
status: proposed
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
last_reviewed: 2026-07-15
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

Validation should return category-level findings containing the expected value,
observed value, severity, and a safe user-facing description. This supports
preview, retry prompts, evaluation, and debugging without storing full user
prompts.

## Retry

One automatic retry may include the failed preservation categories. A second
failure returns control to the client, which follows the
[Failure Policy](../policies/failure-policy.md).
