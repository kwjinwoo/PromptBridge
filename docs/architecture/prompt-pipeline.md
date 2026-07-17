---
id: prompt-pipeline
title: Prompt Processing Pipeline
type: architecture
status: in-progress
authority: canonical
relations:
  - type: implements
    target: translate-mode
  - type: depends-on
    target: protected-elements
  - type: triggers
    target: preservation-validator
last_reviewed: 2026-07-17
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

## Implementation status

The Phase 3 [Ollama runtime boundary](../../src/promptbridge/runtime.py) now uses
the Phase 1 generation settings, rejects non-loopback endpoints, and feeds model
output through the Phase 2 preservation pipeline. The
[standard-input/JSON bridge](../../src/promptbridge/cli.py) returns safe-to-apply
text or a structured runtime, restoration, or validation failure without placing
source text in process arguments or failure messages. Python tests cover the
runtime contract and sanitized failures.

Ollama 0.32.0 now runs as a user service on `127.0.0.1:11434`, and the selected
`qwen3.5:4b` model digest `2a654d98e6fb` is installed. A real model-backed
technical prompt completed restoration and validation without retry. A
production-pipeline diagnostic over all 16 committed synthetic Phase 1 cases
allowed 12 safe results and rejected four after the bounded retry because the
model reordered or omitted required placeholders. No rejected result was marked
safe to apply.

The runtime request uses Ollama's system-instruction field and sends required
category-bearing placeholders separately from the source. This was needed for
the selected model to retain multiple opaque technical elements. Semantic
requirement-coverage scoring and durable Phase 4 client/service packaging remain
open.
