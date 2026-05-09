"""Command-line entry point for promptdiff.

Run without arguments (or with --gui) to launch the graphical interface::

    python -m promptdiff
    python -m promptdiff --gui

Compare two inline strings::

    python -m promptdiff "hello world" "hello there"

Compare two files (prefix the path with ``@``)::

    python -m promptdiff @prompt_v1.txt @prompt_v2.txt --format unified
"""

from __future__ import annotations

import argparse
import sys


def _load(s: str) -> str:
    """Return file contents when *s* starts with ``@``, otherwise return *s*."""
    if s.startswith("@"):
        path = s[1:]
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    return s


def _cli() -> None:
    parser = argparse.ArgumentParser(
        prog="promptdiff",
        description=(
            "Compare two prompt strings and print a structured or unified diff.\n"
            "Prefix a path with '@' to read from a file."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="launch the graphical interface (default when no arguments are given)",
    )
    parser.add_argument(
        "a",
        nargs="?",
        metavar="A",
        help="first prompt string, or @path to read from a file",
    )
    parser.add_argument(
        "b",
        nargs="?",
        metavar="B",
        help="second prompt string, or @path to read from a file",
    )
    parser.add_argument(
        "--format",
        choices=["structured", "unified"],
        default="structured",
        help="output format (default: structured)",
    )
    parser.add_argument(
        "--no-similarity",
        action="store_true",
        help="suppress the similarity score printed to stderr",
    )

    args = parser.parse_args()

    # Launch GUI when --gui is given or when no positional arguments are provided.
    if args.gui or (args.a is None and args.b is None):
        from promptdiff.gui import run
        run()
        return

    if args.a is None or args.b is None:
        parser.error("both A and B must be provided when not using --gui")

    a = _load(args.a)
    b = _load(args.b)

    from promptdiff import diff, format_unified, similarity

    if args.format == "unified":
        output = format_unified(a, b)
        print(output, end="")
    else:
        for op, line in diff(a, b):
            prefix = "  " if op == "equal" else ("+ " if op == "add" else "- ")
            print(prefix + line, end="")
            if not line.endswith("\n"):
                print()

    if not args.no_similarity:
        sim = similarity(a, b)
        print(f"\nSimilarity: {sim:.4f}", file=sys.stderr)


if __name__ == "__main__":
    _cli()
