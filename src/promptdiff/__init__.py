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
from typing import List, Tuple

__version__ = "0.1.0"
__all__ = ["diff", "format_unified", "similarity"]


def diff(a: str, b: str) -> list:
    """Return a line-aware diff between two strings.

    The result is a list of two-tuples of the form (op, line) where op is
    one of equal, add, or remove and line is the corresponding line.
    Trailing newlines are preserved on each line so that callers can
    re-concatenate the lines without losing structure. A replace region
    is expanded into a sequence of remove entries followed by add entries
    so the caller does not need to handle a separate replace op.
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("diff expects two strings")

    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(a=a_lines, b=b_lines)
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
        elif tag == "replace":
            for line in a_lines[i1:i2]:
                out.append(("remove", line))
            for line in b_lines[j1:j2]:
                out.append(("add", line))
    return out


def format_unified(a: str, b: str) -> str:
    """Return a unified diff string comparing two prompt strings.

    The output follows the standard unified diff format produced by
    difflib with header labels of a and b. Lines in the input that do not
    end with a newline have one appended so the output is well-formed.
    When the two inputs are identical, the result is the empty string.
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

    The result is a float in the closed interval from 0.0 to 1.0. Two
    identical strings produce 1.0 and two strings with no shared bigrams
    produce 0.0. Empty inputs are handled as a special case: two empty
    strings are considered identical and return 1.0, while a single empty
    string compared to any non-empty string returns 0.0. Strings of length
    one share no bigrams with anything and therefore behave like the empty
    case unless they match exactly.
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
