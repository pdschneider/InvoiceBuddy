# src/qt_interface/qt_settings/qt_advanced.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox)
from PySide6.QtCore import Qt


def create_advanced_settings_tab(globs):
    """
    Create the General Settings tab for Qt interface.
    Returns a QWidget that can be added directly to the tab widget.
    """

    # Create the main widget that will BE the tab
    tab_widget = QWidget()
    tab_widget.setStyleSheet("color: #d0d0d0;")
    layout = QVBoxLayout(tab_widget)
    layout.setContentsMargins(20, 20, 20, 20)  # More padding
    layout.setSpacing(20)  # More space between elements
    layout.setAlignment(Qt.AlignTop)  # Align everything to top

    # Title
    title = QLabel("Advanced Settings")
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
    layout.addWidget(title)

    # Logging Level
    logging_levels = ["Debug", "Info", "Warning", "Error", "Critical"]
    globs.logging_level_box = QComboBox()
    globs.logging_level_box.addItems(logging_levels)
    globs.logging_level_box.setFixedWidth(100)
    globs.logging_level_box.setCurrentText(globs.logging_level.capitalize())

    layout.addWidget(globs.logging_level_box)

    # Add some spacer at the bottom so it doesn't hug the edge
    layout.addStretch()

    return tab_widget
