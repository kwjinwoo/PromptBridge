---
id: roadmap-phase-3-hotkey-prototype
title: Phase 3 — Hotkey Prototype
type: roadmap-phase
status: not-started
authority: canonical
relations:
  - type: part-of
    target: project-roadmap
  - type: depends-on
    target: roadmap-phase-2-preservation-validator
  - type: implements
    target: clipboard-state-machine
  - type: depends-on
    target: prompt-pipeline
  - type: informs
    target: application-compatibility
last_reviewed: 2026-07-15
---

# Phase 3 — Hotkey Prototype

## Objective

Prove the complete selection-to-replacement workflow before building the full
menu-bar application.

## Scope

- Register a global hotkey.
- Copy selected text using keyboard events.
- Back up and conditionally restore the clipboard.
- Call the local prompt engine.
- Paste only a validated result into an unchanged target context.
- Handle permission, timeout, focus, and concurrent-invocation failures.

## Target applications

ChatGPT, Codex, VS Code, Chrome, Safari, Terminal, and TextEdit.

## Exit criteria

- The end-to-end flow succeeds in the initial target applications or documented
  incompatibilities have explicit fallback behavior.
- Focus changes prevent automatic paste.
- User clipboard changes are not silently overwritten.
- A runtime or validation failure preserves the selected source.
