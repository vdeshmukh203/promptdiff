# Contributing to promptdiff

Thank you for considering a contribution!  This document explains how to set
up a development environment, run the test suite, and submit changes.

## Development Setup

```bash
git clone https://github.com/vdeshmukh203/promptdiff.git
cd promptdiff
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

To check branch coverage:

```bash
pytest --cov=promptdiff --cov-report=term-missing
```

## Code Style

- The library is intentionally **standard-library only** for the core module
  (`promptdiff/__init__.py`).  Do not introduce external runtime dependencies.
- The GUI module (`promptdiff/gui.py`) may use `tkinter`, which ships with the
  standard Python distribution.
- Follow the existing docstring style (NumPy section format).
- All public functions must include `Parameters`, `Returns`, and `Raises`
  sections, plus at least one `Examples` entry.

## Submitting Changes

1. Fork the repository and create a feature branch.
2. Write tests for any new behaviour; the test suite must remain at 100 %
   branch coverage for the core module.
3. Open a pull request against `main`.  Please describe *why* the change is
   needed, not just what it does.

## Reporting Bugs

Open an issue at <https://github.com/vdeshmukh203/promptdiff/issues> with a
minimal reproducible example.

## Code of Conduct

All contributors are expected to be respectful and constructive.  Harassment
of any kind will not be tolerated.
