# src.interface.components.budget
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QScrollArea, QLineEdit, QMessageBox,
    QApplication
)
from PySide6.QtCore import Qt, QTimer
from shiboken6 import Shiboken
from src.utils.save import save_categories


class BudgetPage(QWidget):
    """Full-width budgeting page (categories/subcategories for now)."""

    def __init__(self, globs_obj, parent=None):
        super().__init__(parent)
        self.globs = globs_obj

        # Outer layout holds only the scroll area
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 20, 20, 20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("border: none;")

        # Everything that used to go in `layout` goes in here
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        content.setStyleSheet("background-color: transparent;")
        layout.setSpacing(12)

        # Header Row
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra spacing
        header_layout.setSpacing(10)  # Gap between widgets

        title = QLabel("Budget")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)

        header_layout.addStretch()  # Pushes title left

        layout.addLayout(header_layout)

        # A frame that will hold all the category sections
        categories_frame = QFrame()
        categories_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)

        self.categories_layout = QVBoxLayout(categories_frame)
        self.categories_layout.setContentsMargins(0, 0, 0, 0)
        self.categories_layout.setSpacing(12)

        for name, data in globs_obj.categories.items():
            section = self._create_category_section(name, data)
            self.categories_layout.addWidget(section)

        layout.addWidget(categories_frame)

        # Add Category Button
        self.add_btn = QPushButton("+ Add Category")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setMaximumWidth(250)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.add_btn.clicked.connect(lambda: self._add_category())
        layout.addWidget(self.add_btn, alignment=Qt.AlignLeft)

        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    def _add_category(self):
        """Adds an inline editable frame for a new category."""
        self.add_btn.hide()
        edit_frame = QFrame()
        edit_frame.setMaximumWidth(450)
        edit_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(edit_frame)
        layout.setContentsMargins(12, 12, 12, 12)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("New category name...")
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #333339;
                color: white;
                border: 1px solid #505055;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #2ecc71; }
        """)
        layout.addWidget(line_edit)

        def commit():
            name = line_edit.text().strip()
            if name and name not in self.globs.categories:
                self.globs.categories[name] = {}
                save_categories(self.globs)
                self.categories_layout.addWidget(self._create_category_section(name, {}))
            edit_frame.deleteLater()
            self.add_btn.show()

        def cancel():
            edit_frame.deleteLater()
            self.add_btn.show()

        def key_press(event):
            if event.key() == Qt.Key_Escape:
                cancel()
            else:
                QLineEdit.keyPressEvent(line_edit, event)
        line_edit.keyPressEvent = key_press

        line_edit.returnPressed.connect(commit)
        original_focus_out = line_edit.focusOutEvent

        def custom_focus_out(event):
            cancel()
            original_focus_out(event)

        line_edit.focusOutEvent = custom_focus_out

        self.categories_layout.addWidget(edit_frame)
        line_edit.setFocus()

    def _create_category_section(self, name, data):
        """Builds one category block: header + subcategory rows."""
        frame = QFrame()
        frame.setMaximumWidth(450)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #333;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        header = QLabel(name)
        header.setStyleSheet("""
            background-color: transparent;
            border: none;
            color: #2ecc71;
            font-size: 15px;
            font-weight: bold;
        """)

        header.setCursor(Qt.PointingHandCursor)

        def open_edit(event):
            self._edit_category(frame.category_name, header, frame)
        header.mousePressEvent = open_edit

        header_row = QHBoxLayout()
        header_row.addWidget(header)
        header_row.addStretch()
        layout.addLayout(header_row)

        frame.category_name = name
        frame.header_label = header
        frame.header_row = header_row

        for sub in data.get("subcategories", []):
            row = QLabel(sub)
            row.setStyleSheet("""
                QLabel {
                    color: #dddddd;
                    font-size: 14px;
                    background-color: transparent;
                    border: none;
                    border-bottom: 1px solid #3a3a40;
                    padding: 8px 4px 8px 8px;
                }
            """)
            row.setCursor(Qt.PointingHandCursor)
            row.mousePressEvent = lambda event, s=sub, r=row: self._edit_subcategory(frame, r, s)
            layout.addWidget(row)

        add_sub_btn = QPushButton("+ add subcategory")
        add_sub_btn.setCursor(Qt.PointingHandCursor)
        add_sub_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4da6ff;
                border: none;
                font-size: 12px;
                padding: 3px 0px;
                text-align: left;
            }
            QPushButton:hover { color: #7dbfff; }
        """)

        layout.addWidget(add_sub_btn)
        add_sub_btn.clicked.connect(lambda: self._add_subcategory(frame))
        frame.add_sub_btn = add_sub_btn

        return frame

    def _edit_category(self, name, label, frame):
        """Creates line edit for changing category names."""
        label.hide()
        edit = QLineEdit(name)
        edit.setStyleSheet("""
            QLineEdit {
                background-color: #333339;
                color: white;
                border: 1px solid #505055;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 15px;
            }
            QLineEdit:focus { border: 1px solid #2ecc71; }
        """)
        frame.header_row.insertWidget(0, edit)
        edit.setFocus()
        edit.selectAll()

        # Allow to delete categories that are not Income
        delete_btn = None
        if name != "Income":
            delete_btn = QPushButton("🗑 Delete Category")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setFocusPolicy(Qt.StrongFocus)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #e74c3c;
                    border: none;
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                    color: white;
                }
            """)
            frame.header_row.addWidget(delete_btn)
            frame.delete_btn = delete_btn

            delete_btn.clicked.connect(lambda: self._delete_category(name, frame))

        def cancel():
            # Remove Delete Button
            if getattr(frame, "delete_btn", None):
                frame.delete_btn.deleteLater()
                frame.delete_btn = None
            edit.deleteLater()
            label.show()

        frame.cancel_edit = cancel

        def key_press(event):
            if event.key() == Qt.Key_Escape:
                cancel()
            else:
                QLineEdit.keyPressEvent(edit, event)
        edit.keyPressEvent = key_press

        original_focus_out = edit.focusOutEvent

        def custom_focus_out(event):
            original_focus_out(event)
            def check():
                if QApplication.focusWidget() is delete_btn:
                    return  # Focus went to the delete button; keep editing
                if edit.isVisible():
                    cancel()
            QTimer.singleShot(0, check)

        edit.focusOutEvent = custom_focus_out

        def commit():
            # Remove Delete BVutton
            if getattr(frame, "delete_btn", None):
                frame.delete_btn.deleteLater()
                frame.delete_btn = None
            new_name = edit.text().strip()
            if new_name and new_name != name and new_name not in self.globs.categories:
                rebuilt = {}
                for key, value in self.globs.categories.items():
                    rebuilt[new_name if key == name else key] = value
                self.globs.categories = rebuilt
                save_categories(self.globs)
                label.setText(new_name)
                frame.category_name = new_name
            edit.deleteLater()
            label.show()

        edit.returnPressed.connect(commit)

    def _delete_category(self, name, frame):
        confirm = QMessageBox.question(
            self,
            "Delete Category",
            f'Delete "{name}" and all its subcategories?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            if getattr(frame, "cancel_edit", None):
                frame.cancel_edit()
            return

        del self.globs.categories[name]
        save_categories(self.globs)
        frame.deleteLater()


    def _add_subcategory(self, frame):
        frame.add_sub_btn.hide()

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("New subcategory name...")
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #333339;
                color: white;
                border: 1px solid #505055;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #2ecc71; }
        """)
        frame.layout().addWidget(line_edit)
        line_edit.setFocus()

        def cancel():
            line_edit.deleteLater()
            frame.add_sub_btn.show()

        def key_press(event):
            if event.key() == Qt.Key_Escape:
                cancel()
            else:
                QLineEdit.keyPressEvent(line_edit, event)
        line_edit.keyPressEvent = key_press

        original_focus_out = line_edit.focusOutEvent

        def custom_focus_out(event):
            original_focus_out(event)
            def check():
                if QApplication.focusWidget() is not line_edit and line_edit.isVisible():
                    cancel()
            QTimer.singleShot(0, check)

        line_edit.focusOutEvent = custom_focus_out

        def commit():
            new_name = line_edit.text().strip()
            if new_name:
                data = self.globs.categories[frame.category_name]
                subs = data.setdefault("subcategories", [])
                if new_name not in subs:
                    subs.append(new_name)
                    save_categories(self.globs)
                    row = QLabel(new_name)
                    row.setStyleSheet("""
                        QLabel {
                            color: #dddddd;
                            font-size: 14px;
                            background-color: transparent;
                            border: none;
                            border-bottom: 1px solid #3a3a40;
                            padding: 8px 4px 8px 8px;
                        }
                    """)
                    row.setCursor(Qt.PointingHandCursor)
                    row.mousePressEvent = lambda event, s=new_name: self._edit_subcategory(frame, row, s)
                    frame.layout().insertWidget(frame.layout().count() - 2, row)
            line_edit.deleteLater()
            frame.add_sub_btn.show()

        line_edit.returnPressed.connect(commit)

    def _edit_subcategory(self, frame, row, name):
        row.hide()

        edit_row = QFrame()
        edit_row.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        row_layout = QHBoxLayout(edit_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        trash_btn = QPushButton("🗑")
        trash_btn.setFixedSize(24, 24)
        trash_btn.setCursor(Qt.PointingHandCursor)
        trash_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3f;
                color: #e74c3c;
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                color: white;
            }
        """)
        trash_btn.clicked.connect(lambda: self._delete_subcategory(frame, row, name))
        row_layout.addWidget(trash_btn)

        line_edit = QLineEdit(name)
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #333339;
                color: white;
                border: 1px solid #505055;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #2ecc71; }
        """)
        row_layout.addWidget(line_edit)
        row_layout.addStretch()

        frame.layout().insertWidget(frame.layout().indexOf(row), edit_row)
        frame._active_sub_edit = edit_row
        line_edit.setFocus()
        line_edit.selectAll()

        def cancel():
            edit_row.deleteLater()
            row.show()

        def key_press(event):
            if event.key() == Qt.Key_Escape:
                cancel()
            else:
                QLineEdit.keyPressEvent(line_edit, event)
        line_edit.keyPressEvent = key_press

        original_focus_out = line_edit.focusOutEvent

        def custom_focus_out(event):
            original_focus_out(event)
            def check():
                if not Shiboken.isValid(line_edit):
                    return
                if QApplication.focusWidget() is trash_btn:
                    return
                if line_edit.isVisible():
                    cancel()
            QTimer.singleShot(0, check)

        frame.cancel_sub_edit = cancel

        def commit():
            new_name = line_edit.text().strip()
            if new_name and new_name != name:
                data = self.globs.categories[frame.category_name]
                subs = data.setdefault("subcategories", [])
                if new_name not in subs:
                    subs[subs.index(name)] = new_name
                    save_categories(self.globs)
                    row.setText(new_name)
                    row.mousePressEvent = lambda event, s=new_name, r=row: self._edit_subcategory(frame, r, s)
            edit_row.deleteLater()
            row.show()

        line_edit.returnPressed.connect(commit)
        line_edit.focusOutEvent = custom_focus_out

    def _delete_subcategory(self, frame, row, name):
        confirm = QMessageBox.question(
            self,
            "Delete Subcategory",
            f'Delete "{name}" from {frame.category_name}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            if getattr(frame, "cancel_sub_edit", None):
                frame.cancel_sub_edit()
            return

        data = self.globs.categories[frame.category_name]
        subs = data.get("subcategories", [])
        if name in subs:
            subs.remove(name)
            save_categories(self.globs)
        row.deleteLater()
        edit_row = getattr(frame, "_active_sub_edit", None)
        if edit_row:
            edit_row.deleteLater()
            frame._active_sub_edit = None
        row.deleteLater()

        frame._active_sub_edit = edit_row
