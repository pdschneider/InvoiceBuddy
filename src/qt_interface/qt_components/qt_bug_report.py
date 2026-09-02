# src/qt_interface/qt_components/qt_about.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QScrollArea,
                               QMessageBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor
from src.qt_interface.qt_styles import dark
import webbrowser
import logging
import urllib.parse


def create_report_panel(globs):
    """Creates a panel for bug reports."""

    report_panel = QWidget(globs.window)
    report_panel.setFixedSize(450, 250)
    report_panel.setStyleSheet("""
        background-color: rgb(43, 43, 43);
        border-radius: 10px;
    """)
    report_panel.hide()

    layout = QVBoxLayout(report_panel)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)

    # Header
    header_layout = QHBoxLayout()
    title = QLabel("Report a Bug")
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
    title.setAlignment(Qt.AlignCenter)
    header_layout.addWidget(title)

    layout.addLayout(header_layout)

    # Scrollable Area
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setStyleSheet(dark.scroll_area)

    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(10)

    scroll_area.setWidget(content_widget)
    layout.addWidget(scroll_area)

    # Description
    desc_label = QLabel(
        """Report a bug via GitHub Issues, Codeberg Issues, or Email"""
    )
    desc_label.setStyleSheet("font-size: 13px; color: #ddd; padding: 5px;")
    desc_label.setAlignment(Qt.AlignCenter)
    desc_label.setWordWrap(True)
    content_layout.addStretch()
    content_layout.addWidget(desc_label)

    layout.addLayout(content_layout)

    # Buttons Layout
    buttons_layout = QHBoxLayout()

    # GitHub
    github_btn = QPushButton()
    github_btn.setIcon(globs.github_icon)
    github_btn.setIconSize(QSize(40,40))
    github_btn.setStyleSheet(dark.social_button)
    github_btn.clicked.connect(lambda: webbrowser.open(
        url="https://github.com/pdschneider/InvoiceBuddy/issues"))
    github_btn.setToolTip("Report a bug on GitHub")
    buttons_layout.addWidget(github_btn)

    # Codeberg
    codeberg_btn = QPushButton()
    codeberg_btn.setIcon(globs.codeberg_icon)
    codeberg_btn.setIconSize(QSize(40,40))
    codeberg_btn.setStyleSheet(dark.social_button)
    codeberg_btn.setToolTip("Report a bug on Codeberg")
    codeberg_btn.clicked.connect(lambda: webbrowser.open(
            url="https://codeberg.org/pdschneider/InvoiceBuddy/issues/new/choose"))
    buttons_layout.addWidget(codeberg_btn)

    # Email
    mail_btn = QPushButton()
    mail_btn.setIcon(globs.mail_icon)
    mail_btn.setIconSize(QSize(40,40))
    mail_btn.setStyleSheet(dark.social_button)
    mail_btn.setToolTip("Report a bug via Email")
    mail_btn.clicked.connect(lambda: report_bug(globs))
    buttons_layout.addWidget(mail_btn)

    layout.addLayout(buttons_layout)

    # Close Button
    close_btn = QPushButton("Close")
    close_btn.setStyleSheet(dark.close_button)
    close_btn.setCursor(QCursor(Qt.PointingHandCursor))
    close_btn.clicked.connect(lambda: toggle_report_panel(globs))
    layout.addWidget(close_btn)

    globs.report_panel = report_panel
    return report_panel


def toggle_report_panel(globs):
    """Shows or hides the bug report panel, centered on the window."""
    if globs.report_panel.isVisible():
        globs.report_panel.hide()
        globs.dim_overlay.hide()
    else:
        if hasattr(globs, 'settings_panel') and globs.settings_panel.isVisible():
            globs.settings_panel.hide()
        if hasattr(globs, 'changelog_panel') and globs.changelog_panel.isVisible():
            globs.changelog_panel.hide()
        if hasattr(globs, 'about_panel') and globs.about_panel.isVisible():
            globs.about_panel.hide()
        if hasattr(globs, 'docs_panel') and globs.docs_panel.isVisible():
            globs.docs_panel.hide()

        tb_h = globs.title_bar.height()
        globs.dim_overlay.resize(globs.window.width(), globs.window.height() - tb_h)
        globs.dim_overlay.move(0, tb_h)
        globs.dim_overlay.show()
        globs.dim_overlay.raise_()

        parent_w = globs.window.width()
        parent_h = globs.window.height()
        panel_w = globs.report_panel.width()
        panel_h = globs.report_panel.height()

        x = (parent_w - panel_w) // 2
        y = (parent_h - panel_h) // 2
        globs.report_panel.move(x, y)
        globs.report_panel.show()
        globs.report_panel.raise_()


def report_bug(globs):
    """Opens the default mail application to report a bug."""

    # Display a messagebox first
    reply = QMessageBox.question(
        globs.window,
        "Report Bug?",
        f"Would you like to open your default email application for a bug report?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes)
    
    # Opens up the default email application
    if reply == QMessageBox.StandardButton.Yes:
        logging.debug(f"Bug Report button clicked.")
        to = "bugs@phillipplays.com"
        subject = "Bug Report for Invoice Buddy"
        body = f"Thank you very much for making a report! " \
        f"Let me know what problem occurred, the behavior your expected, " \
        f"and feel free to also include any logs or screenshots that may help! " \
        f" | Invoice Buddy Version: {globs.current_version} | OS: {globs.os_name}"
        encoded_body = urllib.parse.quote(body)
        mailto = f"mailto:{to}?subject={subject}&body={encoded_body}"
        webbrowser.open(mailto)
