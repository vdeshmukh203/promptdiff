---
title: 'promptdiff: A Python library for comparing and scoring LLM prompt strings'
tags:
  - Python
  - prompt engineering
  - large language models
  - diff
  - similarity
  - text comparison
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

`promptdiff` is a lightweight, pure-Python library for computing structured
line-level diffs and character-bigram cosine similarity scores between two text
strings.  The library targets the practice of *prompt engineering*—the iterative
refinement of natural-language instructions passed to large language models
(LLMs)—where practitioners need to inspect and quantify changes between
successive prompt versions as they iterate toward desired model behaviour.

The library exposes three composable public functions: `diff`, which returns a
list of labelled edit operations; `format_unified`, which renders a standard
unified-diff string; and `similarity`, which returns a floating-point cosine
similarity score based on character bigrams.  A Tkinter-based graphical
interface ships alongside the library and requires no additional installation
beyond the Python standard library.

# Statement of Need

The rapid adoption of LLMs in production systems has created a software
engineering discipline centred on the design and maintenance of *prompts*—
natural-language instructions that condition model behaviour
[@brown2020gpt3; @wei2022emergent].  Unlike traditional source code, prompts
are prose artefacts whose changes are poorly served by conventional code-review
tools.  Practitioners regularly need to answer questions such as: *Which lines
changed between iteration 4 and iteration 5 of this prompt?* or *How
semantically similar are two prompt variants that produce different outputs?*

Existing diff utilities (e.g., GNU diff, Python's `difflib`) address the first
question but provide no notion of textual similarity, while string-similarity
libraries (e.g., `rapidfuzz` [@rapidfuzz], `textdistance`) address the second
but are not oriented towards prompt-engineering workflows and introduce
non-trivial installation overhead.  `promptdiff` fills this gap by offering
both capabilities in a single, dependency-free package.

The library is intentionally minimal: it relies exclusively on the Python
standard library (Python ≥ 3.9) and is designed to be embedded in larger
toolchains—experiment-tracking systems, automated prompt-regression tests, or
CI pipelines—without adding third-party dependencies.

# Mathematics

The similarity score is computed as the cosine similarity of character-bigram
frequency vectors.  For a string $s$, define

$$\mathbf{v}_s[b] = \bigl|\{i : s[i{:}i{+}2] = b\}\bigr|$$

as the count of bigram $b$ in $s$.  The similarity between strings $a$ and $b$
is then

$$\text{similarity}(a, b) =
  \frac{\mathbf{v}_a \cdot \mathbf{v}_b}
       {\|\mathbf{v}_a\| \, \|\mathbf{v}_b\|} \in [0, 1].$$

Character bigrams capture local character-level overlap and are robust to minor
rewordings, making them more sensitive to surface-level prompt edits than
whole-word approaches while remaining far lighter than embedding-based
semantic similarity methods [@sentence_transformers].

The structured diff is produced by Python's `difflib.SequenceMatcher`, which
implements the Ratcliff/Obershelp algorithm [@ratcliff1988], augmented with
an expansion step that converts `replace` opcodes into explicit `remove`/`add`
sequences for downstream consumers.

# Usage

The library is installed via pip and has no external runtime dependencies:

```bash
pip install promptdiff
```

The three core functions are used as follows:

```python
from promptdiff import diff, format_unified, similarity

a = "You are a helpful assistant.\nAnswer concisely.\n"
b = "You are a helpful assistant.\nAnswer in three sentences or fewer.\n"

for op, line in diff(a, b):
    print(op, repr(line))
# equal  'You are a helpful assistant.\n'
# remove 'Answer concisely.\n'
# add    'Answer in three sentences or fewer.\n'

print(similarity(a, b))
# 0.6736...
```

A graphical interface is launched with:

```bash
python -m promptdiff
```

# Acknowledgements

The author thanks the open-source Python community for maintaining the
`difflib` module that underpins this library.

# References
