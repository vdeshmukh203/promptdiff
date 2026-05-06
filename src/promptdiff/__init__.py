"""promptdiff - Compute and format diffs between prompt strings.

This module provides utilities for comparing prompt text. It exposes a
line-aware diff, a unified diff string, a character-bigram cosine
similarity score, and an aggregate summary. All functions use only the
Python standard library and are pure: no global state, no I/O, and no
external API calls.
"""

from __future__ import annotations

import difflib
import math
from collections import Counter

__version__ = "0.2.0"
__all__ = ["diff", "format_unified", "similarity", "summary"]


def diff(a: str, b: str) -> list[tuple[str, str]]:
    """Return a line-aware diff between two strings.

    The result is a list of two-tuples ``(op, line)`` where *op* is one of
    ``"equal"``, ``"add"``, or ``"remove"`` and *line* is the corresponding
    text with its trailing newline preserved.  A replace region is expanded
    into remove entries followed by add entries so callers do not need to
    handle a separate replace operation.

    ``autojunk=False`` is passed to :class:`~difflib.SequenceMatcher` to
    prevent the heuristic from suppressing tokens that appear frequently, which
    matters for prompt strings that often contain repetitive structure (e.g.
    few-shot examples).

    Parameters
    ----------
    a:
        The original string.
    b:
        The revised string.

    Returns
    -------
    list[tuple[str, str]]
        Sequence of ``(op, line)`` pairs.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> ops = diff("hello\\nworld\\n", "hello\\nthere\\n")
    >>> [(op, line.strip()) for op, line in ops]
    [('equal', 'hello'), ('remove', 'world'), ('add', 'there')]
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("diff expects two strings")

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
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
        elif tag == "replace":
            for line in a_lines[i1:i2]:
                out.append(("remove", line))
            for line in b_lines[j1:j2]:
                out.append(("add", line))
    return out


def format_unified(a: str, b: str, *, context: int = 3) -> str:
    """Return a unified diff string comparing two prompt strings.

    The output follows the standard unified diff format produced by
    :mod:`difflib` with header labels ``a`` and ``b``.  Lines in the input
    that do not end with a newline have one appended so the output is
    well-formed.  When the two inputs are identical the result is the empty
    string.

    Parameters
    ----------
    a:
        The original string.
    b:
        The revised string.
    context:
        Number of surrounding context lines included in each hunk (default 3).

    Returns
    -------
    str
        Unified diff text, or the empty string when *a* and *b* are equal.

    Raises
    ------
    TypeError
        If either of the first two arguments is not a :class:`str`.

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
    return "".join(
        difflib.unified_diff(a_lines, b_lines, fromfile="a", tofile="b", n=context)
    )


def _bigrams(s: str) -> Counter[str]:
    if len(s) < 2:
        return Counter()
    return Counter(s[i : i + 2] for i in range(len(s) - 1))


def similarity(a: str, b: str) -> float:
    """Return the cosine similarity of character bigrams in two strings.

    The result is a :class:`float` in the closed interval ``[0.0, 1.0]``.
    Two identical strings produce ``1.0``; two strings sharing no bigrams
    produce ``0.0``.  Empty inputs are handled as a special case: two empty
    strings return ``1.0``, while an empty string compared with any non-empty
    string returns ``0.0``.  A string of length one has no bigrams and behaves
    like the empty case unless the two strings are identical.

    Parameters
    ----------
    a:
        The first string.
    b:
        The second string.

    Returns
    -------
    float
        Cosine similarity in ``[0.0, 1.0]``.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> similarity("hello world", "hello world")
    1.0
    >>> similarity("hello world", "goodbye world") > 0
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


def summary(a: str, b: str) -> dict[str, object]:
    """Return an aggregate comparison summary for two prompt strings.

    Combines line-level diff counts with the character-bigram cosine
    similarity into a single :class:`dict` so callers can inspect all
    metrics in one call.

    Parameters
    ----------
    a:
        The original string.
    b:
        The revised string.

    Returns
    -------
    dict
        A mapping with keys:

        ``similarity`` (:class:`float`)
            Cosine similarity in ``[0.0, 1.0]``.
        ``added`` (:class:`int`)
            Number of lines present in *b* but not in *a*.
        ``removed`` (:class:`int`)
            Number of lines present in *a* but not in *b*.
        ``equal`` (:class:`int`)
            Number of unchanged lines.

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> s = summary("a\\nb\\n", "a\\nc\\n")
    >>> s["added"], s["removed"], s["equal"]
    (1, 1, 1)
    """
    ops = diff(a, b)
    counts: dict[str, int] = {"equal": 0, "add": 0, "remove": 0}
    for op, _ in ops:
        counts[op] += 1
    return {
        "similarity": similarity(a, b),
        "added": counts["add"],
        "removed": counts["remove"],
        "equal": counts["equal"],
    }
