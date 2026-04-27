"""promptdiff - Compute and format diffs between prompt strings.

This module provides utilities for comparing prompt text. It exposes a
line-aware diff, a unified diff string, and a character-bigram cosine
similarity score. All functions use only the Python standard library and
are pure: no global state, no I/O, and no external API calls.

Typical usage::

    from promptdiff import diff, format_unified, similarity

    a = "You are a helpful assistant.\\nAnswer concisely."
    b = "You are a helpful assistant.\\nAnswer in detail."

    for op, line in diff(a, b):
        prefix = {"equal": " ", "add": "+", "remove": "-"}[op]
        print(prefix, line, end="")

    print(format_unified(a, b))
    print(similarity(a, b))   # e.g. 0.894
"""

from __future__ import annotations

import difflib
import math
from collections import Counter

__version__ = "0.1.0"
__author__ = "Vaibhav Deshmukh"
__all__ = ["diff", "format_unified", "similarity"]

# Operation labels returned by diff().
_OP_EQUAL = "equal"
_OP_ADD = "add"
_OP_REMOVE = "remove"


def diff(a: str, b: str) -> list[tuple[str, str]]:
    """Return a line-aware diff between two strings.

    Parameters
    ----------
    a:
        The original (before) string.
    b:
        The revised (after) string.

    Returns
    -------
    list[tuple[str, str]]
        A list of ``(operation, line)`` pairs.  *operation* is one of
        ``"equal"``, ``"add"``, or ``"remove"``; *line* retains its
        trailing newline so that ``"".join(line for _, line in result)``
        reconstructs the relevant string without losing structure.
        Replace regions are expanded into a contiguous block of
        ``"remove"`` entries followed by ``"add"`` entries, so callers
        never encounter a ``"replace"`` opcode.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> diff("hello\\nworld\\n", "hello\\nthere\\n")
    [('equal', 'hello\\n'), ('remove', 'world\\n'), ('add', 'there\\n')]
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("diff expects two str arguments")

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)
    out: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for line in a_lines[i1:i2]:
                out.append((_OP_EQUAL, line))
        elif tag == "delete":
            for line in a_lines[i1:i2]:
                out.append((_OP_REMOVE, line))
        elif tag == "insert":
            for line in b_lines[j1:j2]:
                out.append((_OP_ADD, line))
        elif tag == "replace":
            for line in a_lines[i1:i2]:
                out.append((_OP_REMOVE, line))
            for line in b_lines[j1:j2]:
                out.append((_OP_ADD, line))
    return out


def format_unified(
    a: str,
    b: str,
    fromfile: str = "a",
    tofile: str = "b",
    context: int = 3,
) -> str:
    """Return a unified diff string comparing two prompt strings.

    Parameters
    ----------
    a:
        The original (before) string.
    b:
        The revised (after) string.
    fromfile:
        Label used in the ``---`` header line (default ``"a"``).
    tofile:
        Label used in the ``+++`` header line (default ``"b"``).
    context:
        Number of unchanged context lines surrounding each hunk
        (default ``3``, matching the POSIX ``diff -u`` convention).

    Returns
    -------
    str
        A unified-diff string.  When *a* and *b* are identical the
        result is the empty string.  Lines that do not end with a
        newline have one appended internally so the output is
        well-formed; this does not modify the caller's strings.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> out = format_unified("hello\\n", "world\\n")
    >>> "--- a" in out and "+++ b" in out
    True
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("format_unified expects two str arguments")
    if not isinstance(fromfile, str) or not isinstance(tofile, str):
        raise TypeError("fromfile and tofile must be str")
    if not isinstance(context, int) or context < 0:
        raise ValueError("context must be a non-negative integer")

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    # Normalise missing trailing newlines so unified diff output is valid.
    if a_lines and not a_lines[-1].endswith("\n"):
        a_lines[-1] += "\n"
    if b_lines and not b_lines[-1].endswith("\n"):
        b_lines[-1] += "\n"
    return "".join(
        difflib.unified_diff(
            a_lines, b_lines, fromfile=fromfile, tofile=tofile, n=context
        )
    )


def _bigrams(s: str) -> Counter[str]:
    """Return a frequency counter of overlapping character bigrams in *s*.

    Returns an empty :class:`~collections.Counter` for strings shorter
    than two characters.  This function is part of the public API and
    may be used directly when callers need raw bigram vectors.
    """
    if len(s) < 2:
        return Counter()
    return Counter(s[i : i + 2] for i in range(len(s) - 1))


def similarity(a: str, b: str) -> float:
    """Return the cosine similarity of character bigrams in two strings.

    The score is computed as

    .. math::

        \\text{sim}(a, b) = \\frac{\\sum_{g} f_a(g)\\, f_b(g)}
                                  {\\|f_a\\|_2 \\cdot \\|f_b\\|_2}

    where :math:`f_x(g)` is the count of bigram *g* in string *x*.

    Parameters
    ----------
    a:
        First string.
    b:
        Second string.

    Returns
    -------
    float
        A value in the closed interval ``[0.0, 1.0]``.  Identical
        strings return ``1.0``; strings with no shared bigrams return
        ``0.0``.  Two empty strings return ``1.0``; one empty string
        compared with any non-empty string returns ``0.0``.  Single-
        character strings contain no bigrams and therefore behave like
        the empty case unless they are equal.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

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
        raise TypeError("similarity expects two str arguments")

    if a == b:
        return 1.0
    if not a or not b:
        return 0.0

    av = _bigrams(a)
    bv = _bigrams(b)
    if not av or not bv:
        return 0.0

    dot = sum(av[k] * bv[k] for k in av.keys() & bv.keys())
    na = math.sqrt(sum(v * v for v in av.values()))
    nb = math.sqrt(sum(v * v for v in bv.values()))
    if na == 0.0 or nb == 0.0:  # guard: unreachable after _bigrams checks
        return 0.0
    return dot / (na * nb)
