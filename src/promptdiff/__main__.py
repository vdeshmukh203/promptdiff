"""Entry point for ``python -m promptdiff``.

Launches the Tkinter graphical interface.  If a display is unavailable the
error from Tkinter is surfaced directly with a helpful hint.
"""

from __future__ import annotations


def main() -> None:
    try:
        from promptdiff.gui import main as _gui_main
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            f"Cannot start GUI: {exc}\n"
            "Ensure Tkinter is installed (e.g. 'apt install python3-tk')."
        ) from exc
    _gui_main()


if __name__ == "__main__":
    main()
