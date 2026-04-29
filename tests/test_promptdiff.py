"""Tests for promptdiff."""

import pytest

from promptdiff import diff, format_unified, similarity, word_diff


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------


def test_diff_identical_strings():
    result = diff("hello\nworld\n", "hello\nworld\n")
    assert all(op == "equal" for op, _ in result)
    assert "".join(line for _, line in result) == "hello\nworld\n"


def test_diff_one_line_changed():
    result = diff("hello\nworld\n", "hello\nthere\n")
    ops = [op for op, _ in result]
    assert "equal" in ops
    assert "remove" in ops
    assert "add" in ops


def test_diff_addition():
    result = diff("a\nb\n", "a\nb\nc\n")
    added = [line for op, line in result if op == "add"]
    assert added == ["c\n"]


def test_diff_deletion():
    result = diff("a\nb\nc\n", "a\nc\n")
    removed = [line for op, line in result if op == "remove"]
    assert removed == ["b\n"]


def test_diff_returns_list():
    result = diff("x", "y")
    assert isinstance(result, list)


def test_diff_empty_inputs():
    assert diff("", "") == []


def test_diff_type_error():
    with pytest.raises(TypeError):
        diff(123, "hello")
    with pytest.raises(TypeError):
        diff("hello", None)


def test_diff_type_error_message():
    with pytest.raises(TypeError, match="str"):
        diff(123, "hello")


def test_diff_reconstruct_a():
    """Lines tagged remove or equal should reconstruct the original string."""
    a = "line1\nline2\nline3\n"
    b = "line1\nLINE2\nline3\n"
    result = diff(a, b)
    reconstructed = "".join(line for op, line in result if op in ("equal", "remove"))
    assert reconstructed == a


def test_diff_reconstruct_b():
    """Lines tagged add or equal should reconstruct the revised string."""
    a = "line1\nline2\nline3\n"
    b = "line1\nLINE2\nline3\n"
    result = diff(a, b)
    reconstructed = "".join(line for op, line in result if op in ("equal", "add"))
    assert reconstructed == b


def test_diff_no_replace_op():
    """Replace regions must be expanded; 'replace' must never appear as op."""
    result = diff("a\nb\nc\n", "a\nB\nC\n")
    ops = {op for op, _ in result}
    assert "replace" not in ops


def test_diff_multiline_replace():
    a = "x\ny\nz\n"
    b = "x\nA\nB\nz\n"
    result = diff(a, b)
    ops = [op for op, _ in result]
    assert "remove" in ops
    assert "add" in ops


def test_diff_tuples_in_result():
    result = diff("a\n", "b\n")
    for item in result:
        assert isinstance(item, tuple)
        assert len(item) == 2
        op, line = item
        assert op in ("equal", "add", "remove")
        assert isinstance(line, str)


def test_diff_no_trailing_newline():
    result = diff("hello", "hello")
    assert result == [("equal", "hello")]


def test_diff_repeated_lines():
    """autojunk=False: repeated lines are diffed correctly."""
    a = "a\na\na\n"
    b = "a\na\n"
    removed = [line for op, line in diff(a, b) if op == "remove"]
    assert removed == ["a\n"]


# ---------------------------------------------------------------------------
# word_diff
# ---------------------------------------------------------------------------


def test_word_diff_identical():
    result = word_diff("hello world", "hello world")
    assert all(op == "equal" for op, _ in result)


def test_word_diff_one_word_changed():
    result = word_diff("the cat sat", "the dog sat")
    ops = [op for op, _ in result]
    assert "equal" in ops
    assert "remove" in ops
    assert "add" in ops


def test_word_diff_removed_word():
    result = word_diff("a b c", "a c")
    removed = [tok.strip() for op, tok in result if op == "remove"]
    assert removed == ["b"]


def test_word_diff_added_word():
    result = word_diff("a c", "a b c")
    added = [tok.strip() for op, tok in result if op == "add"]
    assert added == ["b"]


def test_word_diff_empty_inputs():
    assert word_diff("", "") == []


def test_word_diff_returns_list():
    result = word_diff("x y", "x z")
    assert isinstance(result, list)


def test_word_diff_type_error():
    with pytest.raises(TypeError):
        word_diff(None, "hello")
    with pytest.raises(TypeError):
        word_diff("hello", 42)


def test_word_diff_no_replace_op():
    result = word_diff("foo bar baz", "foo qux baz")
    ops = {op for op, _ in result}
    assert "replace" not in ops


def test_word_diff_reconstruct_a():
    a = "the quick brown fox"
    b = "the slow green fox"
    result = word_diff(a, b)
    reconstructed = "".join(tok for op, tok in result if op in ("equal", "remove"))
    assert reconstructed.strip() == a


def test_word_diff_reconstruct_b():
    a = "the quick brown fox"
    b = "the slow green fox"
    result = word_diff(a, b)
    reconstructed = "".join(tok for op, tok in result if op in ("equal", "add"))
    assert reconstructed.strip() == b


# ---------------------------------------------------------------------------
# format_unified
# ---------------------------------------------------------------------------


def test_format_unified_returns_str():
    out = format_unified("a\nb\n", "a\nc\n")
    assert isinstance(out, str)
    assert "-b" in out
    assert "+c" in out


def test_format_unified_identical_empty():
    assert format_unified("same\n", "same\n") == ""


def test_format_unified_handles_missing_trailing_newline():
    out = format_unified("hello", "world")
    assert isinstance(out, str)
    assert "hello" in out
    assert "world" in out


def test_format_unified_headers_present():
    out = format_unified("x\n", "y\n")
    assert "--- a" in out
    assert "+++ b" in out


def test_format_unified_type_error():
    with pytest.raises(TypeError):
        format_unified(None, "hi")


def test_format_unified_custom_labels():
    out = format_unified("x\n", "y\n", fromfile="original", tofile="revised")
    assert "--- original" in out
    assert "+++ revised" in out


def test_format_unified_both_empty():
    assert format_unified("", "") == ""


# ---------------------------------------------------------------------------
# similarity
# ---------------------------------------------------------------------------


def test_similarity_identical():
    assert similarity("hello world", "hello world") == 1.0


def test_similarity_completely_different():
    assert similarity("aaaa", "bbbb") == 0.0


def test_similarity_partial_overlap():
    s = similarity("hello world", "hello there")
    assert 0.0 < s < 1.0


def test_similarity_empty_strings():
    assert similarity("", "") == 1.0


def test_similarity_one_empty():
    assert similarity("hello", "") == 0.0
    assert similarity("", "hello") == 0.0


def test_similarity_range():
    s = similarity("the quick brown fox", "the lazy brown dog")
    assert 0.0 <= s <= 1.0


def test_similarity_symmetric():
    s1 = similarity("foo bar", "bar foo")
    s2 = similarity("bar foo", "foo bar")
    assert abs(s1 - s2) < 1e-9


def test_similarity_type_error():
    with pytest.raises(TypeError):
        similarity(1, "hello")


def test_similarity_single_char_different():
    assert similarity("a", "b") == 0.0


def test_similarity_single_char_identical():
    assert similarity("a", "a") == 1.0


def test_similarity_returns_float():
    assert isinstance(similarity("abc", "abd"), float)


def test_similarity_bounded():
    pairs = [
        ("", ""),
        ("a", "b"),
        ("abc", "abc"),
        ("hello world", "hello there"),
        ("x" * 100, "y" * 100),
    ]
    for a, b in pairs:
        s = similarity(a, b)
        assert 0.0 <= s <= 1.0, f"out of range for {a!r}, {b!r}: {s}"
