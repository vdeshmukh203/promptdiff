"""promptdiff GUI - interactive side-by-side prompt comparison."""

from __future__ import annotations

try:
    import tkinter as tk
    from tkinter import font as tkfont
    from tkinter import ttk
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The promptdiff GUI requires Tk.  "
        "Install it with: sudo apt install python3-tk  (Debian/Ubuntu)"
    ) from exc

from promptdiff import format_unified, similarity


def run_gui() -> None:  # pragma: no cover
    """Launch the promptdiff graphical interface."""
    root = tk.Tk()
    _PromptDiffApp(root)
    root.mainloop()


class _PromptDiffApp:
    """Main application window."""

    _ADD_BG = "#ccffcc"
    _ADD_FG = "#004400"
    _DEL_BG = "#ffcccc"
    _DEL_FG = "#550000"
    _HUNK_FG = "#0044aa"

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._root.title("promptdiff")
        self._root.minsize(900, 640)
        self._build()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build(self) -> None:
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        self._root.rowconfigure(1, weight=0)
        self._root.rowconfigure(2, weight=1)

        self._build_inputs()
        self._build_controls()
        self._build_output()

    def _build_inputs(self) -> None:
        frame = ttk.LabelFrame(self._root, text="Prompts", padding=6)
        frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Prompt A  (original)").grid(
            row=0, column=0, sticky="w", pady=(0, 2)
        )
        ttk.Label(frame, text="Prompt B  (revised)").grid(
            row=0, column=1, sticky="w", padx=(8, 0), pady=(0, 2)
        )

        self._text_a = _scrolled_text(frame, height=9)
        self._text_a.grid(row=1, column=0, sticky="nsew")

        self._text_b = _scrolled_text(frame, height=9)
        self._text_b.grid(row=1, column=1, sticky="nsew", padx=(8, 0))

    def _build_controls(self) -> None:
        frame = ttk.Frame(self._root, padding=(8, 2))
        frame.grid(row=1, column=0, sticky="ew")

        ttk.Button(frame, text="Compare", command=self._compare).pack(side=tk.LEFT)
        ttk.Button(frame, text="Clear", command=self._clear).pack(
            side=tk.LEFT, padx=(6, 0)
        )

        self._sim_var = tk.StringVar(value="Similarity: —")
        ttk.Label(frame, textvariable=self._sim_var, foreground="#333333").pack(
            side=tk.LEFT, padx=16
        )

        self._stats_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self._stats_var, foreground="#555555").pack(
            side=tk.LEFT
        )

    def _build_output(self) -> None:
        frame = ttk.LabelFrame(self._root, text="Unified diff", padding=6)
        frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=(4, 8))
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        mono = tkfont.Font(family="Courier", size=10)
        self._out = tk.Text(
            frame,
            wrap=tk.NONE,
            font=mono,
            state=tk.DISABLED,
            background="#fafafa",
        )
        self._out.grid(row=0, column=0, sticky="nsew")

        ys = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self._out.yview)
        ys.grid(row=0, column=1, sticky="ns")
        xs = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self._out.xview)
        xs.grid(row=1, column=0, sticky="ew")
        self._out.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)

        self._out.tag_configure("add", background=self._ADD_BG, foreground=self._ADD_FG)
        self._out.tag_configure("del", background=self._DEL_BG, foreground=self._DEL_FG)
        self._out.tag_configure("hunk", foreground=self._HUNK_FG)
        self._out.tag_configure("header", foreground="#666666")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _compare(self) -> None:
        a = self._text_a.get("1.0", tk.END).rstrip("\n")
        b = self._text_b.get("1.0", tk.END).rstrip("\n")

        score = similarity(a, b)
        self._sim_var.set(f"Similarity: {score:.4f}")

        unified = format_unified(a, b)

        added = sum(1 for ln in unified.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
        removed = sum(1 for ln in unified.splitlines() if ln.startswith("-") and not ln.startswith("---"))
        if unified:
            self._stats_var.set(f"+{added} / -{removed} lines")
        else:
            self._stats_var.set("")

        self._out.configure(state=tk.NORMAL)
        self._out.delete("1.0", tk.END)

        if not unified:
            self._out.insert(tk.END, "(no differences — prompts are identical)\n")
        else:
            for line in unified.splitlines(keepends=True):
                if line.startswith("+") and not line.startswith("+++"):
                    self._out.insert(tk.END, line, "add")
                elif line.startswith("-") and not line.startswith("---"):
                    self._out.insert(tk.END, line, "del")
                elif line.startswith("@@"):
                    self._out.insert(tk.END, line, "hunk")
                elif line.startswith(("---", "+++")):
                    self._out.insert(tk.END, line, "header")
                else:
                    self._out.insert(tk.END, line)

        self._out.configure(state=tk.DISABLED)

    def _clear(self) -> None:
        for widget in (self._text_a, self._text_b):
            widget.delete("1.0", tk.END)
        self._out.configure(state=tk.NORMAL)
        self._out.delete("1.0", tk.END)
        self._out.configure(state=tk.DISABLED)
        self._sim_var.set("Similarity: —")
        self._stats_var.set("")


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _scrolled_text(parent: ttk.Frame, **kwargs: object) -> tk.Text:
    """Return a Text widget with a vertical scrollbar packed into *parent*."""
    container = ttk.Frame(parent)
    container.grid_propagate(True)

    text = tk.Text(container, wrap=tk.WORD, **kwargs)  # type: ignore[arg-type]
    ys = ttk.Scrollbar(container, orient=tk.VERTICAL, command=text.yview)
    text.configure(yscrollcommand=ys.set)

    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    ys.pack(side=tk.RIGHT, fill=tk.Y)

    # Expose the container's grid method on the text widget so callers can
    # call text.grid(...) and the whole container (text + scrollbar) moves.
    text.grid = container.grid  # type: ignore[method-assign]
    return text
