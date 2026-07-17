---
id: application-compatibility
title: Application Compatibility
type: evaluation
status: completed
authority: canonical
relations:
  - type: validates
    target: clipboard-state-machine
  - type: part-of
    target: roadmap-phase-3-hotkey-prototype
last_reviewed: 2026-07-17
---

# Application Compatibility

Compatibility evaluation started with an environment and permission preflight.
Results distinguish copy, paste, focus detection, clipboard restoration, and
permission behavior; a blocked preflight is not counted as an application pass.

## 2026-07-17 environment

- macOS 26.5.2, build 25F84, Apple Silicon
- `promptbridge-hotkey` release executable built with Swift 6.3.3
- Accessibility: approved for the release prototype
- Ollama 0.32.0 and `qwen3.5:4b`: available on `127.0.0.1:11434`
- Synthetic input only; no real prompt or clipboard content was recorded

| Application | Version | Copy selection | Safe paste | Focus detection | Clipboard restore | Permission |
|---|---:|---|---|---|---|---|
| ChatGPT | Unavailable as a distinct bundle | Unverified | Unverified | Unverified | Unverified | No distinct target |
| Codex | 26.707.41301 (5103) | Unverified | Unverified | Unverified | Unverified | Deferred to Phase 6 |
| VS Code | 1.128.0 | Pass with renderer accessibility | Pass | Pass | Pass | Approved; Electron accessibility required |
| Chrome | 150.0.7871.115 | Unverified | Unverified | Unverified | Unverified | Deferred to Phase 6 |
| Safari | 26.5.2 | Unverified | Unverified | Unverified | Unverified | Deferred to Phase 6 |
| Terminal | 2.15 | Unverified | Unverified | Unverified | Unverified | Deferred to Phase 6 |
| TextEdit | 1.20 | Pass | Pass | Pass | Pass | Approved |

The application at `/Applications/ChatGPT.app` identifies itself as
`com.openai.codex`, so this run records it as Codex and does not infer a separate
ChatGPT application result.

## Safe fallback evidence

The executable registered Command-Option-T, detected missing Accessibility
permission during preflight, and disabled automatic capture and paste. The
coordinator returns `permissionDenied` before clipboard capture, so the selected
source and existing clipboard remain untouched. Automated tests retain this
non-pasting contract after permission is granted.

## Runtime follow-up

Ollama 0.32.0 and `qwen3.5:4b` were installed after the initial preflight. The
service was verified listening only on `127.0.0.1:11434`, and the model reports
digest `2a654d98e6fb` with a 3.4 GB local artifact. The production stdin/JSON
bridge completed a synthetic technical transformation and deterministic
preservation validation without retry.

A diagnostic production-pipeline sweep over the 16 committed Phase 1 synthetic
cases produced 12 safe-to-apply results. Four cases failed closed after one retry
because required inline-code placeholders were reordered or omitted. This sweep
confirms runtime integration and safe rejection; it does not replace the Phase 1
quality comparison or satisfy the application compatibility gate.

## Real-target results

TextEdit used a synthetic Korean instruction containing an inline-code
identifier and path. Command-Option-T copied the selected text, transformed it
through the production local runtime, pasted the validated English result into
the same text area, and restored the pre-existing synthetic clipboard sentinel.
The prototype reported `replacement applied`.

VS Code was launched as an isolated process with a temporary user-data directory,
extensions disabled, and `--force-renderer-accessibility`. Its synthetic untitled
buffer completed the same workflow and restored the clipboard. A control run in
the ordinary VS Code process reproduced the Electron failure boundary: with no
focused Accessibility element exposed, the prototype reported
`selection capture failed; source kept` and did not paste. This is a safe
configuration-dependent result, not an unconditional VS Code support claim.

## Remaining compatibility work

The native-editor and Electron gate required by Phase 3 is complete. Codex,
Chrome, Safari, and Terminal remain explicitly unverified and must not be
presented as supported. Phase 6 will turn this table into the broader regression
suite, including versioned success or reproduced incompatibility evidence for
each target.
