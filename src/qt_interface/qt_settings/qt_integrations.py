# src/qt_interface/qt_settings/qt_integrations.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QFileDialog, QLineEdit
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
import webbrowser
import threading
import logging
import os
from src.connections.alphabet import (
    google_connect, list_spreadsheets, delete_token, has_saved_token
)


class AuthWorker(QThread):
    """Runs the Google OAuth flow off the main thread."""

    success = Signal(object)   # emits the gspread client
    failed = Signal(str)       # emits an error message
    stopped = Signal()         # emitted when user cancels

    def __init__(self, secrets_path):
        super().__init__()
        self.secrets_path = secrets_path
        self.cancel_flag = threading.Event()  # new: signals for cancellation

    def run(self):
        try:
            client = google_connect(self.secrets_path, cancel_event=self.cancel_flag)
            if client:
                self.success.emit(client)
            elif self.cancel_flag.is_set():
                self.stopped.emit()
            else:
                self.failed.emit("Authentication failed. Check the logs.")
        except Exception as e:
            self.failed.emit(str(e))


class GoogleSheetsCard(QWidget):
    """Collapsible card for the Google Sheets integration."""

    def __init__(self, globs):
        super().__init__()
        self.setObjectName("googleCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.globs = globs
        self.expanded = False

        self.setStyleSheet("""
            #googleCard {
                background-color: #252528;
                border: 2px solid #444;
                border-radius: 8px;
            }
            #googleCard:hover {
                background-color: #2e2e35;
                border: 2px solid #2ecc71;
            }
        """)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(15, 15, 15, 15)
        outer_layout.setSpacing(10)

        # ===== HEADER (clickable) =====
        self.header = QFrame()
        self.header.setFrameShape(QFrame.NoFrame)
        self.header.setStyleSheet("background-color: transparent;")
        self.header.setCursor(Qt.PointingHandCursor)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        gs_title = QLabel("Google Sheets")
        gs_title.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(gs_title)

        self.status_label = QLabel("Not Connected")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()

        self.chevron = QLabel("▸")
        self.chevron.setStyleSheet("color: #888; font-size: 14px;")
        header_layout.addWidget(self.chevron)

        self.header.mousePressEvent = lambda event: self.toggle()
        outer_layout.addWidget(self.header)

        # Description visible in both collapsed and expanded states
        self.desc_label = QLabel(
            "Link a Google account to sync transactions to Google Sheets "
            "workbooks. Requires OAuth setup.")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #aaa; font-size: 12px; background-color: transparent;")
        outer_layout.addWidget(self.desc_label)
        self.desc_label.mousePressEvent = lambda event: self.toggle()

        # ===== BODY (hidden until expanded) =====
        self.body = QWidget()
        self.body.setStyleSheet("background-color: transparent;")
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 10, 0, 0)
        self.body_layout.setSpacing(10)

        # ===== EXPANDED CONTENT =====
        self.instructions = QLabel(
            "1. Go to <a href='https://console.cloud.google.com/apis/credentials' "
            "style='color: #3498db; text-decoration: underline;'>Google Cloud Console</a><br>"
            "2. Create a project &amp; enable the Sheets and Drive APIs<br>"
            "3. Create OAuth Desktop credentials<br>"
            "4. Download your client_secrets.json file"
        )
        self.instructions.setTextFormat(Qt.RichText)
        self.instructions.setWordWrap(True)
        self.instructions.setStyleSheet(
            "color: #ddd; font-size: 12px; background-color: transparent;")
        self.instructions.linkActivated.connect(
            lambda url: webbrowser.open(url))
        self.body_layout.addWidget(self.instructions)

        # ===== FILE PICKER ROW =====
        file_row = QHBoxLayout()

        self.path_entry = QLineEdit()
        self.path_entry.setPlaceholderText("Path to client_secrets.json")
        self.path_entry.setFixedHeight(36)
        self.path_entry.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a40; border: 1px solid #555;
                border-radius: 4px; padding: 0 10px; color: white; font-size: 12px;
            }
            QLineEdit:focus { border: 1px solid #2ecc71; }
        """)
        file_row.addWidget(self.path_entry, stretch=1)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setFixedHeight(36)
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #444; color: white; border: none;
                border-radius: 4px; font-size: 12px;
            }
            QPushButton:hover { background-color: #555; }
        """)
        self.browse_btn.setCursor(Qt.PointingHandCursor)
        self.browse_btn.clicked.connect(self._browse_for_file)
        file_row.addWidget(self.browse_btn)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedHeight(36)
        self.connect_btn.setFixedWidth(90)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; color: white; border: none;
                border-radius: 4px; font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #27ae60; }
            QPushButton:disabled { background-color: #555; color: #888; }
        """)
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.setEnabled(False)
        self.connect_btn.clicked.connect(self._start_connect)
        file_row.addWidget(self.connect_btn)

        self.body_layout.addLayout(file_row)
        self.path_entry.textChanged.connect(self._validate_path)

        # ===== DISCONNECT BUTTON (hidden until connected) =====
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setFixedHeight(36)
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white; border: none;
                border-radius: 4px; font-size: 12px; font-weight: bold;
                padding: 0 15px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.disconnect_btn.setCursor(Qt.PointingHandCursor)
        self.disconnect_btn.clicked.connect(self._disconnect)
        self.disconnect_btn.hide()
        self.body_layout.addWidget(self.disconnect_btn)

        # ===== RESULT LABEL =====
        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("color: #aaa; font-size: 11px; background-color: transparent;")
        self.body_layout.addWidget(self.result_label)

        self.body.hide()
        outer_layout.addWidget(self.body)

        # Whole card is clickable when collapsed
        self.setCursor(Qt.PointingHandCursor)

        # Restore UI state from saved globs
        if getattr(globs, 'google_auth', False) or has_saved_token():
            self._apply_connected_state()

    def toggle(self):
        self.expanded = not self.expanded
        self.body.setVisible(self.expanded)
        self.chevron.setText("▾" if self.expanded else "▸")

    def _apply_connected_state(self):
        """Put the card into connected mode (used at startup and on success)."""
        self.status_label.setText("Connected ✓")
        self.status_label.setStyleSheet("color: #2ecc71; font-size: 12px;")
        self.path_entry.hide()
        self.browse_btn.hide()
        self.connect_btn.hide()
        self.disconnect_btn.show()

    def _start_connect(self):
        """Begin the OAuth flow using the path from the text box."""
        path = self.path_entry.text().strip()
        if not path or not os.path.isfile(path):
            return

        # Lock the UI while auth runs in the background
        self.browse_btn.setEnabled(False)
        self.browse_btn.hide()  # hide the browse button

        # Small cancel button next to the result label
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(26)
        self.cancel_btn.setFixedWidth(70)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white; border: none;
                border-radius: 4px; font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self._cancel_auth)
        self.body_layout.addWidget(self.cancel_btn)

        # Update status label
        self.result_label.setText("Complete the sign-in in your browser...")
        self.result_label.setStyleSheet("color: #3498db; font-size: 11px; background-color: transparent;")

        # Spin up the worker thread
        self.worker = AuthWorker(path)
        self.worker.success.connect(self._on_auth_success)
        self.worker.failed.connect(self._on_auth_failed)
        self.worker.stopped.connect(self._on_auth_stopped)
        self.worker.start()

        # Lock controls while auth is in progress
        self.connect_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.path_entry.setEnabled(False)

    def _browse_for_file(self):
        """Pick the secrets file and show the path in the text box."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select client_secrets.json",
            os.path.expanduser("~"),
            "JSON Files (*.json)"
        )
        if path:
            self.path_entry.setText(path)
            self._validate_path()

    def _validate_path(self):
        """Enable Connect only when the textbox points to a real file."""
        path = self.path_entry.text().strip()
        valid = bool(path) and os.path.isfile(path)
        self.connect_btn.setEnabled(valid)
        if valid:
            self.result_label.setText(f"File found: {os.path.basename(path)}")
            self.result_label.setStyleSheet("color: #2ecc71; font-size: 11px; background-color: transparent;")
        else:
            self.result_label.setText("")

    def _on_auth_success(self, client):
        """Runs on the main thread when OAuth completes."""
        sheets = list_spreadsheets(client, limit=3)
        if sheets:
            sheet_list = "<br>".join(f"• {s}" for s in sheets)
            self.result_label.setText(f"✅ Connected!<br>{sheet_list}")
        else:
            self.result_label.setText("✅ Connected!")
        self.result_label.setStyleSheet("color: #2ecc71; font-size: 11px; background-color: transparent;")

        self.status_label.setText("Connected ✓")
        self.status_label.setStyleSheet("color: #2ecc71; font-size: 12px;")

        self._reset_ui(self.result_label.text())

        self.globs.google_auth = True
        self._apply_connected_state()

    def _on_auth_failed(self, error_msg):
        """Runs on the main thread when OAuth fails."""
        self.result_label.setText(f"❌ Connection failed: {error_msg}")
        self.result_label.setStyleSheet("color: #e74c3c; font-size: 11px; background-color: transparent;")
        self._reset_ui(self.result_label.text())

    def _disconnect(self):
        """Delete the token and restore the connect UI."""
        self.globs.google_auth = False
        delete_token()
        self.path_entry.show()
        self.browse_btn.show()
        self.connect_btn.show()
        self.disconnect_btn.hide()
        self.status_label.setText("Not Connected")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        self.result_label.setText("")

    def _on_auth_stopped(self):
        """Runs on the main thread when user cancels auth."""
        self._reset_ui("Connection cancelled.")
        self.result_label.setStyleSheet("color: #e74c3c; font-size: 11px; background-color: transparent;")

    def _enable_reopen_button(self):
        """Enable the reopen button once the auth URL is available."""
        if hasattr(self, 'btn_row_widget'):
            self.reopen_btn.setEnabled(True)

    def _cancel_auth(self):
        """Flag the worker to stop; UI cleanup happens via the stopped signal."""
        if hasattr(self, 'worker'):
            self.worker.cancel_flag.set()

    def _reopen_auth_url(self):
        """Open the latest auth URL again."""
        from src.connections.alphabet import CURRENT_AUTH_URL
        if CURRENT_AUTH_URL:
            webbrowser.open(CURRENT_AUTH_URL)
        else:
            logging.warning("No auth URL available yet.")

    def _reset_ui(self, msg):
        """Reset the UI after auth ends."""
        self.cancel_btn.deleteLater()
        self.browse_btn.show()
        self.browse_btn.setEnabled(True)
        self.result_label.setText(msg)
        self.result_label.setStyleSheet("color: #aaa; font-size: 11px; background-color: transparent;")
        self.connect_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.path_entry.setEnabled(True)


def create_integrations_settings_tab(globs):
    """Create the Integrations settings tab."""

    tab_widget = QWidget()
    layout = QVBoxLayout(tab_widget)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)
    layout.setAlignment(Qt.AlignTop)

    # ==================== TITLE ====================
    title = QLabel("Integrations")
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 5px;")
    layout.addWidget(title)

    # ==================== GOOGLE SHEETS CARD ====================
    card = GoogleSheetsCard(globs)
    layout.addWidget(card)

    return tab_widget
