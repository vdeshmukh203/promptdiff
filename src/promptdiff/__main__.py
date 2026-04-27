"""Command-line interface for promptdiff.

Usage examples::

    # Compare two inline strings
    python -m promptdiff "old prompt text" "new prompt text"

    # Compare two files (unified diff format)
    python -m promptdiff --files --format unified before.txt after.txt

    # Suppress the similarity score
    python -m promptdiff --no-score "prompt A" "prompt B"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from promptdiff import __version__, diff, format_unified, similarity

_PREFIX = {"equal": "  ", "add": "+ ", "remove": "- "}


def _read(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        sys.exit(f"promptdiff: cannot read '{path}': {exc.strerror}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="promptdiff",
        description="Compare two prompt strings or text files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  promptdiff 'old prompt' 'new prompt'\n"
            "  promptdiff --files before.txt after.txt\n"
            "  promptdiff --files --format unified v1.txt v2.txt"
        ),
    )
    parser.add_argument("a", help="first string, or path when --files is set")
    parser.add_argument("b", help="second string, or path when --files is set")
    parser.add_argument(
        "--files",
        action="store_true",
        help="treat A and B as file paths (UTF-8 encoded)",
    )
    parser.add_argument(
        "--format",
        choices=["inline", "unified"],
        default="inline",
        metavar="FORMAT",
        help="output format: 'inline' (default) or 'unified'",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=3,
        metavar="N",
        help="context lines for unified format (default: 3)",
    )
    parser.add_argument(
        "--no-score",
        action="store_true",
        help="suppress the similarity score line",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    a = _read(args.a) if args.files else args.a
    b = _read(args.b) if args.files else args.b

    if args.format == "unified":
        out = format_unified(a, b, context=args.context)
        if out:
            print(out, end="")
    else:
        for op, line in diff(a, b):
            print(_PREFIX[op] + line, end="")

    if not args.no_score:
        score = similarity(a, b)
        print(f"\nSimilarity: {score:.4f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
