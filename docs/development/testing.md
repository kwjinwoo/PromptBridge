---
id: testing-convention
title: Test-driven Development and Testing Convention
type: development
status: active
authority: canonical
relations:
  - type: related-to
    target: pre-commit-conventions
  - type: validates
    target: product-invariants
last_reviewed: 2026-07-16
---

# Test-driven Development and Testing Convention

PromptBridge uses test-driven development for executable behavior changes. Work
in small Red-Green-Refactor cycles and keep each cycle focused on one observable
contract.

## Required cycle

### Red

- Write a focused test before changing production behavior.
- Run it and confirm that it fails for the expected missing behavior.
- Treat syntax errors, broken fixtures, missing dependencies, and unrelated
  failures as invalid Red evidence.

### Green

- Implement the smallest change that makes the focused test pass.
- Do not weaken, remove, skip, or over-mock a valid test to obtain a pass.
- Avoid speculative abstractions and unrelated cleanup.

### Refactor

- Improve production and test code only while the focused tests remain green.
- Preserve public contracts, privacy boundaries, and product invariants.
- Move unrelated cleanup into a separate change or cycle.

## Change-specific rules

- Add a regression test before fixing a reproducible defect.
- For behavior-preserving refactoring, establish a passing baseline first; a new
  failing test is required only when behavior also changes.
- Characterize unclear legacy behavior before modifying it.
- If no test harness exists, add the smallest viable harness needed for the
  behavior and record any durable framework choice in this document or an ADR.

TDD normally does not apply to documentation-only changes, generated artifacts,
or disposable exploratory spikes. State the exception and run the relevant
validators. Spike code must not become production code until it enters a tested
implementation cycle.

## Test design

- Test observable behavior and contracts instead of private implementation
  details.
- Keep tests deterministic, isolated, and readable as behavioral examples.
- Prefer real value objects and pure functions; use test doubles at clipboard,
  model, filesystem, clock, process, and network boundaries.
- Cover success, validation failure, preservation failure, and privacy-sensitive
  paths when relevant.
- Use only synthetic, licensed, or sanitized fixtures. Never store actual prompts
  or clipboard contents in tests or snapshots.

## Verification evidence

Run the narrowest relevant test during each cycle, then the affected suite and
applicable repository quality gate before handoff. Report exact commands and
results. Never claim a test passed unless it ran.

Python evaluation tests use the standard-library `unittest` runner with no
additional test dependency:

```shell
PYTHONPATH=src uv run python -m unittest discover -s tests -v
```

No Swift test target is configured yet. Select and document its command when the
first Swift package or target is introduced; until then, report Swift unit tests
as unavailable rather than passed.
