---
id: protected-elements
title: Protected Elements
type: transformation
status: implemented
authority: canonical
relations:
  - type: implements
    target: product-invariants
  - type: informs
    target: prompt-pipeline
  - type: informs
    target: preservation-validator
last_reviewed: 2026-07-17
---

# Protected Elements

Protected elements are technical fragments whose meaning can change when their
text or structure changes.

## Initial categories

| Category | Initial handling | Validation |
|---|---|---|
| Inline code | Replace with a placeholder | Exact restoration |
| File path | Replace with a placeholder | Exact string match |
| URL | Replace with a placeholder | Exact string match |
| Short CLI command | Replace with a placeholder | Exact string match |
| Fenced code block | Keep visible to the model | Byte-level content match |
| Error message | Keep in a protected block | Exact or policy-defined match |
| Identifier and type | Protect when detected confidently | Exact string match |
| Number and version | Preserve in context | Exact semantic token match |

## Placeholder representation

```json
{
  "token": "__PB_TOKEN_0__",
  "original": "`std::span<const BufferBinding>`",
  "type": "inline_code"
}
```

Placeholders must be collision-resistant within the source prompt and restored
before final validation. The implementation must detect missing, duplicated,
reordered where significant, or mutated placeholders.

## Detection boundary

The MVP prioritizes unambiguous syntax such as backticks, fenced blocks, path
patterns, URLs, namespace-qualified names, and command-like text. Words such as
`Buffer`, `Pipeline`, `Device`, and `Metal` are context-sensitive and must not be
protected merely because they can be identifiers.

Markdown AST or Tree-sitter integration is deferred until evidence shows that
regex and Markdown-oriented extraction are insufficient.

## Implementation status

The Phase 2 [preservation module](../../src/promptbridge/preservation.py)
implements the unambiguous MVP categories with non-overlapping regex spans.
Inline code, POSIX paths, HTTP(S) URLs, supported CLI commands, and unambiguous
identifiers receive collision-resistant placeholders. Fenced code, numbers, and
versions remain visible and are validated after restoration. The implementation
does not claim to recognize ambiguous identifiers or arbitrary shell grammar.
