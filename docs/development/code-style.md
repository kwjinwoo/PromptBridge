---
id: code-style-convention
title: Code Documentation and Comment Convention
type: development
status: active
authority: canonical
relations:
  - type: part-of
    target: pre-commit-conventions
  - type: related-to
    target: system-overview
last_reviewed: 2026-07-15
---

# Code Documentation and Comment Convention

Comments explain contracts, rationale, invariants, and non-obvious constraints.
They should not paraphrase code that is already clear from names and types.

## Python docstrings

Python uses Google-style docstrings and Ruff's `D` rules with
`pydocstyle.convention = "google"`.

Document:

- Public modules, classes, functions, methods, and properties.
- Private helpers whose contract, side effects, invariants, or failure behavior
  are not obvious.
- Async, concurrency, resource ownership, privacy, and persistence behavior when
  relevant.

A docstring begins with a concise summary, followed by additional context only
when useful. Use Google sections such as `Args`, `Returns`, `Yields`, `Raises`,
`Attributes`, and `Examples`. Do not repeat type annotations in prose.

```python
def restore_tokens(text: str, tokens: list[ProtectedToken]) -> str:
    """Restore protected tokens in transformed text.

    Args:
        text: Transformed text containing token placeholders.
        tokens: Protected values captured from the source prompt.

    Returns:
        Text with every placeholder restored exactly once.

    Raises:
        TokenRestorationError: If a placeholder is missing or duplicated.
    """
```

Tests are exempt from mandatory docstrings. Test names should describe behavior
and conditions directly.

## Swift documentation comments

Swift uses DocC-compatible `///` documentation comments. SwiftLint's
`missing_docs` rule requires documentation for `public` and `open` declarations.

Also document internal declarations when they define a reusable subsystem
boundary or have non-obvious threading, ownership, security, accessibility, or
failure behavior. Private implementation details need documentation only when a
future reader cannot safely infer the contract from code and types.

```swift
/// Restores protected tokens in transformed text.
///
/// - Parameters:
///   - text: Transformed text containing token placeholders.
///   - tokens: Protected values captured from the source prompt.
/// - Returns: Text with every placeholder restored exactly once.
/// - Throws: `TokenRestorationError` when a placeholder is missing or duplicated.
func restoreTokens(
    in text: String,
    tokens: [ProtectedToken]
) throws -> String
```

Use DocC symbol links and directives such as `Important`, `Warning`, and
`Precondition` when they materially clarify correct use. Keep the first sentence
useful as the generated API summary.

## Implementation comments

Use `//` comments to explain:

- Why a non-obvious approach was chosen.
- Safety, privacy, focus, clipboard, or concurrency invariants.
- Platform or framework behavior that constrains the implementation.
- A workaround and the condition under which it can be removed.
- Intentional divergence from an otherwise expected pattern.

Do not use comments to translate code into prose, preserve dead code, or hide
unclear naming. Tracked work belongs in the issue tracker; a temporary `TODO` or
`FIXME` must state the concrete follow-up and should reference an issue once one
exists.

## Keeping documentation current

Update a docstring or documentation comment in the same change that modifies its
contract. Incorrect documentation is a defect. Review comments for stale
assumptions during refactoring, especially around validation, privacy, clipboard
ownership, and actor or thread boundaries.
