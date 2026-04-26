# promptdiff

Compute and format diffs between prompt strings.

Pure Python, standard library only. Provides a line-aware diff, a
unified diff string, and a character-bigram cosine similarity score.

## Install

```bash
pip install promptdiff
```

## Usage

```python
from promptdiff import diff, format_unified, similarity

a = "hello\nworld\n"
b = "hello\nthere\n"

print(format_unified(a, b))
print(similarity(a, b))
```

## License

MIT - see LICENSE.
