---
title: 'promptdiff: A Pure-Python Library for Diffing and Comparing Prompt Strings'
tags:
  - Python
  - natural language processing
  - prompt engineering
  - text diff
  - large language models
authors:
  - name: Vaibhav Deshmukh
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 2026-04-29
bibliography: paper.bib
---

# Summary

`promptdiff` is a lightweight Python library for computing and visualising
differences between pairs of prompt strings.  It provides three complementary
views of how two texts diverge: a structured line-level diff, a word-level
diff, and a standard unified-diff string.  It also provides a cosine
similarity score derived from character bigrams that gives a continuous
measure of how closely related two prompts are.  All functionality is
implemented with the Python standard library alone—no third-party packages are
required—making the library easy to embed in any Python environment.  An
optional Tkinter graphical interface ships with the package so that
practitioners can compare prompts interactively without writing any code.

# Statement of Need

Large language model (LLM) practitioners routinely iterate on prompts
[@brown2020language; @wei2022chain].  A single production prompt can go
through dozens of revisions as teams tune instructions, few-shot examples,
and output constraints.  Tracking what changed between versions is
surprisingly hard with general-purpose tools: `git diff` operates on files
rather than in-memory strings, and standard text-diff utilities do not expose
structured, programmatically consumable output.

`promptdiff` fills this gap.  It targets three use cases:

1. **Prompt version control** — developers can log and audit every revision
   to a system prompt by diffing consecutive versions and storing the
   structured output alongside their application telemetry.
2. **Automated regression testing** — test suites can assert that a refactored
   prompt preserves specific lines or that similarity to the previous version
   stays above a threshold, catching unintended edits.
3. **Interactive exploration** — the bundled GUI lets researchers visually
   inspect colour-coded diffs without leaving their workflow.

Existing libraries such as `deepdiff` [@deepdiff] focus on Python data
structures rather than raw text, and `difflib` [@python-difflib], while
powerful, requires boilerplate to produce structured output and does not
include a similarity score.  `promptdiff` composes `difflib` internally and
exposes a minimal, documented API designed specifically for the prompt-diff
workflow.

# Functionality

## Core API

`promptdiff` exports four public functions.

**`diff(a, b)`** returns a list of `(op, line)` tuples where `op` is one
of `"equal"`, `"add"`, or `"remove"`.  Replace regions are expanded so that
callers never encounter a `"replace"` tag.  The function disables the
`autojunk` heuristic in `difflib.SequenceMatcher` so that repeated lines
(common in few-shot prompt templates) are diffed faithfully.

**`word_diff(a, b)`** tokenises on whitespace and returns the same
`(op, token)` tuple vocabulary as `diff`, providing finer-grained feedback
on intra-line changes.

**`format_unified(a, b, *, fromfile="a", tofile="b")`** returns a
standard unified-diff string compatible with `patch(1)`.  The `fromfile`
and `tofile` keyword arguments allow callers to substitute meaningful labels
(e.g. `"v1.2"` and `"v1.3"`) for the default `"a"` / `"b"` headers.

**`similarity(a, b)`** computes the cosine similarity of the character-bigram
frequency vectors of `a` and `b`, returning a float in `[0, 1]`.  The bigram
representation is language-agnostic and does not require tokenisation, making
it suitable for prompts in any natural language [@kondrak2005n].  Identical
strings return exactly `1.0`; the two-empty-string case is defined as `1.0`
by convention.

## Graphical Interface

The optional Tkinter GUI (launched with `promptdiff-gui` or
`python -m promptdiff.gui`) provides:

- Two editable text panes for the original and revised prompts.
- A colour-coded diff panel (green for additions, red for removals).
- A real-time similarity score updated on each comparison.
- Swap and Clear buttons plus a `Ctrl+Return` keyboard shortcut.

# Quality Assurance

The repository includes a pytest suite of 44 tests covering normal
operation, edge cases (empty inputs, single-character strings, missing
trailing newlines), type-error handling, and round-trip reconstruction
properties (i.e., that filtering the diff output by tag faithfully recovers
either input string).  Continuous integration runs the suite across Python
3.9, 3.10, 3.11, and 3.12 on every push and pull request.

# References
