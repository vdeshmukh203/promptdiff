"""Tkinter-based GUI for promptdiff.

Launch with::

    python -m promptdiff

or programmatically::

    from promptdiff.gui import main
    main()
"""

from __future__ import annotations

import tkinter as tk
from tkinter import scrolledtext

from promptdiff import diff, format_unified, similarity

# ── palette ───────────────────────────────────────────────────────────────────
_BG_DARK = "#1e1e2e"
_BG_PANEL = "#2a2a3e"
_FG = "#cdd6f4"
_GREEN_FG = "#a6e3a1"
_GREEN_BG = "#1a2f22"
_RED_FG = "#f38ba8"
_RED_BG = "#2f1a1e"
_YELLOW = "#f9e2af"
_BLUE = "#89b4fa"
_BUTTON_BG = "#45475a"
_BUTTON_ACTIVE = "#585b70"
_MONO = "Courier"
_SANS = "TkDefaultFont"


class PromptDiffApp(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("promptdiff")
        self.geometry("1200x780")
        self.minsize(800, 560)
        self.configure(bg=_BG_DARK)
        self._build_ui()

    # ── widget helpers ────────────────────────────────────────────────────────

    def _label(self, parent: tk.Widget, text: str) -> tk.Label:
        return tk.Label(
            parent,
            text=text,
            bg=_BG_DARK,
            fg=_BLUE,
            font=(_SANS, 11, "bold"),
            anchor="w",
        )

    def _text(self, parent: tk.Widget, editable: bool = True) -> scrolledtext.ScrolledText:
        w = scrolledtext.ScrolledText(
            parent,
            bg=_BG_PANEL,
            fg=_FG,
            insertbackground=_FG,
            selectbackground=_BUTTON_BG,
            font=(_MONO, 11),
            relief=tk.FLAT,
            borderwidth=0,
            wrap=tk.NONE,
            undo=editable,
        )
        if not editable:
            w.configure(state=tk.DISABLED)
        return w

    def _button(self, parent: tk.Widget, text: str, command) -> tk.Button:  # type: ignore[type-arg]
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=_BUTTON_BG,
            fg=_FG,
            activebackground=_BUTTON_ACTIVE,
            activeforeground=_FG,
            relief=tk.FLAT,
            padx=18,
            pady=7,
            cursor="hand2",
            font=(_SANS, 10),
        )

    # ── layout ────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # ── input pane ────────────────────────────────────────────────────
        input_frame = tk.Frame(self, bg=_BG_DARK)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 4))

        left = tk.Frame(input_frame, bg=_BG_DARK)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        self._label(left, "Prompt A  (original)").pack(anchor="w", pady=(0, 2))
        self.text_a = self._text(left)
        self.text_a.pack(fill=tk.BOTH, expand=True)

        right = tk.Frame(input_frame, bg=_BG_DARK)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        self._label(right, "Prompt B  (revised)").pack(anchor="w", pady=(0, 2))
        self.text_b = self._text(right)
        self.text_b.pack(fill=tk.BOTH, expand=True)

        # ── controls ──────────────────────────────────────────────────────
        ctrl = tk.Frame(self, bg=_BG_DARK)
        ctrl.pack(fill=tk.X, padx=12, pady=6)

        self._button(ctrl, "Compare  (Ctrl+Return)", self._on_compare).pack(side=tk.LEFT)
        self._button(ctrl, "Clear", self._on_clear).pack(side=tk.LEFT, padx=(8, 0))

        self._score_var = tk.StringVar(value="Similarity: —")
        tk.Label(
            ctrl,
            textvariable=self._score_var,
            bg=_BG_DARK,
            fg=_YELLOW,
            font=(_MONO, 11),
        ).pack(side=tk.LEFT, padx=(20, 0))

        # ── diff output ───────────────────────────────────────────────────
        out_frame = tk.Frame(self, bg=_BG_DARK)
        out_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self._label(out_frame, "Diff output").pack(anchor="w", pady=(0, 2))
        self.diff_out = self._text(out_frame, editable=False)
        self.diff_out.pack(fill=tk.BOTH, expand=True)
        self.diff_out.tag_configure("add", foreground=_GREEN_FG, background=_GREEN_BG)
        self.diff_out.tag_configure("remove", foreground=_RED_FG, background=_RED_BG)
        self.diff_out.tag_configure("equal", foreground=_FG)
        self.diff_out.tag_configure("header", foreground=_BLUE)
        self.diff_out.tag_configure("meta", foreground=_YELLOW)

        # keyboard shortcut
        for w in (self.text_a, self.text_b):
            w.bind("<Control-Return>", lambda _e: self._on_compare())

    # ── event handlers ────────────────────────────────────────────────────────

    def _on_compare(self) -> None:
        a = self.text_a.get("1.0", tk.END).rstrip("\n")
        b = self.text_b.get("1.0", tk.END).rstrip("\n")

        score = similarity(a, b)
        self._score_var.set(f"Similarity: {score:.4f}")

        unified = format_unified(a, b)

        self.diff_out.configure(state=tk.NORMAL)
        self.diff_out.delete("1.0", tk.END)

        if not unified:
            self.diff_out.insert(tk.END, "(no differences — prompts are identical)\n", "equal")
        else:
            for line in unified.splitlines(keepends=True):
                if line.startswith("--- ") or line.startswith("+++ "):
                    tag = "header"
                elif line.startswith("@@"):
                    tag = "meta"
                elif line.startswith("+"):
                    tag = "add"
                elif line.startswith("-"):
                    tag = "remove"
                else:
                    tag = "equal"
                self.diff_out.insert(tk.END, line, tag)

        self.diff_out.configure(state=tk.DISABLED)

    def _on_clear(self) -> None:
        self.text_a.delete("1.0", tk.END)
        self.text_b.delete("1.0", tk.END)
        self.diff_out.configure(state=tk.NORMAL)
        self.diff_out.delete("1.0", tk.END)
        self.diff_out.configure(state=tk.DISABLED)
        self._score_var.set("Similarity: —")


def main() -> None:
    """Launch the promptdiff graphical interface."""
    app = PromptDiffApp()
    app.mainloop()


if __name__ == "__main__":
    main()
