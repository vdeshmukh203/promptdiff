# Changelog

All notable changes to promptdiff are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2026-04-25
### Added
- `diff(a, b)` returning list of opcodes with changed line ranges
- `format_unified(a, b)` producing a unified-diff string
- `similarity(a, b)` computing character-bigram cosine similarity
- Pure standard-library implementation with no external dependencies
- pytest test suite with 100 % branch coverage on core functions
