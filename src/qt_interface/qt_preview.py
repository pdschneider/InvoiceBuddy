# src/qt_interface/qt_preview.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QHBoxLayout, QPushButton, QApplication,
    QScrollArea
)
from PySide6.QtCore import Qt
from pypdf import PdfReader
import os
from src.qt_interface.qt_components.qt_viewer import NativePdfViewer


METADATA_KEYS = {
    "/Counterparty": "Counterparty",
    "/Date": "Date",
    "/Amount": "Amount",
    "/Category": "Category",
    "/Subcategory": "Subcategory",
    "/Description": "Description",
    "/CardNumber": "Card Number",
    "/InvoiceNumber": "Invoice Number",
    "/Net": "Terms (Net)",
    "/Tax": "Tax",
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


def create_pill(label, value, display=None, is_copy_all=False):
    """Builds one clickable metadata pill."""
    pill = QPushButton(display or value)
    pill.setCursor(Qt.PointingHandCursor)
    pill.setToolTip(f"{label} — click to copy '{value}'")

    # Metadata pill styling
    pill.setStyleSheet("""
        QPushButton {
            background-color: #404045;
            color: #dddddd;
            border: 1px solid #505055;
            border-radius: 16px;
            padding: 4px 14px;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #4a4a50;
            color: #2ecc71;
            border-color: #2ecc71;
        }
        QPushButton:pressed {
            background-color: #35353a;
        }
        QToolTip {
            background-color: #2b2b2b;
            color: #dddddd;
            border: 1px solid #505055;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
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

    # Pill Bar with scroll arrows
    pill_bar = QWidget()
    pill_bar.setFixedHeight(38)

    arrow_style = """
        QPushButton {
            background-color: #404045; color: #dddddd;
            border: 1px solid #505055; border-radius: 5px;
            padding: 4px 8px; font-size: 12px;
        }
        QPushButton:hover { color: #2ecc71; border-color: #2ecc71; }
        QPushButton:disabled { color: #555; border-color: #404045; }
    """
    pill_back_btn = QPushButton("<")
    pill_fwd_btn = QPushButton(">")
    for btn in (pill_back_btn, pill_fwd_btn):
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(arrow_style)
        btn.hide()

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setFixedHeight(34)

    pill_container = QWidget()
    pill_layout = QHBoxLayout(pill_container)
    pill_layout.setContentsMargins(0, 0, 0, 0)
    pill_layout.setSpacing(6)
    pill_layout.addStretch()
    scroll.setWidget(pill_container)

    def scroll_pills(delta):
        bar = scroll.horizontalScrollBar()
        bar.setValue(bar.value() + delta)

    def update_arrow_visibility():
        needed = scroll.horizontalScrollBar().maximum() > 0
        pill_back_btn.setVisible(needed)
        pill_fwd_btn.setVisible(needed)

    pill_back_btn.clicked.connect(lambda: scroll_pills(-120))
    pill_fwd_btn.clicked.connect(lambda: scroll_pills(120))
    scroll.horizontalScrollBar().rangeChanged.connect(
        lambda *_: update_arrow_visibility())

    bar_layout = QHBoxLayout(pill_bar)
    bar_layout.setContentsMargins(0, 0, 0, 0)
    bar_layout.setSpacing(4)
    bar_layout.addWidget(pill_back_btn)
    bar_layout.addWidget(scroll, stretch=1)
    bar_layout.addWidget(pill_fwd_btn)

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
            fields = read_file_metadata(filepath)
            
            # Determine column order from sheet config
            sheet_name = globs.file_identity.get(selected, "Sheet")
            sheet_config = next(
                (s for s in globs.sheet_data.get("sheets", []) if s.get("name") == sheet_name),
                None
            )
            column_order = sheet_config.get("column_order", []) if sheet_config else []

            # Map column_order labels to METADATA_KEYS display labels
            label_mapping = {
                "Company": "Counterparty",
                "Date": "Date",
                "Invoice #": "Invoice Number",
                "Card Number": "Card Number",
                "Amount": "Amount",
                "Category": "Category",
                "Subcategory": "Subcategory",
                "Description": "Description",
                "Terms (Net)": "Terms (Net)",
                "Tax": "Tax",
            }

            # Build ordered list of (display_label, value) tuples
            ordered_fields = []
            for col in column_order:
                if not col:  # Skip empty placeholders
                    continue
                # Look up the field label from the mapping
                field_label = label_mapping.get(col, col)
                if field_label in fields:
                    ordered_fields.append((col, fields[field_label]))

            # Render ordered pills
            for label, value in ordered_fields:
                pill_layout.addWidget(create_pill(label, value))

            stack.setCurrentWidget(pdf_viewer)
        else:
            placeholder.setText("Select a file to view preview")
            stack.setCurrentWidget(placeholder)

    globs.update_preview_state = update_preview_state
    update_preview_state()

    return pane
