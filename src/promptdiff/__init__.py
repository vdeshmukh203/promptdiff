"""promptdiff - Compute and format diffs between prompt strings.

This module provides utilities for comparing prompt text. It exposes a
line-aware diff, a unified diff string, and a character-bigram cosine
similarity score. All functions use only the Python standard library and
are pure: no global state, no I/O, and no external API calls.
"""

from __future__ import annotations

import difflib
import math
from collections import Counter
from typing import List, Literal, Tuple

__version__ = "0.2.0"
__all__ = ["diff", "format_unified", "similarity"]

# Type for the operation tag in diff output tuples.
Op = Literal["equal", "add", "remove"]


def diff(a: str, b: str) -> List[Tuple[Op, str]]:
    """Return a line-aware diff between two strings.

    The result is a list of two-tuples ``(op, line)`` where *op* is one of
    ``"equal"``, ``"add"``, or ``"remove"`` and *line* is the corresponding
    text line.  Trailing newlines are preserved on each line so callers can
    re-concatenate without losing structure.  A replace region is expanded
    into a sequence of ``"remove"`` entries followed by ``"add"`` entries,
    so the caller does not need to handle a separate replace op.

    Parameters
    ----------
    a : str
        The original prompt string.
    b : str
        The revised prompt string.

    Returns
    -------
    list of (str, str)
        Sequence of ``(op, line)`` pairs describing the edit script.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> ops = diff("hello\\nworld\\n", "hello\\nthere\\n")
    >>> [op for op, _ in ops]
    ['equal', 'remove', 'add']
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("diff expects two strings")

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(a=a_lines, b=b_lines)
    out: List[Tuple[Op, str]] = []
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
        elif tag == "replace":
            for line in a_lines[i1:i2]:
                out.append(("remove", line))
            for line in b_lines[j1:j2]:
                out.append(("add", line))
    return out


def format_unified(a: str, b: str) -> str:
    """Return a unified diff string comparing two prompt strings.

    The output follows the standard unified diff format produced by
    :func:`difflib.unified_diff` with header labels ``a`` and ``b``.
    Lines that do not end with a newline have one appended so the output
    is well-formed.  When the two inputs are identical, the result is the
    empty string.

    Parameters
    ----------
    a : str
        The original prompt string.
    b : str
        The revised prompt string.

    Returns
    -------
    str
        A unified diff string, or an empty string when *a* and *b* are equal.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> out = format_unified("hello\\nworld\\n", "hello\\nthere\\n")
    >>> "-world" in out and "+there" in out
    True
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("format_unified expects two strings")

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    if a_lines and not a_lines[-1].endswith("\n"):
        a_lines[-1] = a_lines[-1] + "\n"
    if b_lines and not b_lines[-1].endswith("\n"):
        b_lines[-1] = b_lines[-1] + "\n"
    return "".join(difflib.unified_diff(a_lines, b_lines, fromfile="a", tofile="b"))


def _bigrams(s: str) -> Counter:
    if len(s) < 2:
        return Counter()
    return Counter(s[i : i + 2] for i in range(len(s) - 1))


def similarity(a: str, b: str) -> float:
    """Return the cosine similarity of character bigrams in two strings.

    The result is a float in the closed interval ``[0.0, 1.0]``.  Two
    identical strings produce ``1.0`` and two strings with no shared bigrams
    produce ``0.0``.  Empty inputs are handled as a special case: two empty
    strings return ``1.0``, while one empty and one non-empty string return
    ``0.0``.  Single-character strings share no bigrams with anything and
    therefore return ``0.0`` unless they match exactly.

    The score is computed as the cosine similarity of character-bigram
    frequency vectors:

    .. math::

        \\text{similarity}(a, b) =
        \\frac{\\mathbf{v}_a \\cdot \\mathbf{v}_b}
             {\\|\\mathbf{v}_a\\| \\, \\|\\mathbf{v}_b\\|}

    where :math:`\\mathbf{v}_s[k]` counts occurrences of bigram *k* in *s*.

    Parameters
    ----------
    a : str
        The first prompt string.
    b : str
        The second prompt string.

    Returns
    -------
    float
        Cosine similarity score in ``[0.0, 1.0]``.

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
        raise TypeError("similarity expects two strings")

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
