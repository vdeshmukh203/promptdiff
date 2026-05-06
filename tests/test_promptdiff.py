"""Tests for promptdiff."""

import pytest

from promptdiff import diff, format_unified, similarity, summary


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


def test_diff_all_ops_are_tuples():
    for op, line in diff("a\nb\n", "a\nc\n"):
        assert isinstance(op, str)
        assert isinstance(line, str)
        assert op in {"equal", "add", "remove"}


def test_diff_replace_expands_to_remove_then_add():
    """Replace regions must come out as remove(s) followed by add(s)."""
    result = diff("x\n", "y\n")
    ops = [op for op, _ in result]
    # No 'replace' op should be emitted — only remove/add
    assert "replace" not in ops
    assert "remove" in ops
    assert "add" in ops


def test_diff_autojunk_off_for_repetitive_prompts():
    """autojunk=False means repeated identical lines are not treated as junk."""
    repeated = "step: do something\n" * 30
    modified = repeated.replace("do something\n", "do something else\n", 1)
    result = diff(repeated, modified)
    removed = [l for op, l in result if op == "remove"]
    added = [l for op, l in result if op == "add"]
    assert len(removed) == 1
    assert len(added) == 1


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


def test_format_unified_context_zero():
    a = "line1\nline2\nline3\nline4\nline5\n"
    b = "line1\nline2\nXXXX\nline4\nline5\n"
    out_default = format_unified(a, b)
    out_zero = format_unified(a, b, context=0)
    # context=0 should produce fewer lines than the default context=3
    assert len(out_zero.splitlines()) < len(out_default.splitlines())


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


def test_similarity_single_char_strings_same():
    assert similarity("a", "a") == 1.0


def test_similarity_single_char_strings_different():
    assert similarity("a", "b") == 0.0


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------


def test_summary_returns_dict():
    s = summary("a\nb\n", "a\nc\n")
    assert isinstance(s, dict)


def test_summary_keys():
    s = summary("a\nb\n", "a\nc\n")
    assert set(s.keys()) == {"similarity", "added", "removed", "equal"}


def test_summary_identical():
    s = summary("same\nsame\n", "same\nsame\n")
    assert s["added"] == 0
    assert s["removed"] == 0
    assert s["equal"] == 2
    assert s["similarity"] == 1.0


def test_summary_one_line_changed():
    s = summary("a\nb\n", "a\nc\n")
    assert s["added"] == 1
    assert s["removed"] == 1
    assert s["equal"] == 1
    assert 0.0 < s["similarity"] <= 1.0


def test_summary_counts_nonnegative():
    s = summary("x\ny\nz\n", "a\nb\n")
    assert s["added"] >= 0
    assert s["removed"] >= 0
    assert s["equal"] >= 0


def test_summary_type_error():
    with pytest.raises(TypeError):
        summary(None, "hello")


def test_summary_empty_strings():
    s = summary("", "")
    assert s["similarity"] == 1.0
    assert s["added"] == 0
    assert s["removed"] == 0
    assert s["equal"] == 0
