"""Tkinter GUI for promptdiff.

Launch with::

    python -m promptdiff.gui

or, after installing the package::

    promptdiff-gui

The window provides two editable text panes (original and revised prompt),
a colour-coded diff view, and a real-time similarity score.  Ctrl+Return
(or the Diff button) triggers the comparison.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from promptdiff import diff, similarity

# Palette for diff operation tags
_TAG_CFG: dict[str, dict[str, str]] = {
    "add":    {"background": "#e6ffed", "foreground": "#22863a"},
    "remove": {"background": "#ffeef0", "foreground": "#b31d28"},
    "equal":  {"background": "#ffffff", "foreground": "#24292e"},
}

_GUTTER_WIDTH = 2   # chars for the +/- prefix


class _ScrolledText(ttk.Frame):
    """Text widget with attached vertical and horizontal scrollbars."""

    def __init__(self, master: tk.Widget, **text_kw: object) -> None:
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.text = tk.Text(self, **text_kw)  # type: ignore[arg-type]
        self.text.grid(row=0, column=0, sticky=tk.NSEW)

        vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text.xview)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        self.text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)


class PromptDiffApp(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("promptdiff")
        self.minsize(940, 680)
        self._mono = tkfont.Font(family="Courier", size=11)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=8)
        outer.pack(fill=tk.BOTH, expand=True)

        self._build_inputs(outer)
        self._build_toolbar(outer)
        self._build_diff_view(outer)
        self._build_statusbar()

        self.bind("<Control-Return>", lambda _e: self._run_diff())

    def _build_inputs(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Inputs", padding=4)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Original (a)").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 2)
        )
        ttk.Label(frame, text="Revised (b)").grid(
            row=0, column=2, sticky=tk.W, pady=(0, 2)
        )

        kw = dict(height=10, font=self._mono, wrap=tk.NONE, undo=True)
        self._pane_a = _ScrolledText(frame, **kw)
        self._pane_a.grid(row=1, column=0, sticky=tk.NSEW)

        ttk.Separator(frame, orient=tk.VERTICAL).grid(
            row=1, column=1, sticky=tk.NS, padx=4
        )

        self._pane_b = _ScrolledText(frame, **kw)
        self._pane_b.grid(row=1, column=2, sticky=tk.NSEW)

    def _build_toolbar(self, parent: ttk.Frame) -> None:
        bar = ttk.Frame(parent)
        bar.pack(fill=tk.X, pady=(0, 4))

        ttk.Button(bar, text="Diff  (Ctrl+↵)", command=self._run_diff).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        ttk.Button(bar, text="Swap ⇅", command=self._swap).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        ttk.Button(bar, text="Clear", command=self._clear).pack(
            side=tk.LEFT, padx=(0, 4)
        )

        self._sim_var = tk.StringVar(value="Similarity: —")
        ttk.Label(bar, textvariable=self._sim_var, font=("TkDefaultFont", 11)).pack(
            side=tk.RIGHT, padx=8
        )

    def _build_diff_view(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Diff", padding=4)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self._diff_pane = _ScrolledText(
            frame,
            height=14,
            font=self._mono,
            wrap=tk.NONE,
            state=tk.DISABLED,
        )
        self._diff_pane.grid(row=0, column=0, sticky=tk.NSEW)

        for tag, cfg in _TAG_CFG.items():
            self._diff_pane.text.tag_configure(tag, **cfg)

    def _build_statusbar(self) -> None:
        self._status_var = tk.StringVar(
            value="Enter text in the panes above, then click Diff."
        )
        ttk.Label(
            self,
            textvariable=self._status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(4, 2),
        ).pack(fill=tk.X, side=tk.BOTTOM)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _get(self, pane: _ScrolledText) -> str:
        text = pane.text.get("1.0", tk.END)
        # tk.Text always appends a trailing newline; strip it if the user
        # did not type one so that the diff is not distorted.
        if text.endswith("\n"):
            text = text[:-1]
        return text

    def _run_diff(self) -> None:
        a = self._get(self._pane_a)
        b = self._get(self._pane_b)

        chunks = diff(a, b)
        sim = similarity(a, b)

        tw = self._diff_pane.text
        tw.configure(state=tk.NORMAL)
        tw.delete("1.0", tk.END)

        for op, line in chunks:
            prefix = "+ " if op == "add" else ("- " if op == "remove" else "  ")
            tw.insert(tk.END, prefix + line, op)

        # Ensure the view ends with a newline so the last tag renders fully
        if chunks and not tw.get("end-2c") == "\n":
            tw.insert(tk.END, "\n")

        tw.configure(state=tk.DISABLED)

        n_add = sum(1 for op, _ in chunks if op == "add")
        n_rem = sum(1 for op, _ in chunks if op == "remove")
        self._sim_var.set(f"Similarity: {sim:.4f}")
        self._status_var.set(
            f"+{n_add} line{'s' if n_add != 1 else ''}  "
            f"-{n_rem} line{'s' if n_rem != 1 else ''}  "
            f"similarity {sim:.4f}"
        )

    def _clear(self) -> None:
        for pane in (self._pane_a, self._pane_b):
            pane.text.delete("1.0", tk.END)
        tw = self._diff_pane.text
        tw.configure(state=tk.NORMAL)
        tw.delete("1.0", tk.END)
        tw.configure(state=tk.DISABLED)
        self._sim_var.set("Similarity: —")
        self._status_var.set("Cleared.")

    def _swap(self) -> None:
        a = self._get(self._pane_a)
        b = self._get(self._pane_b)
        self._pane_a.text.delete("1.0", tk.END)
        self._pane_a.text.insert("1.0", b)
        self._pane_b.text.delete("1.0", tk.END)
        self._pane_b.text.insert("1.0", a)
        self._status_var.set("Swapped — click Diff to refresh.")


def main() -> None:
    """Launch the promptdiff GUI."""
    app = PromptDiffApp()
    app.mainloop()


if __name__ == "__main__":
    main()
