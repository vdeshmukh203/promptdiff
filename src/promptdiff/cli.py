"""Command-line interface for promptdiff."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from promptdiff import diff, format_unified, similarity, word_diff

_RED = "\033[31m"
_GREEN = "\033[32m"
_RESET = "\033[0m"


def _colorize(text: str, color: str) -> str:
    return f"{color}{text}{_RESET}" if sys.stdout.isatty() else text


def _print_line_diff(result: list[tuple[str, str]]) -> None:
    for op, line in result:
        text = line.rstrip("\n")
        if op == "remove":
            print(_colorize(f"- {text}", _RED))
        elif op == "add":
            print(_colorize(f"+ {text}", _GREEN))
        else:
            print(f"  {text}")


def _print_word_diff(result: list[tuple[str, str]]) -> None:
    parts: list[str] = []
    for op, token in result:
        if op == "remove":
            parts.append(_colorize(token, _RED))
        elif op == "add":
            parts.append(_colorize(token, _GREEN))
        else:
            parts.append(token)
    print(" ".join(parts))


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path) as fh:
        return fh.read()


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``promptdiff`` command."""
    parser = argparse.ArgumentParser(
        prog="promptdiff",
        description="Compute and display diffs between prompt strings.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  promptdiff a.txt b.txt              # line diff\n"
            "  promptdiff --word a.txt b.txt       # word-level diff\n"
            "  promptdiff --unified a.txt b.txt    # unified diff\n"
            "  promptdiff --similarity a.txt b.txt # cosine similarity\n"
            "  echo 'hello' | promptdiff - b.txt   # read A from stdin\n"
        ),
    )
    parser.add_argument("a", metavar="A", help="first file (use - for stdin)")
    parser.add_argument("b", metavar="B", help="second file")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--unified", "-u", action="store_true", help="output unified diff format"
    )
    mode.add_argument(
        "--word", "-w", action="store_true", help="show word-level diff"
    )
    mode.add_argument(
        "--similarity",
        "-s",
        action="store_true",
        help="print cosine similarity score (0.0–1.0)",
    )
    args = parser.parse_args(argv)

    try:
        text_a = _read(args.a)
        text_b = _read(args.b)
    except OSError as exc:
        print(f"promptdiff: {exc}", file=sys.stderr)
        return 1

    if args.unified:
        out = format_unified(text_a, text_b)
        if out:
            print(out, end="")
    elif args.similarity:
        print(f"{similarity(text_a, text_b):.4f}")
    elif args.word:
        _print_word_diff(word_diff(text_a, text_b))
    else:
        _print_line_diff(diff(text_a, text_b))

    return 0


if __name__ == "__main__":
    sys.exit(main())
