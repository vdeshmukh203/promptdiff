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


def test_diff_empty_vs_nonempty():
    result = diff("", "a\n")
    ops = [op for op, _ in result]
    assert ops == ["add"]


def test_diff_nonempty_vs_empty():
    result = diff("a\n", "")
    ops = [op for op, _ in result]
    assert ops == ["remove"]


def test_diff_ops_are_valid():
    result = diff("a\nb\nc\n", "a\nx\nc\n")
    valid_ops = {"equal", "add", "remove"}
    for op, _ in result:
        assert op in valid_ops


def test_diff_reconstruct_b():
    a = "line1\nline2\nline3\n"
    b = "line1\nchanged\nline3\n"
    result = diff(a, b)
    reconstructed = "".join(line for op, line in result if op in ("equal", "add"))
    assert reconstructed == b


def test_diff_type_error():
    with pytest.raises(TypeError):
        diff(123, "hello")
    with pytest.raises(TypeError):
        diff("hello", None)


# ---------------------------------------------------------------------------
# word_diff
# ---------------------------------------------------------------------------


def test_word_diff_identical():
    result = word_diff("hello world", "hello world")
    assert all(op == "equal" for op, _ in result)
    assert [tok for _, tok in result] == ["hello", "world"]


def test_word_diff_one_word_changed():
    result = word_diff("say hello world", "say hello there")
    ops = [op for op, _ in result]
    assert "equal" in ops
    assert "remove" in ops
    assert "add" in ops
    removed = [t for op, t in result if op == "remove"]
    added = [t for op, t in result if op == "add"]
    assert removed == ["world"]
    assert added == ["there"]


def test_word_diff_addition():
    result = word_diff("a b", "a b c")
    added = [t for op, t in result if op == "add"]
    assert added == ["c"]


def test_word_diff_deletion():
    result = word_diff("a b c", "a c")
    removed = [t for op, t in result if op == "remove"]
    assert removed == ["b"]


def test_word_diff_empty_inputs():
    assert word_diff("", "") == []


def test_word_diff_empty_vs_nonempty():
    result = word_diff("", "hello world")
    ops = [op for op, _ in result]
    assert all(op == "add" for op in ops)


def test_word_diff_ops_are_valid():
    result = word_diff("the quick brown fox", "the slow brown dog")
    valid_ops = {"equal", "add", "remove"}
    for op, _ in result:
        assert op in valid_ops


def test_word_diff_returns_list():
    assert isinstance(word_diff("x", "y"), list)


def test_word_diff_type_error():
    with pytest.raises(TypeError):
        word_diff(None, "hello")
    with pytest.raises(TypeError):
        word_diff("hello", 42)


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


def test_format_unified_custom_labels():
    out = format_unified("x\n", "y\n", fromfile="v1", tofile="v2")
    assert "--- v1" in out
    assert "+++ v2" in out


def test_format_unified_type_error():
    with pytest.raises(TypeError):
        format_unified(None, "hi")
    with pytest.raises(TypeError):
        format_unified("hi", 0)


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


def test_similarity_single_char_equal():
    assert similarity("a", "a") == 1.0


def test_similarity_single_char_different():
    assert similarity("a", "b") == 0.0


def test_similarity_type_error():
    with pytest.raises(TypeError):
        similarity(1, "hello")
    with pytest.raises(TypeError):
        similarity("hello", [])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_line_diff(tmp_path):
    from promptdiff.cli import main

    fa = tmp_path / "a.txt"
    fb = tmp_path / "b.txt"
    fa.write_text("hello\nworld\n")
    fb.write_text("hello\nthere\n")
    rc = main([str(fa), str(fb)])
    assert rc == 0


def test_cli_unified(tmp_path, capsys):
    from promptdiff.cli import main

    fa = tmp_path / "a.txt"
    fb = tmp_path / "b.txt"
    fa.write_text("hello\nworld\n")
    fb.write_text("hello\nthere\n")
    rc = main(["--unified", str(fa), str(fb)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "-world" in out
    assert "+there" in out


def test_cli_similarity(tmp_path, capsys):
    from promptdiff.cli import main

    fa = tmp_path / "a.txt"
    fb = tmp_path / "b.txt"
    fa.write_text("hello world")
    fb.write_text("hello world")
    rc = main(["--similarity", str(fa), str(fb)])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert float(out) == pytest.approx(1.0)


def test_cli_word_diff(tmp_path):
    from promptdiff.cli import main

    fa = tmp_path / "a.txt"
    fb = tmp_path / "b.txt"
    fa.write_text("say hello world")
    fb.write_text("say hello there")
    rc = main(["--word", str(fa), str(fb)])
    assert rc == 0


def test_cli_missing_file(tmp_path, capsys):
    from promptdiff.cli import main

    rc = main([str(tmp_path / "no.txt"), str(tmp_path / "no2.txt")])
    assert rc == 1
    assert "promptdiff:" in capsys.readouterr().err


def test_cli_identical_unified(tmp_path, capsys):
    from promptdiff.cli import main

    fa = tmp_path / "a.txt"
    fa.write_text("same\n")
    rc = main(["--unified", str(fa), str(fa)])
    assert rc == 0
    assert capsys.readouterr().out == ""
