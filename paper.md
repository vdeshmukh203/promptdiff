---
title: 'promptdiff: Lightweight Comparison Utilities for LLM Prompt Strings'
tags:
  - Python
  - natural language processing
  - prompt engineering
  - large language models
  - text comparison
  - software tools
authors:
  - name: Vaibhav Deshmukh
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 27 April 2026
bibliography: paper.bib
---

# Summary

Iterative refinement of natural language prompts is now a routine part of
working with large language models (LLMs).  Practitioners routinely edit
prompts—clarifying instructions, adjusting tone, inserting few-shot
examples—and need to understand exactly what changed between versions and
how semantically close the revisions remain.  General-purpose diff tools
such as `diff(1)` and `git diff` answer the first question but provide no
signal on semantic proximity, while full-text similarity libraries answer
the second question but produce no structured diff.

`promptdiff` fills the gap: it is a pure-Python, zero-dependency library
that provides (1) a line-aware structured diff, (2) a standard unified-diff
formatter, and (3) a character-bigram cosine similarity score, together with
a Tkinter-based graphical user interface and an `argparse` command-line
interface.  The entire package relies exclusively on the Python standard
library and is therefore trivially portable across platforms and Python
environments without requiring additional installation steps.

# Statement of Need

Prompt engineering has rapidly matured from an informal practice into a
systematic discipline [@white2023prompt; @sahoo2024systematic].
Practitioners routinely maintain versioned prompt libraries and compare
prompt candidates to evaluate the effect of each revision
[@zamfirescu2023johnny].  Existing version-control and diff tools were
designed for source code and treat every textual change uniformly, offering
no domain-specific signal for prompts.  Semantic similarity metrics such as
BLEU [@papineni2002bleu] and BERTScore [@zhang2020bertscore] require
substantial dependencies and are calibrated for translation or
summarisation rather than prompt comparison.

`promptdiff` targets the gap between these extremes: a small, portable
utility that any Python 3.9+ environment can import without additional
installation steps, and that surfaces both structural and
lexical-similarity information in a single library call.

# Functionality

## Structured diff (`diff`)

`diff(a, b)` splits both strings on line boundaries using
`splitlines(keepends=True)`, feeds the resulting sequences to
`difflib.SequenceMatcher` [@vanrossum2024difflib] with `autojunk=False`,
and flattens the resulting opcodes into a list of `(operation, line)`
tuples where `operation` is one of `"equal"`, `"add"`, or `"remove"`.
Replace regions are expanded into contiguous remove/add blocks so callers
never encounter a composite opcode.  This representation is convenient for
downstream rendering, filtering, and aggregation.

## Unified diff (`format_unified`)

`format_unified(a, b)` wraps `difflib.unified_diff` to produce a standard
unified-diff string with configurable file labels (`fromfile`, `tofile`)
and context width (`context`).  It normalises missing trailing newlines
before passing lines to the differ so that single-line and multi-line
inputs are handled uniformly.

## Cosine similarity (`similarity`)

`similarity(a, b)` computes the cosine similarity of character bigram
frequency vectors:

$$\text{sim}(a, b) =
  \frac{\displaystyle\sum_{g \in \mathcal{G}} f_a(g)\, f_b(g)}
       {\sqrt{\displaystyle\sum_{g} f_a(g)^2}\;
        \sqrt{\displaystyle\sum_{g} f_b(g)^2}}$$

where $f_x(g)$ is the count of bigram $g$ in string $x$ and $\mathcal{G}$
is the intersection of bigrams shared by both strings (with zeros
contributing nothing to the dot product).  The score lies in
$\left[0, 1\right]$: identical strings return $1.0$ and strings with no
shared bigrams return $0.0$.  Character bigrams are a language-agnostic,
lightweight feature that captures local character patterns without
requiring tokenisation or an external vocabulary [@kondrak2005n].  Limiting
the sum to the intersection set avoids iterating over the full bigram
universe and keeps the function $O(|a| + |b|)$ in both time and space.

## Graphical user interface

`promptdiff-gui` launches a Tkinter desktop application with two editable
text panes (before/after), a colour-highlighted diff panel (green for
additions, red for removals), and a live similarity score display.  Users
can open plain-text files directly from the interface and trigger
comparisons with the Ctrl+Return keyboard shortcut.  The GUI shares the
same three core functions and adds no dependencies beyond the Python
standard library.

## Command-line interface

The `promptdiff` command accepts two string arguments or, with `--files`,
two file paths, and writes either an inline or unified diff to standard
output together with the similarity score.

# Quality Assurance

The library ships with a test suite (pytest) that covers all public
functions across normal cases, boundary conditions (empty strings, single
characters, strings without trailing newlines), Unicode input, and
Windows-style line endings.  The command-line interface is tested with
inline strings, file arguments, and error paths (missing files).
Continuous integration runs the full test suite on Ubuntu across Python
versions 3.9, 3.10, 3.11, and 3.12 on every push and pull request.

# Acknowledgements

The author thanks the Python Software Foundation for the `difflib` module
that underpins the diff functionality.

# References
