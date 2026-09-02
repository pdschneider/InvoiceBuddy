# src/qt_interface/qt_components/qt_mailbox.py
from src.managers.file_management import send_to_trash
from src.managers.printers import print_selected_files
from src.interface.components.gui_actions import smart_spreadsheet_button, pdf_button
from src.managers.file_management import archive_files
from src.utils.toast import show_toast
from src.qt_interface.qt_styles import dark
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
                               QLabel, QHBoxLayout, QPushButton, QFrame, QCheckBox,
                               QLineEdit, QSizePolicy, QScrollArea)
from PySide6.QtCore import Qt, QSize, QEvent, QPoint
from pypdf import PdfReader
import os
import logging
import shutil


def load_sheet_identity(filepath, globs_obj):
    """Read /Sheet from PDF metadata, default to first sheet."""

    default_sheet = globs_obj.sheet_data.get("sheets", [{}])[0].get("name", "Sheet")

    try:
        reader = PdfReader(filepath)
        if reader.metadata:
            sheet = reader.metadata.get("/Sheet")
            if sheet:
                sheet_name = str(sheet)
                valid_names = [s.get("name") for s in globs_obj.sheet_data.get("sheets", [])]
                if sheet_name in valid_names:
                    return sheet_name
        return default_sheet
    except Exception as e:
        logging.debug(f"Could not read /Sheet from {os.path.basename(filepath)}: {e}")
        return default_sheet


class AssignSheetDialog(QWidget):
    """Floating popup panel for bulk-assigning files to a sheet."""

    def __init__(self, globs_obj, checked_files, mailbox, parent=None):
        super().__init__(parent)
        self.globs = globs_obj
        self.checked_files = checked_files
        self.mailbox = mailbox
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(220)

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
        layout.setSpacing(4)

        title = QLabel("Assign to Sheet")
        title.setStyleSheet("color: white; font-size: 13px; font-weight: bold; margin-bottom: 4px; border: none;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        scroll.setMaximumHeight(250)

        list_widget = QWidget()
        list_widget.setStyleSheet("background-color: #2d2d30;")
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(2)

        sheets = self.globs.sheet_data.get("sheets", [])
        for sheet in sheets:
            row = self._create_sheet_item(sheet)
            list_layout.addWidget(row)

        list_layout.addStretch()
        scroll.setWidget(list_widget)
        layout.addWidget(scroll)

        main_layout.addWidget(container)

    def _create_sheet_item(self, sheet):
        """Create a clickable row with colored dot and sheet name."""
        name = sheet.get("name", "Sheet")
        color = sheet.get("color", "#888")

        row = QFrame()
        row.setFixedHeight(34)
        row.setCursor(Qt.PointingHandCursor)
        row.setStyleSheet("""
            QFrame { background-color: transparent; border-radius: 4px; }
            QFrame:hover { background-color: #3a3a40; }
        """)

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(8, 4, 8, 4)
        row_layout.setSpacing(10)

        dot = QLabel()
        dot.setFixedSize(12, 12)
        dot.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        row_layout.addWidget(dot)

        label = QLabel(name)
        label.setStyleSheet("color: white; font-size: 13px; background-color: transparent; border: none;")
        row_layout.addWidget(label)
        row_layout.addStretch()

        row.mousePressEvent = lambda event, s=name: self._select_sheet(s)

        return row

    def _select_sheet(self, sheet_name):
        """Assign all checked files to the selected sheet and close."""
        for filename in self.checked_files:
            self.globs.file_identity[filename] = sheet_name
        self.mailbox._refresh_pills()
        self.close()


class SendToBuddyDialog(QWidget):
    """Floating popup panel for sending checked files to a buddy."""

    def __init__(self, globs_obj, checked_files, mailbox, parent=None):
        super().__init__(parent)
        self.globs = globs_obj
        self.checked_files = checked_files
        self.mailbox = mailbox
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(220)

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
        layout.setSpacing(4)

        title = QLabel("Send to Buddy")
        title.setStyleSheet("color: white; font-size: 13px; font-weight: bold; margin-bottom: 4px; border: none;")
        layout.addWidget(title)

        # Filter valid buddies
        valid_buddies = [(name, folder) for name, folder in self.globs.buddies.items()
                         if name != "inbox" and folder and os.path.isdir(folder)]

        for name, folder in valid_buddies:
            row = self._create_buddy_item(name, folder)
            layout.addWidget(row)

        main_layout.addWidget(container)

    def _create_buddy_item(self, name, folder):
        """Create a clickable row with envelope icon and buddy name."""
        row = QFrame()
        row.setFixedHeight(34)
        row.setCursor(Qt.PointingHandCursor)
        row.setStyleSheet("""
            QFrame { background-color: transparent; border-radius: 4px; }
            QFrame:hover { background-color: #3a3a40; }
        """)

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(8, 4, 8, 4)
        row_layout.setSpacing(10)

        icon = QLabel("📨")
        icon.setStyleSheet("background-color: transparent; border: none; font-size: 14px;")
        row_layout.addWidget(icon)

        label = QLabel(name.capitalize())
        label.setStyleSheet("color: white; font-size: 13px; background-color: transparent; border: none;")
        row_layout.addWidget(label)
        row_layout.addStretch()

        row.mousePressEvent = lambda event, n=name, f=folder: self._send_to_buddy(n, f)

        return row

    def _send_to_buddy(self, name, target_dir):
        """Move checked files to the buddy's directory."""

        # Exit if target directory does not exist
        if not os.path.isdir(target_dir):
            logging.error(f"Target directory does not exist: {target_dir}")
            self.close()
            return

        moved_count = 0
        errors = []
        already_present = []

        for filename in self.checked_files:
            src_file = os.path.join(self.globs.current_folder, filename)
            dst_file = os.path.join(target_dir, filename)

            # Append error if source file does not exist
            if not os.path.isfile(src_file):
                errors.append(filename)
                continue

            # Append error if file already exists in buddy's folder
            if os.path.isfile(dst_file):
                errors.append(filename)
                already_present.append(filename)
                continue

            try:
                shutil.move(src_file, dst_file)
                moved_count += 1

            except Exception as e:
                logging.error(f"Failed to move {filename}: {e}")
                errors.append(filename)

        # Log and show toast
        if moved_count:
            logging.info(f"Sent {moved_count} files to {name} successfully!")
        if errors:
            logging.error(f"Unable to move {len(errors)} files: {errors}")
        if already_present:
            logging.error(f"Already present in {name}'s inbox: {already_present}")
            show_toast(self.globs,
                       message=f"Unable to move {len(already_present)} files - already present in {name}'s inbox",
                       _type="error")

        # Refresh the mailbox
        if hasattr(self.globs, 'mailbox_widget') and self.globs.mailbox_widget:
            self.globs.mailbox_widget.refresh_files(self.globs.current_folder)

        self.close()


class MailboxWidget(QWidget):
    def __init__(self, globs_obj, parent=None):
        super().__init__(parent)
        self.globs = globs_obj
        self.globs.files = []  # Store ALL filenames
        self.selected_files = set()
        self.globs.checked_files = set()

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(48)
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(10, 12, 10, 12)
        header_layout.setSpacing(7)

        # Master Checkbox
        self.master_checkbox = QCheckBox()
        self.master_checkbox.setStyleSheet("QCheckBox { spacing: 0; border: 2px solid #555}")
        self.master_checkbox.toggled.connect(self._toggle_all)

        header_layout.addWidget(self.master_checkbox)

        # Header Label
        self.header_label = QLabel("Inbox")
        self.header_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: white;
            padding: 0; /* No extra padding, let the layout handle it */
            border-bottom: 1px solid #333; /* Just the bottom line */
        """)
        self.header_label.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()

        # Contextual buttons (hidden until files are checked)
        self.action_buttons = QWidget()
        action_layout = QHBoxLayout(self.action_buttons)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(5)

        # Auto-Name Button
        self.auto_name_btn = QPushButton("🪄")
        self.auto_name_btn.setFixedSize(24, 24)
        self.auto_name_btn.setStyleSheet(dark.mailbox_button)
        self.auto_name_btn.setCursor(Qt.PointingHandCursor)
        self.auto_name_btn.setToolTip("Auto-Name")
        self.auto_name_btn.clicked.connect(lambda e: pdf_button(self.globs, directory=self.globs.current_folder, file_list=self.globs.checked_files))
        action_layout.addWidget(self.auto_name_btn)

        # Enter to Spreadsheet Button
        self.enter_data_btn = QPushButton("✏️")
        self.enter_data_btn.setFixedSize(24, 24)
        self.enter_data_btn.setStyleSheet(dark.mailbox_button)
        self.enter_data_btn.setCursor(Qt.PointingHandCursor)
        self.enter_data_btn.setToolTip("Enter to Spreadsheet")
        self.enter_data_btn.clicked.connect(lambda e: smart_spreadsheet_button(self.globs, file_list=self.globs.checked_files))
        action_layout.addWidget(self.enter_data_btn)

        # Archive Button
        self.archive_btn = QPushButton("📁")
        self.archive_btn.setFixedSize(24, 24)
        self.archive_btn.setStyleSheet(dark.mailbox_button)
        self.archive_btn.setCursor(Qt.PointingHandCursor)
        self.archive_btn.setToolTip("Archive Files")
        self.archive_btn.clicked.connect(lambda e: archive_files(self.globs, self.globs.checked_files))
        action_layout.addWidget(self.archive_btn)

        # Send Button
        self.send_btn = QPushButton("📨")
        self.send_btn.setFixedSize(24, 24)
        self.send_btn.setStyleSheet(dark.mailbox_button)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setToolTip("Send to Buddy")
        self.send_btn.clicked.connect(lambda: self._on_send_clicked())
        action_layout.addWidget(self.send_btn)

        # Assign Sheets Button
        self.assign_btn = QPushButton("🏷️")
        self.assign_btn.setFixedSize(24, 24)
        self.assign_btn.setStyleSheet(dark.mailbox_button)
        self.assign_btn.setCursor(Qt.PointingHandCursor)
        self.assign_btn.setToolTip("Assign Sheets")
        self.assign_btn.clicked.connect(lambda: self._on_assign_clicked())
        action_layout.addWidget(self.assign_btn)

        # Print Button
        self.print_btn = QPushButton("🖨")
        self.print_btn.setFixedSize(24, 24)
        self.print_btn.setStyleSheet(dark.mailbox_button)
        self.print_btn.setCursor(Qt.PointingHandCursor)
        self.print_btn.setToolTip("Print")
        self.print_btn.clicked.connect(lambda: self._on_contextual_print())
        action_layout.addWidget(self.print_btn)

        # Delete Button
        self.delete_btn = QPushButton("🗑")
        self.action_buttons.setFixedHeight(32)
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setStyleSheet(dark.delete_button)
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setToolTip("Delete")
        self.delete_btn.clicked.connect(lambda: self._on_contextual_delete())
        action_layout.addWidget(self.delete_btn)

        self.action_buttons.hide()
        header_layout.addWidget(self.action_buttons)

        layout.addWidget(self.header_widget)

        # The List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: none;
                color: white;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background-color: #3a3a3a;
                color: #2ecc71;
            }
            QListWidget::item:hover {
                background-color: #333;
            }
        """)
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)

        # Connect signals
        self.list_widget.itemClicked.connect(self._on_item_click)
        self.list_widget.itemDoubleClicked.connect(self._on_double_click)

        layout.addWidget(self.list_widget)

        # Store reference
        globs_obj.mailbox_widget = self

    def refresh_files(self, folder_path):
        """Clears the list and repopulates with PDFs from folder."""
        self.list_widget.clear()
        self.globs.files = []
        self.selected_files.clear()
        self.globs.checked_files.clear()
        self.action_buttons.hide()

        # Reset Master Checkbox
        self.master_checkbox.setChecked(False)

        if not os.path.isdir(folder_path):
            return

        # Get PDFs
        pdf_files = sorted([f for f in os.listdir(folder_path) 
                            if f.lower().endswith(".pdf")])

        for filename in pdf_files:
            self.globs.files.append(filename)

            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 50))
            self.list_widget.addItem(item)

            row_widget = self._create_row_widget(filename, folder_path)
            self.list_widget.setItemWidget(item, row_widget)

    def _create_row_widget(self, filename, folder_path):
        row = QFrame()
        row.setFrameShape(QFrame.NoFrame)
        row.setStyleSheet("background-color: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 5, 10, 5)
        row_layout.setSpacing(10)

        # CHECKBOX
        checkbox = QCheckBox()
        checkbox.setStyleSheet("QCheckBox { spacing: 0; border: 2px solid #555}")
        checkbox.setCursor(Qt.PointingHandCursor)
        checkbox.toggled.connect(lambda checked, f=filename: self._on_checkbox_toggled(f, checked))
        row_layout.addWidget(checkbox)

        # Label
        base_name = os.path.splitext(filename)[0] 
        label = QLabel(base_name)
        label.setStyleSheet("color: white; font-size: 13px; background-color: transparent; border: none;")
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setWordWrap(False)
        label.setCursor(Qt.PointingHandCursor)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Double click starts editing
        label.mouseDoubleClickEvent = lambda event: self._start_editing(filename, folder_path, label, row, row_layout)

        row_layout.addWidget(label)

        row.file_data = {
            'filename': filename,
            'folder_path': folder_path,
            'label': label,
            'row': row,
            'row_layout': row_layout
        }

        # PILL
        full_path = os.path.join(folder_path, filename)
        sheet_name = load_sheet_identity(full_path, self.globs)
        self.globs.file_identity[filename] = sheet_name

        # Find matching color
        sheet_color = "#888"
        for s in self.globs.sheet_data.get("sheets", []):
            if s.get("name") == sheet_name:
                sheet_color = s.get("color", "#888")
                break

        pill = QLabel(sheet_name)
        pill.setObjectName("sheetPill")
        pill.setFixedHeight(24)
        pill.setAlignment(Qt.AlignCenter)
        pill.setStyleSheet(f"""
            background-color: {sheet_color};
            color: white;
            border-radius: 12px;
            padding: 0 12px;
            font-size: 11px;
            font-weight: bold;
        """)
        pill.setCursor(Qt.PointingHandCursor)
        pill.mousePressEvent = lambda event, f=filename: self._cycle_sheet(f)
        row_layout.addWidget(pill)

        return row

    def _on_item_click(self, item):
        """Handle single click."""
        # Get the filename from our internal list
        filename = self.globs.files[self.list_widget.row(item)]
        self.globs.selected_file = filename

        # Construct the full path
        if hasattr(self.globs, 'current_folder') and self.globs.current_folder:
            full_path = os.path.join(self.globs.current_folder, filename)

            logging.debug(f"Attempting to load: {full_path}")

            # Check if the viewer exists and load the file
            if hasattr(self.globs, 'pdf_viewer') and self.globs.pdf_viewer:
                self.globs.pdf_viewer.load_pdf(full_path)
            else:
                logging.error("PDF Viewer not found in globs!")
        else:
            logging.error("Inbox path not set in globs!")

    def _on_double_click(self, item):
        """Handle double click (start editing)."""
        filename = self.globs.files[self.list_widget.row(item)]
        row_widget = self.list_widget.itemWidget(item)

        if row_widget and hasattr(row_widget, 'file_data'):
            file_data = row_widget.file_data
            self._start_editing(
                file_data['filename'],
                file_data['folder_path'],
                file_data['label'],
                file_data['row'],
                file_data['row_layout']
            )

    def _on_checkbox_toggled(self, filename, checked):
        """Tracks which files have their checkboxes checked and updates master."""
        if checked:
            self.globs.checked_files.add(filename)
        else:
            self.globs.checked_files.discard(filename)

        # Update Master Checkbox State
        # BLOCK SIGNALS so this doesn't trigger _toggle_all recursively
        self.master_checkbox.blockSignals(True)

        if len(self.globs.checked_files) == len(self.globs.files) and len(self.globs.files) > 0:
            self.master_checkbox.setChecked(True)
        else:
            self.master_checkbox.setChecked(False)

        self.master_checkbox.blockSignals(False)

        logging.debug(f"Checked: {filename}")

        # Show/hide contextual buttons
        if len(self.globs.checked_files) > 0:
            self.action_buttons.show()
            self._update_send_button_visibility()
        else:
            self.action_buttons.hide()

    def _cycle_sheet(self, filename):
        """Cycle through sheets when pill is clicked."""
        sheets = self.globs.sheet_data.get("sheets", [])
        if not sheets:
            return

        current = self.globs.file_identity.get(filename, sheets[0].get("name", "Sheet"))
        names = [s.get("name", "Sheet") for s in sheets]

        if current in names:
            next_idx = (names.index(current) + 1) % len(names)
        else:
            next_idx = 0

        new_name = names[next_idx]
        new_color = sheets[next_idx].get("color", "#888")
        self.globs.file_identity[filename] = new_name

        # Update the pill in place
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            row_widget = self.list_widget.itemWidget(item)
            if row_widget and hasattr(row_widget, 'file_data') and row_widget.file_data['filename'] == filename:
                pill = row_widget.findChild(QLabel, "sheetPill")
                if pill:
                    pill.setText(new_name)
                    pill.setStyleSheet(f"""
                        background-color: {new_color};
                        color: white;
                        border-radius: 12px;
                        padding: 0 12px;
                        font-size: 11px;
                        font-weight: bold;
                    """)
                break

        logging.debug(f"Cycled {filename} to {new_name}")

    def get_checked_files(self):
        """Returns a list of filenames whose checkboxes are checked."""
        return list(self.globs.checked_files)

    def _toggle_all(self, checked):
        """Checks or unchecks all files based on the master checkbox."""
        # Update internal state
        if checked:
            self.globs.checked_files = set(self.globs.files)
        else:
            self.globs.checked_files.clear()

        # Update the UI of all rows
        # BLOCK SIGNALS on the list items so we don't trigger _on_checkbox_toggled recursively
        self.list_widget.blockSignals(True)

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            row_widget = self.list_widget.itemWidget(item)
            if row_widget:
                checkbox = row_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(checked)

        self.list_widget.blockSignals(False)

        logging.debug(f"Master toggle: {'All Checked' if checked else 'All Unchecked'}")

    def _start_editing(self, filename, folder_path, label, row, row_layout):
        """Creates a Line Edit on the fly."""

        # Close any existing editor first (One at a time)
        if hasattr(self, 'active_editor') and self.active_editor:
            self.active_editor.deleteLater()
            self.active_editor = None

        label.hide()

        line_edit = QLineEdit(os.path.splitext(filename)[0])

        # Explicitly set line edit height
        line_edit.setMinimumHeight(20)
        line_edit.setMaximumHeight(25)

        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                font-size: 14px; 
                font-family: inherit;
            }
            QLineEdit:focus { border: 1px solid #2ecc71; }
        """)

        row_layout.insertWidget(1, line_edit)
        line_edit.selectAll()
        line_edit.setFocus()

        self.active_editor = line_edit
        self.active_label = label
        self.active_filename = filename
        self.active_folder = folder_path

        def finish(save=True):
            if self.active_editor is None:
                return  # Already finished, don't run again

            if not save:
                line_edit.deleteLater()
                label.show()
                self.active_editor = None
                return

            new_base = line_edit.text().strip()
            if not new_base:
                line_edit.deleteLater()
                label.show()
                self.active_editor = None
                return

            new_filename = new_base + ".pdf"
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)

            if os.path.exists(new_path) and new_path != old_path:
                logging.error(f"File exists: {new_filename}")
                line_edit.deleteLater()
                label.show()
                self.active_editor = None
                return

            try:
                os.rename(old_path, new_path)
                if filename in self.globs.files:
                    self.globs.files[self.globs.files.index(filename)] = new_filename
                label.setText(new_base)
                line_edit.deleteLater()
                label.show()
                self.active_editor = None

                if hasattr(self.globs, 'selected_file') and self.globs.selected_file == filename:
                    self.globs.selected_file = new_filename
                    if hasattr(self.globs, 'pdf_viewer'):
                        self.globs.pdf_viewer.load_pdf(new_path)
            except Exception as e:
                logging.error(f"Rename failed: {e}")
                line_edit.deleteLater()
                label.show()
                self.active_editor = None

        line_edit.returnPressed.connect(lambda: finish(save=True))
        # Handle Click Away: Override focusOutEvent (more reliable than editingFinished)
        original_focus_out = line_edit.focusOutEvent
        def custom_focus_out(event):
            finish(save=False)  # Click away = cancel
            original_focus_out(event)
        line_edit.focusOutEvent = custom_focus_out

        # Handle Escape
        original_key = line_edit.keyPressEvent
        def custom_key(event):
            if event.key() == Qt.Key_Escape:
                finish(save=False)
            else:
                original_key(event)
        line_edit.keyPressEvent = custom_key

    def eventFilter(self, obj, event):
        """Global event filter to catch Escape key for the active editor."""
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            if obj == self.active_editor:
                obj.deleteLater()
                row_layout = obj.parent().layout()
                label = row_layout.itemAt(1).widget()
                for i in range(row_layout.count()):
                    w = row_layout.itemAt(i).widget()
                    if isinstance(w, QLabel):
                        w.show()
                        break
                self.active_editor = None
                return True
        return super().eventFilter(obj, event)

    def _save_edit(self, old_filename, folder_path, label, line_edit):
        """Saves the edited filename and renames the file on disk."""
        new_base = line_edit.text().strip()

        if not new_base:
            # Empty name, cancel edit
            line_edit.hide()
            label.show()
            return

        # Preserve the .pdf extension
        new_filename = new_base + ".pdf"

        # Build full paths
        old_path = os.path.join(folder_path, old_filename)
        new_path = os.path.join(folder_path, new_filename)

        # Check if new name already exists
        if os.path.exists(new_path) and new_path != old_path:
            logging.error(f"File already exists: {new_filename}")
            line_edit.hide()
            label.show()
            return

        try:
            # Rename the file on disk
            os.rename(old_path, new_path)

            # Update internal file list
            if old_filename in self.globs.files:
                idx = self.globs.files.index(old_filename)
                self.globs.files[idx] = new_filename

            # Update the label text
            label.setText(new_base)

            # Switch back to label view
            line_edit.hide()
            label.show()

            logging.debug(f"Renamed: {old_filename} -> {new_filename}")

            # Refresh the PDF viewer if this file is currently selected
            if hasattr(self.globs, 'selected_file') and self.globs.selected_file == old_filename:
                self.globs.selected_file = new_filename
                if hasattr(self.globs, 'pdf_viewer') and self.globs.pdf_viewer:
                    self.globs.pdf_viewer.load_pdf(new_path)

        except Exception as e:
            logging.error(f"Failed to rename file: {e}")
            line_edit.hide()
            label.show()

    def _refresh_pills(self):
        """Update all pill colors and text from globs.file_identity."""
        sheets = self.globs.sheet_data.get("sheets", [])

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            row_widget = self.list_widget.itemWidget(item)
            if row_widget and hasattr(row_widget, 'file_data'):
                filename = row_widget.file_data['filename']
                sheet_name = self.globs.file_identity.get(filename, "Sheet")

                sheet_color = "#888"
                for s in sheets:
                    if s.get("name") == sheet_name:
                        sheet_color = s.get("color", "#888")
                        break

                pill = row_widget.findChild(QLabel, "sheetPill")
                if pill:
                    pill.setText(sheet_name)
                    pill.setStyleSheet(f"""
                        background-color: {sheet_color};
                        color: white;
                        border-radius: 12px;
                        padding: 0 12px;
                        font-size: 11px;
                        font-weight: bold;
                    """)

    def _on_contextual_delete(self):
        """Delete all checked files."""
        result = send_to_trash(self.globs, list(self.globs.checked_files))
        if not result:
            return

    def _on_contextual_print(self):
        """Print all checked files."""
        print_selected_files(self.globs, list(self.globs.checked_files))

    def _on_assign_clicked(self):
        """Open assign sheet dialog for checked files."""
        checked = list(self.globs.checked_files)
        if not checked:
            return

        dialog = AssignSheetDialog(self.globs, checked, self)
        pos = self.assign_btn.mapToGlobal(QPoint(0, self.assign_btn.height() + 4))
        dialog.move(pos)
        dialog.show()

    def _on_send_clicked(self):
        """Open send to buddy dialog for checked files."""
        checked = list(self.globs.checked_files)
        if not checked:
            return

        # Check if any buddies exist
        valid_buddies = [(name, folder) for name, folder in self.globs.buddies.items()
                         if name != "inbox" and folder and os.path.isdir(folder)]

        if not valid_buddies:
            logging.warning("No valid buddies configured.")
            return

        dialog = SendToBuddyDialog(self.globs, checked, self)
        pos = self.send_btn.mapToGlobal(QPoint(0, self.send_btn.height() + 4))
        dialog.move(pos)
        dialog.show()

    def _update_send_button_visibility(self):
        """Show send button only if valid buddies exist."""
        valid_buddies = [(name, folder) for name, folder in self.globs.buddies.items()
                         if name != "inbox" and folder and os.path.isdir(folder)]
        if valid_buddies:
            self.send_btn.show()
        else:
            self.send_btn.hide()
