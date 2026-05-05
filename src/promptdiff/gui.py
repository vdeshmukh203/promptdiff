"""promptdiff.gui - Tkinter-based visual diff tool for prompt strings.

Launch with::

    python -m promptdiff.gui

or, after installation::

    promptdiff-gui
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from promptdiff import __version__, diff, format_unified, similarity

# Colour palette (accessible, works on light and dark OS themes)
_CLR_ADD = "#d4edda"       # soft green  – added lines
_CLR_REMOVE = "#f8d7da"    # soft red    – removed lines
_CLR_EQUAL = "#ffffff"     # white       – unchanged lines
_CLR_HEADER = "#e9ecef"    # light grey  – unified-diff header lines
_CLR_SCORE_HIGH = "#28a745"   # green  – similarity ≥ 0.7
_CLR_SCORE_MED = "#fd7e14"    # orange – similarity ≥ 0.4
_CLR_SCORE_LOW = "#dc3545"    # red    – similarity < 0.4


def _score_colour(score: float) -> str:
    if score >= 0.7:
        return _CLR_SCORE_HIGH
    if score >= 0.4:
        return _CLR_SCORE_MED
    return _CLR_SCORE_LOW


class _ScrolledText(tk.Frame):
    """Text widget with vertical and horizontal scrollbars."""

    def __init__(self, master: tk.Widget, **text_kw) -> None:
        super().__init__(master)
        self.text = tk.Text(self, wrap=tk.NONE, **text_kw)
        vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        hsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text.xview)
        self.text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    # convenience pass-throughs
    def get(self, *args) -> str:
        return self.text.get(*args)

    def insert(self, *args) -> None:
        self.text.insert(*args)

    def delete(self, *args) -> None:
        self.text.delete(*args)

    def configure(self, **kw) -> None:
        self.text.configure(**kw)

    def tag_configure(self, *args, **kw) -> None:
        self.text.tag_configure(*args, **kw)

    def tag_add(self, *args) -> None:
        self.text.tag_add(*args)


class PromptDiffApp(tk.Tk):
    """Main application window for the promptdiff GUI."""

    def __init__(self) -> None:
        super().__init__()
        self.title(f"promptdiff {__version__}")
        self.geometry("1100x720")
        self.minsize(700, 480)
        self._mono = tkfont.Font(family="Courier", size=11)
        self._build_menu()
        self._build_ui()
        self._apply_tags()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Clear all", command=self._clear_all,
                              accelerator="Ctrl+L")
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.destroy,
                              accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)
        self.bind_all("<Control-l>", lambda _e: self._clear_all())
        self.bind_all("<Control-q>", lambda _e: self.destroy())
        self.bind_all("<Control-Return>", lambda _e: self._compare())

    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=2)
        self.grid_columnconfigure(0, weight=1)

        # ── top: two input panels ──────────────────────────────────────
        top = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED,
                             sashwidth=5)
        top.grid(row=0, column=0, sticky="nsew", padx=6, pady=(6, 0))

        left_frame = tk.LabelFrame(top, text="Prompt A  (original)")
        right_frame = tk.LabelFrame(top, text="Prompt B  (revised)")

        self._input_a = _ScrolledText(left_frame, font=self._mono)
        self._input_a.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._input_b = _ScrolledText(right_frame, font=self._mono)
        self._input_b.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        top.add(left_frame, stretch="always")
        top.add(right_frame, stretch="always")

        # ── middle: controls + score ───────────────────────────────────
        ctrl = tk.Frame(self, pady=4)
        ctrl.grid(row=1, column=0, sticky="ew", padx=6)

        compare_btn = ttk.Button(ctrl, text="Compare  (Ctrl+Return)",
                                 command=self._compare)
        compare_btn.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Button(ctrl, text="Clear", command=self._clear_all).pack(
            side=tk.LEFT, padx=(0, 20)
        )

        tk.Label(ctrl, text="Similarity:").pack(side=tk.LEFT)
        self._score_var = tk.StringVar(value="—")
        self._score_lbl = tk.Label(ctrl, textvariable=self._score_var,
                                   font=tkfont.Font(size=14, weight="bold"),
                                   width=8)
        self._score_lbl.pack(side=tk.LEFT, padx=(4, 0))

        # ── bottom: tabbed diff output ─────────────────────────────────
        nb = ttk.Notebook(self)
        nb.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))

        diff_tab = tk.Frame(nb)
        nb.add(diff_tab, text="Structured diff")

        unified_tab = tk.Frame(nb)
        nb.add(unified_tab, text="Unified diff")

        # structured diff view
        diff_tab.grid_rowconfigure(0, weight=1)
        diff_tab.grid_columnconfigure(0, weight=1)
        self._diff_view = _ScrolledText(diff_tab, font=self._mono,
                                        state=tk.DISABLED)
        self._diff_view.grid(sticky="nsew", padx=4, pady=4)

        # unified diff view
        unified_tab.grid_rowconfigure(0, weight=1)
        unified_tab.grid_columnconfigure(0, weight=1)
        self._unified_view = _ScrolledText(unified_tab, font=self._mono,
                                           state=tk.DISABLED)
        self._unified_view.grid(sticky="nsew", padx=4, pady=4)

    def _apply_tags(self) -> None:
        for view in (self._diff_view, self._unified_view):
            view.tag_configure("add", background=_CLR_ADD)
            view.tag_configure("remove", background=_CLR_REMOVE)
            view.tag_configure("equal", background=_CLR_EQUAL)
            view.tag_configure("header", background=_CLR_HEADER,
                               foreground="#6c757d")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _compare(self) -> None:
        a = self._input_a.get("1.0", tk.END).rstrip("\n")
        b = self._input_b.get("1.0", tk.END).rstrip("\n")

        # similarity score
        score = similarity(a, b)
        self._score_var.set(f"{score:.1%}")
        self._score_lbl.configure(fg=_score_colour(score))

        # structured diff
        self._diff_view.configure(state=tk.NORMAL)
        self._diff_view.delete("1.0", tk.END)
        opcodes = diff(a, b)
        for op, line in opcodes:
            tag = op  # "equal" | "add" | "remove"
            prefix = " " if op == "equal" else ("+" if op == "add" else "-")
            self._diff_view.insert(tk.END, prefix + line, tag)
        if not opcodes:
            self._diff_view.insert(tk.END, "(no content)", "equal")
        self._diff_view.configure(state=tk.DISABLED)

        # unified diff
        self._unified_view.configure(state=tk.NORMAL)
        self._unified_view.delete("1.0", tk.END)
        unified = format_unified(a, b)
        if unified:
            for line in unified.splitlines(keepends=True):
                if line.startswith("+") and not line.startswith("+++"):
                    tag = "add"
                elif line.startswith("-") and not line.startswith("---"):
                    tag = "remove"
                elif line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
                    tag = "header"
                else:
                    tag = "equal"
                self._unified_view.insert(tk.END, line, tag)
        else:
            self._unified_view.insert(tk.END, "(prompts are identical)", "equal")
        self._unified_view.configure(state=tk.DISABLED)

    def _clear_all(self) -> None:
        for widget in (self._input_a, self._input_b):
            widget.delete("1.0", tk.END)
        for view in (self._diff_view, self._unified_view):
            view.configure(state=tk.NORMAL)
            view.delete("1.0", tk.END)
            view.configure(state=tk.DISABLED)
        self._score_var.set("—")
        self._score_lbl.configure(fg="black")


def main() -> None:
    """Entry point for the ``promptdiff-gui`` command."""
    app = PromptDiffApp()
    app.mainloop()


if __name__ == "__main__":
    main()
