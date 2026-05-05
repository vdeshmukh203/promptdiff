# Changelog

All notable changes to promptdiff are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - 2026-05-05

### Added
- `promptdiff.gui` module: `tkinter`-based graphical user interface with
  colour-coded structured diff view, unified diff tab, and similarity score
  indicator; launched via `promptdiff-gui` console script.
- `context` parameter to `format_unified()` (default `3`, matching `diff -u`)
  allowing callers to control the number of unchanged context lines.
- `py.typed` marker (PEP 561) so type checkers recognise the package as typed.
- `paper.md` and `paper.bib` for JOSS submission.
- `__author__` module-level attribute.

### Changed
- Return type annotation of `diff()` is now the precise
  `List[Tuple[str, str]]` alias `_DiffResult` rather than the bare `list`.
- Error messages from all public functions now include the function name and
  the actual types received, improving debuggability.
- `SequenceMatcher` is now constructed with `autojunk=False` to prevent
  heuristic suppression of repeated lines in large prompts.
- `pyproject.toml`: version bumped to `0.2.0`; added `Bug Tracker` URL,
  `Development Status`, audience, and topic classifiers.

### Fixed
- `format_unified()` no longer accepts a negative `context` value (raises
  `ValueError` with a descriptive message).

## [0.1.0] - 2026-04-25

### Added
- `diff(a, b)` returning list of opcodes with changed line ranges.
- `format_unified(a, b)` producing a unified-diff string.
- `similarity(a, b)` computing character-bigram cosine similarity.
- Pure standard-library implementation with no external dependencies.
- pytest test suite with 100 % branch coverage on core functions.
