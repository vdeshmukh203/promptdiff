"""Tests for promptdiff."""

import pytest

from promptdiff import DiffLine, diff, format_unified, similarity


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


def test_diff_returns_diffline_namedtuples():
    result = diff("a\n", "b\n")
    for entry in result:
        assert isinstance(entry, DiffLine)
        assert hasattr(entry, "op")
        assert hasattr(entry, "line")


def test_diff_ops_are_valid():
    valid_ops = {"equal", "add", "remove"}
    result = diff("foo\nbar\n", "foo\nbaz\n")
    for op, _ in result:
        assert op in valid_ops


def test_diff_reconstruct_b_from_diff():
    a = "line1\nline2\nline3\n"
    b = "line1\nchanged\nline3\nline4\n"
    result = diff(a, b)
    reconstructed = "".join(line for op, line in result if op in ("equal", "add"))
    assert reconstructed == b


def test_diff_no_replace_tag():
    result = diff("alpha\nbeta\n", "alpha\ngamma\n")
    ops = {op for op, _ in result}
    assert "replace" not in ops


def test_diff_unicode():
    a = "café\n"
    b = "café au lait\n"
    result = diff(a, b)
    assert any(op == "add" for op, _ in result)


def test_diff_multiline_replace_expands_to_remove_then_add():
    a = "x\ny\n"
    b = "p\nq\n"
    result = diff(a, b)
    ops = [op for op, _ in result]
    # All removes should appear before all adds
    last_remove = max((i for i, op in enumerate(ops) if op == "remove"), default=-1)
    first_add = min((i for i, op in enumerate(ops) if op == "add"), default=len(ops))
    assert last_remove < first_add


def test_diff_autojunk_repeated_lines():
    # With autojunk=True, repeated lines are treated as noise and may be
    # suppressed. autojunk=False gives accurate results for short prompts.
    repeated = "same\n" * 20
    changed = "same\n" * 19 + "different\n"
    result = diff(repeated, changed)
    removed = [line for op, line in result if op == "remove"]
    added = [line for op, line in result if op == "add"]
    assert removed == ["same\n"]
    assert added == ["different\n"]


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


def test_format_unified_unicode():
    out = format_unified("こんにちは\n", "こんにちは世界\n")
    assert isinstance(out, str)
    assert "世界" in out


def test_format_unified_empty_to_nonempty():
    out = format_unified("", "new content\n")
    assert "+new content" in out


def test_format_unified_nonempty_to_empty():
    out = format_unified("old content\n", "")
    assert "-old content" in out


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


def test_similarity_single_char_equal():
    assert similarity("a", "a") == 1.0


def test_similarity_single_char_different():
    assert similarity("a", "b") == 0.0


def test_similarity_unicode():
    s = similarity("日本語テキスト", "日本語テスト")
    assert 0.0 < s <= 1.0


def test_similarity_result_clamped():
    # Even for pathological inputs the result must stay in [0, 1].
    for a, b in [("a" * 100, "a" * 100), ("abc", "xyz"), ("ab", "ba")]:
        s = similarity(a, b)
        assert 0.0 <= s <= 1.0


def test_similarity_short_strings_no_bigrams():
    # Single-char strings that are not equal have no bigrams → 0.0
    assert similarity("x", "y") == 0.0


def test_similarity_long_prompt():
    prompt = "You are a helpful assistant. " * 50
    modified = prompt.replace("helpful", "knowledgeable", 1)
    s = similarity(prompt, modified)
    # Should be very high but not necessarily 1.0
    assert s > 0.9
