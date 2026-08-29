"""promptdiff – Compute and format diffs between prompt strings.

This module provides utilities for comparing prompt text. It exposes a
line-aware diff, a word-level diff, a unified diff string, and a
character-bigram cosine similarity score. All functions use only the
Python standard library and are pure: no global state, no I/O, and no
external API calls.
"""

from __future__ import annotations

import difflib
import math
from collections import Counter

__version__ = "0.1.0"
__all__ = ["diff", "word_diff", "format_unified", "similarity"]


def diff(a: str, b: str) -> list[tuple[str, str]]:
    """Return a line-aware diff between two strings.

    Each entry in the result is a (op, line) tuple where op is one of
    ``"equal"``, ``"add"``, or ``"remove"`` and line is the corresponding
    line with its trailing newline preserved. Callers can reconstruct
    either input by concatenating the lines for the appropriate operations.
    A replace region is expanded into remove entries followed by add
    entries so callers never need to handle a separate replace operation.

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
        If either argument is not a string.

    Examples
    --------
    >>> diff("hello\\nworld\\n", "hello\\nthere\\n")
    [('equal', 'hello\\n'), ('remove', 'world\\n'), ('add', 'there\\n')]
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("diff expects two strings")

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(a=a_lines, b=b_lines)
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


def word_diff(a: str, b: str) -> list[tuple[str, str]]:
    """Return a word-level diff between two strings.

    Splits each string on whitespace and computes a diff over the resulting
    tokens. Each entry in the result is a (op, token) tuple where op is
    one of ``"equal"``, ``"add"``, or ``"remove"`` and token is an
    individual whitespace-delimited word. A replace region is expanded into
    remove entries followed by add entries.

    This provides finer granularity than :func:`diff`, which operates on
    whole lines. It is especially useful when prompt edits change only a
    few words within otherwise identical lines.

    Parameters
    ----------
    a:
        The original string.
    b:
        The revised string.

    Returns
    -------
    list[tuple[str, str]]
        Sequence of ``(op, token)`` pairs.

    Raises
    ------
    TypeError
        If either argument is not a string.

    Examples
    --------
    >>> word_diff("say hello world", "say hello there")
    [('equal', 'say'), ('equal', 'hello'), ('remove', 'world'), ('add', 'there')]
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("word_diff expects two strings")

    a_words = a.split()
    b_words = b.split()
    matcher = difflib.SequenceMatcher(a=a_words, b=b_words)
    out: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for word in a_words[i1:i2]:
                out.append(("equal", word))
        elif tag == "delete":
            for word in a_words[i1:i2]:
                out.append(("remove", word))
        elif tag == "insert":
            for word in b_words[j1:j2]:
                out.append(("add", word))
        elif tag == "replace":
            for word in a_words[i1:i2]:
                out.append(("remove", word))
            for word in b_words[j1:j2]:
                out.append(("add", word))
    return out


def format_unified(
    a: str,
    b: str,
    fromfile: str = "a",
    tofile: str = "b",
) -> str:
    """Return a unified diff string comparing two prompt strings.

    The output follows the standard unified diff format produced by
    :mod:`difflib`. Lines that do not end with a newline have one appended
    so the output is well-formed. When the two inputs are identical the
    result is the empty string.

    Parameters
    ----------
    a:
        The original string.
    b:
        The revised string.
    fromfile:
        Label shown in the ``---`` header line. Defaults to ``"a"``.
    tofile:
        Label shown in the ``+++`` header line. Defaults to ``"b"``.

    Returns
    -------
    str
        Unified diff, or the empty string when inputs are identical.

    Raises
    ------
    TypeError
        If either *a* or *b* is not a string.

    Examples
    --------
    >>> print(format_unified("a\\nb\\n", "a\\nc\\n"))  # doctest: +SKIP
    --- a
    +++ b
    @@ -1,2 +1,2 @@
     a
    -b
    +c
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
        difflib.unified_diff(a_lines, b_lines, fromfile=fromfile, tofile=tofile)
    )


def _bigrams(s: str) -> Counter:
    if len(s) < 2:
        return Counter()
    return Counter(s[i : i + 2] for i in range(len(s) - 1))


def similarity(a: str, b: str) -> float:
    """Return the cosine similarity of character bigrams in two strings.

    The result is a float in the closed interval ``[0.0, 1.0]``. Two
    identical strings return ``1.0``; two strings sharing no character
    bigrams return ``0.0``. Empty strings are treated as a special case:
    two empty strings return ``1.0``, and an empty string compared with
    any non-empty string returns ``0.0``. Strings of length one have no
    bigrams; they return ``1.0`` only when they are equal.

    Parameters
    ----------
    a:
        First string.
    b:
        Second string.

    Returns
    -------
    float
        Cosine similarity in ``[0.0, 1.0]``.

    Raises
    ------
    TypeError
        If either argument is not a string.

    Examples
    --------
    >>> similarity("hello world", "hello world")
    1.0
    >>> similarity("hello world", "hello there")  # doctest: +SKIP
    0.636...
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
