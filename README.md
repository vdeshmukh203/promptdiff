# promptdiff

[![CI](https://github.com/vdeshmukh203/promptdiff/actions/workflows/ci.yml/badge.svg)](https://github.com/vdeshmukh203/promptdiff/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/promptdiff)](https://pypi.org/project/promptdiff/)
[![Python](https://img.shields.io/pypi/pyversions/promptdiff)](https://pypi.org/project/promptdiff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Pure-Python library for comparing LLM prompt strings.  No external
dependencies — only the Python standard library.

## Features

| Function | Description |
|---|---|
| `diff(a, b)` | Line-level diff as `list[tuple[str, str]]` with ops `equal`, `add`, `remove` |
| `format_unified(a, b)` | Standard unified-diff string with optional `context` lines |
| `similarity(a, b)` | Character-bigram cosine similarity in `[0.0, 1.0]` |
| `summary(a, b)` | Dict combining similarity score and added/removed/equal line counts |
| `promptdiff-gui` | Tk-based GUI for interactive side-by-side comparison |

## Install

```bash
pip install promptdiff
```

The GUI uses `tkinter` which ships with CPython.  On Debian/Ubuntu, install it
with:

```bash
sudo apt install python3-tk
```

## Quick start

```python
from promptdiff import diff, format_unified, similarity, summary

a = "You are a helpful assistant.\nAnswer concisely.\n"
b = "You are a helpful assistant.\nAnswer in bullet points.\n"

# Unified diff (standard format)
print(format_unified(a, b))
# --- a
# +++ b
# @@ -1,2 +1,2 @@
#  You are a helpful assistant.
# -Answer concisely.
# +Answer in bullet points.

# Similarity score
print(similarity(a, b))   # e.g. 0.7453...

# Line-level opcodes
for op, line in diff(a, b):
    print(op, repr(line))
# equal 'You are a helpful assistant.\n'
# remove 'Answer concisely.\n'
# add 'Answer in bullet points.\n'

# All-in-one summary
print(summary(a, b))
# {'similarity': 0.7453..., 'added': 1, 'removed': 1, 'equal': 1}
```

## GUI

Launch the graphical interface:

```bash
promptdiff-gui
# or
python -m promptdiff
```

The GUI provides two editable panes for the original and revised prompts, a
**Compare** button, a real-time similarity score, and a colour-coded diff view
(green for additions, red for removals).

## API reference

### `diff(a, b) → list[tuple[str, str]]`

Returns a line-aware diff.  Each element is a pair `(op, line)` where `op` is
one of `"equal"`, `"add"`, or `"remove"` and `line` is the text with its
trailing newline preserved.  Replace regions are decomposed into remove-then-add
sequences.

`autojunk=False` is used internally so that frequently-repeating tokens (common
in few-shot prompts) are never silently suppressed.

### `format_unified(a, b, *, context=3) → str`

Returns a standard unified-diff string with header labels `a` and `b`.  The
`context` keyword controls how many surrounding lines appear in each hunk.
Returns `""` when `a == b`.

### `similarity(a, b) → float`

Computes the cosine similarity of the character-bigram frequency vectors of `a`
and `b`.  The metric is language-agnostic and requires no tokeniser.  Returns
`1.0` for identical strings and `0.0` when no bigrams are shared.

### `summary(a, b) → dict`

Convenience function that returns:

```python
{
    "similarity": float,   # cosine similarity
    "added":      int,     # lines in b but not a
    "removed":    int,     # lines in a but not b
    "equal":      int,     # unchanged lines
}
```

## Contributing

Bug reports and pull requests are welcome on the
[issue tracker](https://github.com/vdeshmukh203/promptdiff/issues).

Run the test suite with:

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).
