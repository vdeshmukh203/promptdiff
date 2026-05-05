"""Tests for promptdiff."""

import pytest

from promptdiff import diff, format_unified, similarity


# ---------------------------------------------------------------------------
# diff()
# ---------------------------------------------------------------------------

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

    def test_empty_inputs(self):
        assert diff("", "") == []

    def test_empty_a(self):
        result = diff("", "line\n")
        assert all(op == "add" for op, _ in result)

    def test_empty_b(self):
        result = diff("line\n", "")
        assert all(op == "remove" for op, _ in result)

    def test_no_replace_opcode(self):
        """diff() must never emit a 'replace' operation."""
        result = diff("old line\n", "new line\n")
        ops = {op for op, _ in result}
        assert "replace" not in ops

    def test_reconstruct_a(self):
        a = "first\nsecond\nthird\n"
        b = "first\nchanged\nthird\nfourth\n"
        result = diff(a, b)
        reconstructed = "".join(
            line for op, line in result if op in ("equal", "remove")
        )
        assert reconstructed == a

    def test_reconstruct_b(self):
        a = "first\nsecond\n"
        b = "first\nchanged\nextra\n"
        result = diff(a, b)
        reconstructed = "".join(
            line for op, line in result if op in ("equal", "add")
        )
        assert reconstructed == b

    def test_multiline_replace(self):
        result = diff("a\nb\nc\n", "x\ny\nc\n")
        removed = [line for op, line in result if op == "remove"]
        added = [line for op, line in result if op == "add"]
        assert "a\n" in removed and "b\n" in removed
        assert "x\n" in added and "y\n" in added

    def test_type_error_first_arg(self):
        with pytest.raises(TypeError, match="diff()"):
            diff(123, "hello")

    def test_type_error_second_arg(self):
        with pytest.raises(TypeError, match="diff()"):
            diff("hello", None)

    def test_large_inputs(self):
        a = "".join(f"line {i}\n" for i in range(1000))
        b = "".join(f"line {i}\n" for i in range(500, 1500))
        result = diff(a, b)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_no_trailing_newline(self):
        result = diff("hello", "hello")
        assert result[0] == ("equal", "hello")


# ---------------------------------------------------------------------------
# format_unified()
# ---------------------------------------------------------------------------

class TestFormatUnified:
    def test_returns_str(self):
        out = format_unified("a\nb\n", "a\nc\n")
        assert isinstance(out, str)
        assert "-b" in out
        assert "+c" in out

    def test_identical_returns_empty(self):
        assert format_unified("same\n", "same\n") == ""

    def test_handles_missing_trailing_newline(self):
        out = format_unified("hello", "world")
        assert isinstance(out, str)
        assert "hello" in out
        assert "world" in out

    def test_headers_present(self):
        out = format_unified("x\n", "y\n")
        assert "--- a" in out
        assert "+++ b" in out

    def test_context_parameter(self):
        lines = [f"line{i}\n" for i in range(20)]
        a = "".join(lines)
        b_lines = lines[:]
        b_lines[10] = "CHANGED\n"
        b = "".join(b_lines)
        out_default = format_unified(a, b)
        out_zero = format_unified(a, b, context=0)
        # context=0 produces fewer unchanged lines → shorter output
        assert len(out_zero) < len(out_default)

    def test_context_invalid_raises(self):
        with pytest.raises(ValueError):
            format_unified("a\n", "b\n", context=-1)

    def test_type_error_first_arg(self):
        with pytest.raises(TypeError, match="format_unified()"):
            format_unified(None, "hi")

    def test_type_error_second_arg(self):
        with pytest.raises(TypeError, match="format_unified()"):
            format_unified("hi", 42)

    def test_unified_diff_format(self):
        out = format_unified("a\nb\nc\n", "a\nB\nc\n")
        lines = out.splitlines()
        # Must have a hunk header
        assert any(line.startswith("@@") for line in lines)


# ---------------------------------------------------------------------------
# similarity()
# ---------------------------------------------------------------------------

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

    def test_one_empty_a(self):
        assert similarity("", "hello") == 0.0

    def test_one_empty_b(self):
        assert similarity("hello", "") == 0.0

    def test_range(self):
        s = similarity("the quick brown fox", "the lazy brown dog")
        assert 0.0 <= s <= 1.0

    def test_symmetric(self):
        s1 = similarity("foo bar", "bar foo")
        s2 = similarity("bar foo", "foo bar")
        assert abs(s1 - s2) < 1e-12

    def test_single_char_not_identical(self):
        assert similarity("a", "b") == 0.0

    def test_single_char_identical(self):
        assert similarity("a", "a") == 1.0

    def test_type_error_first_arg(self):
        with pytest.raises(TypeError, match="similarity()"):
            similarity(1, "hello")

    def test_type_error_second_arg(self):
        with pytest.raises(TypeError, match="similarity()"):
            similarity("hello", [])

    def test_score_increases_with_overlap(self):
        base = "You are a helpful assistant."
        minor = "You are a very helpful assistant."
        major = "You are a pizza delivery robot."
        assert similarity(base, minor) > similarity(base, major)

    def test_multiline_prompts(self):
        a = "System: You are helpful.\nUser: Tell me a joke.\n"
        b = "System: You are helpful.\nUser: Tell me a story.\n"
        s = similarity(a, b)
        assert 0.0 < s < 1.0
