"""promptdiff.gui – Tkinter-based graphical interface for promptdiff.

Launch from the command line::

    python -m promptdiff.gui
    # or, after installation:
    promptdiff-gui

Or call programmatically::

    from promptdiff.gui import run
    run()
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from promptdiff import __version__, diff, format_unified, similarity

# ── Colour palette (Catppuccin Mocha) ────────────────────────────────────────
_BG = "#1e1e2e"
_PANEL = "#181825"
_ENTRY = "#313244"
_FG = "#cdd6f4"
_ACCENT = "#89b4fa"
_ADD_BG = "#a6e3a1"
_ADD_FG = "#1e1e2e"
_REM_BG = "#f38ba8"
_REM_FG = "#1e1e2e"


class _ScrolledText(tk.Frame):
    """A tk.Text widget with attached vertical and horizontal scrollbars."""

    def __init__(self, master: tk.Widget, **text_kw: object) -> None:
        super().__init__(master, bg=_ENTRY)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.text = tk.Text(self, **text_kw)  # type: ignore[arg-type]
        sy = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        sx = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")


class PromptDiffApp(tk.Tk):
    """Main application window for the promptdiff GUI."""

    def __init__(self) -> None:
        super().__init__()
        self.title(f"promptdiff {__version__}")
        self.geometry("1100x720")
        self.minsize(800, 500)
        self.configure(bg=_BG)
        self._last_a: str = ""
        self._last_b: str = ""
        self._last_diff: list[tuple[str, str]] = []
        self._build_ui()
        # Keyboard shortcut: Ctrl+Return triggers compare
        self.bind_all("<Control-Return>", lambda _e: self._compare())

    # ----------------------------------------------------------------- layout

    def _build_ui(self) -> None:
        mono = tkfont.Font(family="Courier", size=11)
        hl_font = ("Helvetica", 11, "bold")

        # ── input pane (two side-by-side editors) ─────────────────────────
        input_pane = tk.Frame(self, bg=_BG)
        input_pane.pack(fill="both", expand=True, padx=12, pady=(12, 4))
        input_pane.columnconfigure(0, weight=1)
        input_pane.columnconfigure(1, weight=1)
        input_pane.rowconfigure(1, weight=1)

        for col, label in enumerate(("Prompt A  (original)", "Prompt B  (modified)")):
            tk.Label(
                input_pane, text=label, bg=_BG, fg=_ACCENT, font=hl_font,
            ).grid(row=0, column=col, sticky="w", padx=4, pady=(0, 3))

        editor_kw: dict[str, object] = dict(
            bg=_ENTRY, fg=_FG, font=mono, relief="flat",
            wrap="none", undo=True, insertbackground=_FG,
            padx=6, pady=4,
        )
        self._editor_a = _ScrolledText(input_pane, **editor_kw)
        self._editor_a.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        self._editor_b = _ScrolledText(input_pane, **editor_kw)
        self._editor_b.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        # ── control bar ────────────────────────────────────────────────────
        bar = tk.Frame(self, bg=_PANEL, pady=7)
        bar.pack(fill="x", padx=12, pady=2)

        tk.Button(
            bar, text="Compare  (Ctrl+↵)", command=self._compare,
            bg=_ACCENT, fg=_PANEL, font=hl_font,
            relief="flat", padx=14, pady=4, cursor="hand2",
            activebackground=_FG, activeforeground=_PANEL,
        ).pack(side="left", padx=(8, 4))

        tk.Button(
            bar, text="Clear", command=self._clear,
            bg=_ENTRY, fg=_FG, font=("Helvetica", 11),
            relief="flat", padx=14, pady=4, cursor="hand2",
            activebackground=_BG, activeforeground=_FG,
        ).pack(side="left", padx=4)

        self._sim_var = tk.StringVar(value="Similarity: —")
        tk.Label(
            bar, textvariable=self._sim_var, bg=_PANEL, fg=_FG,
            font=("Helvetica", 11),
        ).pack(side="right", padx=14)

        # ── view toggle ────────────────────────────────────────────────────
        view_bar = tk.Frame(self, bg=_BG)
        view_bar.pack(fill="x", padx=16, pady=(4, 0))

        self._view = tk.StringVar(value="line")
        for label, val in (("Line diff", "line"), ("Unified diff", "unified")):
            tk.Radiobutton(
                view_bar, text=label, variable=self._view, value=val,
                command=self._refresh_output,
                bg=_BG, fg=_FG, selectcolor=_PANEL,
                activebackground=_BG, activeforeground=_ACCENT,
                font=("Helvetica", 10),
            ).pack(side="left", padx=6)

        # ── output pane ────────────────────────────────────────────────────
        tk.Label(
            self, text="Diff Output", bg=_BG, fg=_ACCENT, font=hl_font,
        ).pack(anchor="w", padx=16, pady=(6, 2))

        self._output = _ScrolledText(
            self,
            bg=_ENTRY, fg=_FG, font=mono, relief="flat",
            wrap="none", state="disabled", insertbackground=_FG,
            padx=6, pady=4,
        )
        self._output.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for tag, kw in (
            ("add",    {"background": _ADD_BG, "foreground": _ADD_FG}),
            ("remove", {"background": _REM_BG, "foreground": _REM_FG}),
            ("equal",  {"foreground": _FG}),
            ("meta",   {"foreground": _ACCENT}),
        ):
            self._output.text.tag_configure(tag, **kw)  # type: ignore[arg-type]

    # ----------------------------------------------------------------- actions

    def _compare(self) -> None:
        self._last_a = self._editor_a.text.get("1.0", "end-1c")
        self._last_b = self._editor_b.text.get("1.0", "end-1c")
        self._last_diff = diff(self._last_a, self._last_b)
        sim = similarity(self._last_a, self._last_b)
        self._sim_var.set(f"Similarity: {sim:.3f}")
        self._refresh_output()

    def _clear(self) -> None:
        for editor in (self._editor_a, self._editor_b):
            editor.text.delete("1.0", "end")
        self._last_a = self._last_b = ""
        self._last_diff = []
        self._sim_var.set("Similarity: —")
        self._write_line_diff([])

    def _refresh_output(self) -> None:
        if self._view.get() == "unified":
            text = format_unified(self._last_a, self._last_b) or "(no differences)\n"
            self._write_unified(text)
        else:
            self._write_line_diff(self._last_diff)

    # ----------------------------------------------------------- rendering

    def _write_line_diff(self, items: list[tuple[str, str]]) -> None:
        t = self._output.text
        t.configure(state="normal")
        t.delete("1.0", "end")
        prefix_map = {"equal": "  ", "add": "+ ", "remove": "- "}
        for op, line in items:
            t.insert("end", prefix_map.get(op, "  ") + line, op)
        t.configure(state="disabled")

    def _write_unified(self, text: str) -> None:
        t = self._output.text
        t.configure(state="normal")
        t.delete("1.0", "end")
        for line in text.splitlines(keepends=True):
            if line.startswith("+") and not line.startswith("+++"):
                tag = "add"
            elif line.startswith("-") and not line.startswith("---"):
                tag = "remove"
            elif line.startswith(("@@", "---", "+++")):
                tag = "meta"
            else:
                tag = "equal"
            t.insert("end", line, tag)
        t.configure(state="disabled")


def run() -> None:
    """Launch the promptdiff GUI."""
    PromptDiffApp().mainloop()


if __name__ == "__main__":
    run()
