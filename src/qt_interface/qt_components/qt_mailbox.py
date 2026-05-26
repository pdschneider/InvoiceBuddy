# src/qt_interface/qt_components/qt_mailbox.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
                               QLabel, QHBoxLayout, QPushButton, QFrame, QCheckBox,
                               QLineEdit, QSizePolicy)
from PySide6.QtCore import Qt, QSize, QEvent
from PySide6.QtGui import QIcon
import os
import logging


class MailboxWidget(QWidget):
    def __init__(self, globals_obj, parent=None):
        super().__init__(parent)
        self.globals = globals_obj
        self.files = []  # Store filenames
        self.selected_files = set()
        self.checked_files = set()

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_layout = QHBoxLayout()

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

        layout.addLayout(header_layout)

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
        globals_obj.mailbox_widget = self

    def refresh_files(self, folder_path):
        """Clears the list and repopulates with PDFs from folder."""
        self.list_widget.clear()
        self.files = []
        self.selected_files.clear()
        self.checked_files.clear()

        # Reset Master Checkbox
        self.master_checkbox.setChecked(False)

        if not os.path.isdir(folder_path):
            return

        # Get PDFs
        pdf_files = sorted([f for f in os.listdir(folder_path) 
                            if f.lower().endswith(".pdf")])

        for filename in pdf_files:
            self.files.append(filename)

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
        label.setStyleSheet("color: white; font-size: 14px;")
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setWordWrap(False)
        label.setCursor(Qt.PointingHandCursor)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # <-- ADD THIS
        
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
        
        return row

    def _on_item_click(self, item):
        """Handle single click."""
        # Get the filename from our internal list
        filename = self.files[self.list_widget.row(item)]
        self.globals.selected_file = filename
        
        # Construct the full path
        # IMPORTANT: Ensure globals.inbox is the correct absolute path
        if hasattr(self.globals, 'inbox') and self.globals.inbox:
            full_path = os.path.join(self.globals.inbox, filename)
            
            logging.debug(f"Attempting to load: {full_path}")
            
            # Check if the viewer exists and load the file
            if hasattr(self.globals, 'pdf_viewer') and self.globals.pdf_viewer:
                self.globals.pdf_viewer.load_pdf(full_path)
            else:
                logging.error("PDF Viewer not found in globals!")
        else:
            logging.error("Inbox path not set in globals!")

    def _on_double_click(self, item):
        """Handle double click (start editing)."""
        filename = self.files[self.list_widget.row(item)]
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
            self.checked_files.add(filename)
        else:
            self.checked_files.discard(filename)
        
        # Update Master Checkbox State
        # BLOCK SIGNALS so this doesn't trigger _toggle_all recursively
        self.master_checkbox.blockSignals(True)
        
        if len(self.checked_files) == len(self.files) and len(self.files) > 0:
            self.master_checkbox.setChecked(True)
        else:
            self.master_checkbox.setChecked(False)
            
        self.master_checkbox.blockSignals(False)
        
        logging.debug(f"Checked: {filename}")


    def get_checked_files(self):
        """Returns a list of filenames whose checkboxes are checked."""
        return list(self.checked_files)

    def _toggle_all(self, checked):
        """Checks or unchecks all files based on the master checkbox."""
        # Update internal state
        if checked:
            self.checked_files = set(self.files)
        else:
            self.checked_files.clear()
        
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
                if filename in self.files:
                    self.files[self.files.index(filename)] = new_filename
                label.setText(new_base)
                line_edit.deleteLater()
                label.show()
                self.active_editor = None
                
                if hasattr(self.globals, 'selected_file') and self.globals.selected_file == filename:
                    self.globals.selected_file = new_filename
                    if hasattr(self.globals, 'pdf_viewer'):
                        self.globals.pdf_viewer.load_pdf(new_path)
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
                # Call the finish logic with save=False
                # We need to reconstruct the logic or call a helper
                # Let's just do the cancel logic directly here
                obj.deleteLater()
                # Find the label to show it
                # The label is the sibling in the layout
                row_layout = obj.parent().layout()
                # The label is at index 1 (since we inserted line_edit at 1, label was there)
                # Actually, we hid the label, so it's still in the layout at index 1?
                # No, we hid it. It's still there.
                label = row_layout.itemAt(1).widget() # This might be the line_edit if we aren't careful
                # Let's just use the stored filename to find the row?
                # Easier: The label is the widget we hid.
                # Let's just iterate the layout to find the QLabel
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
            if old_filename in self.files:
                idx = self.files.index(old_filename)
                self.files[idx] = new_filename
            
            # Update the label text
            label.setText(new_base)
            
            # Switch back to label view
            line_edit.hide()
            label.show()
            
            logging.debug(f"Renamed: {old_filename} -> {new_filename}")
            
            # Refresh the PDF viewer if this file is currently selected
            if hasattr(self.globals, 'selected_file') and self.globals.selected_file == old_filename:
                self.globals.selected_file = new_filename
                if hasattr(self.globals, 'pdf_viewer') and self.globals.pdf_viewer:
                    self.globals.pdf_viewer.load_pdf(new_path)
            
        except Exception as e:
            logging.error(f"Failed to rename file: {e}")
            line_edit.hide()
            label.show()