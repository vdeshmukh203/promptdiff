"""promptdiff - Compute and format diffs between prompt strings.

This module provides utilities for comparing LLM prompt text. It exposes a
line-aware structured diff, a unified diff string, and a character-bigram
cosine similarity score. All functions use only the Python standard library,
are free of global state, perform no I/O, and make no external API calls.
"""

from __future__ import annotations

import difflib
import math
from collections import Counter
from typing import List, NamedTuple

__version__ = "0.1.0"
__version_info__ = (0, 1, 0)
__all__ = ["diff", "format_unified", "similarity", "DiffLine"]


class DiffLine(NamedTuple):
    """A single entry produced by :func:`diff`.

    Attributes
    ----------
    op : str
        The operation tag: ``"equal"``, ``"add"``, or ``"remove"``.
    line : str
        The text of the line with its original trailing newline preserved.
    """

    op: str
    line: str


def diff(a: str, b: str) -> List[DiffLine]:
    """Return a line-aware diff between two prompt strings.

    Parameters
    ----------
    a : str
        The original (left-hand) prompt string.
    b : str
        The revised (right-hand) prompt string.

    Returns
    -------
    list[DiffLine]
        A list of :class:`DiffLine` named tuples.  Each entry carries an
        *op* field (``"equal"``, ``"add"``, or ``"remove"``) and a *line*
        field containing the text with its trailing newline preserved.  A
        replace region is expanded into a run of ``"remove"`` entries
        followed by a run of ``"add"`` entries so callers never encounter a
        raw *replace* tag.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> result = diff("hello\\n", "world\\n")
    >>> [(op, line.rstrip()) for op, line in result]
    [('remove', 'hello'), ('add', 'world')]
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("diff expects two strings")

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    # autojunk=False prevents SequenceMatcher from treating frequently
    # repeated lines as noise, which gives accurate diffs for short prompts.
    matcher = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)
    out: List[DiffLine] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            out.extend(DiffLine("equal", line) for line in a_lines[i1:i2])
        elif tag == "delete":
            out.extend(DiffLine("remove", line) for line in a_lines[i1:i2])
        elif tag == "insert":
            out.extend(DiffLine("add", line) for line in b_lines[j1:j2])
        elif tag == "replace":
            out.extend(DiffLine("remove", line) for line in a_lines[i1:i2])
            out.extend(DiffLine("add", line) for line in b_lines[j1:j2])
    return out


def format_unified(a: str, b: str) -> str:
    """Return a unified diff string comparing two prompt strings.

    Parameters
    ----------
    a : str
        The original (left-hand) prompt string.
    b : str
        The revised (right-hand) prompt string.

    Returns
    -------
    str
        A unified diff string in the format produced by
        :func:`difflib.unified_diff` with header labels ``a`` and ``b``.
        Lines that do not end with a newline character have one appended so
        that the output is well-formed.  When the two inputs are identical,
        the result is the empty string.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> out = format_unified("hello\\n", "world\\n")
    >>> "-hello" in out and "+world" in out
    True
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("format_unified expects two strings")

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    if a_lines and not a_lines[-1].endswith("\n"):
        a_lines[-1] += "\n"
    if b_lines and not b_lines[-1].endswith("\n"):
        b_lines[-1] += "\n"
    return "".join(difflib.unified_diff(a_lines, b_lines, fromfile="a", tofile="b"))


def _bigrams(s: str) -> Counter:
    """Return a Counter of character bigrams in *s*."""
    if len(s) < 2:
        return Counter()
    return Counter(s[i : i + 2] for i in range(len(s) - 1))


def similarity(a: str, b: str) -> float:
    """Return the cosine similarity of character bigrams in two strings.

    Parameters
    ----------
    a : str
        The first string.
    b : str
        The second string.

    Returns
    -------
    float
        A value in the closed interval ``[0.0, 1.0]``.  Two identical
        strings return ``1.0``; two strings with no shared bigrams return
        ``0.0``.  Empty strings are a special case: two empty strings are
        considered identical (``1.0``), while one empty string compared to
        any non-empty string returns ``0.0``.  Strings of length one have no
        bigrams, so unless they compare equal they also return ``0.0``.

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
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("similarity expects two strings")

    if a == b:
        return 1.0
    if not a or not b:
        return 0.0

    av = _bigrams(a)
    bv = _bigrams(b)
    if not av or not bv:
        return 0.0

    # Only iterate over shared keys; missing Counter keys are zero.
    dot = sum(av[k] * bv[k] for k in av.keys() & bv.keys())
    na = math.sqrt(sum(v * v for v in av.values()))
    nb = math.sqrt(sum(v * v for v in bv.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return min(1.0, max(0.0, dot / (na * nb)))
