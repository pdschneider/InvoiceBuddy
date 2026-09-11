# src/qt_interface/qt_preview.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout,
                               QLabel, QFrame,
                               QHBoxLayout, QPushButton,
                               QApplication)
from PySide6.QtCore import Qt
from pypdf import PdfReader
import os
from src.qt_interface.qt_components.qt_viewer import NativePdfViewer


METADATA_KEYS = {
    "/Date": "Date",
    "/Company": "Vendor",
    "/InvoiceNumber": "Inv #",
    "/CardNumber": "Card",
}


def read_file_metadata(filepath):
    """Reads auto-name metadata keys from a PDF, skipping missing ones."""
    fields = {}
    try:
        reader = PdfReader(filepath)
        if reader.metadata:
            for key, label in METADATA_KEYS.items():
                value = reader.metadata.get(key)
                if value:
                    fields[label] = str(value)
    except Exception:
        pass
    return fields


def create_pill(label, value):
    """Builds one clickable metadata pill."""
    pill = QPushButton(f"{label}: {value}")
    pill.setCursor(Qt.PointingHandCursor)
    pill.setToolTip(f"Click to copy {label}")
    pill.setStyleSheet("""
        QPushButton {
            background-color: #3a3a3f;
            color: white;
            border: 1px solid #555;
            border-radius: 12px;
            padding: 2px 10px;
            font-size: 11px;
        }
        QPushButton:hover {
            border-color: #2ecc71;
            color: #2ecc71;
        }
    """)
    pill.clicked.connect(lambda: QApplication.clipboard().setText(value))
    return pill


def create_preview_pane(globs):
    """Creates the right pane with PDF preview and action buttons."""

    pane = QWidget()
    layout = QVBoxLayout(pane)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(0)

    # Pill Bar
    pill_bar = QFrame()
    pill_bar.setFixedHeight(38)
    pill_bar.setStyleSheet("""
        QFrame {
            background-color: transparent;
            border: none;
        }
    """)
    pill_layout = QHBoxLayout(pill_bar)
    pill_layout.setContentsMargins(0, 0, 0, 0)
    pill_layout.addStretch()

    # placeholder label lives visually inside the bar for now (removed in step 2)
    layout.addWidget(pill_bar)

    # PDF preview
    pdf_viewer = NativePdfViewer()

    # Placeholder shown when there's nothing to preview
    placeholder = QLabel("Select a file to view preview")
    placeholder.setAlignment(Qt.AlignCenter)
    placeholder.setStyleSheet("""
        color: #888;
        font-size: 14px;
        font-style: italic;
        background-color: #2b2b2b;
        border-radius: 5px;
    """)

    # Stack them so they occupy the same space; only one is visible at a time
    from PySide6.QtWidgets import QStackedLayout
    stack = QStackedLayout()
    stack.setStackingMode(QStackedLayout.StackAll)
    stack.addWidget(pdf_viewer)
    stack.addWidget(placeholder)

    container = QWidget()
    container.setLayout(stack)
    layout.addWidget(container, stretch=1)

    # Store references
    globs.pdf_viewer = pdf_viewer
    globs.preview_placeholder = placeholder
    globs.pill_bar = pill_bar
    globs.pill_layout = pill_layout

    def update_preview_state():
        """Switches between placeholder messages and the PDF viewer."""
        files = getattr(globs, 'files', []) or []
        selected = getattr(globs, 'selected_file', None)

        # Clear old pills first — every path rebuilds (or leaves them gone)
        while pill_layout.count() > 1:  # keep the stretch at index 0
            item = pill_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        if not files:
            placeholder.setText("All caught up!")
            stack.setCurrentWidget(placeholder)
        elif selected:
            # Populate from metadata
            filepath = os.path.join(globs.current_folder, selected)
            for label, value in read_file_metadata(filepath).items():
                pill_layout.addWidget(create_pill(label, value))

            stack.setCurrentWidget(pdf_viewer)
        else:
            placeholder.setText("Select a file to view preview")
            stack.setCurrentWidget(placeholder)

    globs.update_preview_state = update_preview_state
    update_preview_state()

    return pane
