# src/qt_interface/qt_preview.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout,
                               QLabel, QFrame)
from src.qt_interface.qt_components.qt_viewer import NativePdfViewer


def create_preview_pane(globs):
    """Creates the right pane with PDF preview and action buttons."""

    pane = QWidget()
    layout = QVBoxLayout(pane)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)

    # === METADATA EDITOR (Top) ===
    meta_frame = QFrame()
    meta_frame.setStyleSheet("background-color: #333; border-radius: 5px;")
    meta_layout = QVBoxLayout(meta_frame)
    meta_layout.setContentsMargins(10, 10, 10, 10)

    meta_title = QLabel("Select a file to view details")
    meta_title.setStyleSheet("color: #aaa; font-style: italic;")
    meta_layout.addWidget(meta_title)

    layout.addWidget(meta_frame)

    # === PDF PREVIEW (Middle) ===
    # Create the native viewer instance
    pdf_viewer = NativePdfViewer()

    # Add it to the layout, stretching it to fill available space
    layout.addWidget(pdf_viewer, stretch=1)

    # Store reference in globs so the Mailbox can access it later
    globs.pdf_viewer = pdf_viewer

    # Store references
    globs.preview_meta = meta_title

    return pane
