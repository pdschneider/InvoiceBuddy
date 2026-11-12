# src.interface.components.accounts
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QLineEdit, QMessageBox,
    QApplication
)
from PySide6.QtCore import (Qt, QRegularExpression, QTimer)
from PySide6.QtGui import QRegularExpressionValidator
from src.interface.styles import dark
from src.utils.save import save_ledger


class AccountsPage(QWidget):
    """Full-width accounts page (ledger accounts + starting balances)."""

    def __init__(self, globs_obj, parent=None):
        super().__init__(parent)
        self.globs = globs_obj

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 20, 20, 20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; } " + dark.scrollbar)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 150)
        content.setStyleSheet("background-color: transparent;")
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Accounts")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Frame holding all account sections
        accounts_frame = QFrame()
        accounts_frame.setStyleSheet("""
            QFrame { background-color: transparent; border: none; }
        """)
        self.accounts_layout = QVBoxLayout(accounts_frame)
        self.accounts_layout.setContentsMargins(0, 0, 0, 0)
        self.accounts_layout.setSpacing(12)

        for name, data in self.globs.ledger.items():
            section = self._create_account_section(name, data)
            self.accounts_layout.addWidget(section)

        layout.addWidget(accounts_frame)

        # Add Account Button
        self.add_btn = QPushButton("+ Add Account")
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
        self.add_btn.clicked.connect(lambda: self._add_account())
        layout.addWidget(self.add_btn, alignment=Qt.AlignLeft)

        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    def _create_account_section(self, name, data):
        """One account block: name header + starting balance row."""
        frame = QFrame()
        frame.setMaximumWidth(450)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #333;
                border-radius: 8px;
            }
        """)

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 12, 12, 12)
        frame_layout.setSpacing(4)

        header = QLabel(name)
        header.setStyleSheet("""
            background-color: transparent; border: none;
            color: #2ecc71; font-size: 15px; font-weight: bold;
        """)
        header_row = QHBoxLayout()
        header_row.addWidget(header)
        header_row.addStretch()
        layout_row = frame_layout.addLayout(header_row)

        frame.account_name = name
        frame.header_label = header
        frame.header_row = header_row

        header.setCursor(Qt.PointingHandCursor)

        def open_edit(event):
            self._edit_account(frame.account_name, header, frame)
        header.mousePressEvent = open_edit

        balance = data.get("starting_balance", 0)
        balance_label = QLabel(f"Starting Balance: ${balance:,.2f}")
        balance_label.setStyleSheet("""
            QLabel {
                color: #dddddd; font-size: 14px;
                background-color: transparent; border: none;
                border-bottom: 1px solid #3a3a40;
                padding: 8px 4px 8px 8px;
            }
        """)

        balance_label.setCursor(Qt.PointingHandCursor)
        balance_label.mousePressEvent = lambda event: self._edit_balance(frame)
        frame.balance_label = balance_label

        frame_layout.addWidget(balance_label)

        return frame

    def _edit_account(self, name, label, frame):
        """Click-to-rename mode: label swaps for a line edit."""
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

        # Delete only when the account has no transactions
        delete_btn = None
        if not self.globs.ledger[name].get("transactions"):
            delete_btn = QPushButton("🗑 Delete Account")
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
            delete_btn.clicked.connect(lambda: self._delete_account(name, frame))


        def cancel():
            if getattr(frame, "delete_btn", None):
                frame.delete_btn.deleteLater()
                frame.delete_btn = None
            edit.deleteLater()
            label.show()

        def key_press(event):
            if event.key() == Qt.Key_Escape:
                cancel()
            else:
                QLineEdit.keyPressEvent(edit, event)
        edit.keyPressEvent = key_press

        def commit():
            new_name = edit.text().strip()
            if new_name and new_name != name and new_name not in self.globs.ledger:
                rebuilt = {}
                for key, value in self.globs.ledger.items():
                    rebuilt[new_name if key == name else key] = value
                self.globs.ledger = rebuilt
                save_ledger(self.globs)
                label.setText(new_name)
                frame.account_name = new_name
            if getattr(frame, "delete_btn", None):
                frame.delete_btn.deleteLater()
                frame.delete_btn = None
            edit.deleteLater()
            label.show()

        edit.returnPressed.connect(commit)

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

    def _edit_balance(self, frame):
        label = frame.balance_label
        label.hide()

        edit = QLineEdit()
        edit.setFixedHeight(32)
        edit.setFixedWidth(140)
        edit.setStyleSheet("""
            QLineEdit {
                background-color: #333339;
                color: white;
                border: 1px solid #505055;
                border-radius: 6px;
                padding: 0 10px 0 28px;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #2ecc71; }
        """)

        dollar = QLabel("$", edit)
        dollar.setGeometry(8, 0, 14, 32)
        dollar.setAlignment(Qt.AlignCenter)
        dollar.setStyleSheet("color: #888888; font-size: 14px; border: none; background: transparent;")

        edit.textEdited.connect(lambda _t: self._format_amount_live(edit))
        edit.editingFinished.connect(lambda: self._format_amount_final(edit))
        edit.setValidator(QRegularExpressionValidator(
            QRegularExpression(r"-?\d{1,7}(\.\d{1,2})?"), edit))

        frame.layout().insertWidget(frame.layout().indexOf(label), edit)

        current = self.globs.ledger[frame.account_name].get("starting_balance", 0)
        edit.setText(f"{current:,.2f}")
        edit.setFocus()
        edit.selectAll()

        edit.setFocus()

        name = frame.account_name

        def refresh():
            balance = self.globs.ledger[name].get("starting_balance", 0)
            label.setText(f"Starting Balance: ${balance:,.2f}")

        def commit():
            try:
                value = float(edit.text().replace(",", "") or 0)
            except ValueError:
                value = 0.0
            self.globs.ledger[name]["starting_balance"] = value
            save_ledger(self.globs)
            refresh()
            edit.deleteLater()
            label.show()

        def cancel():
            edit.deleteLater()
            label.show()

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
                if edit.isVisible():
                    cancel()
            QTimer.singleShot(0, check)

        edit.focusOutEvent = custom_focus_out
        edit.returnPressed.connect(commit)

    def _delete_account(self, name, frame):
        confirm = QMessageBox.question(
            self,
            "Delete Account",
            f'Delete "{name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return

        del self.globs.ledger[name]
        save_ledger(self.globs)
        frame.deleteLater()

    def _add_account(self):
        """Inline frame for entering a new account name + starting balance."""
        self.add_btn.hide()

        edit_frame = QFrame()
        edit_frame.setMaximumWidth(450)
        edit_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 8px;
            }
        """)

        edit_layout = QVBoxLayout(edit_frame)
        edit_layout.setContentsMargins(12, 12, 12, 12)

        name_edit = QLineEdit()
        name_edit.setPlaceholderText("New account name...")
        name_edit.setStyleSheet("""
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

        name_label = QLabel("Account Name")
        name_label.setStyleSheet("color: #999999; font-size: 12px; background: transparent; border: none;")
        edit_layout.addWidget(name_label)
        edit_layout.addWidget(name_edit)

        balance_edit = QLineEdit()
        balance_edit.setFixedHeight(32)
        balance_edit.setFixedWidth(140)

        balance_edit.setStyleSheet("""
            QLineEdit {
                background-color: #333339;
                color: white;
                border: 1px solid #505055;
                border-radius: 6px;
                padding: 0 10px 0 28px;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #2ecc71; }
        """)

        dollar = QLabel("$", balance_edit)
        dollar.setGeometry(8, 0, 14, 32)
        dollar.setAlignment(Qt.AlignCenter)
        dollar.setStyleSheet("color: #888888; font-size: 14px; border: none; background: transparent;")

        balance_edit.textEdited.connect(lambda _t: self._format_amount_live(balance_edit))
        balance_edit.editingFinished.connect(lambda: self._format_amount_final(balance_edit))

        name_edit.textEdited.connect(lambda _t: validate())
        balance_edit.textEdited.connect(lambda _t: validate())

        # Only digits, optional leading minus, optional 2-decimal fraction
        amount_regex = QRegularExpression(r"-?\d{1,7}(\.\d{1,2})?")
        balance_edit.setValidator(QRegularExpressionValidator(amount_regex, balance_edit))

        bal_label = QLabel("Starting Balance")
        bal_label.setStyleSheet("color: #999999; font-size: 12px; background: transparent; border: none;")
        edit_layout.addWidget(bal_label)
        edit_layout.addWidget(balance_edit)

        def commit():
            name = name_edit.text().strip()
            accounts = self.globs.ledger
            if name and name not in accounts:
                # Blank or invalid balance stays 0
                try:
                    balance = float(balance_edit.text().replace(",", "") or 0)
                except ValueError:
                    balance = 0.0

                accounts[name] = {
                    "starting_balance": balance,
                    "transactions": []
                }
                save_ledger(self.globs)

                section = self._create_account_section(
                    name, accounts[name])
                self.accounts_layout.addWidget(section)

            edit_frame.deleteLater()
            self.add_btn.show()

        def cancel():
            edit_frame.deleteLater()
            self.add_btn.show()

        def key_press(event, widget):
            if event.key() == Qt.Key_Escape:
                cancel()
            else:
                QLineEdit.keyPressEvent(widget, event)

        name_edit.keyPressEvent = lambda e: key_press(e, name_edit)
        balance_edit.keyPressEvent = lambda e: key_press(e, balance_edit)

        name_edit.returnPressed.connect(balance_edit.setFocus)
        balance_edit.returnPressed.connect(commit)

        self.accounts_layout.addWidget(edit_frame)

        def validate():
            name = name_edit.text().strip()
            ok = bool(name) and name not in self.globs.ledger and bool(balance_edit.text().strip())
            commit_btn.setEnabled(ok)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 8, 0, 0)

        commit_btn = QPushButton("Add")
        commit_btn.setCursor(Qt.PointingHandCursor)
        commit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; color: white;
                border: none; border-radius: 6px;
                padding: 6px 16px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #3a3a3f; color: #777777;
            }
        """)
        commit_btn.clicked.connect(commit)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3f; color: #dddddd;
                border: 1px solid #505055; border-radius: 6px;
                padding: 6px 16px; font-size: 13px;
            }
            QPushButton:hover { color: #e74c3c; border-color: #e74c3c; }
        """)
        cancel_btn.clicked.connect(cancel)

        btn_row.addWidget(commit_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        edit_layout.addLayout(btn_row)
        validate()
        name_edit.setFocus()

    def _format_amount_live(self, edit):
        """Live formatting: one optional leading minus, digits, 2 decimals, commas."""
        raw = edit.text().replace(",", "")

        if not raw:
            return

        # Peel off a single leading minus (max one)
        negative = raw.startswith("-")
        if negative:
            raw = raw[1:]
            if not raw:
                return  # lone dash typed

        # Reject anything that's not digits and at most one dot
        if not raw.replace(".", "").isdigit():
            clean = "".join(c for c in raw if c.isdigit() or c == ".")
            clean = ("-" if negative else "") + clean
            pos = edit.cursorPosition()
            edit.blockSignals(True)
            edit.setText(clean)
            edit.setCursorPosition(max(0, min(pos - 1, len(clean))))
            edit.blockSignals(False)
            return

        if raw.count(".") > 1:
            pos = edit.cursorPosition()
            clean = ("-" if negative else "") + raw[:pos]
            edit.blockSignals(True)
            edit.setText(clean)
            edit.setCursorPosition(len(clean))
            edit.blockSignals(False)
            return

        whole, dot, frac = raw.partition(".")

        # Leading zeros: only "0" alone
        if whole and len(whole) > 1 and whole[0] == "0":
            whole = whole.lstrip("0") or "0"

        # Max 2 decimals
        if len(frac) > 2:
            frac = frac[:2]

        new_text = whole + (dot + frac if dot else "")
        if whole:
            new_text = f"{int(whole):,}" + (dot + frac if dot else "")

        # Re-attach the minus
        if negative:
            new_text = "-" + new_text

        if new_text != edit.text():
            pos = edit.cursorPosition()
            edit.blockSignals(True)
            edit.setText(new_text)
            offset = new_text.count(",")
            edit.setCursorPosition(min(pos + offset, len(new_text)))
            edit.blockSignals(False)

    def _format_amount_final(self, edit):
        """On blur: force exactly 2 decimal places (negatives preserved)."""
        raw = edit.text().replace(",", "")
        if not raw or raw == "-":
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
