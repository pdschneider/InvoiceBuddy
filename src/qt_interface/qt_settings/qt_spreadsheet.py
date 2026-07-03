# src/qt_interface/qt_settings/qt_spreadsheet.py
from src.managers.file_management import browse_file
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider,
                               QHBoxLayout, QPushButton, QLineEdit,
                               QColorDialog, QMessageBox, QScrollArea,
                               QSpinBox, QComboBox, QFileDialog)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
import logging
import os

COLUMN_OPTIONS = ["Company", "Date", "Invoice #", "Card Number", ""]


def create_spreadsheet_settings_tab(globals):
    """Create the Spreadsheet Settings tab."""

    tab_widget = QWidget()
    layout = QVBoxLayout(tab_widget)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)
    layout.setAlignment(Qt.AlignTop)

    # ==================== TITLE ====================
    title = QLabel("Spreadsheet")
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 5px;")
    layout.addWidget(title)

    # ==================== SCROLLABLE SHEETS AREA ====================
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QScrollArea.NoFrame)
    scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

    scroll_content = QWidget()
    scroll_content.setStyleSheet("background-color: transparent;")
    scroll_layout = QVBoxLayout(scroll_content)
    scroll_layout.setContentsMargins(0, 10, 0, 10)
    scroll_layout.setSpacing(8)
    scroll_layout.setAlignment(Qt.AlignTop)

    globals.sheets_scroll_layout = scroll_layout

    scroll_area.setWidget(scroll_content)
    layout.addWidget(scroll_area, stretch=1)

    # ==================== ADD BUTTON ====================
    add_button = QPushButton("+ Add New Sheet")
    add_button.setMinimumHeight(35)
    add_button.setStyleSheet("""
        QPushButton {
            background-color: #2ecc71; color: white; border: none;
            border-radius: 4px; font-weight: bold; font-size: 13px;
        }
        QPushButton:hover { background-color: #27ae60; }
    """)
    add_button.clicked.connect(lambda: on_add_sheet(globals))
    layout.addWidget(add_button)

    # Populate initially
    populate_sheets_list(globals)

    return tab_widget


def generate_unique_name(existing_names):
    """Generate a unique name like 'Sheet', 'Sheet 2', etc."""
    base = "Sheet"
    candidate = base
    counter = 2
    while candidate in existing_names:
        candidate = f"{base} {counter}"
        counter += 1
    return candidate


def populate_sheets_list(globals):
    """Build the sheets list from globals.sheet_data."""
    layout = globals.sheets_scroll_layout
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

    sheet_defs = globals.sheet_data.get("sheets", [])

    sheet_defs[:] = [s for s in sheet_defs if s.get("workbook")]
    if len(sheet_defs) == 0:
        sheet_defs.append({"name": "Sheet", "color": "#2ecc71", "workbook": ""})
        globals.sheet_data["sheets"] = sheet_defs

    if len(sheet_defs) == 0:
        sheet_defs.append({
            "name": "Sheet", "color": "#2ecc71", "workbook": "",
            "first_row": 3, "first_column": 1,
            "column_order": ["Company", "Date", "Invoice #", ""]
        })
        globals.sheet_data["sheets"] = sheet_defs

    for idx, sheet in enumerate(sheet_defs):
        sheet.setdefault("first_row", 3)
        sheet.setdefault("first_column", 1)
        sheet.setdefault("column_order", ["Company", "Date", "Invoice #", ""])
        sheet.setdefault("workbook", "")
        row = create_sheet_row(globals, idx, sheet)
        layout.addWidget(row)


def _input_style():
    """Shared stylesheet for text inputs."""
    return """
        QLineEdit {
            background-color: #3a3a40; border: 1px solid #555;
            border-radius: 4px; padding: 5px 8px; color: white; font-size: 13px;
        }
        QLineEdit:focus { border: 1px solid #3498db; }
    """


def _combo_style():
    """Shared stylesheet for combo boxes."""
    return """
        QComboBox {
            background-color: #3a3a40; border: 1px solid #555;
            border-radius: 4px; padding: 4px 8px; color: white; font-size: 12px;
            min-width: 90px;
        }
        QComboBox:hover { border: 1px solid #3498db; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView {
            background-color: #2d2d30; color: white;
            selection-background-color: #3498db;
        }
    """


def _spin_style():
    """Shared stylesheet for spin boxes."""
    return """
        QSpinBox {
            background-color: #3a3a40; border: 1px solid #555;
            border-radius: 4px; padding: 4px 8px; color: white; font-size: 12px;
            min-width: 50px;
        }
        QSpinBox:focus { border: 1px solid #3498db; }
    """


def _label_style():
    """Shared stylesheet for field labels."""
    return "color: #aaa; font-size: 12px;"


def create_sheet_row(globals, idx, sheet):
    """Create a single sheet row widget with two lines."""

    # ===== COLLAPSED MODE: No workbook selected yet =====
    if not sheet.get("workbook"):
        row_widget = QWidget()
        row_widget.setStyleSheet("background-color: #2d2d30; border-radius: 6px;")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(12, 10, 12, 10)
        row_layout.setSpacing(10)

        add_btn = QPushButton("+ Add Spreadsheet")
        add_btn.setMinimumHeight(36)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; border: 1px solid #2980b9;
                border-radius: 6px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9; border: 1px solid #2ecc71;
            }
        """)

        def on_browse_collapsed():
            from src.managers.file_management import browse_file
            temp_var = type('obj', (object,), {'setText': lambda s, v: setattr(temp_var, '_val', v)})()
            browse_file(globals, temp_var, _type="workbook")
            if hasattr(temp_var, '_val'):
                globals.sheet_data["sheets"][idx]["workbook"] = temp_var._val
                globals.sheet_data["sheets"][idx].setdefault("name", f"Sheet {idx + 1}")
                globals.sheet_data["sheets"][idx].setdefault("color", "#2ecc71")
                globals.sheet_data["sheets"][idx].setdefault("first_row", 3)
                globals.sheet_data["sheets"][idx].setdefault("first_column", 1)
                globals.sheet_data["sheets"][idx].setdefault("column_order", ["Company", "Date", "Invoice #", ""])
                populate_sheets_list(globals)

        add_btn.clicked.connect(lambda checked: on_browse_collapsed())

        row_layout.addWidget(add_btn)

        # Only show delete if there are other sheets
        if len(globals.sheet_data.get("sheets", [])) > 1:
            delete_btn = QPushButton("✕")
            delete_btn.setFixedSize(32, 32)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c; color: white; border: 1px solid #c0392b;
                    border-radius: 4px; font-size: 14px; font-weight: bold;
                }
                QPushButton:hover { background-color: #c0392b; }
            """)
            delete_btn.clicked.connect(lambda checked, i=idx: on_delete_sheet(globals, i))
            row_layout.addWidget(delete_btn)

        return row_widget

    # ===== EXPANDED MODE: Normal full row =====
    row_widget = QWidget()
    row_widget.setStyleSheet("background-color: #2d2d30; border-radius: 6px;")
    row_layout = QVBoxLayout(row_widget)
    row_layout.setContentsMargins(12, 10, 12, 10)
    row_layout.setSpacing(8)

    # ===== LINE 1: Color | Name | Workbook | Browse | Delete =====
    line1 = QHBoxLayout()
    line1.setSpacing(10)

    # Color picker
    hex_color = sheet.get("color", "#2ecc71")
    color_btn = QPushButton()
    color_btn.setFixedSize(32, 32)
    color_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {hex_color}; border: 2px solid #fff; border-radius: 16px;
        }}
        QPushButton:hover {{ border: 2px solid #ffd700; }}
    """)
    color_btn.setToolTip("Click to pick color")
    color_btn.clicked.connect(lambda checked, i=idx: on_color_click(globals, i))
    line1.addWidget(color_btn)

    # Name input
    name_input = QLineEdit()
    name_input.setText(sheet.get("name", "Sheet"))
    name_input.setPlaceholderText("Sheet name")
    name_input.setMinimumWidth(120)
    name_input.setStyleSheet(_input_style())
    name_input.textChanged.connect(lambda text, i=idx: on_name_changed(globals, i, text))
    line1.addWidget(name_input)

    # Workbook path display
    wb_label = QLabel()
    wb_path = sheet.get("workbook", "")
    if wb_path:
        wb_label.setText(os.path.basename(wb_path))
        wb_label.setToolTip(wb_path)
    else:
        wb_label.setText("No workbook selected")
    wb_label.setStyleSheet("color: #2ecc71; font-size: 12px;")
    line1.addWidget(wb_label, stretch=1)

    # Browse button
    browse_btn = QPushButton("Browse")
    browse_btn.setFixedWidth(70)
    browse_btn.setStyleSheet("""
        QPushButton {
            background-color: #444; color: white; border: 1px solid #555;
            border-radius: 4px; font-size: 12px;
        }
        QPushButton:hover { background-color: #555; }
    """)
    browse_btn.clicked.connect(lambda checked, i=idx, lbl=wb_label: browse_file_wrapper(globals, i, lbl))
    line1.addWidget(browse_btn)

    # Delete button
    delete_btn = QPushButton("✕")
    delete_btn.setFixedSize(32, 32)
    delete_btn.setStyleSheet("""
        QPushButton {
            background-color: #e74c3c; color: white; border: 1px solid #c0392b;
            border-radius: 4px; font-size: 14px; font-weight: bold;
        }
        QPushButton:hover { background-color: #c0392b; }
    """)
    delete_btn.setToolTip("Remove this sheet")
    delete_btn.clicked.connect(lambda checked, i=idx: on_delete_sheet(globals, i))
    line1.addWidget(delete_btn)

    row_layout.addLayout(line1)

    # ===== LINE 2: First Row | First Column =====
    line2 = QHBoxLayout()
    line2.setSpacing(15)

    # First Row
    row_label = QLabel("First Row:")
    row_label.setStyleSheet(_label_style())
    line2.addWidget(row_label)

    row_spin = QSpinBox()
    row_spin.setRange(1, 50)
    row_spin.setValue(sheet.get("first_row", 3))
    row_spin.setStyleSheet(_spin_style())
    row_spin.valueChanged.connect(lambda val, i=idx: on_field_changed(globals, i, "first_row", val))
    line2.addWidget(row_spin)

    # First Column
    col_label = QLabel("First Col:")
    col_label.setStyleSheet(_label_style())
    line2.addWidget(col_label)

    col_spin = QSpinBox()
    col_spin.setRange(1, 50)
    col_spin.setValue(sheet.get("first_column", 1))
    col_spin.setStyleSheet(_spin_style())
    col_spin.valueChanged.connect(lambda val, i=idx: on_field_changed(globals, i, "first_column", val))
    line2.addWidget(col_spin)

    line2.addStretch()
    row_layout.addLayout(line2)

    # ===== LINE 3: Column Order =====
    line3 = QHBoxLayout()
    line3.setSpacing(8)

    order_label = QLabel("Order:")
    order_label.setStyleSheet(_label_style())
    line3.addWidget(order_label)

    column_order = sheet.get("column_order", ["Company", "Date", "Invoice #", ""])
    for pos in range(4):
        combo = QComboBox()
        combo.addItems(COLUMN_OPTIONS)
        current_val = column_order[pos] if pos < len(column_order) else ""
        combo.setCurrentText(current_val)
        combo.setStyleSheet(_combo_style())
        combo.currentTextChanged.connect(
            lambda text, i=idx, p=pos: on_column_order_changed(globals, i, p, text)
        )
        line3.addWidget(combo)

    line3.addStretch()
    row_layout.addLayout(line3)

    return row_widget


def on_field_changed(globals, index, field, value):
    """Generic handler for numeric field changes."""
    sheet_defs = globals.sheet_data.get("sheets", [])
    if 0 <= index < len(sheet_defs):
        sheet_defs[index][field] = value


def on_column_order_changed(globals, index, position, value):
    """Update column_order list when a combo box changes."""
    sheet_defs = globals.sheet_data.get("sheets", [])
    if 0 <= index < len(sheet_defs):
        col_order = sheet_defs[index].setdefault("column_order", ["", "", "", ""])
        while len(col_order) < 4:
            col_order.append("")
        col_order[position] = value


def on_color_click(globals, index):
    """Open color dialog for sheet at index."""
    sheet_defs = globals.sheet_data.get("sheets", [])
    current_color = sheet_defs[index].get("color", "#2ecc71")

    color = QColorDialog.getColor(QColor(current_color))

    if color.isValid():
        hex_color = color.name()
        sheet_defs[index]["color"] = hex_color
        populate_sheets_list(globals)


def on_name_changed(globals, index, value):
    """Update sheet name in data model."""
    sheet_defs = globals.sheet_data.get("sheets", [])
    if 0 <= index < len(sheet_defs):
        sheet_defs[index]["name"] = value.strip() or "Unnamed"


def browse_file_wrapper(globals, index, label_widget):
    """Wrapper to call the global browse_file with PySide6 mode."""
    from src.managers.file_management import browse_file
    
    # Create a temporary text variable for compatibility
    temp_var = type('obj', (object,), {'setText': lambda s, v: setattr(temp_var, '_val', v)})()
    
    browse_file(globals, temp_var, _type="workbook")
    
    if hasattr(temp_var, '_val'):
        file_path = temp_var._val
        globals.sheet_data["sheets"][index]["workbook"] = file_path
        label_widget.setText(os.path.basename(file_path))
        label_widget.setToolTip(file_path)
        label_widget.setStyleSheet("color: #2ecc71; font-size: 12px;")


def on_add_sheet(globals):
    """Add a new sheet definition."""
    sheet_defs = globals.sheet_data.setdefault("sheets", [])

    existing_names = [s.get("name", "") for s in sheet_defs]
    new_name = generate_unique_name(existing_names)

    # Find last used workbook path
    last_workbook = ""
    for s in reversed(sheet_defs):
        if s.get("workbook"):
            last_workbook = s["workbook"]
            break

    sheet_defs.append({
        "name": new_name,
        "color": "#3498db",
        "workbook": last_workbook,
        "first_row": 3,
        "first_column": 1,
        "column_order": ["Company", "Date", "Invoice #", ""]
    })

    populate_sheets_list(globals)


def on_delete_sheet(globals, index):
    """Delete sheet after confirmation."""
    sheet_defs = globals.sheet_data.get("sheets", [])

    reply = QMessageBox.question(
        None,
        "Delete Sheet?",
        f"Are you sure you want to delete '{sheet_defs[index].get('name')}'?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.Yes:
        sheet_defs.pop(index)
        populate_sheets_list(globals)
