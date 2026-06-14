# src/qt_interface/qt_settings/qt_advanced.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                               QCheckBox, QComboBox, QSlider,
                               QHBoxLayout)
from PySide6.QtCore import Qt
import logging


def create_spreadsheet_settings_tab(globals):
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
    title = QLabel("Spreadsheet Settings")
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
    layout.addWidget(title)

    # Slider Layout
    slider_layout = QHBoxLayout()

    # Spreadsheet Labels
    local_label = QLabel()
    local_label.setText("Local Spreadsheet")

    google_label = QLabel()
    google_label.setText("Google Sheets")

    # Slider
    globals.spreadsheet_toggle = QSlider()
    globals.spreadsheet_toggle.setRange(0, 1)
    globals.spreadsheet_toggle.setOrientation(Qt.Horizontal)
    globals.spreadsheet_toggle.setFixedWidth(100)
    globals.spreadsheet_toggle.valueChanged.connect(lambda: change_label())
    
    slider_layout.addWidget(local_label, alignment=Qt.AlignLeft)
    slider_layout.addWidget(globals.spreadsheet_toggle, alignment=Qt.AlignCenter)
    slider_layout.addWidget(google_label, alignment=Qt.AlignRight)
    layout.addLayout(slider_layout)

    # Highlight Text Based on Slider Position
    def change_label():
        """Changes the text color dependong on where the slider is."""
        if not globals.spreadsheet_toggle.value():
            local_label.setStyleSheet("color:white;")
            google_label.setStyleSheet("color:black;")
        else:
            local_label.setStyleSheet("color:black;")
            google_label.setStyleSheet("color:white;")
    
    # Set initial label color
    change_label()

    # Add some spacer at the bottom so it doesn't hug the edge
    layout.addStretch()

    return tab_widget
