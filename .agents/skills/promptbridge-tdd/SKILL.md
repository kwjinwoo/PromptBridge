---
name: promptbridge-tdd
description: Apply PromptBridge's test-driven development workflow to executable behavior changes. Use for Python or Swift implementation, bug fixes, behavior-changing refactors, and reviews or plans that must define a Red-Green-Refactor sequence; establish a focused failing test, make the minimum implementation pass, refactor safely, and report verification evidence.
---

# PromptBridge TDD

Implement executable behavior through small, evidence-backed Red-Green-Refactor
cycles.

## Build context

1. Use `$promptbridge-read-docs` to load the task-specific product and technical
   context.
2. Read `docs/development/testing.md` completely.
3. Inspect the existing source, tests, test configuration, and repository status.
4. Identify the smallest observable behavior and the product invariant or
   contract it supports.

Do not invent a test command or framework that the repository does not contain.
If the task introduces the first test target, establish only the smallest viable
harness and document the choice when it becomes a durable convention.

## Classify the change

- For new or changed behavior, use the complete Red-Green-Refactor cycle.
- For a reproducible defect, first add a regression test that demonstrates it.
- For behavior-preserving refactoring, establish a passing baseline and preserve
  or improve coverage; a deliberately failing test is not required.
- For documentation-only, generated-file, or disposable exploratory work, state
  why TDD does not apply and run the relevant non-test validators.

## Red

1. Write one focused test against observable behavior.
2. Run that test before editing production behavior.
3. Confirm it fails for the expected missing behavior, not because of a typo,
   broken fixture, missing dependency, or unrelated failure.
4. Record the failing command and meaningful result in working context.

If the test unexpectedly passes, improve the assertion or reassess whether the
requested behavior already exists before implementing anything.

## Green

1. Make the smallest production change that satisfies the failing test.
2. Avoid unrelated cleanup or speculative generalization.
3. Run the focused test until it passes.
4. Do not weaken, delete, skip, or over-mock a valid test merely to reach green.

## Refactor

Improve names, structure, duplication, and test clarity only while the focused
tests remain green. Preserve public contracts, privacy boundaries, and product
invariants. Separate larger cleanup into another cycle when it is not necessary
for the behavior under test.

## Verify and hand off

1. Repeat the cycle for the next independently observable behavior.
2. Run the affected test group, then the applicable repository quality gate.
3. Update canonical docs, status, roadmap, or ADRs when the behavior or durable
   convention changed.
4. Report the Red evidence, final passing commands, and any skipped, unavailable,
   or failing checks.

Use only synthetic, licensed, or sanitized fixtures. Replace real clipboard,
prompt, model, filesystem, or network boundaries with deterministic test doubles
unless an explicitly authorized integration test requires the boundary.
