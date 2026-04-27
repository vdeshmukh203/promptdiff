"""Tkinter-based graphical user interface for promptdiff.

Launch with::

    python -m promptdiff.gui
    # or, after installation:
    promptdiff-gui

The window contains three panels arranged vertically:

- **Before / After** — two side-by-side editable text areas with
  optional file-open buttons.
- **Diff** — a read-only panel showing the structured diff, with
  additions highlighted in green and removals in red.

A similarity score is shown in the toolbar and updated on every
comparison.  Press **Ctrl+Return** (or click *Compare*) to run.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, font as tkfont, scrolledtext, ttk

from promptdiff import diff, similarity

# ── colour palette ────────────────────────────────────────────────────────────
_ADD_BG = "#d4edda"
_ADD_FG = "#155724"
_REM_BG = "#f8d7da"
_REM_FG = "#721c24"
_EQ_FG = "#343a40"
_MONO_FAMILY = "Courier"
_MONO_SIZE = 11

_PREFIX = {"equal": "  ", "add": "+ ", "remove": "- "}


class _EditorPane:
    """A labelled, scrollable text editor with an Open-file toolbar."""

    def __init__(self, parent: ttk.PanedWindow, label: str) -> None:
        self.frame = ttk.LabelFrame(parent, text=label, padding=2)
        bar = ttk.Frame(self.frame)
        bar.pack(fill=tk.X, padx=2, pady=(2, 0))
        ttk.Button(bar, text="Open…", command=self._open).pack(side=tk.LEFT)
        ttk.Button(bar, text="Clear", command=self._clear_text).pack(
            side=tk.LEFT, padx=(4, 0)
        )
        self.text = scrolledtext.ScrolledText(
            self.frame,
            font=tkfont.Font(family=_MONO_FAMILY, size=_MONO_SIZE),
            undo=True,
            relief=tk.FLAT,
            wrap=tk.NONE,
        )
        self.text.pack(fill=tk.BOTH, expand=True)

    def get(self) -> str:
        return self.text.get("1.0", "end-1c")

    def _open(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[
                ("Text / Markdown", "*.txt *.md *.rst"),
                ("All files", "*.*"),
            ]
        )
        if not path:
            return
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)

    def _clear_text(self) -> None:
        self.text.delete("1.0", tk.END)


class PromptDiffApp:
    """Root application window."""

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._root.title("promptdiff")
        self._root.geometry("1150x760")
        self._root.minsize(700, 500)
        self._build()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build(self) -> None:
        self._build_toolbar()
        self._build_editor_panes()
        self._build_diff_panel()
        self._root.bind("<Control-Return>", lambda _e: self._compare())

    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self._root, padding=(6, 4))
        bar.pack(fill=tk.X)

        ttk.Button(bar, text="Compare  (Ctrl+↵)", command=self._compare).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        ttk.Button(bar, text="Clear all", command=self._clear_all).pack(
            side=tk.LEFT
        )

        self._score_var = tk.StringVar(value="Similarity: —")
        ttk.Label(
            bar,
            textvariable=self._score_var,
            font=tkfont.Font(size=11, weight="bold"),
        ).pack(side=tk.RIGHT, padx=8)

        ttk.Separator(self._root, orient=tk.HORIZONTAL).pack(fill=tk.X)

    def _build_editor_panes(self) -> None:
        pw = ttk.PanedWindow(self._root, orient=tk.HORIZONTAL)
        pw.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._before = _EditorPane(pw, "Before")
        self._after = _EditorPane(pw, "After")
        pw.add(self._before.frame, weight=1)
        pw.add(self._after.frame, weight=1)

    def _build_diff_panel(self) -> None:
        frame = ttk.LabelFrame(self._root, text="Diff", padding=2)
        frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        self._diff_out = scrolledtext.ScrolledText(
            frame,
            font=tkfont.Font(family=_MONO_FAMILY, size=_MONO_SIZE),
            state=tk.DISABLED,
            relief=tk.FLAT,
            wrap=tk.NONE,
        )
        self._diff_out.pack(fill=tk.BOTH, expand=True)
        self._diff_out.tag_configure("add", background=_ADD_BG, foreground=_ADD_FG)
        self._diff_out.tag_configure("remove", background=_REM_BG, foreground=_REM_FG)
        self._diff_out.tag_configure("equal", foreground=_EQ_FG)

    # ── actions ───────────────────────────────────────────────────────────────

    def _compare(self) -> None:
        a = self._before.get()
        b = self._after.get()

        score = similarity(a, b)
        self._score_var.set(f"Similarity: {score:.3f}")

        hunks = diff(a, b)
        widget = self._diff_out
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        for op, line in hunks:
            widget.insert(tk.END, _PREFIX[op] + line, op)
        widget.configure(state=tk.DISABLED)

    def _clear_all(self) -> None:
        self._before._clear_text()
        self._after._clear_text()
        widget = self._diff_out
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.configure(state=tk.DISABLED)
        self._score_var.set("Similarity: —")


# ── entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    """Launch the promptdiff GUI."""
    root = tk.Tk()
    PromptDiffApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
