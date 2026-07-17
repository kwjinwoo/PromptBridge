# PromptBridge

Developer-aware Korean-to-English prompt transformation for macOS.

PromptBridge is a planned local-first macOS utility that transforms Korean
developer instructions into clear English prompts while preserving code,
identifiers, commands, paths, formatting, and technical intent.

## Project status

PromptBridge has completed Phase 3: the local prompt pipeline, deterministic
preservation validator, Swift replacement coordinator, and executable global
hotkey prototype are implemented and tested. The real workflow passed in
TextEdit and in an isolated VS Code process with Electron renderer accessibility
enabled, including clipboard restoration. Phase 4, the menu-bar macOS
application, is next. Ollama 0.32.0 and the selected local `qwen3.5:4b` model are
installed and verified on loopback.

- [Current status](docs/status.md)
- [Roadmap](docs/roadmap/index.md)

## Product direction

- Preserve task intent, constraints, and protected technical elements.
- Apply transformed text only after preservation checks succeed.
- Keep prompts and runtime services on the local machine by default.
- Let developers remain in their current editor, terminal, browser, or AI tool.

The [Product Overview](docs/product/overview.md) and
[Product Invariants](docs/product/invariants.md) are the canonical sources for
scope and behavioral constraints.

## Documentation

The [`docs/`](docs/index.md) directory is maintained as the project's canonical
wiki. Documents use YAML frontmatter and typed relations to provide generated
knowledge-graph navigation.

Start with the [documentation index](docs/index.md), then follow links by product,
architecture, policy, decision, evaluation, development, or roadmap area.

## Development

Python tooling is managed with [uv](https://docs.astral.sh/uv/). Synchronize the
development environment and run the local quality gate with:

```shell
uv sync
uv run pre-commit run --all-files
```

Run the Phase 3 prototype from the repository root while the local Ollama
service and `qwen3.5:4b` model are available:

```shell
swift run promptbridge-hotkey
```

Grant Accessibility permission to the built prototype executable, then select a
synthetic test instruction and press Command-Option-T. The prototype fails
closed without that permission or when the runtime, validation, focus, or
clipboard ownership check fails. See the
[compatibility matrix](docs/evaluation/compatibility-matrix.md) before treating
an application as supported.

Executable behavior is developed with Red-Green-Refactor. See the
[testing convention](docs/development/testing.md),
[commit convention](docs/development/commit-convention.md), and
[code style convention](docs/development/code-style.md) before contributing.

Do not commit actual prompts, clipboard contents, credentials, private paths, or
unredacted logs. Use only synthetic, licensed, or sanitized fixtures.
