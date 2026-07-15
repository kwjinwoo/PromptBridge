# PromptBridge repository instructions

## Task context

- Before substantive planning, implementation, diagnosis, review, or repository
  guidance, use `$promptbridge-read-docs` to build task-specific context from the
  docs knowledge graph.
- Read only the relevant graph neighborhood. Do not load the entire docs tree by
  default.
- Treat canonical docs, accepted ADRs, source code, tests, and configuration as
  evidence. Surface conflicts instead of silently resolving them.
- Never present proposed, deferred, or not-started behavior as implemented.

## Documentation maintenance

- Use `$promptbridge-maintain-docs` whenever a change affects documentation,
  product behavior, architecture, policies, decisions, roadmap, status,
  evaluation conclusions, or development conventions.
- Follow the nested `docs/AGENTS.md` instructions for every file under `docs/`.
- Keep generated navigation synchronized with canonical frontmatter.

## Change discipline

- Make the smallest change that satisfies the task, and preserve unrelated user
  changes.
- Avoid broad rewrites, unnecessary dependencies, abstractions, service
  boundaries, or runtimes.
- Record material, unaccepted design choices as proposed ADRs.
- Keep implementation, tests, and affected canonical docs consistent in the
  same change.

## Dependency management

- Manage Python dependencies with `uv add` and `uv remove`; never edit `uv.lock`
  manually, and commit it when dependency resolution changes.
- Manage Swift dependencies with Swift Package Manager and commit
  `Package.resolved` when it changes.
- Do not vendor dependencies without a documented decision.
- Any dependency that can send prompt data off-device requires explicit privacy
  review and an ADR.

## Development workflow

- Manage Python tooling with uv.
- Run repository tools through `uv run`.
- Follow `docs/development/commit-convention.md` for commit messages.
- Follow `docs/development/code-style.md` for Python docstrings and Swift
  documentation comments.

## Verification

- Run the narrowest relevant checks while iterating, then complete the
  applicable quality gate before handoff.
- Add regression tests for fixes and tests for new or changed behavior.
- Never claim a check passed unless it ran; report skipped, unavailable, or
  failing checks.

## Quality gate coverage

- Use `uv run pre-commit run --all-files` for tracked repository files.
- Because `--all-files` can miss untracked files, pass new files explicitly to
  pre-commit until they are tracked or covered by a repository check script.

## Definition of done

- The requested outcome is complete and relevant tests and validators pass.
- Affected docs, status, roadmap, ADRs, and generated navigation are synchronized.
- No unrelated files changed, and remaining risks or unverified checks are
  reported.

## Privacy and safety

- Do not persist actual prompts, clipboard contents, credentials, private paths,
  or unredacted logs in source, tests, documentation, or agent artifacts.
- Preserve the local-first boundary and bind runtime services to localhost.
- Do not add telemetry, remote inference, prompt history, or persistent clipboard
  storage without explicit authorization and a privacy decision.
- Use only synthetic, licensed, or sanitized fixtures, and never let validation
  failure trigger automatic text replacement.
