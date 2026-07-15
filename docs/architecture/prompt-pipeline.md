---
id: prompt-pipeline
title: Prompt Processing Pipeline
type: architecture
status: proposed
authority: canonical
relations:
  - type: implements
    target: translate-mode
  - type: depends-on
    target: protected-elements
  - type: triggers
    target: preservation-validator
last_reviewed: 2026-07-15
---

# Prompt Processing Pipeline

## Processing sequence

```text
Source text
→ segment Markdown and natural language
→ detect protected elements
→ replace eligible elements with placeholders
→ construct a mode-specific LLM request
→ invoke the local runtime
→ restore placeholders
→ validate preservation and output shape
→ return a structured result to the macOS client
```

## Stage responsibilities

### Segmentation

Identify fenced code, inline code, paths, URLs, commands, likely identifiers,
errors, logs, numbers, versions, and ordinary natural language. Detection should
return spans and categories so restoration does not depend on broad string
replacement.

### Protection

Assign collision-resistant placeholders only to categories whose context can be
safely hidden. Code blocks remain visible because the model may need them to
translate the surrounding instruction correctly.

### Transformation

Construct instructions for the selected mode, use low-variance model settings,
and require prompt-only output. Runtime failures are returned separately from
validation failures.

### Restoration and validation

Restore each placeholder exactly once, validate the output, and produce either a
safe result or structured failure details. The pipeline never pastes directly;
that responsibility belongs to the [Clipboard State Machine](clipboard-state-machine.md).

## Structured result

The eventual API should distinguish at least:

- transformed text
- selected mode
- protected elements
- validation results by category
- runtime error
- retry count
- elapsed time by stage
