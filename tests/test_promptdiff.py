"""Tests for promptdiff."""

import pytest

from promptdiff import diff, format_unified, similarity


# ══════════════════════════════════════════════════════════════════════════════
# diff()
# ══════════════════════════════════════════════════════════════════════════════

class TestDiff:
    def test_identical_strings(self):
        result = diff("hello\nworld\n", "hello\nworld\n")
        assert all(op == "equal" for op, _ in result)
        assert "".join(line for _, line in result) == "hello\nworld\n"

    def test_one_line_changed(self):
        result = diff("hello\nworld\n", "hello\nthere\n")
        ops = [op for op, _ in result]
        assert "equal" in ops
        assert "remove" in ops
        assert "add" in ops

    def test_addition(self):
        result = diff("a\nb\n", "a\nb\nc\n")
        added = [line for op, line in result if op == "add"]
        assert added == ["c\n"]

    def test_deletion(self):
        result = diff("a\nb\nc\n", "a\nc\n")
        removed = [line for op, line in result if op == "remove"]
        assert removed == ["b\n"]

    def test_returns_list(self):
        assert isinstance(diff("x", "y"), list)

    def test_tuples_in_result(self):
        for item in diff("a\n", "b\n"):
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_empty_inputs(self):
        assert diff("", "") == []

    def test_empty_vs_nonempty(self):
        result = diff("", "hello\n")
        assert result == [("add", "hello\n")]

    def test_nonempty_vs_empty(self):
        result = diff("hello\n", "")
        assert result == [("remove", "hello\n")]

    def test_no_replace_op_in_output(self):
        """replace opcodes must be expanded into remove + add pairs."""
        result = diff("foo\n", "bar\n")
        ops = {op for op, _ in result}
        assert "replace" not in ops

    def test_newlines_preserved(self):
        result = diff("a\nb\n", "a\nc\n")
        for _, line in result:
            assert line.endswith("\n")

    def test_reconstruction_from_adds(self):
        """Collecting add lines should reproduce the target string."""
        a = "x\ny\n"
        b = "x\nz\nw\n"
        result = diff(a, b)
        reconstructed = "".join(
            line for op, line in result if op in ("equal", "add")
        )
        assert reconstructed == b

    def test_autojunk_disabled(self):
        """Repeated identical lines must not be silently classified as junk."""
        # Without autojunk=False a block of identical short lines could be
        # treated as noise, causing them to be omitted from the diff output.
        repeated = "x\n" * 20
        result = diff(repeated, repeated)
        assert len(result) == 20
        assert all(op == "equal" for op, _ in result)

    def test_type_error_first_arg(self):
        with pytest.raises(TypeError):
            diff(123, "hello")

    def test_type_error_second_arg(self):
        with pytest.raises(TypeError):
            diff("hello", None)

    def test_multiline_no_trailing_newline(self):
        result = diff("a\nb", "a\nb")
        assert all(op == "equal" for op, _ in result)


# ══════════════════════════════════════════════════════════════════════════════
# format_unified()
# ══════════════════════════════════════════════════════════════════════════════

class TestFormatUnified:
    def test_returns_str(self):
        out = format_unified("a\nb\n", "a\nc\n")
        assert isinstance(out, str)

    def test_contains_removed_line(self):
        out = format_unified("a\nb\n", "a\nc\n")
        assert "-b" in out

    def test_contains_added_line(self):
        out = format_unified("a\nb\n", "a\nc\n")
        assert "+c" in out

    def test_identical_returns_empty(self):
        assert format_unified("same\n", "same\n") == ""

    def test_missing_trailing_newline(self):
        out = format_unified("hello", "world")
        assert isinstance(out, str)
        assert "hello" in out
        assert "world" in out

    def test_default_headers(self):
        out = format_unified("x\n", "y\n")
        assert "--- a" in out
        assert "+++ b" in out

    def test_custom_fromfile(self):
        out = format_unified("x\n", "y\n", fromfile="v1.txt")
        assert "--- v1.txt" in out

    def test_custom_tofile(self):
        out = format_unified("x\n", "y\n", tofile="v2.txt")
        assert "+++ v2.txt" in out

    def test_type_error_first_arg(self):
        with pytest.raises(TypeError):
            format_unified(None, "hi")

    def test_type_error_second_arg(self):
        with pytest.raises(TypeError):
            format_unified("hi", 42)

    def test_type_error_fromfile(self):
        with pytest.raises(TypeError):
            format_unified("a\n", "b\n", fromfile=1)  # type: ignore[arg-type]

    def test_empty_inputs_returns_empty(self):
        assert format_unified("", "") == ""


# ══════════════════════════════════════════════════════════════════════════════
# similarity()
# ══════════════════════════════════════════════════════════════════════════════

class TestSimilarity:
    def test_identical(self):
        assert similarity("hello world", "hello world") == 1.0

    def test_completely_different(self):
        assert similarity("aaaa", "bbbb") == 0.0

    def test_partial_overlap(self):
        s = similarity("hello world", "hello there")
        assert 0.0 < s < 1.0

    def test_empty_strings(self):
        assert similarity("", "") == 1.0

    def test_one_empty_left(self):
        assert similarity("", "hello") == 0.0

    def test_one_empty_right(self):
        assert similarity("hello", "") == 0.0

    def test_range(self):
        s = similarity("the quick brown fox", "the lazy brown dog")
        assert 0.0 <= s <= 1.0

    def test_symmetric(self):
        s1 = similarity("foo bar", "bar foo")
        s2 = similarity("bar foo", "foo bar")
        assert abs(s1 - s2) < 1e-9

    def test_single_char_equal(self):
        assert similarity("x", "x") == 1.0

    def test_single_char_different(self):
        assert similarity("x", "y") == 0.0

    def test_type_error_first_arg(self):
        with pytest.raises(TypeError):
            similarity(1, "hello")

    def test_type_error_second_arg(self):
        with pytest.raises(TypeError):
            similarity("hello", [])

    def test_long_identical(self):
        s = "You are a helpful assistant.\n" * 50
        assert similarity(s, s) == 1.0

    def test_near_identical(self):
        a = "Answer concisely."
        b = "Answer concisely!"
        s = similarity(a, b)
        assert s > 0.8
