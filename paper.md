---
title: 'promptdiff: A Pure-Python Library for Structured Comparison of LLM Prompt Strings'
tags:
  - Python
  - large language models
  - prompt engineering
  - diff
  - natural language processing
  - text similarity
authors:
  - name: Vaibhav Deshmukh
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 2026-04-25
bibliography: paper.bib
---

# Summary

`promptdiff` is a lightweight, pure-Python library for comparing and analysing
differences between Large Language Model (LLM) prompt strings. The library
provides three core operations: a structured line-aware diff, standard
unified-diff output, and a character-bigram cosine similarity score. It ships
with a `tkinter`-based graphical user interface that renders colour-coded diffs
and similarity scores interactively. The entire implementation relies solely on
the Python standard library, making `promptdiff` trivially embeddable in any
Python environment without dependency conflicts.

# Statement of Need

Iterative refinement of prompt templates is a central workflow in modern LLM
application development. Practitioners routinely create many variants of a
prompt — adjusting phrasing, adding constraints, restructuring context — and
need to understand how those variants differ and how similar they are
[@Sahoo2024; @White2023]. This need arises in at least three recurring
scenarios:

1. **Version control for prompts.** Teams maintain prompt libraries that evolve
   over time. Without diff tooling tailored to prompt text, changes are hard to
   audit and review.
2. **Regression testing.** Automated pipelines compare the active prompt against
   a golden reference to detect unintended mutations before deployment.
3. **A/B experimentation.** Researchers need a normalised similarity metric to
   quantify how far apart two prompt variants are and correlate prompt distance
   with output quality.

General-purpose diff utilities (e.g., Unix `diff`, Python's `difflib`) solve
the structural comparison problem but provide no similarity metric. Embedding
systems and semantic similarity models (e.g., sentence-transformers
[@Reimers2019]) address similarity but require heavy dependencies and do not
produce human-readable diffs. `promptdiff` fills this gap by offering both
capabilities together in a single, dependency-free package.

# Implementation

## Structured diff

`diff(a, b)` splits each input into lines with `str.splitlines(keepends=True)`
and delegates to `difflib.SequenceMatcher` with `autojunk=False` to prevent
heuristic suppression of repeated lines. The resulting opcodes are translated
into a flat list of `(operation, line)` tuples where `operation` is one of
`"equal"`, `"add"`, or `"remove"`. Replace regions are decomposed into
consecutive remove/add entries so the caller never needs to handle a fourth
operation type. The representation is intentionally minimal: it is easy to
serialise, filter, and render.

## Unified diff

`format_unified(a, b, context=3)` wraps `difflib.unified_diff` with consistent
newline normalisation (appending `\n` to a final line that lacks one) and
exposes a `context` parameter to control the size of unchanged surrounding
regions. The output conforms to the unified diff standard [@Stallman1991] and
can be piped to any tool that consumes that format.

## Similarity metric

`similarity(a, b)` implements cosine similarity over character-bigram frequency
vectors [@Manning2008]:

$$\text{sim}(a, b) =
\frac{\displaystyle\sum_{k} \mathrm{bg}_k(a)\,\mathrm{bg}_k(b)}
{\sqrt{\displaystyle\sum_{k} \mathrm{bg}_k(a)^2}\;\cdot\;
 \sqrt{\displaystyle\sum_{k} \mathrm{bg}_k(b)^2}}$$

where $\mathrm{bg}_k(s)$ is the count of bigram $k$ in string $s$. Character
bigrams capture local character-level structure without requiring tokenisation
or a vocabulary, making the metric robust to prompt text that mixes natural
language with code snippets, JSON, and special tokens. Edge cases (empty
strings, strings shorter than two characters) are handled explicitly to avoid
division by zero. The metric is symmetric and normalised to $[0.0, 1.0]$.

## Graphical user interface

The optional GUI (launched via `promptdiff-gui`) is implemented with the
standard-library `tkinter` toolkit. It provides two editable text panels for
prompt input, a **Compare** button that populates a colour-coded structured
diff view and a unified diff view, and a large similarity score indicator
colour-graded from red (low similarity) through orange to green (high
similarity). The GUI requires no additional installation beyond `tkinter`,
which ships with CPython on all major platforms.

# Acknowledgements

The author thanks the open-source Python community for the high-quality
standard-library tools — `difflib`, `collections`, and `tkinter` — that make
this library possible without external dependencies.

# References
