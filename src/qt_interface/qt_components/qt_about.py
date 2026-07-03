from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
import webbrowser


def create_about_panel(globals):
    """Creates the about overlay panel."""

    about_panel = QWidget(globals.window)
    about_panel.setFixedSize(450, 550)
    about_panel.setStyleSheet("""
        background-color: rgb(43, 43, 43);
        border-radius: 10px;
    """)
    about_panel.hide()

    layout = QVBoxLayout(about_panel)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)

    # === HEADER ===
    header_layout = QHBoxLayout()
    title = QLabel("About")
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
    header_layout.addWidget(title)
    header_layout.addStretch()

    close_header_btn = QPushButton("×")
    close_header_btn.setFixedSize(30, 30)
    close_header_btn.setStyleSheet("background-color: transparent; color: white; border: none; font-size: 18px;")
    close_header_btn.setCursor(QCursor(Qt.PointingHandCursor))
    close_header_btn.clicked.connect(lambda: toggle_about_panel(globals))
    header_layout.addWidget(close_header_btn)

    layout.addLayout(header_layout)

    # === SCROLLABLE CONTENT ===
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setStyleSheet("""
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        QScrollBar:vertical {
            background-color: #333;
            width: 8px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background-color: #4a4a4a;
            min-height: 50px;
            border-radius: 4px;
        }
    """)

    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(10)

    # === ABOUT TEXT ===
    desc_label = QLabel(
        "Invoice Buddy is your helper to automate the invoice entry process.\n\n"
        "The program does three things:\n\n"
        "1) Automatically detects invoice data from each file and writes it to the filename.\n"
        "2) Writes that data to a spreadsheet.\n"
        "3) Moves processed files to their proper folder for archival.\n\n"
        "Files are separated into three categories: Invoices, Credit Card Receipts, and Purchase Orders.\n\n"
        "Always look over generated content to ensure its accuracy before continuing.\n\n"
        "On Windows, Invoice Buddy comes bundled with: Poppler (MIT), Tesseract (Apache 2.0)"
    )
    desc_label.setStyleSheet("font-size: 13px; color: #ddd; padding: 5px;")
    desc_label.setWordWrap(True)
    content_layout.addWidget(desc_label)

    # Version
    version_label = QLabel(f"Current Version: {globals.current_version}")
    version_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2ecc71; padding-top: 10px;")
    version_label.setAlignment(Qt.AlignCenter)
    content_layout.addWidget(version_label)

    content_layout.addStretch()
    scroll_area.setWidget(content_widget)
    layout.addWidget(scroll_area, stretch=1)

    # === CLOSE BUTTON ===
    close_btn = QPushButton("Close")
    close_btn.setStyleSheet("""
        QPushButton {
            background-color: #3a3a3a;
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
    """)
    close_btn.setCursor(QCursor(Qt.PointingHandCursor))
    close_btn.clicked.connect(lambda: toggle_about_panel(globals))
    layout.addWidget(close_btn)

    globals.about_panel = about_panel
    return about_panel


def toggle_about_panel(globals):
    """Shows or hides the about panel, centered on the window."""
    if globals.about_panel.isVisible():
        globals.about_panel.hide()
        globals.dim_overlay.hide()
    else:
        if hasattr(globals, 'settings_panel') and globals.settings_panel.isVisible():
            globals.settings_panel.hide()
        if hasattr(globals, 'changelog_panel') and globals.changelog_panel.isVisible():
            globals.changelog_panel.hide()

        globals.dim_overlay.resize(globals.window.width(), globals.window.height() - 35)
        globals.dim_overlay.move(0, 35)
        globals.dim_overlay.show()
        globals.dim_overlay.raise_()

        parent_w = globals.window.width()
        parent_h = globals.window.height()
        panel_w = globals.about_panel.width()
        panel_h = globals.about_panel.height()

        x = (parent_w - panel_w) // 2
        y = (parent_h - panel_h) // 2
        globals.about_panel.move(x, y)
        globals.about_panel.show()
        globals.about_panel.raise_()
