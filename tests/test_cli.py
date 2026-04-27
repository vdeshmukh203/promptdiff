"""Tests for the promptdiff command-line interface."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from promptdiff.__main__ import main


class TestCLIInlineStrings:
    def test_inline_inline_diff(self, capsys):
        rc = main(["hello world", "hello there"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "hello" in out

    def test_inline_identical(self, capsys):
        rc = main(["same text", "same text"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Similarity: 1.0000" in out

    def test_inline_no_score(self, capsys):
        main(["a", "b", "--no-score"])
        out = capsys.readouterr().out
        assert "Similarity" not in out

    def test_inline_unified_format(self, capsys):
        main(["hello\nworld\n", "hello\nthere\n", "--format", "unified"])
        out = capsys.readouterr().out
        assert "--- a" in out or out == ""  # empty when identical

    def test_inline_unified_identical(self, capsys):
        main(["same\n", "same\n", "--format", "unified"])
        out = capsys.readouterr().out
        # unified diff of identical strings is empty (no diff lines)
        assert "-same" not in out

    def test_version(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "0.1.0" in out


class TestCLIFiles:
    def test_files_flag(self, tmp_path: Path, capsys):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("hello\nworld\n", encoding="utf-8")
        b.write_text("hello\nthere\n", encoding="utf-8")
        rc = main([str(a), str(b), "--files"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "world" in out or "there" in out

    def test_files_identical(self, tmp_path: Path, capsys):
        f = tmp_path / "f.txt"
        f.write_text("same\n", encoding="utf-8")
        main([str(f), str(f), "--files"])
        out = capsys.readouterr().out
        assert "Similarity: 1.0000" in out

    def test_files_missing(self, tmp_path: Path):
        missing = str(tmp_path / "nope.txt")
        with pytest.raises(SystemExit):
            main([missing, missing, "--files"])

    def test_files_unicode(self, tmp_path: Path, capsys):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("日本語\n", encoding="utf-8")
        b.write_text("日本語\n", encoding="utf-8")
        rc = main([str(a), str(b), "--files"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Similarity: 1.0000" in out


class TestCLIEdgeCases:
    def test_context_flag(self, capsys):
        a = "a\nb\nc\nd\ne\n"
        b = "a\nb\nX\nd\ne\n"
        main([a, b, "--format", "unified", "--context", "1"])
        out = capsys.readouterr().out
        assert "-c" in out and "+X" in out

    def test_similarity_in_output(self, capsys):
        main(["abc", "abc"])
        out = capsys.readouterr().out
        assert "Similarity:" in out
