# src/qt_interface/qt_components/qt_changelog.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from src.interface.changelog import parse_changelog, markdown_to_plain
from src.qt_interface.qt_styles import dark
import logging


def create_changelog_panel(globs):
    """Creates the changelog overlay panel with phone-like dimensions."""

    changelog_panel = QWidget(globs.window)
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
    close_header_btn.clicked.connect(lambda: toggle_changelog_panel(globs))
    header_layout.addWidget(close_header_btn)

    layout.addLayout(header_layout)

    # Scrollable Area
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setStyleSheet(dark.scroll_area)

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

    # Close Button
    close_btn = QPushButton("Close")
    close_btn.setStyleSheet(dark.close_button)
    close_btn.setCursor(QCursor(Qt.PointingHandCursor))
    close_btn.clicked.connect(lambda: toggle_changelog_panel(globs))
    layout.addWidget(close_btn)

    globs.changelog_panel = changelog_panel
    return changelog_panel


def toggle_changelog_panel(globs):
    """Shows or hides the changelog panel, centered on the window."""
    if globs.changelog_panel.isVisible():
        globs.changelog_panel.hide()
        globs.dim_overlay.hide()
    else:
        # Close any active panels first
        if hasattr(globs, 'settings_panel') and globs.settings_panel.isVisible():
            globs.settings_panel.hide()
        if hasattr(globs, 'about_panel') and globs.about_panel.isVisible():
            globs.about_panel.hide()
        if hasattr(globs, 'report_panel') and globs.report_panel.isVisible():
            globs.report_panel.hide()
        if hasattr(globs, 'docs_panel') and globs.docs_panel.isVisible():
            globs.docs_panel.hide()

        tb_h = globs.title_bar.height()
        globs.dim_overlay.resize(globs.window.width(), globs.window.height() - tb_h)
        globs.dim_overlay.move(0, tb_h)
        globs.dim_overlay.show()
        globs.dim_overlay.raise_()

        parent_w = globs.window.width()
        parent_h = globs.window.height()
        panel_w = globs.changelog_panel.width()
        panel_h = globs.changelog_panel.height()

        x = (parent_w - panel_w) // 2
        y = (parent_h - panel_h) // 2

        globs.changelog_panel.move(x, y)
        globs.changelog_panel.show()
        globs.changelog_panel.raise_()
