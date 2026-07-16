---
id: product-overview
title: Product Overview
type: product
status: active
authority: canonical
relations:
  - type: defines
    target: product-invariants
  - type: defines
    target: project-terminology
  - type: constrains
    target: system-overview
last_reviewed: 2026-07-16
---

# Product Overview

PromptBridge is a macOS utility that transforms Korean developer instructions
into clear English prompts while preserving code and technical meaning.

## Problem

General translation tools optimize for natural prose. Developer prompts mix
natural language with identifiers, paths, commands, code blocks, errors, logs,
versions, and formatting. A natural translation can accidentally mutate those
elements, omit a requirement, or add a requirement that was never requested.

## Core workflow

```text
Select Korean developer prompt
→ invoke a global hotkey
→ analyze and protect technical elements
→ transform natural language into English
→ restore and validate protected elements
→ replace the selected text only when validation succeeds
```

## Product goals

- Preserve the user's task type, scope, constraints, uncertainty, and format.
- Preserve technical elements exactly where required.
- Prevent unsafe replacement when validation fails or application focus changes.
- Keep the user in the current AI tool or editor.
- Process prompts locally by default.

## MVP scope

The MVP targets Korean-to-English developer prompt transformation on macOS. It
includes a menu-bar application, a global hotkey, Translate Mode, a local LLM
backend, preservation validation, safe text replacement, and a preview on
failure.

The MVP excludes general document translation, OCR, voice translation, cloud
synchronization, automatic prompt execution, response collection, and
multi-platform support.

## Primary users and environments

The initial user is a Korean-speaking developer working in tools such as
ChatGPT, Codex, VS Code, Chrome, Safari, Terminal, and TextEdit.

## Success criteria

- Automatically applied transformations preserve every protected technical
  element.
- Translate Mode does not introduce new requirements.
- Validation failure never damages the current input.
- A short prompt usually completes within one to two seconds while the model is
  warm.
- Prompt text is not sent to an external translation service by default.

See [Product Invariants](invariants.md) for normative constraints and
[Project Terminology](terminology.md) for shared vocabulary.
