# Contributing to promptdiff

Thank you for your interest in contributing!  This document covers everything
you need to get started.

## Development setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/<your-username>/promptdiff.git
cd promptdiff

# 2. Install in editable mode with development dependencies
pip install -e ".[dev]"
```

## Running the tests

```bash
pytest
```

All tests must pass before submitting a pull request.  GUI-specific tests
that require a live display are automatically skipped in headless environments
such as CI — this is expected behaviour.

## Code style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Type-annotate all public functions using built-in generics (Python ≥ 3.9
  style, e.g. `list[tuple[str, str]]`).
- Keep the library **dependency-free**: the core package (`promptdiff`) must
  use only the Python standard library.  The GUI uses only `tkinter`, which
  ships with CPython.
- Write docstrings for every public symbol.  Use NumPy-style sections
  (*Parameters*, *Returns*, *Raises*, *Examples*) for functions.
- Default to writing **no inline comments** unless the *why* is non-obvious.

## Pull request checklist

- [ ] All existing tests pass (`pytest`).
- [ ] New or changed behaviour is covered by new tests.
- [ ] Docstrings are updated where needed.
- [ ] `CHANGELOG.md` has an entry under `[Unreleased]`.
- [ ] The PR description explains the motivation and summarises the change.

## Reporting bugs and requesting features

Please open an issue at
<https://github.com/vdeshmukh203/promptdiff/issues> with a minimal
reproducible example for bugs or a concise description for feature requests.

## License

By contributing you agree that your contributions will be licensed under the
[MIT License](LICENSE).
