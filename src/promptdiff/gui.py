"""Tkinter graphical interface for promptdiff.

Launch with::

    python -m promptdiff --gui

or directly::

    python -m promptdiff.gui
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from promptdiff import __version__, diff, format_unified, similarity

# Colour palette (GitHub-inspired diff colours)
_ADD_BG = "#d4edda"
_ADD_FG = "#155724"
_REMOVE_BG = "#f8d7da"
_REMOVE_FG = "#721c24"
_HEADER_FG = "#0366d6"
_EQUAL_FG = "#24292e"

_ABOUT_TEXT = (
    f"promptdiff  {__version__}\n\n"
    "Compare LLM prompt strings with structured\n"
    "diffs and cosine-bigram similarity scores.\n\n"
    "Pure Python · standard library only\n"
    "MIT licence"
)


class _ScrolledText(ttk.Frame):
    """A Text widget bundled with a vertical scrollbar."""

    def __init__(self, master: tk.Widget, **text_kw: object) -> None:
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.text = tk.Text(self, **text_kw)  # type: ignore[arg-type]
        sb = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=sb.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")


class App(tk.Tk):
    """Main application window for the promptdiff GUI."""

    def __init__(self) -> None:
        super().__init__()
        self.title("promptdiff")
        self.minsize(860, 580)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self._mono = tkfont.Font(family="Courier", size=11)
        self._bold = tkfont.Font(family="TkDefaultFont", size=10, weight="bold")

        self._build_menu()
        self._build_toolbar()
        self._build_editors()
        self._build_output()

        self.bind("<Control-Return>", lambda _e: self._compare())
        self.bind("<Control-l>", lambda _e: self._clear())
        self.bind("<Control-q>", lambda _e: self.destroy())

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        bar = tk.Menu(self)

        file_menu = tk.Menu(bar, tearoff=False)
        file_menu.add_command(
            label="Compare", command=self._compare, accelerator="Ctrl+Enter"
        )
        file_menu.add_command(
            label="Clear All", command=self._clear, accelerator="Ctrl+L"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Quit", command=self.destroy, accelerator="Ctrl+Q"
        )
        bar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(bar, tearoff=False)
        help_menu.add_command(label="About promptdiff", command=self._show_about)
        bar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=bar)

    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self, padding=(6, 4))
        bar.grid(row=0, column=0, sticky="ew")

        ttk.Button(
            bar, text="Compare  (Ctrl+Enter)", command=self._compare
        ).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="Clear", command=self._clear).pack(side="left", padx=(0, 12))

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=6)

        self._sim_var = tk.StringVar(value="Similarity: —")
        ttk.Label(bar, textvariable=self._sim_var, font=self._bold).pack(side="left", padx=6)

    def _build_editors(self) -> None:
        pane = ttk.Frame(self, padding=(6, 2, 6, 2))
        pane.grid(row=1, column=0, sticky="nsew")
        pane.columnconfigure(0, weight=1)
        pane.columnconfigure(1, weight=1)
        pane.rowconfigure(1, weight=1)

        ttk.Label(pane, text="Prompt A", font=self._bold).grid(
            row=0, column=0, sticky="w", pady=(0, 2)
        )
        ttk.Label(pane, text="Prompt B", font=self._bold).grid(
            row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 2)
        )

        self._editor_a = _ScrolledText(
            pane, font=self._mono, wrap="word", undo=True, height=10, relief="flat",
            borderwidth=1, highlightthickness=1, highlightbackground="#ced4da"
        )
        self._editor_a.grid(row=1, column=0, sticky="nsew", padx=(0, 3))

        self._editor_b = _ScrolledText(
            pane, font=self._mono, wrap="word", undo=True, height=10, relief="flat",
            borderwidth=1, highlightthickness=1, highlightbackground="#ced4da"
        )
        self._editor_b.grid(row=1, column=1, sticky="nsew", padx=(3, 0))

    def _build_output(self) -> None:
        nb = ttk.Notebook(self, padding=(6, 0, 6, 6))
        nb.grid(row=2, column=0, sticky="nsew")

        # Tab 1 – structured diff
        f1 = ttk.Frame(nb)
        nb.add(f1, text="  Structured diff  ")
        f1.columnconfigure(0, weight=1)
        f1.rowconfigure(0, weight=1)
        self._struct = _ScrolledText(
            f1, font=self._mono, wrap="none", state="disabled",
            height=12, relief="flat", borderwidth=0
        )
        self._struct.grid(row=0, column=0, sticky="nsew")
        self._struct.text.tag_configure("add", background=_ADD_BG, foreground=_ADD_FG)
        self._struct.text.tag_configure("remove", background=_REMOVE_BG, foreground=_REMOVE_FG)
        self._struct.text.tag_configure("equal", foreground=_EQUAL_FG)

        # Tab 2 – unified diff
        f2 = ttk.Frame(nb)
        nb.add(f2, text="  Unified diff  ")
        f2.columnconfigure(0, weight=1)
        f2.rowconfigure(0, weight=1)
        self._unified = _ScrolledText(
            f2, font=self._mono, wrap="none", state="disabled",
            height=12, relief="flat", borderwidth=0
        )
        self._unified.grid(row=0, column=0, sticky="nsew")
        self._unified.text.tag_configure("add", background=_ADD_BG, foreground=_ADD_FG)
        self._unified.text.tag_configure("remove", background=_REMOVE_BG, foreground=_REMOVE_FG)
        self._unified.text.tag_configure("header", foreground=_HEADER_FG)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _compare(self) -> None:
        a = self._editor_a.text.get("1.0", "end-1c")
        b = self._editor_b.text.get("1.0", "end-1c")
        self._render_structured(a, b)
        self._render_unified(a, b)
        sim = similarity(a, b)
        self._sim_var.set(f"Similarity: {sim:.4f}")

    def _render_structured(self, a: str, b: str) -> None:
        widget = self._struct.text
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        for op, line in diff(a, b):
            prefix = "  " if op == "equal" else ("+ " if op == "add" else "- ")
            widget.insert("end", prefix + line, op)
            if not line.endswith("\n"):
                widget.insert("end", "\n", op)
        widget.configure(state="disabled")

    def _render_unified(self, a: str, b: str) -> None:
        widget = self._unified.text
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        for line in format_unified(a, b).splitlines(keepends=True):
            if line.startswith("+"):
                tag = "add"
            elif line.startswith("-"):
                tag = "remove"
            elif line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
                tag = "header"
            else:
                tag = ""
            widget.insert("end", line, tag)
        widget.configure(state="disabled")

    def _clear(self) -> None:
        for editor in (self._editor_a, self._editor_b):
            editor.text.delete("1.0", "end")
        for out in (self._struct, self._unified):
            out.text.configure(state="normal")
            out.text.delete("1.0", "end")
            out.text.configure(state="disabled")
        self._sim_var.set("Similarity: —")

    def _show_about(self) -> None:
        messagebox.showinfo("About promptdiff", _ABOUT_TEXT, parent=self)


def run() -> None:
    """Launch the promptdiff graphical interface."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run()
