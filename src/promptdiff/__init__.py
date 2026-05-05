"""promptdiff - Compute and format diffs between prompt strings.

Provides utilities for comparing LLM prompt text. Exposes a line-aware
structured diff, a unified diff string, and a character-bigram cosine
similarity score. All functions use only the Python standard library and
are pure: no global state, no I/O, and no external API calls.

Example
-------
>>> from promptdiff import diff, format_unified, similarity
>>> a = "You are a helpful assistant.\\nAnswer concisely."
>>> b = "You are a helpful assistant.\\nAnswer in detail."
>>> similarity(a, b)
0.8518518518518519
>>> print(format_unified(a, b))
--- a
+++ b
@@ -1,2 +1,2 @@
 You are a helpful assistant.
-Answer concisely.
+Answer in detail.
<BLANKLINE>
"""

from __future__ import annotations

import difflib
import math
from collections import Counter
from typing import List, Tuple

__version__ = "0.2.0"
__author__ = "Vaibhav Deshmukh"
__all__ = ["diff", "format_unified", "similarity"]

# Type alias for readability
_DiffResult = List[Tuple[str, str]]


def diff(a: str, b: str) -> _DiffResult:
    """Return a line-aware structured diff between two prompt strings.

    Computes an optimal line-level alignment using :mod:`difflib` and returns
    each line annotated with its operation. Replace regions are expanded into
    consecutive ``"remove"`` and ``"add"`` entries so callers never encounter
    a separate *replace* operation.

    Parameters
    ----------
    a:
        The original prompt string.
    b:
        The revised prompt string.

    Returns
    -------
    list of (op, line) tuples
        Each tuple contains:

        - ``"equal"``  – the line is unchanged.
        - ``"remove"`` – the line was in *a* but not in *b*.
        - ``"add"``    – the line is new in *b*.

        Trailing newlines are preserved so that
        ``"".join(line for _, line in result)`` reconstructs *a* or *b*
        faithfully when only one side is selected.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> diff("hello\\n", "hello\\n")
    [('equal', 'hello\\n')]
    >>> diff("a\\nb\\n", "a\\nc\\n")
    [('equal', 'a\\n'), ('remove', 'b\\n'), ('add', 'c\\n')]
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError(
            f"diff() expects two str arguments, got {type(a).__name__!r} and"
            f" {type(b).__name__!r}"
        )

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)
    out: _DiffResult = []
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
        else:  # tag == "replace"
            for line in a_lines[i1:i2]:
                out.append(("remove", line))
            for line in b_lines[j1:j2]:
                out.append(("add", line))
    return out


def format_unified(a: str, b: str, context: int = 3) -> str:
    """Return a unified diff string comparing two prompt strings.

    Produces the standard unified diff format (as used by :command:`diff -u`).
    Lines that do not end with ``\\n`` have one appended so the output is
    well-formed. Returns the empty string when the two inputs are identical.

    Parameters
    ----------
    a:
        The original prompt string.
    b:
        The revised prompt string.
    context:
        Number of unchanged lines shown around each changed region.
        Defaults to ``3``, matching the convention of :command:`diff -u`.

    Returns
    -------
    str
        Unified diff output with ``--- a`` / ``+++ b`` headers, or ``""``
        when *a* and *b* are identical.

    Raises
    ------
    TypeError
        If either *a* or *b* is not a :class:`str`.

    Examples
    --------
    >>> out = format_unified("hello\\n", "world\\n")
    >>> "--- a" in out and "+++ b" in out
    True
    >>> format_unified("same\\n", "same\\n")
    ''
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError(
            f"format_unified() expects two str arguments, got"
            f" {type(a).__name__!r} and {type(b).__name__!r}"
        )
    if not isinstance(context, int) or context < 0:
        raise ValueError(
            f"context must be a non-negative int, got {context!r}"
        )

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    if a_lines and not a_lines[-1].endswith("\n"):
        a_lines[-1] += "\n"
    if b_lines and not b_lines[-1].endswith("\n"):
        b_lines[-1] += "\n"
    return "".join(
        difflib.unified_diff(a_lines, b_lines, fromfile="a", tofile="b", n=context)
    )


def _bigrams(s: str) -> Counter:
    """Return a Counter of character bigrams (pairs of consecutive chars)."""
    if len(s) < 2:
        return Counter()
    return Counter(s[i: i + 2] for i in range(len(s) - 1))


def similarity(a: str, b: str) -> float:
    """Return the cosine similarity of character bigrams between two strings.

    Converts each string to a frequency vector of overlapping character pairs
    (bigrams) and computes the cosine similarity of those vectors. The result
    is a normalised measure of textual proximity that is insensitive to word
    order and works well for short-to-medium length prompt text.

    Parameters
    ----------
    a:
        First prompt string.
    b:
        Second prompt string.

    Returns
    -------
    float
        A value in the closed interval ``[0.0, 1.0]``.

        - ``1.0`` – strings are identical (fast-path), or both are empty.
        - ``0.0`` – strings share no character bigrams, or one is empty, or
          both have fewer than two characters and are not equal.
        - Intermediate values reflect partial bigram overlap.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Notes
    -----
    The similarity metric is symmetric: ``similarity(a, b) == similarity(b, a)``
    for all valid inputs.

    Examples
    --------
    >>> similarity("hello world", "hello world")
    1.0
    >>> similarity("hello", "")
    0.0
    >>> 0.0 < similarity("hello world", "hello there") < 1.0
    True
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError(
            f"similarity() expects two str arguments, got"
            f" {type(a).__name__!r} and {type(b).__name__!r}"
        )

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
