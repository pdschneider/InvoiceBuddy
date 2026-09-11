# src/utils/toast.py
from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import QTimer, Qt
import tkinter as tk
import src.utils.fonts as fonts
import logging


def _place_toast(root, toast):
    """Reposition toast at the bottom right of *root*."""
    root.update_idletasks()
    x = root.winfo_x() + root.winfo_width() - toast.winfo_reqwidth() - 20
    y = root.winfo_y() + root.winfo_height() - toast.winfo_reqheight() - 20
    toast.geometry(f"+{x}+{y}")


class ToastQueue:
    """Serializes toasts and ignores duplicate messages."""

    def __init__(self):
        self.pending = []
        self.active_msg = None

    def submit(self, globs, message, duration, _type):
        if message == self.active_msg:
            return  # Same message already on screen
        if any(msg == message for msg, _, _ in self.pending):
            return  # Same message already waiting
        self.pending.append((message, duration, _type))
        if self.active_msg is None:
            self._show_next(globs)

    def _show_next(self, globs):
        if not self.pending:
            self.active_msg = None
            return
        message, duration, _type = self.pending.pop(0)
        self.active_msg = message
        _display_toast(globs, message, duration, _type,
                       on_finished=lambda: self._finished(globs))

    def _finished(self, globs):
        self.active_msg = None
        self._show_next(globs)


_toast_queue = ToastQueue()


def _display_toast(globs, message, duration, _type, on_finished):
    """Spawns one toast widget; calls on_finished when it closes."""
    if _type == "error":
        bg_color, border_color = "#6b1f24", "#e74c3c"
    else:
        bg_color, border_color = "#3a3a3f", "#666"

    # Translucent top-level window (transparent canvas)
    toast = QWidget(globs.window)
    toast.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
    toast.setAttribute(Qt.WA_TranslucentBackground)

    # The styled box is a CHILD widget, not the window itself
    label = QLabel(message, toast)
    label.setStyleSheet(f"""
        background-color: {bg_color}; color: white;
        padding: 6px 16px; border: 1px solid {border_color};
        border-radius: 15px; font-size: 14px;
    """)

    # Size the window to the label
    label.adjustSize()
    toast.resize(label.size())

    win = globs.window
    x = win.x() + win.width() - toast.width() - 20
    y = win.y() + win.height() - toast.height() - 20
    toast.move(x, y)
    toast.show()
    toast.raise_()

    timer = QTimer()
    def reposition():
        if toast.isVisible():
            x = win.x() + win.width() - toast.width() - 20
            y = win.y() + win.height() - toast.height() - 20
            toast.move(x, y)
            toast.raise_()
        else:
            timer.stop()
    timer.timeout.connect(reposition)
    timer.start(16)

    def close():
        timer.stop()
        toast.close()
        toast.deleteLater()
        on_finished()

    QTimer.singleShot(duration, close)


def show_toast(globs, message, duration=3000, _type=None):
    """Shows a toast notification at the bottom right of the screen."""

    if globs.legacy_mode:
        # Create the toast window
        toast = tk.Toplevel(globs.root)
        toast.overrideredirect(True)

        # Styling
        try:
            if _type == "error":
                background = "#8B0000"
            else:
                background = globs.theme_dict["CTkFrame"]["text_color"]
        except Exception:
            logging.warning("Theme lookup failed – using dark background")
            background = "#333333"
        toast.configure(bg=background)

        # Message label
        lbl = tk.Label(toast, text=message, fg="white", bg=background,
                    font=fonts.body_font, padx=10, pady=5)
        lbl.pack()

        # Initial placement
        _place_toast(globs.root, toast)

        # Keep the toast glued to the parent while it moves/resizes
        def on_parent_move(event):
            _place_toast(globs.root, toast)

        # bind() returns an identifier string – store it so we can unbind later
        bind_id = globs.root.bind("<Configure>", on_parent_move)

        # Handles auto-close
        after_id = None   # will hold the `after` timer id

        def close():
            # Cancel the pending after call if it hasn't fired yet
            if after_id is not None:
                toast.after_cancel(after_id)

            # Remove the configure binding using the stored id
            globs.root.unbind("<Configure>", bind_id)

            # Finally destroy the toast window
            toast.destroy()

        # Schedule the automatic close
        after_id = toast.after(duration, close)

        # Optional: allow manual click‑to‑dismiss
        toast.bind("<Button-1>", lambda e: close())

    else:
        _toast_queue.submit(globs, message, duration, _type)
