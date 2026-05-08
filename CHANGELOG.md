# Changelog

All notable changes to promptdiff are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - 2026-05-08
### Added
- `promptdiff.gui` — Tkinter-based graphical interface with syntax-coloured
  diff output, similarity score display, and `Ctrl+Return` keyboard shortcut
- `python -m promptdiff` entry point that launches the GUI
- `promptdiff-gui` console script entry point
- `py.typed` marker for PEP 561 compliance
- JOSS submission paper (`paper.md`, `paper.bib`)
- `CONTRIBUTING.md` with development setup and code-style guidelines

### Changed
- `diff()` return type annotation tightened from `list` to
  `List[Tuple[Literal["equal","add","remove"], str]]`
- All public functions now include NumPy-style docstrings with `Parameters`,
  `Returns`, `Raises`, and `Examples` sections
- `__version__` bumped to `0.2.0`
- `pyproject.toml` gains `[dev]` optional dependencies, `[project.scripts]`,
  pytest, coverage, and mypy configuration tables
- `README.md` expanded with statement of need, full API reference, GUI usage,
  and citation block

### Fixed
- `format_unified` type guard now also raises `TypeError` when the second
  argument is not a string (was silently handled by `difflib` in some cases)

## [0.1.0] - 2026-04-25
### Added
- `diff(a, b)` returning list of opcodes with changed line ranges
- `format_unified(a, b)` producing a unified-diff string
- `similarity(a, b)` computing character-bigram cosine similarity
- Pure standard-library implementation with no external dependencies
- pytest test suite with 100 % branch coverage on core functions
