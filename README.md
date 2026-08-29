# promptdiff

**Compute and format diffs between prompt strings.**

Pure Python (standard library only for the core). Provides a line-aware diff,
a word-level diff, a unified diff string, and a character-bigram cosine
similarity score — all as pure functions with no global state, no I/O, and
no external API calls.

---

## Statement of need

LLM prompts are iteratively refined; it is difficult to track, review, or
audit changes across prompt versions using general-purpose code-diff tools,
which are optimised for structured source code rather than free-form prose.
`promptdiff` fills this gap with a minimal, dependency-free API that treats
prompts as first-class text artifacts, and a web GUI that gives immediate
visual feedback on how a prompt changed and how similar the two versions are.

---

## Installation

```bash
pip install promptdiff          # core library + CLI
pip install promptdiff[gui]     # core + web GUI (adds Flask)
pip install promptdiff[dev]     # core + GUI + pytest (development)
```

Python 3.9 or later is required.

---

## Quick start

```python
from promptdiff import diff, word_diff, format_unified, similarity

a = "You are a helpful assistant.\nAnswer concisely.\n"
b = "You are a helpful assistant.\nAnswer briefly and clearly.\n"

# Line-level diff
for op, line in diff(a, b):
    print(op, repr(line))
# equal 'You are a helpful assistant.\n'
# remove 'Answer concisely.\n'
# add 'Answer briefly and clearly.\n'

# Word-level diff
for op, token in word_diff(a, b):
    print(op, token)
# equal Answer
# remove concisely.
# add briefly
# add and
# add clearly.

# Unified diff (patch format)
print(format_unified(a, b))

# Cosine similarity of character bigrams
print(similarity(a, b))   # e.g. 0.847
```

---

## API reference

### `diff(a, b)`

Return a line-aware diff between two strings.

| Parameter | Type  | Description         |
|-----------|-------|---------------------|
| `a`       | `str` | Original string     |
| `b`       | `str` | Revised string      |

**Returns** `list[tuple[str, str]]` — each entry is `(op, line)` where `op`
is one of `"equal"`, `"add"`, or `"remove"`. Trailing newlines on each line
are preserved. Replace regions are expanded into consecutive remove / add
entries.

**Raises** `TypeError` if either argument is not a string.

---

### `word_diff(a, b)`

Return a word-level diff between two strings. Splits on whitespace; each
token in the result is an individual word.

| Parameter | Type  | Description         |
|-----------|-------|---------------------|
| `a`       | `str` | Original string     |
| `b`       | `str` | Revised string      |

**Returns** `list[tuple[str, str]]` — each entry is `(op, token)` with the
same op vocabulary as `diff()`.

**Raises** `TypeError` if either argument is not a string.

---

### `format_unified(a, b, fromfile="a", tofile="b")`

Return a unified diff string in standard patch format.

| Parameter  | Type  | Description                                |
|------------|-------|--------------------------------------------|
| `a`        | `str` | Original string                            |
| `b`        | `str` | Revised string                             |
| `fromfile` | `str` | Label for the `---` header (default `"a"`) |
| `tofile`   | `str` | Label for the `+++` header (default `"b"`) |

**Returns** `str` — unified diff, or the empty string when inputs are
identical.

**Raises** `TypeError` if either `a` or `b` is not a string.

---

### `similarity(a, b)`

Return the cosine similarity of character bigrams in two strings.

| Parameter | Type  | Description     |
|-----------|-------|-----------------|
| `a`       | `str` | First string    |
| `b`       | `str` | Second string   |

**Returns** `float` in `[0.0, 1.0]`. Two identical strings return `1.0`;
two strings sharing no bigrams return `0.0`. Two empty strings return `1.0`;
a single empty string compared with any non-empty string returns `0.0`.

**Raises** `TypeError` if either argument is not a string.

---

## Command-line interface

```
promptdiff A B [--unified | --word | --similarity]
```

```
promptdiff a.txt b.txt              # coloured line diff (default)
promptdiff --word a.txt b.txt       # word-level diff
promptdiff --unified a.txt b.txt    # unified patch format
promptdiff --similarity a.txt b.txt # cosine similarity score
echo "hello" | promptdiff - b.txt   # read A from stdin
```

Output is coloured when writing to a terminal (ANSI escape codes). Colour is
suppressed automatically when stdout is redirected.

---

## Web GUI

```bash
pip install promptdiff[gui]
promptdiff-gui                  # opens http://127.0.0.1:5000
promptdiff-gui --port 8080      # custom port
promptdiff-gui --no-browser     # start server without opening a tab
```

The GUI provides:

- Side-by-side text areas for Prompt A and Prompt B
- **Line diff** and **Word diff** views with colour highlighting
- A similarity badge that changes colour (green ≥ 0.75, yellow ≥ 0.4, red < 0.4)
- **Copy unified diff** button (copies to clipboard)
- Keyboard shortcut **Ctrl+Enter** / **Cmd+Enter** to run a line diff

The GUI backend exposes a minimal JSON API (`/api/diff`, `/api/word-diff`,
`/api/unified`, `/api/similarity`) that can also be used programmatically.

---

## Contributing

Bug reports and pull requests are welcome at
<https://github.com/vdeshmukh203/promptdiff/issues>.

To run the test suite:

```bash
pip install promptdiff[dev]
pytest
```

---

## License

MIT — see [LICENSE](LICENSE).
