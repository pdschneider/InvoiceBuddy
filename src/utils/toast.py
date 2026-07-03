# src/utils/toast.py
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QCursor
import tkinter as tk
import src.utils.fonts as fonts
import logging


def _place_toast(root, toast):
    """Reposition toast at the bottom right of *root*."""
    root.update_idletasks()
    x = root.winfo_x() + root.winfo_width() - toast.winfo_reqwidth() - 20
    y = root.winfo_y() + root.winfo_height() - toast.winfo_reqheight() - 20
    toast.geometry(f"+{x}+{y}")


def show_toast(globals, message, duration=3000, _type=None):
    """Shows a toast notification at the bottom right of the screen."""
    
    if globals.legacy_mode:
        # Create the toast window
        toast = tk.Toplevel(globals.root)
        toast.overrideredirect(True)

        # Styling
        try:
            if _type == "error":
                background = "#8B0000"
            else:
                background = globals.theme_dict["CTkFrame"]["text_color"]
        except Exception:
            logging.warning("Theme lookup failed – using dark background")
            background = "#333333"
        toast.configure(bg=background)

        # Message label
        lbl = tk.Label(toast, text=message, fg="white", bg=background,
                    font=fonts.body_font, padx=10, pady=5)
        lbl.pack()

        # Initial placement
        _place_toast(globals.root, toast)

        # Keep the toast glued to the parent while it moves/resizes
        def on_parent_move(event):
            _place_toast(globals.root, toast)

        # bind() returns an identifier string – store it so we can unbind later
        bind_id = globals.root.bind("<Configure>", on_parent_move)

        # Handles auto-close
        after_id = None   # will hold the `after` timer id

        def close():
            # Cancel the pending after call if it hasn't fired yet
            if after_id is not None:
                toast.after_cancel(after_id)

            # Remove the configure binding using the stored id
            globals.root.unbind("<Configure>", bind_id)

            # Finally destroy the toast window
            toast.destroy()

        # Schedule the automatic close
        after_id = toast.after(duration, close)

        # Optional: allow manual click‑to‑dismiss
        toast.bind("<Button-1>", lambda e: close())

    else:
        if _type == "error":
            bg_color = "#8B0000"
        else:
            bg_color = "#1a5276"

        toast = QLabel(message, globals.window)
        toast.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        toast.setStyleSheet(f"""
            background-color: {bg_color}; color: white;
            padding: 12px 18px; border-radius: 8px; font-size: 15px; font-weight: bold;
        """)
        toast.adjustSize()

        # Position at bottom-right of main window
        win = globals.window
        x = win.x() + win.width() - toast.width() - 20
        y = win.y() + win.height() - toast.height() - 20
        toast.move(x, y)
        toast.show()
        toast.raise_()

        # Reposition toast as window moves
        timer = QTimer()
        def reposition():
            if toast.isVisible():
                x = win.x() + win.width() - toast.width() - 20
                y = win.y() + win.height() - toast.height() - 20
                toast.move(x, y)
                toast.raise_()
            else:
                timer.stop()
                toast.deleteLater()

        timer.timeout.connect(reposition)
        timer.start(16)

        QTimer.singleShot(duration, toast.close)
