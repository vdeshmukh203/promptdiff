"""Tests for promptdiff.gui.

The GUI cannot be instantiated in a headless CI environment, so this module
tests only the importability of the module and the non-GUI helper logic that
drives the diff/format/similarity calls.  Full interactive widget tests
require a live display and are automatically skipped otherwise.
"""

from __future__ import annotations

import importlib.util

import pytest

# ── tkinter / display availability ────────────────────────────────────────────
tk_available = True
try:
    import tkinter as _tk
    _root = _tk.Tk()
    _root.withdraw()
except Exception:
    tk_available = False
else:
    _root.destroy()

_skip_no_tk = pytest.mark.skipif(
    not tk_available, reason="No display / tkinter not available"
)


# ── import-level smoke tests ───────────────────────────────────────────────────

def test_gui_module_importable():
    """promptdiff.gui source file must exist as a discoverable module."""
    spec = importlib.util.find_spec("promptdiff.gui")
    assert spec is not None, "promptdiff.gui module not found"


@_skip_no_tk
def test_run_callable():
    """promptdiff.gui.run must be a callable."""
    from promptdiff import gui
    assert callable(gui.run)


@_skip_no_tk
def test_app_class_exists():
    """PromptDiffApp class must be defined in the gui module."""
    from promptdiff.gui import PromptDiffApp
    assert PromptDiffApp is not None


# ── logic tests (no display required) ─────────────────────────────────────────

def test_diff_pipeline_produces_expected_ops():
    from promptdiff import diff
    items = diff("hello\nworld\n", "hello\nthere\n")
    ops = [op for op, _ in items]
    assert "equal" in ops
    assert "remove" in ops
    assert "add" in ops


def test_unified_pipeline_for_gui():
    from promptdiff import format_unified
    out = format_unified("hello\n", "world\n", fromfile="Prompt A", tofile="Prompt B")
    assert "--- Prompt A" in out
    assert "+++ Prompt B" in out


def test_similarity_pipeline_for_gui():
    from promptdiff import similarity
    assert similarity("abc", "abc") == 1.0
    assert similarity("abc", "xyz") == 0.0


def test_unified_identical_returns_empty():
    from promptdiff import format_unified
    assert format_unified("same\n", "same\n") == ""


# ── widget tests (display required) ───────────────────────────────────────────

@_skip_no_tk
def test_scrolled_text_has_text_attribute():
    import tkinter as tk
    from promptdiff.gui import _ScrolledText

    root = tk.Tk()
    root.withdraw()
    try:
        st = _ScrolledText(root, bg="white", fg="black", font=("Courier", 10))
        assert hasattr(st, "text")
        assert isinstance(st.text, tk.Text)
    finally:
        root.destroy()


@_skip_no_tk
def test_app_title_contains_version():
    from promptdiff import __version__
    from promptdiff.gui import PromptDiffApp

    app = PromptDiffApp()
    app.withdraw()
    try:
        assert __version__ in app.title()
    finally:
        app.destroy()
