# src/qt_interface/qt_components/qt_transaction_editor.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QScrollArea,
                               QLineEdit, QSizePolicy, QCheckBox)
from PySide6.QtCore import Qt, QPoint
from pypdf import PdfReader, PdfWriter
import os
import logging
from src.managers.data_processing import parse_spreadsheet
from src.managers.file_management import archive_files
from src.qt_interface.qt_styles import dark


class TransactionEditor(QWidget):
    """Takes over the mailbox area to edit one file's metadata."""

    def __init__(self, globs_obj, parent=None):
        super().__init__(parent)
        self.globs = globs_obj

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header row: Back button + filename
        header = QHBoxLayout()

        back_btn = QPushButton("← Back to Inbox")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3f; color: #dddddd;
                border: 1px solid #505055; border-radius: 14px;
                padding: 4px 14px; font-size: 12px;
            }
            QPushButton:hover { color: #2ecc71; border-color: #2ecc71; }
        """)
        back_btn.clicked.connect(self.close_editor)
        header.addWidget(back_btn)

        self.filename_label = QLabel("(no file)")
        self.filename_label.setStyleSheet(
            "color: white; font-size: 14px; font-weight: bold; border: none;")
        header.addWidget(self.filename_label)
        header.addStretch()

        # Save button
        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; color: white;
                border: none; border-radius: 14px;
                padding: 4px 16px; font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #27ae60; }
            QPushButton:pressed { background-color: #219a52; }
        """)
        save_btn.clicked.connect(self.save_transaction)
        header.addWidget(save_btn)

        # Ellipsis menu button
        options_btn = QPushButton("⋯")
        options_btn.setCursor(Qt.PointingHandCursor)
        options_btn.setFixedSize(28, 28)
        options_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3f; color: #dddddd;
                border: 1px solid #505055; border-radius: 14px;
                font-size: 14px;
            }
            QPushButton:hover { color: #2ecc71; border-color: #2ecc71; }
        """)
        options_btn.setToolTip("Options")
        options_btn.clicked.connect(lambda: self._show_options_popup(options_btn))
        header.addWidget(options_btn)

        layout.addLayout(header)
        # Field definitions: (key, label)
        self.basic_fields = [
            ("/Amount", "Amount"),
            ("/Date", "Date"),
            ("/Counterparty", "Counterparty"),
            ("/Category", "Category"),
            ("/Subcategory", "Subcategory"),
            ("/Description", "Description"),
        ]
        self.advanced_fields = [
            ("/CardNumber", "Card Number"),
            ("/InvoiceNumber", "Invoice Number"),
            ("/Net", "Terms (Net)"),
            ("/Tax", "Tax"),
        ]

        # Scroll area wrapping all fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; }} {dark.scrollbar}")

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 5, 0, 0)
        form_layout.setSpacing(20)
        form_container.setLayout(form_layout)

        self.inputs = {}

        input_style = """
            QLineEdit {
                background-color: #2b2b2b; color: white;
                border: 1px solid #505055; border-radius: 8px;
                padding: 8px 12px; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #2ecc71; background-color: #303030; }
        """

        def add_field(key, label, parent_layout):
            wrapper = QVBoxLayout()
            wrapper.setSpacing(2)
            wrapper.setContentsMargins(0, 0, 0, 0)

            field_label = QLabel(label)
            field_label.setStyleSheet("color: #bbbbbb; font-size: 12px; border: none;")
            edit = QLineEdit()
            edit.setStyleSheet(input_style)
            edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.inputs[key] = edit

            wrapper.addWidget(field_label)
            wrapper.addWidget(edit)
            parent_layout.addLayout(wrapper)

        # Basic fields
        for key, label in self.basic_fields:
            add_field(key, label, form_layout)

        # Advanced toggle
        self.advanced_toggle = QPushButton("Advanced ▾")
        self.advanced_toggle.setCursor(Qt.PointingHandCursor)
        self.advanced_toggle.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #888;
                border: none; font-size: 12px; text-align: left;
                padding: 4px 0;
            }
            QPushButton:hover { color: #dddddd; }
        """)
        self.advanced_toggle.clicked.connect(self._toggle_advanced)
        form_layout.addWidget(self.advanced_toggle)

        # Advanced frame (starts VISIBLE by default)
        self.advanced_frame = QFrame()
        self.advanced_frame.setStyleSheet("background-color: transparent;")
        adv_layout = QVBoxLayout(self.advanced_frame)
        adv_layout.setContentsMargins(0, 5, 0, 0)
        adv_layout.setSpacing(8)
        for key, label in self.advanced_fields:
            add_field(key, label, adv_layout)
        form_layout.addWidget(self.advanced_frame)

        form_layout.addStretch(1)

        scroll.setWidget(form_container)
        layout.addWidget(scroll, stretch=1)

    def open_for_file(self, filename):
        """Load a file into the editor and swap the left pane to it."""
        self.current_filename = filename
        self.filename_label.setText(filename)
        self.load_metadata()
        self.left_stack.setCurrentWidget(self)
        logging.debug(f"Transaction editor opened for {filename}")

    def load_metadata(self):
        """Read metadata from PDF and populate fields."""
        filepath = os.path.join(self.globs.current_folder, self.current_filename)
        try:
            reader = PdfReader(filepath)
            meta = reader.metadata or {}

            for key, edit in self.inputs.items():
                # PDF metadata keys are case-sensitive (e.g. "/Counterparty")
                value = meta.get(key) or ""
                edit.setText(str(value))
        except Exception as e:
            logging.warning(f"Could not load metadata from {self.current_filename}: {e}")

    def close_editor(self):
        """Return to the mailbox view."""
        self.left_stack.setCurrentWidget(self.globs.mailbox)

    def _show_options_popup(self, anchor_btn):
        """Floating options menu anchored to the ellipsis button."""
        self.options_popup = _OptionsPopup(self, self.globs)
        pos = anchor_btn.mapToGlobal(QPoint(anchor_btn.width(), 0))
        self.options_popup.move(pos)
        self.options_popup.show()

    def _toggle_advanced(self):
        # Toggle visibility
        self.advanced_frame.setVisible(not self.advanced_frame.isVisible())
        self.advanced_toggle.setText("Advanced ▾" if self.advanced_frame.isVisible() else "Advanced ▸")

    def save_transaction(self):
        """Write all field values to PDF metadata and regenerate filename."""
        # Gather field values (skip empty ones)
        new_meta = {}
        for key, edit in self.inputs.items():
            val = edit.text().strip()
            if val:
                new_meta[key] = val

        # Determine sheet config to get column_order
        sheet_name = self.globs.file_identity.get(self.current_filename, "Sheet")
        sheet_config = next(
            (s for s in self.globs.sheet_data.get("sheets", []) if s.get("name") == sheet_name),
            None
        )
        column_order = sheet_config.get("column_order", []) if sheet_config else []

        # Build filename from column_order (only fields that exist in new_meta)
        field_key_map = {
            "Amount": "/Amount",
            "Date": "/Date",
            "Counterparty": "/Counterparty",
            "Category": "/Category",
            "Subcategory": "/Subcategory",
            "Description": "/Description",
            "Card Number": "/CardNumber",
            "Invoice Number": "/InvoiceNumber",
            "Terms (Net)": "/Net",
            "Tax": "/Tax",
        }

        filename_parts = []
        for col in column_order:
            if not col:
                continue
            key = field_key_map.get(col)
            if key and key in new_meta:
                filename_parts.append(new_meta[key])

        new_base = " ".join(filename_parts)
        new_name = new_base + ".pdf" if new_base else self.current_filename

        # Handle duplicate filenames
        search_dir = self.globs.current_folder
        counter = 1
        old_path = os.path.join(search_dir, self.current_filename)
        new_path = os.path.join(search_dir, new_name)

        while os.path.exists(new_path) and new_path != old_path:
            if new_base:
                base = new_base
            else:
                base = os.path.splitext(self.current_filename)[0]
            new_name = f"{base} ({counter}).pdf"
            new_path = os.path.join(search_dir, new_name)
            counter += 1

        try:
            # Write metadata
            reader = PdfReader(old_path)
            writer = PdfWriter()
            writer.append(reader)
            meta = reader.metadata or {}
            meta.update(new_meta)
            writer.add_metadata(meta)

            # Rename file
            with open(new_path, "wb") as f:
                writer.write(f)

            if new_name != self.current_filename:
                os.remove(old_path)
                self.globs.file_identity[new_name] = self.globs.file_identity.pop(self.current_filename, "Sheet")
                self.filename_label.setText(new_name)
                self.current_filename = new_name
            
            # One-click mode: also enter to spreadsheet and archive
            if getattr(self.globs, 'simple_entry', False):
                parse_spreadsheet(self.globs, [self.current_filename])
                archive_files(self.globs, [self.current_filename], confirm=False)

            logging.info(f"Saved transaction for {self.current_filename}")
            self.close_editor()

        except Exception as e:
            logging.error(f"Save failed for {self.current_filename}: {e}")

class _OptionsPopup(QWidget):
    """Floating popup with per-transaction options."""

    def __init__(self, editor, globs, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(260)

        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d30;
                border: 1px solid #444;
                border-radius: 8px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self.check = QCheckBox("Enter to Spreadsheet && Archive on Save")
        self.check.setChecked(bool(getattr(globs, 'simple_entry', False)))
        self.check.setStyleSheet("""
            QCheckBox { color: #dddddd; font-size: 12px; spacing: 6px; }
            QCheckBox::indicator {
                width: 14px; height: 14px; border-radius: 3px;
                border: 1px solid #505055; background-color: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                background-color: #2ecc71; border-color: #2ecc71;
            }
            QCheckBox::indicator:hover { border-color: #2ecc71; }
        """)
        self.check.toggled.connect(
            lambda checked: setattr(globs, 'simple_entry', checked))
        layout.addWidget(self.check)

        main_layout.addWidget(container)
