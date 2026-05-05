# promptdiff

**Compute and format structured diffs between LLM prompt strings.**

Pure Python · standard library only · no external dependencies · typed

---

## Overview

`promptdiff` provides three focused utilities for comparing prompt text:

| Function | Description |
|---|---|
| `diff(a, b)` | Line-aware structured diff → list of `(op, line)` tuples |
| `format_unified(a, b)` | Human-readable unified diff string |
| `similarity(a, b)` | Character-bigram cosine similarity in `[0.0, 1.0]` |

It also ships a `tkinter`-based **graphical user interface** (`promptdiff-gui`)
for interactive side-by-side comparison with colour-coded output.

## Install

```bash
pip install promptdiff
```

Requires Python ≥ 3.9. No third-party packages needed.
The GUI uses `tkinter` which ships with CPython on all major platforms.

## Quick start

```python
from promptdiff import diff, format_unified, similarity

a = "You are a helpful assistant.\nAnswer concisely."
b = "You are a helpful assistant.\nAnswer in detail and cite sources."

# Structured diff
for op, line in diff(a, b):
    prefix = {" equal": " ", "add": "+", "remove": "-"}[op]
    print(prefix, line, end="")

# Unified diff
print(format_unified(a, b))

# Similarity score (0.0 = completely different, 1.0 = identical)
print(f"Similarity: {similarity(a, b):.1%}")
```

Output:

```
  You are a helpful assistant.
- Answer concisely.
+ Answer in detail and cite sources.

--- a
+++ b
@@ -1,2 +1,2 @@
 You are a helpful assistant.
-Answer concisely.
+Answer in detail and cite sources.

Similarity: 64.5%
```

## API reference

### `diff(a, b) -> list[tuple[str, str]]`

Returns a list of `(op, line)` tuples describing the line-level changes from
*a* to *b*.

- `op` is `"equal"`, `"add"`, or `"remove"` — never `"replace"`.
- Trailing newlines are preserved so you can reconstruct either side by
  joining the relevant lines.

```python
diff("a\nb\n", "a\nc\n")
# → [('equal', 'a\n'), ('remove', 'b\n'), ('add', 'c\n')]
```

### `format_unified(a, b, context=3) -> str`

Unified diff string with `--- a` / `+++ b` headers. Returns `""` when
identical. The optional `context` parameter controls how many unchanged
lines appear around each changed region (default `3`).

```python
print(format_unified("hello\n", "world\n"))
# --- a
# +++ b
# @@ -1 +1 @@
# -hello
# +world
```

### `similarity(a, b) -> float`

Character-bigram cosine similarity. Returns a float in `[0.0, 1.0]`.

- `1.0` — strings are identical (or both empty).
- `0.0` — no shared bigrams, or one string is empty.
- Intermediate values — partial overlap.

The metric is symmetric: `similarity(a, b) == similarity(b, a)`.

```python
similarity("hello world", "hello there")  # → ~0.63
similarity("hello", "hello")              # → 1.0
similarity("foo", "bar")                  # → 0.0
```

## Graphical interface

Launch the GUI from the command line after installation:

```bash
promptdiff-gui
```

Or run directly without installing:

```bash
python -m promptdiff.gui
```

The GUI provides:

- Two editable text panels (**Prompt A** and **Prompt B**)
- A **Compare** button (also bound to `Ctrl+Return`)
- A colour-graded similarity score (green ≥ 70 %, orange ≥ 40 %, red < 40 %)
- A **Structured diff** tab with colour-coded added/removed/equal lines
- A **Unified diff** tab with standard diff formatting

## Use cases

- **Prompt version control** — diff a prompt against its previous version
  before committing.
- **Regression testing** — assert that a refactored prompt is above a
  similarity threshold to a golden reference.
- **A/B experimentation** — quantify how far apart two prompt variants are
  and correlate prompt distance with output quality.
- **Prompt review workflows** — surface changed lines clearly in code review.

## Contributing

Bug reports and pull requests are welcome at
<https://github.com/vdeshmukh203/promptdiff>.

## Citation

If you use `promptdiff` in research, please cite it using the metadata in
[`CITATION.cff`](CITATION.cff) or the reference below:

```
Deshmukh, V. (2026). promptdiff: A Pure-Python Library for Structured
Comparison of LLM Prompt Strings. https://github.com/vdeshmukh203/promptdiff
```

## License

MIT — see [`LICENSE`](LICENSE).
