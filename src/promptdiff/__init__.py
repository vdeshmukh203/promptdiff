"""promptdiff - Compute and format diffs between prompt strings.

This module provides utilities for comparing prompt text. It exposes a
line-aware diff, a word-level diff, a unified diff formatter, and a
character-bigram cosine similarity score. All functions use only the Python
standard library and are pure: no global state, no I/O, and no external
API calls.
"""

from __future__ import annotations

import difflib
import math
import re
from collections import Counter
from typing import List, Tuple

__version__ = "0.2.0"
__all__ = ["diff", "word_diff", "format_unified", "similarity"]


def diff(a: str, b: str) -> List[Tuple[str, str]]:
    """Return a line-aware diff between two strings.

    The result is a list of ``(op, line)`` tuples where *op* is one of
    ``"equal"``, ``"add"``, or ``"remove"`` and *line* is the corresponding
    text, including its trailing newline when one is present.

    Replace regions are expanded into a run of ``"remove"`` entries followed
    by a run of ``"add"`` entries so that callers need not handle a separate
    replace operation.  ``autojunk`` is disabled so that repeated lines in
    short prompts are always diffed correctly.

    Parameters
    ----------
    a:
        The original prompt string.
    b:
        The revised prompt string.

    Returns
    -------
    list of (op, line) tuples

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
        raise TypeError(
            f"diff expects two str arguments, got {type(a).__name__!r}"
            f" and {type(b).__name__!r}"
        )

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)
    out: List[Tuple[str, str]] = []
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


def word_diff(a: str, b: str) -> List[Tuple[str, str]]:
    """Return a word-level diff between two strings.

    Tokenises each string into whitespace-delimited tokens (each token
    carries its trailing whitespace) and produces a list of ``(op, token)``
    tuples using the same ``"equal"``/``"add"``/``"remove"`` vocabulary as
    :func:`diff`.  The sequence of tokens from either string can be
    re-joined to reconstruct the original input.

    Parameters
    ----------
    a:
        The original string.
    b:
        The revised string.

    Returns
    -------
    list of (op, token) tuples

    Raises
    ------
    TypeError
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> ops = word_diff("the cat sat", "the dog sat")
    >>> [(op, tok.strip()) for op, tok in ops]
    [('equal', 'the'), ('remove', 'cat'), ('add', 'dog'), ('equal', 'sat')]
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError(
            f"word_diff expects two str arguments, got {type(a).__name__!r}"
            f" and {type(b).__name__!r}"
        )

    def _tokenise(s: str) -> List[str]:
        return re.findall(r"\S+\s*", s)

    a_toks = _tokenise(a)
    b_toks = _tokenise(b)
    matcher = difflib.SequenceMatcher(None, a_toks, b_toks, autojunk=False)
    out: List[Tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for tok in a_toks[i1:i2]:
                out.append(("equal", tok))
        elif tag == "delete":
            for tok in a_toks[i1:i2]:
                out.append(("remove", tok))
        elif tag == "insert":
            for tok in b_toks[j1:j2]:
                out.append(("add", tok))
        else:  # replace
            for tok in a_toks[i1:i2]:
                out.append(("remove", tok))
            for tok in b_toks[j1:j2]:
                out.append(("add", tok))
    return out


def format_unified(
    a: str, b: str, *, fromfile: str = "a", tofile: str = "b"
) -> str:
    """Return a unified diff string comparing two prompt strings.

    The output follows the standard unified diff format produced by
    :mod:`difflib`.  Lines that do not end with a newline have one appended
    so that the output is well-formed.  When the two inputs are identical
    the result is the empty string.

    Parameters
    ----------
    a:
        The original prompt string.
    b:
        The revised prompt string.
    fromfile:
        Label used in the ``---`` header line (default ``"a"``).
    tofile:
        Label used in the ``+++`` header line (default ``"b"``).

    Returns
    -------
    str
        A unified diff, or the empty string when *a* and *b* are identical.

    Raises
    ------
    TypeError
        If either *a* or *b* is not a :class:`str`.

    Examples
    --------
    >>> out = format_unified("a\\nb\\n", "a\\nc\\n")
    >>> "-b" in out and "+c" in out
    True
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError(
            f"format_unified expects two str arguments, got {type(a).__name__!r}"
            f" and {type(b).__name__!r}"
        )

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    if a_lines and not a_lines[-1].endswith("\n"):
        a_lines[-1] += "\n"
    if b_lines and not b_lines[-1].endswith("\n"):
        b_lines[-1] += "\n"
    return "".join(
        difflib.unified_diff(a_lines, b_lines, fromfile=fromfile, tofile=tofile)
    )


def _bigrams(s: str) -> Counter:
    if len(s) < 2:
        return Counter()
    return Counter(s[i : i + 2] for i in range(len(s) - 1))


def similarity(a: str, b: str) -> float:
    """Return the cosine similarity of character bigrams in two strings.

    The result is a float in the closed interval ``[0.0, 1.0]``.  Two
    identical strings return ``1.0``; two strings with no shared bigrams
    return ``0.0``.

    Special cases:

    * Two empty strings return ``1.0`` (they are identical).
    * One empty string compared with any non-empty string returns ``0.0``.
    * Strings shorter than two characters have no bigrams and are treated
      as zero-magnitude vectors unless they are identical.

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
        If either argument is not a :class:`str`.

    Examples
    --------
    >>> similarity("hello", "hello")
    1.0
    >>> similarity("hello", "world")  # doctest: +ELLIPSIS
    0.2...
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError(
            f"similarity expects two str arguments, got {type(a).__name__!r}"
            f" and {type(b).__name__!r}"
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
