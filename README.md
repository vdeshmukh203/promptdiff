# promptdiff

[![CI](https://github.com/vdeshmukh203/promptdiff/actions/workflows/ci.yml/badge.svg)](https://github.com/vdeshmukh203/promptdiff/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

**promptdiff** is a pure-Python library for computing structured diffs and
cosine-similarity scores between LLM prompt strings.  It uses only the Python
standard library — no external dependencies required.

---

## Statement of need

Prompt engineering for large language models (LLMs) is an iterative process.
Practitioners regularly revise system prompts, few-shot examples, and
instruction blocks, but lack lightweight, dependency-free tooling to inspect
what changed between versions or to quantify how similar two prompt variants
are.  `promptdiff` fills this gap with three composable primitives:

| Function | What it returns |
|---|---|
| `diff(a, b)` | Line-aware structured diff as a list of `DiffLine` named tuples |
| `format_unified(a, b)` | Unified diff string (standard `-`/`+` format) |
| `similarity(a, b)` | Cosine similarity of character bigrams ∈ [0.0, 1.0] |

The library is designed for use in automated evaluation pipelines, Jupyter
notebooks, experiment logging frameworks, and the bundled GUI.

---

## Installation

```bash
pip install promptdiff
```

To install with development dependencies:

```bash
pip install "promptdiff[dev]"
```

---

## Quick start

### Python API

```python
from promptdiff import diff, format_unified, similarity

a = "You are a helpful assistant.\nAnswer concisely.\n"
b = "You are a helpful assistant.\nAnswer in detail.\n"

# Structured diff
for op, line in diff(a, b):
    prefix = "  " if op == "equal" else ("+ " if op == "add" else "- ")
    print(prefix + line, end="")
# Output:
#   You are a helpful assistant.
# - Answer concisely.
# + Answer in detail.

# Unified diff
print(format_unified(a, b))

# Similarity score
print(similarity(a, b))  # e.g. 0.8734...
```

### Command-line interface

```bash
# Compare two inline strings
promptdiff "Answer concisely." "Answer in detail."

# Compare files (prefix paths with @)
promptdiff @prompt_v1.txt @prompt_v2.txt --format unified

# Suppress the similarity score
promptdiff "foo" "bar" --no-similarity
```

### Graphical interface

```bash
# Launch the GUI (also the default when no arguments are given)
promptdiff --gui
python -m promptdiff
```

The GUI provides:
- Side-by-side editable text areas for Prompt A and Prompt B
- Live similarity score
- **Structured diff** tab — colour-coded added/removed/equal lines
- **Unified diff** tab — standard unified diff with syntax highlighting

---

## API reference

### `diff(a, b) → list[DiffLine]`

Returns a list of `DiffLine(op, line)` named tuples where `op` is one of
`"equal"`, `"add"`, or `"remove"`, and `line` is the raw text (trailing
newline preserved).  Replace regions are expanded into remove + add runs.

### `format_unified(a, b) → str`

Returns a unified diff string with headers `--- a` / `+++ b`.  Returns the
empty string when `a == b`.  Missing trailing newlines are appended
automatically.

### `similarity(a, b) → float`

Returns the cosine similarity of the character-bigram frequency vectors of
`a` and `b`, clamped to `[0.0, 1.0]`.  Identical strings return `1.0`;
strings with no shared bigrams return `0.0`.

### `DiffLine`

A `NamedTuple` with fields `op: str` and `line: str`.

---

## Development

```bash
git clone https://github.com/vdeshmukh203/promptdiff
cd promptdiff
pip install -e ".[dev]"
pytest
pytest --cov=promptdiff --cov-report=term-missing
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Citation

If you use `promptdiff` in your research, please cite it using the metadata in
[CITATION.cff](CITATION.cff) or:

```bibtex
@software{promptdiff,
  author  = {Deshmukh, Vaibhav},
  title   = {promptdiff: Compute and format diffs between prompt strings},
  version = {0.1.0},
  year    = {2026},
  url     = {https://github.com/vdeshmukh203/promptdiff},
  license = {MIT}
}
```

---

## License

MIT — see [LICENSE](LICENSE).
