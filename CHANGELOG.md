# Changelog

All notable changes to promptdiff are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - 2026-05-07

### Added
- `promptdiff.gui` — Tkinter-based graphical interface with side-by-side
  editors, colour-coded line-diff and unified-diff views, similarity score
  display, and `Ctrl+Enter` keyboard shortcut.
- `promptdiff-gui` CLI entry point (installed via `pip install promptdiff`).
- `fromfile` / `tofile` keyword arguments on `format_unified()` for custom
  header labels.
- `[dev]` optional-dependency group (`pip install "promptdiff[dev]"`).
- `CONTRIBUTING.md` with development setup and PR checklist.
- Expanded test suite: 40 tests covering new parameters, autojunk behaviour,
  GUI module importability, and additional edge cases.

### Fixed
- `diff()` now passes `autojunk=False` to `SequenceMatcher`, preventing
  the junk-detection heuristic from silently suppressing frequently repeated
  lines in short prompt texts.

### Changed
- Version bump from 0.1.0 → 0.2.0.
- Return-type annotation of `diff()` tightened from `list` to
  `list[tuple[str, str]]`.
- Removed unused `from typing import List, Tuple` import.
- NumPy-style docstrings with *Parameters*, *Returns*, *Raises*, and
  *Examples* sections on all public functions.
- `pyproject.toml`: added version classifiers, topic classifiers, Bug Tracker
  and Changelog URL, and `[tool.pytest.ini_options]`.
- `README.md` expanded to include statement of need, full API reference,
  GUI documentation, testing instructions, and citation block.

## [0.1.0] - 2026-04-25

### Added
- `diff(a, b)` returning list of opcodes with changed line ranges.
- `format_unified(a, b)` producing a unified-diff string.
- `similarity(a, b)` computing character-bigram cosine similarity.
- Pure standard-library implementation with no external dependencies.
- pytest test suite with 100 % branch coverage on core functions.
