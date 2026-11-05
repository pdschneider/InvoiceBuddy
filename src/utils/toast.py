# src/utils/toast.py
from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import QTimer, Qt


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
    _toast_queue.submit(globs, message, duration, _type)
