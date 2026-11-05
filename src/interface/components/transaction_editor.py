# src.interface.components.transaction_editor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QLineEdit, QSizePolicy, QCheckBox, QDateEdit,
    QCompleter, QStackedLayout, QMessageBox
)
from PySide6.QtCore import (
    Qt, QPoint, QDate, QTimer, QStringListModel
)
from pypdf import PdfReader, PdfWriter
import os
import logging
from src.managers.data_processing import parse_spreadsheet
from src.managers.file_management import archive_files
from src.utils.save import save_counterparties, ensure_uuid
from src.interface.styles import dark


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

        self.field_labels = {}
        self.inputs = {}

        input_style = """
            QLineEdit {
                background-color: #2b2b2b; color: white;
                border: 1px solid #505055; border-radius: 8px;
                padding: 0px 12px; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #2ecc71; background-color: #303030; }
        """

        def add_field(key, label, parent_layout):
            wrapper = QHBoxLayout()
            wrapper.setSpacing(10)
            wrapper.setContentsMargins(0, 0, 0, 0)

            if not hasattr(self, "category_button"):
                self.category_button = QPushButton("Select")
                self.category_button.setCursor(Qt.PointingHandCursor)
                self.category_button.setFixedHeight(36)
                self.category_button.setMaximumWidth(240)
                self.category_button.clicked.connect(
                    lambda: self._open_category_picker())
                self.category_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2b2b2b; color: #888888;
                        border: 1px solid #505055; border-radius: 14px;
                        padding: 4px 14px; font-size: 13px; text-align: center;
                    }
                    QPushButton:hover { border-color: #6a6a70; }
                """)

            field_label = QLabel(label)
            field_label.setFixedWidth(120)
            field_label.setStyleSheet("color: #bbbbbb; font-size: 13px; font-weight: 600; border: none;")

            if key == "/Date":
                edit = QDateEdit()
                edit.setCalendarPopup(True)
                edit.setDisplayFormat("MM-dd-yy")  # Change to MM-dd-yyyy for longer year format
                edit.setMinimumDate(QDate(1900, 1, 1))
                edit.setDate(QDate(1900, 1, 1))
                edit.setSpecialValueText(" ")
                edit.setButtonSymbols(QDateEdit.NoButtons)
                edit.setFixedSize(140, 36)
                edit.setStyleSheet("""
                    QDateEdit {
                        background-color: #2b2b2b; color: white;
                        border: 1px solid #505055; border-radius: 8px;
                        padding: 0px 12px; font-size: 14px;
                        selection-background-color: #2ecc71;
                    }
                    QDateEdit::down-button {
                        background: transparent;
                        border: none;
                        border-top-right-radius: 8px;
                        border-bottom-right-radius: 8px;
                        width: 24px;
                    }
                    QDateEdit:hover { border-color: #6a6a70; }
                    QDateEdit:focus { border: 1px solid #2ecc71; background-color: #303030; }
                """)
            else:
                edit = QLineEdit()
                edit.setStyleSheet(input_style)

            self.field_labels[edit] = field_label
            if key == "/Category":
                edit.hide()
                stack = QStackedLayout()
                stack.addWidget(edit)
                stack.addWidget(self.category_button)
                stack_holder = QWidget()
                stack_holder.setLayout(stack)
                stack_holder.setMaximumWidth(280)
                self.category_stack = stack
                stack.setCurrentIndex(1)
            edit.installEventFilter(self)
            edit.setFixedHeight(36)
            if key != "/Date":
                edit.setMaximumWidth(280)
                edit.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

            self.inputs[key] = edit
            if key != "/Category":
                stack_holder = None

            # Adds drop down list to counterparty widget
            if key == "/Counterparty":
                completer = QCompleter(list(self.globs.counterparties))
                self.counterparty_completer = completer
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                edit.setCompleter(completer)
                edit.textChanged.connect(
                    lambda text, c=completer:
                    QTimer.singleShot(0, c.popup().hide) if not text else None)
                completer.popup().setStyleSheet("""
                    QListView {
                        background-color: #2d2d30;
                        border: 1px solid #505055;
                        border-radius: 8px;
                        color: #dddddd;
                        padding: 4px;
                    }
                    QListView::item {
                        padding: 6px 10px;
                        border-radius: 4px;
                    }
                    QListView::item:hover,
                    QListView::item:selected {
                        background-color: #2ecc71;
                        color: white;
                    }
                    QScrollBar:vertical { width: 0; border: 0; }
                """)

                # Stacked pair: line edit (page 0) + button (page 1)
                stack = QStackedLayout()
                self.counterparty_stack = stack
                stack.addWidget(edit)

                # Page 1: name button + delete button in a row
                btn_row = QWidget()
                row_layout = QHBoxLayout(btn_row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(6)

                self.counterparty_button = QPushButton("")
                self.counterparty_button.setCursor(Qt.PointingHandCursor)
                self.counterparty_button.setFixedHeight(36)
                self.counterparty_button.setMaximumWidth(240)
                self.counterparty_button.clicked.connect(self._reopen_counterparty)
                self.counterparty_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2d4a3e; color: #dddddd;
                        border: 1px solid #2ecc71; border-radius: 14px;
                        padding: 4px 14px; font-size: 13px; text-align: left;
                    }
                    QPushButton:hover { background-color: #35604f; }
                """)
                row_layout.addWidget(self.counterparty_button)

                self.trash_button = QPushButton("🗑")
                self.trash_button.setCursor(Qt.PointingHandCursor)
                self.trash_button.setFixedSize(28, 28)
                self.trash_button.setToolTip("Delete counterparty from saved list")
                self.trash_button.setFocusPolicy(Qt.NoFocus)
                self.trash_button.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a3f; color: #e74c3c;
                        border: 1px solid #505055; border-radius: 14px;
                        font-size: 12px;
                    }
                    QPushButton:hover { color: white; background-color: #c0392b; border-color: #c0392b; }
                """)
                self.trash_button.clicked.connect(self._delete_counterparty)
                row_layout.addWidget(self.trash_button)

                stack.addWidget(btn_row)

                stack_holder = QWidget()
                stack_holder.setLayout(stack)
                stack_holder.setMaximumWidth(280)

            wrapper.addWidget(field_label)
            if key in ("/Amount", "/Tax"):
                edit.setFixedWidth(140)
                edit.setStyleSheet(input_style + """
                    QLineEdit { padding-left: 28px; }
                """)
                dollar = QLabel("$", edit)
                dollar.setGeometry(8, 0, 14, 36)
                dollar.setStyleSheet("color: #888888; font-size: 14px; border: none; background: transparent;")
                edit.textEdited.connect(lambda _t, e=edit: self._format_amount_live(e))
                edit.editingFinished.connect(lambda e=edit: self._format_amount_final(e))
                wrapper.addWidget(edit)
            else:
                wrapper.addWidget(stack_holder if stack_holder else edit)
            wrapper.addStretch()
            if key != "/Subcategory":
                parent_layout.addLayout(wrapper)

        # Basic fields
        for key, label in self.basic_fields:
            add_field(key, label, form_layout)

        # Advanced toggle
        self.advanced_toggle = QPushButton("Advanced ▾")
        self.advanced_toggle.setCursor(Qt.PointingHandCursor)
        self.advanced_toggle.setFocusPolicy(Qt.NoFocus)
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
        self.counterparty_completer.setModel(QStringListModel(list(self.globs.counterparties)))
        self.current_filename = filename
        self.load_metadata()

        # Buttonify counterparty if this file already has one
        edit = self.inputs["/Counterparty"]
        if edit.text().strip():
            self._solidify_counterparty(edit, autofill=False)
        else:
            self.counterparty_stack.setCurrentIndex(0)
            self.counterparty_button.setText("")

        self._refresh_category_button()

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
                value = str(meta.get(key) or "")
                if key == "/Date":
                    for fmt in ("MM-dd-yyyy", "M-d-yyyy", "MM-dd-yy", "M-d-yy"):
                        qdate = QDate.fromString(value, fmt)
                        if qdate.isValid():
                            break
                    # Two-digit years from auto-name: Qt assumes 19xx, bump to 20xx
                    if qdate.isValid() and qdate.year() < 1970:
                        qdate = qdate.addYears(100)
                    edit.setDate(qdate if qdate.isValid() else QDate(1900, 1, 1))
                else:
                    edit.setText(value)
                if key == "/Amount" and value:
                    self._format_amount_final(edit)
        except Exception as e:
            logging.warning(f"Could not load metadata from {self.current_filename}: {e}")

    def close_editor(self):
        """Return to the mailbox view."""
        self.left_stack.setCurrentWidget(self.globs.mailbox)

    def _open_category_picker(self):
        self.category_picker = _CategoryPickerPopup(
            self.globs, self._on_category_picked)
        pos = self.category_button.mapToGlobal(
            QPoint(0, self.category_button.height()))
        self.category_picker.move(pos)
        self.category_picker.show()

    def _on_category_picked(self, category, subcategory):
        self.inputs["/Category"].setText(category)
        self.inputs["/Subcategory"].setText(subcategory)
        self._refresh_category_button()

    def _refresh_category_button(self):
        """Gray 'Select' if unset; green pill if a valid category is stored."""
        cat = self.inputs["/Category"].text().strip()
        sub = self.inputs["/Subcategory"].text().strip()
        valid = cat in self.globs.categories and sub in \
            self.globs.categories.get(cat, {}).get("subcategories", [])

        logging.debug(f"REFRESH: cat='{cat}', sub='{sub}', categories={list(self.globs.categories)}")
        
        if cat and sub and valid:
            self.category_button.setText(sub)
            self.category_button.setStyleSheet("""
                QPushButton {
                    background-color: #2d4a3e; color: #dddddd;
                    border: 1px solid #2ecc71; border-radius: 14px;
                    padding: 4px 14px; font-size: 13px; text-align: center;
                }
                QPushButton:hover { background-color: #35604f; }
            """)
        else:
            self.category_button.setText("Select")
            self.category_button.setStyleSheet("""
                QPushButton {
                    background-color: #2b2b2b; color: #888888;
                    border: 1px solid #505055; border-radius: 14px;
                    padding: 4px 14px; font-size: 13px; text-align: center;
                }
                QPushButton:hover { border-color: #6a6a70; }
            """)

    def _show_options_popup(self, anchor_btn):
        """Floating options menu anchored to the ellipsis button."""
        self.options_popup = _OptionsPopup(self, self.globs)
        pos = anchor_btn.mapToGlobal(QPoint(anchor_btn.width(), 0))
        self.options_popup.move(pos)
        self.options_popup.show()

    def _reopen_counterparty(self):
        """Button click: swap back to the editable line edit."""
        self.counterparty_stack.setCurrentIndex(0)
        edit = self.inputs["/Counterparty"]
        edit.setFocus()
        edit.selectAll()

    def _delete_counterparty(self):
        """Ask, then remove the shown counterparty from the saved list."""
        name = self.counterparty_button.text()
        if not name:
            return
        confirm = QMessageBox.question(
            self,
            "Remove Counterparty",
            f'Remove "{name}" from your saved counterparties?\n'
            "It will no longer appear in the drop-down until saved again.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return
        if name in self.globs.counterparties:
            del self.globs.counterparties[name]
            save_counterparties(self.globs)
            logging.info(f"Deleted counterparty: {name}")
        self.inputs["/Counterparty"].clear()
        self.counterparty_stack.setCurrentIndex(0)
        self.counterparty_button.setText("")

    def _solidify_counterparty(self, edit, autofill=True):
        """Convert the counterparty edit into a button showing its text."""
        name = edit.text().strip()
        logging.debug(f"SOLIDIFY called with name: '{name}'")
        self.counterparty_button.setText(name)
        self.counterparty_stack.setCurrentIndex(1)

        # Autofill remembered category/description (only if fields are empty)
        if autofill:
            record = self.globs.counterparties.get(name, {})
            record_map = {
                "/Category": "Category",
                "/Subcategory": "Subcategory",
                "/Description": "Description",
            }
            for key, record_key in record_map.items():
                field = self.inputs[key]
                logging.debug(f"TRYING {key}: current='{field.text().strip()}', stored='{record.get(record_key)}'")
                if not field.text().strip() and record.get(record_key):
                    field.setText(record[record_key])
        self._refresh_category_button()

    def _toggle_advanced(self):
        # Toggle visibility
        self.advanced_frame.setVisible(not self.advanced_frame.isVisible())
        self.advanced_toggle.setText("Advanced ▾" if self.advanced_frame.isVisible() else "Advanced ▸")

    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress and obj is self.inputs.get("/Counterparty"):
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and obj.text().strip():
                self._solidify_counterparty(obj)
                self.focusNextChild()
                return True
        elif event.type() == event.Type.FocusIn:
            label = self.field_labels.get(obj)
            if label:
                label.setStyleSheet("color: #2ecc71; font-size: 13px; font-weight: 600; border: none;")
            # Blank date (sentinel): seed with today, drop cursor at month section
            if isinstance(obj, QDateEdit):
                if obj.date() == QDate(1900, 1, 1):
                    obj.setDate(QDate.currentDate())
                obj.setSelectedSection(QDateEdit.MonthSection)
        elif event.type() == event.Type.FocusOut:
            if obj is self.inputs.get("/Counterparty") and obj.text().strip():
                self._solidify_counterparty(obj)
            label = self.field_labels.get(obj)
            if label:
                label.setStyleSheet("color: #bbbbbb; font-size: 13px; font-weight: 600; border: none;")
        return super().eventFilter(obj, event)

    def _format_amount_live(self, edit):
        """Live formatting: reject bad chars, enforce 2 decimals, insert commas."""
        raw = edit.text().replace(",", "")
        
        # Reject empty or invalid characters
        if not raw:
            return
        
        # Only digits and at most one dot
        if not raw.replace(".", "").isdigit():
            # Remove any invalid char just typed
            clean = "".join(c for c in raw if c.isdigit() or c == ".")
            pos = edit.cursorPosition()
            edit.blockSignals(True)
            edit.setText(clean)
            edit.setCursorPosition(max(0, min(pos - 1, len(clean))))
            edit.blockSignals(False)
            return
        
        if raw.count(".") > 1:
            # Block extra dots
            pos = edit.cursorPosition()
            clean = raw[:pos]
            edit.blockSignals(True)
            edit.setText(clean)
            edit.setCursorPosition(len(clean))
            edit.blockSignals(False)
            return
        
        # Split whole and fraction
        if "." in raw:
            whole, frac = raw.split(".", 1)
        else:
            whole, frac = raw, None
        
        # Leading zeros: only allow "0" by itself, not "01", "00", etc.
        if whole and len(whole) > 1 and whole[0] == "0":
            whole = whole.lstrip("0") or "0"
        
        # Limit decimals to 2
        if frac and len(frac) > 2:
            frac = frac[:2]
        
        # Reconstruct
        if whole:
            formatted_whole = f"{int(whole):,}"
        else:
            formatted_whole = ""
        new_text = formatted_whole + ("." + frac if frac is not None else "")
        
        if new_text != edit.text():
            pos = edit.cursorPosition()
            edit.blockSignals(True)
            edit.setText(new_text)

            # Try to keep cursor in the correct spot
            offset = new_text.count(",")
            edit.setCursorPosition(min(pos + offset, len(new_text)))
            edit.blockSignals(False)

    def _format_amount_final(self, edit):
        """On blur/save: force exactly 2 decimal places."""
        raw = edit.text().replace(",", "")
        if not raw:
            return
        try:
            value = float(raw)
        except ValueError:
            return
        formatted = f"{value:,.2f}"
        if formatted != edit.text():
            edit.blockSignals(True)
            edit.setText(formatted)
            edit.blockSignals(False)

    def save_transaction(self):
        """Write all field values to PDF metadata and regenerate filename."""
        # Ensure Amount is finalized (adds .00 if missing) before saving
        self._format_amount_final(self.inputs["/Amount"])
        # Gather field values (skip empty ones)
        new_meta = {}

        for key, edit in self.inputs.items():
            val = edit.text().strip()
            if key == "/Amount":
                val = val.replace(",", "")
            if val:
                new_meta[key] = val

        # Auto-add new counterparty
        counterparty = new_meta.get("/Counterparty", "").strip()
        if counterparty:
            record = self.globs.counterparties.setdefault(counterparty, {})
            if new_meta.get("/Category"):
                record["Category"] = new_meta["/Category"]
            if new_meta.get("/Subcategory"):
                record["Subcategory"] = new_meta["/Subcategory"]
            if new_meta.get("/Description"):
                record["Description"] = new_meta["/Description"]
            save_counterparties(self.globs)
            logging.info(f"Saved counterparty data: {counterparty}")

        # Determine sheet config to get column_order
        sheet_name = self.globs.file_identity.get(self.current_filename, "Sheet")
        sheet_config = next(
            (s for s in self.globs.sheet_data.get("sheets", []) if s.get("name") == sheet_name),
            None
        )
        if sheet_config:
            column_order = sheet_config.get("column_order", [])
            if sheet_config.get("separate_filename") and sheet_config.get("filename_order"):
                column_order = sheet_config.get("filename_order", [])
        else:
            column_order = []

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

        # Windows: fail early if the file is locked/open elsewhere
        try:
            with open(old_path, "rb+"):
                pass
        except PermissionError:
            answer = QMessageBox.question(
                self,
                "File Locked",
                f'"{self.current_filename}" is open in another program '
                "and can't be renamed on save.\n\n"
                "Save metadata anyway (this will leave the old file behind), "
                "or cancel and close it first?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel)
            if answer != QMessageBox.StandardButton.Save:
                return

        try:
            # Write metadata
            reader = PdfReader(old_path)
            writer = PdfWriter()
            writer.append(reader)
            meta = dict(reader.metadata or {})
            for key in self.inputs:
                if key not in new_meta:
                    meta.pop(key, None)
            meta.update(new_meta)
            ensure_uuid(meta)
            writer.add_metadata(meta)

            # Rename file
            with open(new_path, "wb") as f:
                writer.write(f)

            if new_name != self.current_filename:
                try:
                    os.remove(old_path)
                except PermissionError:
                    logging.warning(
                        f"Original left behind (locked): {self.current_filename}")
                self.globs.file_identity[new_name] = self.globs.file_identity.pop(self.current_filename, "Sheet")
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


class _CategoryPickerPopup(QWidget):
    """Floating menu listing subcategories grouped under their categories."""

    def __init__(self, globs, on_pick, parent=None):
        super().__init__(parent)
        self.on_pick = on_pick
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

        inner = QVBoxLayout(container)
        inner.setContentsMargins(8, 8, 8, 8)
        inner.setSpacing(0)

        for category, data in globs.categories.items():
            header = QPushButton(category)
            header.setEnabled(False)  # not selectable, just a label
            header.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none;
                    color: #2ecc71; font-size: 13px; font-weight: bold;
                    text-align: left; padding: 6px 4px 2px 4px;
                }
            """)
            inner.addWidget(header)

            for sub in data.get("subcategories", []):
                btn = QPushButton("    " + sub)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent; border: none;
                        color: #dddddd; font-size: 13px; text-align: left;
                        padding: 4px 4px 4px 16px;
                    }
                    QPushButton:hover { color: #2ecc71; }
                """)
                btn.clicked.connect(
                    lambda _=False, c=category, s=sub: self._pick(c, s))
                inner.addWidget(btn)

        inner.addStretch()
        main_layout.addWidget(container)

    def _pick(self, category, subcategory):
        self.on_pick(category, subcategory)
        self.close()
