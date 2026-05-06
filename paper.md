---
title: 'promptdiff: A Python library for structured comparison of LLM prompt strings'
tags:
  - Python
  - large language models
  - prompt engineering
  - diff
  - text similarity
authors:
  - name: Vaibhav Deshmukh
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 25 April 2026
bibliography: paper.bib
---

# Summary

Large language model (LLM) applications depend critically on the precise wording
of their input prompts.  Even small textual changes — adjusting a system
instruction, rewording an example, or adding a constraint — can substantially
alter model behaviour [@openai2023gpt4].  `promptdiff` is a small,
dependency-free Python library that provides structured tools for comparing
prompt strings: a line-level diff with explicit `add`/`remove`/`equal`
operations, a unified-diff formatter, a character-bigram cosine-similarity score,
and an aggregate summary function.  A `tkinter`-based graphical interface is also
included for interactive use.  The library restricts itself to the Python
standard library so that it can be embedded in any project without introducing
transitive dependency conflicts.

# Statement of need

Prompt engineering has become a central activity in applied machine learning
[@white2023prompt].  Practitioners frequently iterate on prompts, A/B-test
variants, run regression suites, and need to review diffs before deploying
changes to production systems.  Existing general-purpose diff tools — such as
`difflib` from the Python standard library or the Unix `diff` utility — operate
on raw text and do not provide (1) programmatic access to individual change
operations or (2) a continuous similarity metric.  `promptdiff` fills this gap
by exposing a clean, typed Python API that:

1. **Separates diff computation from rendering**, enabling downstream tools (test
   frameworks, monitoring dashboards, Jupyter notebooks) to process change
   operations programmatically.
2. **Provides a cosine-similarity score** based on character bigrams, giving a
   model-agnostic measure of prompt proximity without requiring access to any
   particular tokeniser.
3. **Disables the autojunk heuristic** in `SequenceMatcher` by default, which
   prevents frequently-repeating tokens — common in few-shot prompt templates —
   from being silently excluded from the diff.
4. **Ships a graphical user interface** for interactive side-by-side comparison,
   making the library accessible to practitioners who prefer visual tools.

# Functionality

## Line-level diff (`diff`)

`diff(a, b)` returns a `list[tuple[str, str]]` in which the first element of
each pair is one of `"equal"`, `"add"`, or `"remove"` and the second element is
the corresponding line with its trailing newline preserved.  Replace operations
are decomposed into remove-then-add sequences, giving callers a simple
three-opcode alphabet.  The implementation wraps
`difflib.SequenceMatcher` [@vanrossum2024difflib] with `autojunk=False`.

## Unified diff (`format_unified`)

`format_unified(a, b, *, context=3)` produces a standard unified-diff string
with `a` and `b` as header labels.  The function normalises the trailing newline
of the last line so that the output is always well-formed.  The `context`
keyword controls how many surrounding lines are included in each hunk.  Returns
the empty string when the two inputs are identical.

## Cosine similarity (`similarity`)

`similarity(a, b)` computes the cosine similarity of the character-bigram
frequency vectors of the two input strings [@manning2008introduction].  The
metric is language-agnostic, requires no tokeniser, and runs in linear time with
respect to string length.  The result is a float in `[0.0, 1.0]`; identical
strings return `1.0` and strings sharing no bigrams return `0.0`.  Two empty
strings return `1.0`; an empty string compared with any non-empty string returns
`0.0`.

## Aggregate summary (`summary`)

`summary(a, b)` returns a single `dict` combining the similarity score with the
counts of added, removed, and equal lines.  This is a convenience function
intended for use in testing and monitoring pipelines where both metrics are
needed in one call.

## Graphical user interface

Running `promptdiff-gui` (or `python -m promptdiff`) launches a `tkinter`-based
desktop application.  The interface provides two editable text panes for the
original and revised prompts, a **Compare** button, a real-time similarity
score, a line-change counter, and a colour-coded diff view (green for additions,
red for removals, blue for hunk headers).  Because `tkinter` ships with CPython,
no additional packages are required.

# Testing

`promptdiff` ships with a `pytest` suite covering all public functions across
normal operation, edge cases (empty strings, single-character inputs, missing
trailing newlines), and error conditions (non-string arguments).  The test suite
is executed against Python 3.9, 3.10, 3.11, and 3.12 on every push via GitHub
Actions.

# Acknowledgements

The author thanks the Python Software Foundation for the `difflib` and `tkinter`
modules that form the implementation backbone of this library.

# References
