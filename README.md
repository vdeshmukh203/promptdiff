# promptdiff

[![CI](https://github.com/vdeshmukh203/promptdiff/actions/workflows/ci.yml/badge.svg)](https://github.com/vdeshmukh203/promptdiff/actions)
[![PyPI](https://img.shields.io/pypi/v/promptdiff)](https://pypi.org/project/promptdiff/)
[![Python](https://img.shields.io/pypi/pyversions/promptdiff)](https://pypi.org/project/promptdiff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Lightweight, zero-dependency comparison utilities for LLM prompt strings.

`promptdiff` provides three primitives for iterative prompt engineering:

| Function | Description |
|---|---|
| `diff(a, b)` | Line-aware structured diff → list of `(op, line)` tuples |
| `format_unified(a, b)` | Standard unified-diff string (like `git diff`) |
| `similarity(a, b)` | Character-bigram cosine similarity score in `[0, 1]` |

All functions are **pure Python**, use only the **standard library**, and
have **no side effects**. Compatible with Python 3.9–3.12.

---

## Installation

```bash
pip install promptdiff
```

For development (includes test dependencies):

```bash
pip install -e ".[dev]"
```

---

## Quick start

### As a library

```python
from promptdiff import diff, format_unified, similarity

before = "You are a helpful assistant.\nAnswer concisely.\n"
after  = "You are a helpful assistant.\nAnswer in detail with examples.\n"

# Structured diff
for op, line in diff(before, after):
    prefix = {"equal": " ", "add": "+", "remove": "-"}[op]
    print(prefix, line, end="")
#   You are a helpful assistant.
# - Answer concisely.
# + Answer in detail with examples.

# Unified diff
print(format_unified(before, after))
# --- a
# +++ b
# @@ -1,2 +1,2 @@
#  You are a helpful assistant.
# -Answer concisely.
# +Answer in detail with examples.

# Similarity score
print(similarity(before, after))  # e.g. 0.7237
```

### Command-line interface

After installation the `promptdiff` command is available:

```bash
# Compare two inline strings
promptdiff "old prompt" "new prompt"

# Compare two files
promptdiff --files before.txt after.txt

# Unified diff format with custom context window
promptdiff --files --format unified --context 5 v1.txt v2.txt

# Suppress the similarity score
promptdiff --no-score "prompt A" "prompt B"

# Show version
promptdiff --version
```

### Graphical user interface

```bash
promptdiff-gui
# or
python -m promptdiff.gui
```

The GUI opens a desktop window with:

- **Before / After** panes — editable text areas with file-open buttons.
- **Diff** panel — colour-highlighted diff (green additions, red removals).
- **Similarity score** — updated on every comparison.
- **Ctrl+Return** keyboard shortcut to run the comparison.

---

## API reference

### `diff(a, b) → list[tuple[str, str]]`

Returns a list of `(operation, line)` tuples.

| `operation` | Meaning |
|---|---|
| `"equal"` | Line is unchanged |
| `"add"` | Line was added in `b` |
| `"remove"` | Line was removed from `a` |

Trailing newlines are preserved on each line so that the original strings
can be reconstructed by joining the appropriate lines.  Replace regions
are expanded into contiguous remove/add blocks.

**Raises** `TypeError` if either argument is not a `str`.

---

### `format_unified(a, b, *, fromfile="a", tofile="b", context=3) → str`

Returns a standard unified-diff string.  Produces an empty string when
`a == b`.  Accepts optional keyword arguments:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `fromfile` | `str` | `"a"` | Label on the `---` header |
| `tofile` | `str` | `"b"` | Label on the `+++` header |
| `context` | `int` | `3` | Unchanged lines shown around each hunk |

**Raises** `TypeError` / `ValueError` on bad arguments.

---

### `similarity(a, b) → float`

Returns the cosine similarity of character bigram frequency vectors,
a value in the closed interval `[0.0, 1.0]`.

- Identical strings → `1.0`
- No shared bigrams → `0.0`
- Both empty → `1.0`
- One empty → `0.0`

Character bigrams are a language-agnostic feature that captures local
lexical patterns without requiring tokenisation or an external vocabulary.

**Raises** `TypeError` if either argument is not a `str`.

---

## Contributing

Contributions are welcome.  Please open an issue before submitting a pull
request for significant changes.

```bash
git clone https://github.com/vdeshmukh203/promptdiff
cd promptdiff
pip install -e ".[dev]"
pytest
```

---

## Citation

If you use `promptdiff` in published research, please cite:

```bibtex
@software{deshmukh2026promptdiff,
  author  = {Deshmukh, Vaibhav},
  title   = {promptdiff: Lightweight Comparison Utilities for {LLM} Prompt Strings},
  year    = {2026},
  url     = {https://github.com/vdeshmukh203/promptdiff},
  version = {0.1.0},
}
```

---

## License

MIT — see [LICENSE](LICENSE).
