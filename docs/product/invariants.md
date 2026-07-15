---
id: product-invariants
title: Product Invariants
type: product
status: proposed
authority: canonical
relations:
  - type: constrains
    target: translate-mode
  - type: constrains
    target: refine-mode
  - type: constrains
    target: prompt-pipeline
  - type: constrains
    target: preservation-validator
  - type: constrains
    target: clipboard-state-machine
  - type: constrains
    target: failure-policy
  - type: constrains
    target: privacy-boundary
last_reviewed: 2026-07-15
---

# Product Invariants

These constraints define behavior that implementations must not weaken without
an explicit architectural decision.

## Intent preservation

- The transformed prompt must preserve whether the user requested analysis,
  explanation, implementation, modification, or review.
- Scope, constraints, ordering, requested output format, and uncertainty must not
  be silently changed.
- Translate Mode must not add requirements absent from the source.
- Refine Mode may restructure clear intent but must not invent features,
  technologies, performance targets, or design goals.
- PromptBridge transforms the instruction; it must not answer or execute it.

## Technical preservation

- Protected identifiers, paths, URLs, commands, versions, and numeric values must
  remain exact according to their validation policy.
- Fenced code contents must remain byte-for-byte identical in the MVP.
- Markdown structure must remain valid and materially equivalent.
- A transformation must not be automatically applied when required preservation
  checks fail.

## Safe replacement

- The original clipboard must be backed up before PromptBridge modifies it.
- A failed transformation must leave the selected source text intact.
- Automatic paste must stop if the active application or target context changes.
- Concurrent hotkey invocations must not race to replace the same selection.
- Runtime errors and preservation failures must be reported distinctly.

## Privacy

- Prompt content must stay on the local machine by default.
- Prompt text and results must not be persisted by default.
- Local runtime services must listen on localhost only.
- Logs, evaluation fixtures, and documentation must not capture real user prompt
  contents without explicit sanitization and consent.

## Performance

- The model must remain warm across requests when supported.
- Preprocessing and validation overhead should remain materially smaller than
  model inference time.
- A timeout must fail safely without replacing the input.
