---
id: system-overview
title: System Overview
type: architecture
status: proposed
authority: canonical
relations:
  - type: implements
    target: product-overview
  - type: depends-on
    target: prompt-pipeline
  - type: depends-on
    target: clipboard-state-machine
  - type: depends-on
    target: preservation-validator
last_reviewed: 2026-07-15
---

# System Overview

PromptBridge consists of a macOS client, a prompt-processing pipeline, a local
LLM backend, and deterministic preservation validation.

```mermaid
flowchart TD
    A["macOS menu-bar app"] --> B["Clipboard and focus capture"]
    B --> C["Prompt pipeline"]
    C --> D["Local LLM backend"]
    D --> E["Restoration and validator"]
    E -->|"success"| F["Safe replacement"]
    E -->|"failure"| G["Keep source and show preview"]
```

## macOS client

The client owns global hotkeys, clipboard backup and restoration, keyboard
events, active-application checks, preview UI, settings, permissions, timeouts,
and user-facing errors. The likely implementation is Swift and SwiftUI using
`NSPasteboard`, `CGEvent`, `AXUIElement`, `NSPanel`, and `NSStatusItem`.

## Prompt processing

The processing layer segments text, extracts protected elements, constructs a
mode-specific request, calls the configured backend, restores protected values,
and invokes validation. See [Prompt Pipeline](prompt-pipeline.md).

## Local LLM backend

The backend boundary must allow runtime implementations to change without
coupling transformation or validation logic to a specific server. Ollama is the
initial proposed MVP runtime; see [ADR-0002](../decisions/ADR-0002-ollama-mvp.md).

## Validator

The validator is deterministic wherever possible and decides whether automatic
application is allowed. It reports structured failures rather than a single
boolean. See [Preservation Validator](preservation-validator.md).
