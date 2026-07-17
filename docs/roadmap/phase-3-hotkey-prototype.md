---
id: roadmap-phase-3-hotkey-prototype
title: Phase 3 — Hotkey Prototype
type: roadmap-phase
status: completed
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
last_reviewed: 2026-07-17
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

Phase 3 is complete only when all of the following have repository evidence:

- An executable macOS prototype registers one global hotkey and drives selection
  copy, local transformation, deterministic preservation validation, conditional
  paste, and clipboard recovery without requiring the Phase 4 menu-bar UI.
- The local prompt-engine bridge accepts prompt text through standard input,
  returns a structured result without persisting prompt content, rejects
  non-loopback runtime endpoints, and distinguishes runtime, restoration, and
  validation failures.
- Automatic paste occurs only when the transformation is safe to apply, the
  captured application and focused target are unchanged, and the clipboard is
  still owned by the active request.
- Focus changes, user clipboard changes, copy and runtime timeouts, missing
  Accessibility permission, and concurrent invocation all fail closed. No such
  path pastes a result or silently overwrites newer clipboard content.
- Clipboard backup and conditional restoration preserve all pasteboard item
  representations available to the prototype rather than only plain text.
- Automated tests cover the successful end-to-end state transition and every
  fail-closed condition above with synthetic data and deterministic test doubles.
- At least one native editor target and one browser or Electron target complete
  the real selection-to-replacement workflow with clipboard restoration. Test
  doubles and permission fallback results do not satisfy this compatibility gate.
- The compatibility matrix records macOS and application versions plus copy,
  paste, focus, clipboard restoration, and permission results for the native and
  browser-or-Electron gate targets. Untested target applications remain
  explicitly unverified and are deferred to the Phase 6 compatibility suite
  rather than being presented as supported.
- Focused Python and Swift tests, the complete Python and Swift suites,
  documentation graph validation, and the repository pre-commit quality gate
  pass.

## Phase boundary

The prototype may use a subprocess standard-input/JSON bridge between the Swift
client and Python prompt pipeline. That bridge is Phase 3 integration evidence,
not a durable Phase 4 service-boundary decision. Menu-bar UI, settings,
launch-at-login, polished previews, and packaging remain Phase 4 work.

## Current evidence

The repository now contains the local
[prompt-engine bridge](../../src/promptbridge/cli.py), executable
[hotkey prototype](../../Sources/PromptBridgeHotkey/main.swift), and tested
[replacement coordinator](../../Sources/PromptBridgeCore/ReplacementCoordinator.swift).
Automated safety contracts are passing, and the executable registers
Command-Option-T. A real integration run exposed that a Foundation run loop did
not dispatch the registered Carbon hotkey; the executable now receives and
dispatches Carbon events directly. The same synthetic TextEdit scenario then
completed selection copy, local transformation, safe paste, and clipboard
restoration.

Ollama 0.32.0 and the selected `qwen3.5:4b` model are installed, bound to
loopback, and verified through the production pipeline. A separate VS Code
1.128.0 process launched with Electron renderer accessibility enabled completed
the same end-to-end workflow and restored the clipboard. With renderer
accessibility disabled, VS Code did not expose a focused Accessibility element
and the prototype failed closed before copy or paste. These native and Electron
results satisfy the Phase 3 real-target gate; broader application certification
remains Phase 6 work. See the
[compatibility matrix](../evaluation/compatibility-matrix.md) for versioned
evidence and exact conditions.
