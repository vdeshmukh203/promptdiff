# Changelog

All notable changes to promptdiff are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - 2026-05-06

### Added
- `summary(a, b)` returning similarity score and added/removed/equal line counts
  in a single dict
- `src/promptdiff/gui.py` — `tkinter`-based graphical user interface with
  colour-coded diff view, similarity score, and line-change counter
- `promptdiff-gui` console script entry point to launch the GUI
- `python -m promptdiff` support via `__main__.py`
- `context` keyword argument on `format_unified` to control hunk size
- `paper.md` and `paper.bib` for JOSS submission
- Dev extra (`pip install "promptdiff[dev]"`) pulling in `pytest` and
  `pytest-cov`

### Changed
- Type hints updated to Python 3.9+ built-in generics (`list[...]`, `tuple[...]`
  instead of `typing.List`, `typing.Tuple`)
- `diff()` now passes `autojunk=False` to `SequenceMatcher` to prevent
  heuristic suppression of frequently-occurring tokens in few-shot prompts
- Version bumped to `0.2.0`
- Expanded README with API reference table, GUI section, and contributing guide

## [0.1.0] - 2026-04-25

### Added
- `diff(a, b)` returning list of opcodes with changed line ranges
- `format_unified(a, b)` producing a unified-diff string
- `similarity(a, b)` computing character-bigram cosine similarity
- Pure standard-library implementation with no external dependencies
- pytest test suite with 100 % branch coverage on core functions
