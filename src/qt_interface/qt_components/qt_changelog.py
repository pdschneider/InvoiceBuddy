from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from src.interface.changelog import parse_changelog, markdown_to_plain
import logging


def create_changelog_panel(globals):
    """Creates the changelog overlay panel with phone-like dimensions."""

    changelog_panel = QWidget(globals.window)
    changelog_panel.setFixedSize(400, 650)
    changelog_panel.setStyleSheet("""
        background-color: rgb(43, 43, 43);
        border-radius: 10px;
    """)
    changelog_panel.hide()

    layout = QVBoxLayout(changelog_panel)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)

    # === HEADER ===
    header_layout = QHBoxLayout()
    title = QLabel("Changelog")
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
    header_layout.addWidget(title)
    header_layout.addStretch()

    close_header_btn = QPushButton("×")
    close_header_btn.setFixedSize(30, 30)
    close_header_btn.setStyleSheet("background-color: transparent; color: white; border: none; font-size: 18px;")
    close_header_btn.setCursor(QCursor(Qt.PointingHandCursor))
    close_header_btn.clicked.connect(lambda: toggle_changelog_panel(globals))
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

    # Load changelog entries
    try:
        for entry in parse_changelog():
            version_label = QLabel(f"{entry['version']}  —  {entry['date']}")
            version_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2ecc71; padding-top: 10px; padding-bottom: 5px;")
            content_layout.addWidget(version_label)

            for txt, _ in markdown_to_plain(entry["body_md"]):
                if txt:
                    line_label = QLabel(txt)
                    line_label.setStyleSheet("font-size: 13px; color: #ddd; padding: 2px 0;")
                    line_label.setWordWrap(True)
                    content_layout.addWidget(line_label)
    except Exception as e:
        logging.error(f"Failed to load changelog: {e}")
        err_label = QLabel(f"Could not load changelog: {e}")
        err_label.setStyleSheet("color: #ff5555;")
        content_layout.addWidget(err_label)

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
    close_btn.clicked.connect(lambda: toggle_changelog_panel(globals))
    layout.addWidget(close_btn)

    globals.changelog_panel = changelog_panel
    return changelog_panel


def toggle_changelog_panel(globals):
    """Shows or hides the changelog panel, centered on the window."""
    if globals.changelog_panel.isVisible():
        globals.changelog_panel.hide()
        globals.dim_overlay.hide()
    else:
        # Close any active settings panels first
        if hasattr(globals, 'settings_panel') and globals.settings_panel.isVisible():
            globals.settings_panel.hide()

        globals.dim_overlay.resize(globals.window.width(), globals.window.height() - 35)
        globals.dim_overlay.move(0, 35)
        globals.dim_overlay.show()
        globals.dim_overlay.raise_()

        parent_w = globals.window.width()
        parent_h = globals.window.height()
        panel_w = globals.changelog_panel.width()
        panel_h = globals.changelog_panel.height()

        x = (parent_w - panel_w) // 2
        y = (parent_h - panel_h) // 2

        globals.changelog_panel.move(x, y)
        globals.changelog_panel.show()
        globals.changelog_panel.raise_()
