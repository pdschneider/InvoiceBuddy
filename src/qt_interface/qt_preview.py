# src/qt_interface/qt_preview.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFrame, QScrollArea)
from PySide6.QtCore import Qt
from src.qt_interface.qt_components.qt_viewer import NativePdfViewer
from src.interface.components.gui_actions import smart_spreadsheet_button, pdf_button
from src.managers.printers import print_selected_files
from src.managers.file_management import archive_files, send_to_trash

def create_preview_pane(globals):
    """Creates the right pane with PDF preview and action buttons."""

    pane = QWidget()
    layout = QVBoxLayout(pane)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)

    # === METADATA EDITOR (Top) ===
    meta_frame = QFrame()
    meta_frame.setStyleSheet("background-color: #333; border-radius: 5px;")
    meta_layout = QVBoxLayout(meta_frame)
    meta_layout.setContentsMargins(10, 10, 10, 10)

    meta_title = QLabel("Select a file to view details")
    meta_title.setStyleSheet("color: #aaa; font-style: italic;")
    meta_layout.addWidget(meta_title)

    layout.addWidget(meta_frame)

    # === PDF PREVIEW (Middle) ===
    # Create the native viewer instance
    pdf_viewer = NativePdfViewer()
    
    # Add it to the layout, stretching it to fill available space
    layout.addWidget(pdf_viewer, stretch=1)

    # Store reference in globals so the Mailbox can access it later
    globals.pdf_viewer = pdf_viewer

    # === ACTION TOOLBAR (Bottom) ===
    actions_frame = QFrame()
    actions_frame.setStyleSheet("background-color: #333; border-radius: 5px;")
    actions_layout = QHBoxLayout(actions_frame)
    actions_layout.setContentsMargins(10, 10, 10, 10)
    actions_layout.setSpacing(10)

    # Helper to create action buttons
    def create_action_btn(text, icon_text, color="#3a3a3a"):
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; border-radius: 4px;")
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    # Buttons
    btn_autoname = create_action_btn("Auto-Name", "🏷️")
    btn_autoname.clicked.connect(lambda e: pdf_button(globals, directory=globals.inbox, file_list=globals.checked_files))
    btn_enter = create_action_btn("Enter", "➡️")
    btn_enter.clicked.connect(lambda e: smart_spreadsheet_button(globals, file_list=globals.checked_files))
    btn_print = create_action_btn("Print", "🖨️")
    btn_print.clicked.connect(lambda e: print_selected_files(globals, globals.checked_files))
    btn_archive = create_action_btn("Archive", "📦")
    btn_archive.clicked.connect(lambda e: archive_files(globals, globals.checked_files))
    btn_delete = create_action_btn("Delete", "🗑️", "#8B0000")
    btn_delete.clicked.connect(lambda e: send_to_trash(globals, globals.checked_files))

    actions_layout.addWidget(btn_autoname)
    actions_layout.addWidget(btn_enter)
    actions_layout.addWidget(btn_print)
    actions_layout.addWidget(btn_archive)
    actions_layout.addWidget(btn_delete)

    layout.addWidget(actions_frame)

    # Store references
    globals.preview_meta = meta_title
    globals.btn_autoname = btn_autoname
    globals.btn_enter = btn_enter
    globals.btn_archive = btn_archive
    globals.btn_delete = btn_delete

    return pane
