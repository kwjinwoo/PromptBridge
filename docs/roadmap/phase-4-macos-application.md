---
id: roadmap-phase-4-macos-application
title: Phase 4 — macOS Application
type: roadmap-phase
status: not-started
authority: canonical
relations:
  - type: part-of
    target: project-roadmap
  - type: implements
    target: system-overview
  - type: depends-on
    target: roadmap-phase-3-hotkey-prototype
last_reviewed: 2026-07-15
---

# Phase 4 — macOS Application

## Objective

Turn the proven workflow into a usable menu-bar MVP.

## Scope

- Menu-bar item and runtime status
- Translate Selection command and configurable global hotkey
- Preview and validation-failure UI
- Accessibility permission guidance
- Runtime, model, timeout, and transformation settings
- Safe clipboard restoration and user-facing error handling

## Exit criteria

- The app performs the MVP workflow from the menu and hotkey.
- Accessibility onboarding is understandable and recoverable.
- Runtime and validation errors are distinguishable.
- Product invariants have automated or documented acceptance evidence.
- Prompt contents are not persisted by default.
