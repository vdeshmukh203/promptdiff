"""Tests for promptdiff core API."""

from __future__ import annotations

import pytest

from promptdiff import diff, format_unified, similarity
from promptdiff import _bigrams


# ── diff() ────────────────────────────────────────────────────────────────────


class TestDiff:
    def test_identical_strings_all_equal(self):
        result = diff("hello\nworld\n", "hello\nworld\n")
        assert all(op == "equal" for op, _ in result)
        assert "".join(line for _, line in result) == "hello\nworld\n"

    def test_one_line_changed_contains_all_ops(self):
        result = diff("hello\nworld\n", "hello\nthere\n")
        ops = {op for op, _ in result}
        assert ops == {"equal", "remove", "add"}

    def test_addition_detected(self):
        result = diff("a\nb\n", "a\nb\nc\n")
        added = [line for op, line in result if op == "add"]
        assert added == ["c\n"]

    def test_deletion_detected(self):
        result = diff("a\nb\nc\n", "a\nc\n")
        removed = [line for op, line in result if op == "remove"]
        assert removed == ["b\n"]

    def test_returns_list_of_tuples(self):
        result = diff("x\n", "y\n")
        assert isinstance(result, list)
        assert all(isinstance(t, tuple) and len(t) == 2 for t in result)

    def test_empty_inputs(self):
        assert diff("", "") == []

    def test_empty_a(self):
        result = diff("", "hello\n")
        assert all(op == "add" for op, _ in result)

    def test_empty_b(self):
        result = diff("hello\n", "")
        assert all(op == "remove" for op, _ in result)

    def test_no_trailing_newline(self):
        result = diff("foo", "foo")
        assert result == [("equal", "foo")]

    def test_multiline_no_trailing_newline(self):
        result = diff("a\nb", "a\nb")
        assert all(op == "equal" for op, _ in result)

    def test_replace_expands_to_remove_then_add(self):
        result = diff("old\n", "new\n")
        ops = [op for op, _ in result]
        # No "replace" op; remove must precede add
        assert "replace" not in ops
        if "remove" in ops and "add" in ops:
            assert ops.index("remove") < ops.index("add")

    def test_unicode_content(self):
        result = diff("héllo\n", "héllo\n")
        assert all(op == "equal" for op, _ in result)

    def test_unicode_change(self):
        result = diff("café\n", "cafe\n")
        ops = {op for op, _ in result}
        assert "remove" in ops or "add" in ops

    def test_only_operations_in_set(self):
        result = diff("a\nb\nc\n", "a\nx\nc\n")
        valid = {"equal", "add", "remove"}
        assert all(op in valid for op, _ in result)

    def test_reconstructed_lines_match_b(self):
        a = "line1\nline2\nline3\n"
        b = "line1\nchanged\nline3\nline4\n"
        result = diff(a, b)
        b_reconstructed = "".join(
            line for op, line in result if op in ("equal", "add")
        )
        assert b_reconstructed == b

    def test_windows_line_endings(self):
        result = diff("a\r\nb\r\n", "a\r\nb\r\n")
        assert all(op == "equal" for op, _ in result)

    def test_type_error_first_arg(self):
        with pytest.raises(TypeError):
            diff(123, "hello")

    def test_type_error_second_arg(self):
        with pytest.raises(TypeError):
            diff("hello", None)

    def test_type_error_both_args(self):
        with pytest.raises(TypeError):
            diff(None, None)

    def test_autojunk_disabled_for_short_inputs(self):
        # With autojunk=True, SequenceMatcher may skip lines appearing in >1%
        # of the text; autojunk=False ensures correctness on small inputs.
        a = "\n".join(["x"] * 5) + "\n"
        b = a
        result = diff(a, b)
        assert all(op == "equal" for op, _ in result)


# ── format_unified() ──────────────────────────────────────────────────────────


class TestFormatUnified:
    def test_returns_str(self):
        assert isinstance(format_unified("a\n", "b\n"), str)

    def test_identical_returns_empty(self):
        assert format_unified("same\n", "same\n") == ""

    def test_addition_marker(self):
        out = format_unified("a\nb\n", "a\nc\n")
        assert "+c" in out
        assert "-b" in out

    def test_handles_missing_trailing_newline(self):
        out = format_unified("hello", "world")
        assert "hello" in out and "world" in out

    def test_headers_present(self):
        out = format_unified("x\n", "y\n")
        assert "--- a" in out
        assert "+++ b" in out

    def test_custom_labels(self):
        out = format_unified("x\n", "y\n", fromfile="before", tofile="after")
        assert "--- before" in out
        assert "+++ after" in out

    def test_context_zero(self):
        out = format_unified("a\nb\nc\n", "a\nB\nc\n", context=0)
        assert "-b" in out and "+B" in out
        # With zero context, unchanged lines are not shown in hunks
        assert out.count(" a") == 0 or "@@" in out

    def test_type_error_first_arg(self):
        with pytest.raises(TypeError):
            format_unified(None, "hi")

    def test_type_error_second_arg(self):
        with pytest.raises(TypeError):
            format_unified("hi", 42)

    def test_type_error_fromfile(self):
        with pytest.raises(TypeError):
            format_unified("a\n", "b\n", fromfile=1)

    def test_invalid_context_negative(self):
        with pytest.raises(ValueError):
            format_unified("a\n", "b\n", context=-1)

    def test_invalid_context_type(self):
        with pytest.raises(ValueError):
            format_unified("a\n", "b\n", context="3")  # type: ignore[arg-type]

    def test_unicode(self):
        out = format_unified("naïve\n", "naive\n")
        assert isinstance(out, str)
        assert "naïve" in out or "naive" in out


# ── similarity() ──────────────────────────────────────────────────────────────


class TestSimilarity:
    def test_identical(self):
        assert similarity("hello world", "hello world") == 1.0

    def test_completely_different(self):
        assert similarity("aaaa", "bbbb") == 0.0

    def test_partial_overlap(self):
        s = similarity("hello world", "hello there")
        assert 0.0 < s < 1.0

    def test_empty_both(self):
        assert similarity("", "") == 1.0

    def test_one_empty(self):
        assert similarity("hello", "") == 0.0
        assert similarity("", "hello") == 0.0

    def test_range(self):
        s = similarity("the quick brown fox", "the lazy brown dog")
        assert 0.0 <= s <= 1.0

    def test_symmetric(self):
        s1 = similarity("foo bar", "bar foo")
        s2 = similarity("bar foo", "foo bar")
        assert abs(s1 - s2) < 1e-9

    def test_single_char_both_same(self):
        assert similarity("a", "a") == 1.0

    def test_single_char_both_different(self):
        assert similarity("a", "b") == 0.0

    def test_single_char_vs_word(self):
        assert similarity("a", "abcdef") == 0.0

    def test_unicode_identical(self):
        assert similarity("日本語", "日本語") == 1.0

    def test_unicode_partial(self):
        s = similarity("日本語テスト", "日本語サンプル")
        assert 0.0 < s < 1.0

    def test_long_strings(self):
        base = "the quick brown fox jumps over the lazy dog " * 50
        modified = base.replace("fox", "cat", 5)
        s = similarity(base, modified)
        assert 0.9 < s <= 1.0

    def test_type_error_first_arg(self):
        with pytest.raises(TypeError):
            similarity(1, "hello")

    def test_type_error_second_arg(self):
        with pytest.raises(TypeError):
            similarity("hello", [])

    def test_type_error_both_args(self):
        with pytest.raises(TypeError):
            similarity(None, None)


# ── _bigrams() ────────────────────────────────────────────────────────────────


class TestBigrams:
    def test_simple(self):
        bg = _bigrams("abc")
        assert bg["ab"] == 1 and bg["bc"] == 1

    def test_repeated(self):
        bg = _bigrams("aaa")
        assert bg["aa"] == 2

    def test_empty(self):
        assert _bigrams("") == {}

    def test_single_char(self):
        assert _bigrams("x") == {}

    def test_length(self):
        s = "hello"
        bg = _bigrams(s)
        assert sum(bg.values()) == len(s) - 1

    def test_unicode(self):
        bg = _bigrams("αβγ")
        assert "αβ" in bg and "βγ" in bg
