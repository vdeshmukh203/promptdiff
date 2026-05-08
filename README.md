# promptdiff

[![PyPI](https://img.shields.io/pypi/v/promptdiff)](https://pypi.org/project/promptdiff/)
[![Python](https://img.shields.io/pypi/pyversions/promptdiff)](https://pypi.org/project/promptdiff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/vdeshmukh203/promptdiff/actions/workflows/ci.yml/badge.svg)](https://github.com/vdeshmukh203/promptdiff/actions)

**Compute and format diffs between LLM prompt strings.**

Pure Python · standard library only · zero dependencies

---

## Statement of Need

The rapid adoption of large language models (LLMs) has created an engineering
discipline centred on the iterative refinement of *prompts*—natural-language
instructions that condition model behaviour.  Unlike traditional source code,
prompts are prose artefacts whose changes are poorly served by conventional
diff tools, which show no notion of *how similar* two versions are.

`promptdiff` fills this gap.  It provides:

- A **line-aware structured diff** (`diff`) that yields labelled edit operations
  suitable for programmatic processing or coloured rendering.
- A **unified diff string** (`format_unified`) that follows the standard format
  produced by `diff(1)` and is ready to display or log.
- A **cosine similarity score** (`similarity`) based on character bigrams, giving
  a numerical measure of how much two prompt variants share.

The library targets prompt-engineering workflows: experiment-tracking systems,
automated prompt-regression test suites, and CI pipelines that need to inspect
and quantify prompt changes without introducing third-party dependencies.

---

## Install

```bash
pip install promptdiff
```

Requires Python ≥ 3.9.  No external packages are needed.

---

## Quick Start

```python
from promptdiff import diff, format_unified, similarity

a = "You are a helpful assistant.\nAnswer concisely.\n"
b = "You are a helpful assistant.\nAnswer in three sentences or fewer.\n"

# structured diff
for op, line in diff(a, b):
    print(op, repr(line))
# equal  'You are a helpful assistant.\n'
# remove 'Answer concisely.\n'
# add    'Answer in three sentences or fewer.\n'

# unified-diff string
print(format_unified(a, b))
# --- a
# +++ b
# @@ -1,2 +1,2 @@
#  You are a helpful assistant.
# -Answer concisely.
# +Answer in three sentences or fewer.

# similarity score  [0.0 – 1.0]
print(similarity(a, b))
# 0.6736...
```

---

## Graphical Interface

A Tkinter-based GUI ships with the package and requires no extra dependencies.

```bash
python -m promptdiff
# or
promptdiff-gui
```

The window shows two side-by-side text editors (Prompt A and Prompt B).
Press **Compare** (or `Ctrl+Return`) to display a syntax-coloured unified diff
and the similarity score.

---

## API Reference

### `diff(a, b) → list[tuple[str, str]]`

Return a line-aware edit script between two strings.

Each element is a `(op, line)` pair where `op` is one of:

| op | meaning |
|----|---------|
| `"equal"` | line is unchanged |
| `"remove"` | line is present in *a* but not *b* |
| `"add"` | line is present in *b* but not *a* |

Trailing newlines are preserved.  Replace regions are expanded into a sequence
of `"remove"` entries followed by `"add"` entries.

Raises `TypeError` if either argument is not a `str`.

---

### `format_unified(a, b) → str`

Return a unified diff string with header labels `a` and `b`.

Returns an empty string when the inputs are identical.  Lines without trailing
newlines have one appended automatically so the output is well-formed.

Raises `TypeError` if either argument is not a `str`.

---

### `similarity(a, b) → float`

Return the character-bigram cosine similarity of two strings in `[0.0, 1.0]`.

Two identical strings return `1.0`; two strings with no shared bigrams return
`0.0`.  Empty strings are handled as a special case: two empty strings return
`1.0`, while one empty string compared with any non-empty string returns `0.0`.

Raises `TypeError` if either argument is not a `str`.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Citation

If you use `promptdiff` in published research, please cite:

```bibtex
@software{promptdiff,
  author  = {Deshmukh, Vaibhav},
  title   = {promptdiff: Compute and format diffs between prompt strings},
  year    = {2026},
  url     = {https://github.com/vdeshmukh203/promptdiff},
  version = {0.2.0}
}
```

---

## License

MIT — see [LICENSE](LICENSE).
