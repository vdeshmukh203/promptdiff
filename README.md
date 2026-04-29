# promptdiff

[![CI](https://github.com/vdeshmukh203/promptdiff/actions/workflows/ci.yml/badge.svg)](https://github.com/vdeshmukh203/promptdiff/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/promptdiff)](https://pypi.org/project/promptdiff/)

Compute and format diffs between prompt strings.

Pure Python, standard-library only.  Provides a line-aware diff, a word-level
diff, a unified diff formatter, and a character-bigram cosine similarity score.
Ships with an optional Tkinter GUI for interactive use.

---

## Install

```bash
pip install promptdiff
```

Requires Python 3.9 or later.  No third-party dependencies.

---

## Quick start

```python
from promptdiff import diff, word_diff, format_unified, similarity

a = "You are a helpful assistant.\nAnswer in English.\n"
b = "You are a helpful assistant.\nAnswer in French.\n"

# Line-level diff
for op, line in diff(a, b):
    print(op, repr(line))
# equal 'You are a helpful assistant.\n'
# remove 'Answer in English.\n'
# add 'Answer in French.\n'

# Word-level diff
for op, tok in word_diff("Answer in English.", "Answer in French."):
    print(op, repr(tok.strip()))
# equal 'Answer'
# equal 'in'
# remove 'English.'
# add 'French.'

# Unified diff (patch-compatible string)
print(format_unified(a, b, fromfile="v1", tofile="v2"))

# Similarity score  [0.0 – 1.0]
print(similarity(a, b))   # e.g. 0.8461...
```

---

## API reference

### `diff(a, b) -> list[tuple[str, str]]`

Returns a list of `(op, line)` tuples.

| `op`     | Meaning                                   |
|----------|-------------------------------------------|
| `equal`  | Line is identical in both strings         |
| `add`    | Line was added in `b`                     |
| `remove` | Line was removed from `a`                 |

Replace regions are expanded into remove/add runs — `"replace"` never appears
as an operation tag.

### `word_diff(a, b) -> list[tuple[str, str]]`

Same `(op, token)` vocabulary as `diff`, but tokenised on whitespace.
Tokens include trailing whitespace so the sequence can be re-joined losslessly.

### `format_unified(a, b, *, fromfile="a", tofile="b") -> str`

Returns a standard unified-diff string compatible with `patch(1)`.
Returns the empty string when `a == b`.

### `similarity(a, b) -> float`

Returns the cosine similarity of character-bigram frequency vectors,
a float in `[0.0, 1.0]`.  Identical strings return `1.0`;
two empty strings also return `1.0` by convention.

---

## GUI

```bash
promptdiff-gui
# or
python -m promptdiff.gui
```

The window opens with two editable text panes (original and revised), a
colour-coded diff panel, and a similarity score.  Press **Ctrl+Return** or
click **Diff** to run the comparison.

---

## Development

```bash
git clone https://github.com/vdeshmukh203/promptdiff
pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## Citation

If you use `promptdiff` in published work, please cite it:

```bibtex
@software{promptdiff,
  title   = {promptdiff},
  author  = {Deshmukh, Vaibhav},
  year    = {2026},
  url     = {https://github.com/vdeshmukh203/promptdiff},
  version = {0.2.0}
}
```

See also [CITATION.cff](CITATION.cff).

---

## License

MIT — see [LICENSE](LICENSE).
