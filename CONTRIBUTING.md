# Contributing to promptdiff

Thank you for your interest in contributing!

## Getting started

```bash
git clone https://github.com/vdeshmukh203/promptdiff
cd promptdiff
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

All tests must pass before a pull request can be merged.  Coverage should not
decrease.

## Code style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- All public functions must have a NumPy-style docstring with `Parameters`,
  `Returns`, `Raises`, and at least one `Examples` entry.
- Type annotations are required for all function signatures.
- No third-party runtime dependencies.  The only permitted runtime imports are
  from the Python standard library.

## Submitting changes

1. Fork the repository and create a feature branch.
2. Write tests for new functionality (aim for full branch coverage).
3. Open a pull request against `main` with a clear description of the change
   and the motivation.

## Reporting bugs

Please open an issue at
<https://github.com/vdeshmukh203/promptdiff/issues> and include a minimal
reproducible example.

## Code of Conduct

All contributors are expected to be respectful and constructive.  Harassment
of any kind is not tolerated.
