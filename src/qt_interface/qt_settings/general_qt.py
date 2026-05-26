# src/qt_interface/qt_settings/general_qt.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox
from PySide6.QtCore import Qt


def create_general_settings_tab(globals):
    """
    Create the General Settings tab for Qt interface.
    Returns a QWidget that can be added directly to the tab widget.
    """

    # Create the main widget that will BE the tab
    tab_widget = QWidget()
    layout = QVBoxLayout(tab_widget)
    layout.setContentsMargins(20, 20, 20, 20)  # More padding
    layout.setSpacing(20)  # More space between elements
    layout.setAlignment(Qt.AlignTop)  # Align everything to top

    # Title
    title = QLabel("General Settings")
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
    layout.addWidget(title)

    # Checkbox for "Check for Updates"
    github_check_checkbox = QCheckBox("Check for Updates on Startup")
    github_check_checkbox.setStyleSheet("color: white; font-size: 14px; margin-left: 10px;")

    # Set the checkbox state from existing globals.github_check
    github_check_checkbox.setChecked(globals.github_check)

    layout.addWidget(github_check_checkbox)

    # Add some spacer at the bottom so it doesn't hug the edge
    layout.addStretch()

    # Store reference for later use in save function
    globals.github_check_checkbox = github_check_checkbox

    return tab_widget
