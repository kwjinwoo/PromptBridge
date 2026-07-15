---
id: application-compatibility
title: Application Compatibility
type: evaluation
status: not-started
authority: canonical
relations:
  - type: validates
    target: clipboard-state-machine
  - type: part-of
    target: roadmap-phase-3-hotkey-prototype
last_reviewed: 2026-07-15
---

# Application Compatibility

Compatibility has not yet been tested. Results must distinguish copy, paste,
focus detection, clipboard restoration, and permission behavior.

| Application | Copy selection | Safe paste | Focus detection | Clipboard restore | Notes |
|---|---|---|---|---|---|
| ChatGPT | Not tested | Not tested | Not tested | Not tested | — |
| Codex | Not tested | Not tested | Not tested | Not tested | — |
| VS Code | Not tested | Not tested | Not tested | Not tested | — |
| Chrome | Not tested | Not tested | Not tested | Not tested | — |
| Safari | Not tested | Not tested | Not tested | Not tested | — |
| Terminal | Not tested | Not tested | Not tested | Not tested | — |
| TextEdit | Not tested | Not tested | Not tested | Not tested | — |

Each result should include the macOS version, application version, input type,
permission state, and reproduction steps for failures.
