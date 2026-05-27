# src/qt_interface/qt_settings/general_qt.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QComboBox
from PySide6.QtCore import Qt
from src.managers.printers import query_printers
import logging


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

    # Check for Updates
    github_check_checkbox = QCheckBox("Check for Updates on Startup")
    github_check_checkbox.setStyleSheet("color: white; font-size: 14px; margin-left: 10px;")
    github_check_checkbox.setChecked(globals.github_check)
    layout.addWidget(github_check_checkbox)

    # Beta Updates
    beta_checkbox = QCheckBox("Include Beta Updates")
    beta_checkbox.setStyleSheet("color: white; font-size: 14px; margin-left: 10px;")
    beta_checkbox.setChecked(globals.beta)
    layout.addWidget(beta_checkbox)

    # Save Window Placement
    window_checkbox = QCheckBox("Save Window Placement")
    window_checkbox.setStyleSheet("color: white; font-size: 14px; margin-left: 10px;")
    window_checkbox.setChecked(globals.dynamic_window_size)
    layout.addWidget(window_checkbox)

    # Legacy Mode
    legacy_checkbox = QCheckBox("Legacy Mode")
    legacy_checkbox.setStyleSheet("color: white; font-size: 14px; margin-left: 10px;")
    legacy_checkbox.setChecked(globals.legacy_mode)
    layout.addWidget(legacy_checkbox)

        # --- PRINTER SELECTION START ---

    # Create a frame to hold the label and combo box for alignment
    printer_frame = QWidget()
    printer_layout = QVBoxLayout(printer_frame)
    printer_layout.setContentsMargins(0, 0, 0, 0)
    printer_layout.setSpacing(5)

    # Label
    printer_label = QLabel("Default Printer")
    printer_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-left: 10px;")
    printer_layout.addWidget(printer_label)

    # Combo Box
    printer_combo = QComboBox()
    printer_combo.setStyleSheet("""
        QComboBox {
            color: white;
            background-color: #333;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 5px;
            font-size: 14px;
            min-width: 200px;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid white;
            margin-right: 10px;
        }
        QComboBox QAbstractItemView {
            background-color: #333;
            color: white;
            selection-background-color: #2ecc71;
            border: none;
        }
    """)

    # Populate with current printers
    try:
        printers = query_printers()
        if not printers:
            printers = ["No Printers Found"]

        printer_combo.addItems(printers)

        # Set the current selection based on globals
        current_printer = getattr(globals, 'default_printer', None)
        if current_printer and current_printer in printers:
            printer_combo.setCurrentText(current_printer)
        elif printers:
            # Default to first if nothing saved or invalid
            printer_combo.setCurrentIndex(0)

    except Exception as e:
        logging.error(f"Failed to load printers: {e}")
        printer_combo.addItem("Error Loading Printers")

    printer_layout.addWidget(printer_combo)

    # Store reference for the save function
    globals.printer_combo = printer_combo

    # Add the frame to the main layout
    layout.addWidget(printer_frame)

    # --- PRINTER SELECTION END ---

    # Add some spacer at the bottom so it doesn't hug the edge
    layout.addStretch()

    # Store references for later use in save function
    globals.github_check_checkbox = github_check_checkbox
    globals.beta_checkbox = beta_checkbox
    globals.window_checkbox = window_checkbox
    globals.legacy_checkbox = legacy_checkbox

    return tab_widget
