---
id: failure-policy
title: Failure Policy
type: policy
status: proposed
authority: canonical
relations:
  - type: implements
    target: product-invariants
  - type: constrains
    target: prompt-pipeline
  - type: constrains
    target: clipboard-state-machine
last_reviewed: 2026-07-15
---

# Failure Policy

PromptBridge must fail without changing the selected source text or losing user
clipboard data.

## Failure classes

- Capture failure: no selection, copy timeout, permission denial
- Runtime failure: unavailable backend, timeout, invalid response
- Restoration failure: missing or malformed protected token
- Validation failure: protected content or required structure changed
- Context failure: active application or target context changed
- Application failure: paste or clipboard restoration could not be confirmed

## Default response

```text
transform
→ validate
→ retry once when the failure is safely retryable
→ validate again
→ show preview or error without replacing the source
```

The preview should identify failed categories and offer safe actions such as
copying the result, retrying, switching to Translate Mode, or keeping the source.

## Non-retryable conditions

Do not retry automatically when application focus changes, the user changes the
clipboard, permission is denied, the request is cancelled, or the source exceeds
an explicit configured limit.

## Error reporting

Runtime and validation errors must remain distinct. User-facing messages should
be actionable but must not expose prompt content, credentials, or raw local
runtime responses unnecessarily.
