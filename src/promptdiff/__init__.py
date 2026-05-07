"""promptdiff – Compute and format diffs between prompt strings.

Provides a line-aware diff, a unified diff string, and a character-bigram
cosine-similarity score.  All functions are pure: no global state, no I/O,
and no external API calls.  The implementation uses only the Python standard
library.

Typical usage::

    from promptdiff import diff, format_unified, similarity

    a = "You are a helpful assistant.\\nAnswer concisely.\\n"
    b = "You are a helpful assistant.\\nAnswer in detail.\\n"

    for op, line in diff(a, b):
        print(op, repr(line))

    print(format_unified(a, b))
    print(similarity(a, b))
"""

from __future__ import annotations

import difflib
import math
from collections import Counter

__version__ = "0.2.0"
__all__ = ["diff", "format_unified", "similarity"]


def diff(a: str, b: str) -> list[tuple[str, str]]:
    """Return a line-aware diff between two strings.

    Parameters
    ----------
    a : str
        The original string.
    b : str
        The modified string.

    Returns
    -------
    list[tuple[str, str]]
        A list of ``(op, line)`` tuples where *op* is one of
        ``"equal"``, ``"add"``, or ``"remove"`` and *line* is the
        corresponding text with its trailing newline preserved.  A
        *replace* region is expanded into a sequence of *remove* entries
        followed by *add* entries so callers never encounter a
        ``"replace"`` op.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> diff("hello\\n", "world\\n")
    [('remove', 'hello\\n'), ('add', 'world\\n')]
    >>> diff("a\\nb\\n", "a\\nb\\nc\\n")
    [('equal', 'a\\n'), ('equal', 'b\\n'), ('add', 'c\\n')]
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("diff() expects two str arguments")

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    # autojunk=False prevents the heuristic from treating frequent lines
    # (e.g. short common phrases) as noise — every line in a prompt matters.
    matcher = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)
    out: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for line in a_lines[i1:i2]:
                out.append(("equal", line))
        elif tag == "delete":
            for line in a_lines[i1:i2]:
                out.append(("remove", line))
        elif tag == "insert":
            for line in b_lines[j1:j2]:
                out.append(("add", line))
        else:  # replace
            for line in a_lines[i1:i2]:
                out.append(("remove", line))
            for line in b_lines[j1:j2]:
                out.append(("add", line))
    return out


def format_unified(
    a: str,
    b: str,
    *,
    fromfile: str = "a",
    tofile: str = "b",
) -> str:
    """Return a unified diff string comparing two prompt strings.

    Parameters
    ----------
    a : str
        The original string.
    b : str
        The modified string.
    fromfile : str, optional
        Label for the original-file header line (default ``"a"``).
    tofile : str, optional
        Label for the modified-file header line (default ``"b"``).

    Returns
    -------
    str
        A unified-diff string in the format produced by ``diff -u``.
        Lines that lack a trailing newline have one appended so the
        output is well-formed.  Returns an empty string when both inputs
        are identical.

    Raises
    ------
    TypeError
        If *a*, *b*, *fromfile*, or *tofile* is not a :class:`str`.

    Examples
    --------
    >>> print(format_unified("hello\\n", "world\\n"))
    --- a
    +++ b
    @@ -1 +1 @@
    -hello
    +world
    <BLANKLINE>
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("format_unified() expects two str arguments")
    if not isinstance(fromfile, str) or not isinstance(tofile, str):
        raise TypeError("fromfile and tofile must be str")

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    if a_lines and not a_lines[-1].endswith("\n"):
        a_lines[-1] += "\n"
    if b_lines and not b_lines[-1].endswith("\n"):
        b_lines[-1] += "\n"
    return "".join(
        difflib.unified_diff(a_lines, b_lines, fromfile=fromfile, tofile=tofile)
    )


def _bigrams(s: str) -> Counter[str]:
    """Return a Counter of all overlapping two-character substrings in *s*."""
    if len(s) < 2:
        return Counter()
    return Counter(s[i : i + 2] for i in range(len(s) - 1))


def similarity(a: str, b: str) -> float:
    """Return the cosine similarity of character bigrams for two strings.

    The metric is computed over the multiset of overlapping two-character
    substrings (bigrams) of each input.  It is order-insensitive within a
    string but captures character-level lexical overlap well for short
    natural-language texts such as LLM prompts.

    Parameters
    ----------
    a : str
        First string.
    b : str
        Second string.

    Returns
    -------
    float
        A value in the closed interval ``[0.0, 1.0]``.  Identical strings
        return ``1.0``; strings with no shared bigrams return ``0.0``.
        Two empty strings return ``1.0``; a non-empty string compared to
        an empty string returns ``0.0``.  Single-character strings have no
        bigrams and compare as ``0.0`` unless they are equal.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> similarity("hello world", "hello world")
    1.0
    >>> similarity("aaaa", "bbbb")
    0.0
    >>> 0.0 < similarity("hello world", "hello there") < 1.0
    True
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("similarity() expects two str arguments")

    if a == b:
        return 1.0
    if not a or not b:
        return 0.0

    av = _bigrams(a)
    bv = _bigrams(b)
    if not av or not bv:
        return 0.0

    keys = set(av) | set(bv)
    dot = sum(av[k] * bv[k] for k in keys)
    na = math.sqrt(sum(v * v for v in av.values()))
    nb = math.sqrt(sum(v * v for v in bv.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)
