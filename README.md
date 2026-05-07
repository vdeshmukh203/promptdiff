# promptdiff

[![CI](https://github.com/vdeshmukh203/promptdiff/actions/workflows/ci.yml/badge.svg)](https://github.com/vdeshmukh203/promptdiff/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/promptdiff.svg)](https://pypi.org/project/promptdiff/)
[![Python](https://img.shields.io/pypi/pyversions/promptdiff.svg)](https://pypi.org/project/promptdiff/)

Compute and format diffs between prompt strings — with a built-in GUI.

Pure Python, standard library only. Provides a line-aware diff, a
unified diff string, and a character-bigram cosine similarity score
tailored for comparing LLM prompt text.

---

## Statement of need

Iterative prompt engineering requires tracking how prompts change between
experiments. General-purpose diff tools are built for source code, not for
short, semantically dense natural-language text where every line matters and
junk-heuristic suppression is harmful. `promptdiff` addresses this gap with
three purpose-built primitives and a GUI that lets practitioners inspect
changes at a glance without writing any code.

---

## Features

| Function | Description |
|---|---|
| `diff(a, b)` | Line-aware diff — list of `(op, line)` tuples with ops `"equal"`, `"add"`, `"remove"` |
| `format_unified(a, b)` | Standard unified-diff string, optional custom file labels |
| `similarity(a, b)` | Character-bigram cosine similarity in `[0.0, 1.0]` |
| `promptdiff-gui` | Tkinter GUI for side-by-side comparison with colour-coded diff output |

**Design principles**

- Pure Python — zero external dependencies (standard library only).
- Pure functions — no global state, no I/O, no side effects.
- `autojunk=False` — every line is treated as significant, even repeated ones.
- Tested on Python 3.9 – 3.12.

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

```python
from promptdiff import diff, format_unified, similarity

a = "You are a helpful assistant.\nAnswer concisely.\n"
b = "You are a helpful assistant.\nAnswer in detail.\n"

# Line-aware diff
for op, line in diff(a, b):
    print(f"{op:>6}  {line!r}")
# equal  'You are a helpful assistant.\n'
# remove 'Answer concisely.\n'
#    add 'Answer in detail.\n'

# Unified diff
print(format_unified(a, b))
# --- a
# +++ b
# @@ -1,2 +1,2 @@
#  You are a helpful assistant.
# -Answer concisely.
# +Answer in detail.

# Similarity score
print(similarity(a, b))   # 0.855...
```

---

## API reference

### `diff(a, b) → list[tuple[str, str]]`

Return a line-aware diff between two strings.

Each element of the returned list is a `(op, line)` tuple where `op` is one
of `"equal"`, `"add"`, or `"remove"`.  Trailing newlines are preserved on
each `line` so the lines can be re-concatenated.  *replace* regions are
expanded into *remove* + *add* sequences — callers never see a `"replace"`
op.

```python
diff("a\nb\n", "a\nc\n")
# [('equal', 'a\n'), ('remove', 'b\n'), ('add', 'c\n')]
```

Raises `TypeError` if either argument is not a `str`.

---

### `format_unified(a, b, *, fromfile="a", tofile="b") → str`

Return a unified diff string in the format produced by `diff -u`.

Lines without a trailing newline have one appended.  Returns an empty string
when both inputs are identical.  `fromfile` and `tofile` control the header
labels.

```python
print(format_unified("old prompt\n", "new prompt\n", fromfile="v1", tofile="v2"))
# --- v1
# +++ v2
# @@ -1 +1 @@
# -old prompt
# +new prompt
```

Raises `TypeError` if any argument is not a `str`.

---

### `similarity(a, b) → float`

Return the cosine similarity of character bigrams in two strings.

The result is in `[0.0, 1.0]`.  Identical strings return `1.0`; strings with
no shared bigrams return `0.0`.  Two empty strings return `1.0`; one empty
vs. one non-empty returns `0.0`.

```python
similarity("hello world", "hello world")  # 1.0
similarity("aaaa",        "bbbb")         # 0.0
similarity("hello world", "hello there") # ~0.63
```

Raises `TypeError` if either argument is not a `str`.

---

## Graphical user interface

Launch the GUI from the command line:

```bash
promptdiff-gui
# or
python -m promptdiff.gui
```

The interface provides:

- **Two side-by-side editors** for Prompt A and Prompt B.
- **Compare button** (also triggered by `Ctrl+Enter`) runs all three
  analysis functions and displays the results.
- **Similarity score** shown in the control bar after comparison.
- **Line diff view** — colour-coded output (green additions, red removals).
- **Unified diff view** — standard `diff -u` format with syntax highlighting.
- **Clear button** to reset the workspace.

The GUI requires only `tkinter`, which ships with CPython on all major
platforms.  No additional packages are needed.

---

## Running the tests

```bash
pip install "promptdiff[dev]"
pytest
```

The test suite covers all public functions (line diff, unified diff,
similarity) plus import-level smoke tests for the GUI module.  Tests that
require a live display are automatically skipped in headless environments.

---

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for
guidelines on setting up the development environment, running tests, and
submitting pull requests.

---

## Citation

If you use `promptdiff` in academic work, please cite:

```bibtex
@software{deshmukh2026promptdiff,
  author  = {Deshmukh, Vaibhav},
  title   = {promptdiff},
  year    = {2026},
  version = {0.2.0},
  url     = {https://github.com/vdeshmukh203/promptdiff},
  license = {MIT}
}
```

A machine-readable citation file is provided at
[CITATION.cff](CITATION.cff).

---

## License

MIT — see [LICENSE](LICENSE).
