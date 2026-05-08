"""Tests for promptdiff."""

import unittest.mock as mock

import pytest

from promptdiff import diff, format_unified, similarity


# ── diff ─────────────────────────────────────────────────────────────────────

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


def test_diff_one_empty():
    result = diff("", "hello\n")
    assert result == [("add", "hello\n")]

    result = diff("hello\n", "")
    assert result == [("remove", "hello\n")]


def test_diff_no_trailing_newline():
    result = diff("a", "b")
    ops = [op for op, _ in result]
    assert "remove" in ops
    assert "add" in ops


def test_diff_replace_expands_to_remove_then_add():
    result = diff("old\n", "new\n")
    ops = [op for op, _ in result]
    # replace must be expanded: remove comes before add
    remove_idx = ops.index("remove")
    add_idx = ops.index("add")
    assert remove_idx < add_idx


def test_diff_preserves_trailing_newlines():
    result = diff("line1\nline2\n", "line1\nline3\n")
    for _op, line in result:
        assert line.endswith("\n")


def test_diff_type_error():
    with pytest.raises(TypeError):
        diff(123, "hello")
    with pytest.raises(TypeError):
        diff("hello", None)


def test_diff_multiline_replace():
    result = diff("a\nb\n", "c\nd\n")
    removed = [line for op, line in result if op == "remove"]
    added = [line for op, line in result if op == "add"]
    assert "a\n" in removed
    assert "b\n" in removed
    assert "c\n" in added
    assert "d\n" in added


# ── format_unified ────────────────────────────────────────────────────────────

def test_format_unified_returns_str():
    out = format_unified("a\nb\n", "a\nc\n")
    assert isinstance(out, str)
    assert "-b" in out
    assert "+c" in out


def test_format_unified_identical_empty():
    assert format_unified("same\n", "same\n") == ""


def test_format_unified_both_empty():
    assert format_unified("", "") == ""


def test_format_unified_handles_missing_trailing_newline():
    out = format_unified("hello", "world")
    assert isinstance(out, str)
    assert "hello" in out
    assert "world" in out


def test_format_unified_headers_present():
    out = format_unified("x\n", "y\n")
    assert "--- a" in out
    assert "+++ b" in out


def test_format_unified_add_only():
    out = format_unified("", "new line\n")
    assert "+new line" in out


def test_format_unified_remove_only():
    out = format_unified("old line\n", "")
    assert "-old line" in out


def test_format_unified_type_error():
    with pytest.raises(TypeError):
        format_unified(None, "hi")
    with pytest.raises(TypeError):
        format_unified("hi", 42)


# ── similarity ────────────────────────────────────────────────────────────────

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


def test_similarity_single_char_different():
    # length-1 strings have no bigrams → 0.0 unless equal
    assert similarity("a", "b") == 0.0


def test_similarity_single_char_identical():
    assert similarity("a", "a") == 1.0


def test_similarity_type_error():
    with pytest.raises(TypeError):
        similarity(1, "hello")
    with pytest.raises(TypeError):
        similarity("hello", None)


# ── GUI import ────────────────────────────────────────────────────────────────

def test_gui_module_importable():
    """gui.py should import without raising even in a headless environment."""
    import importlib
    import sys

    # Stub tkinter if it isn't present (e.g., minimal CI images).
    tk_stub = mock.MagicMock()
    patched = "tkinter" not in sys.modules
    if patched:
        sys.modules.setdefault("tkinter", tk_stub)
        sys.modules.setdefault("tkinter.scrolledtext", tk_stub)

    try:
        # Remove cached module so the import runs fresh under any stub.
        sys.modules.pop("promptdiff.gui", None)
        mod = importlib.import_module("promptdiff.gui")
        assert callable(mod.main)
    finally:
        if patched:
            sys.modules.pop("tkinter", None)
            sys.modules.pop("tkinter.scrolledtext", None)
        sys.modules.pop("promptdiff.gui", None)


# ── __main__ ─────────────────────────────────────────────────────────────────

def test_main_module_calls_gui_main():
    import importlib
    import sys

    sys.modules.pop("promptdiff.__main__", None)
    sys.modules.pop("promptdiff.gui", None)

    gui_stub = mock.MagicMock()
    gui_stub.main = mock.MagicMock()
    sys.modules["promptdiff.gui"] = gui_stub

    try:
        mod = importlib.import_module("promptdiff.__main__")
        mod.main()
        gui_stub.main.assert_called_once()
    finally:
        sys.modules.pop("promptdiff.__main__", None)
        sys.modules.pop("promptdiff.gui", None)
