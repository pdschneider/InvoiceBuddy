# src/interface/setup/setup_wizard.py
from PySide6.QtWidgets import (QWizard, QWizardPage,
                               QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout,
                               QLineEdit, QRadioButton,
                               QCheckBox, QScrollArea,
                               QWidget)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from src.utils.load_settings import load_data_path, load_paths
from src.utils.save_settings import save_settings, save_paths
from src.utils.save_qt import save_sheets, load_settings
from src.managers.file_management import browse_directory
from src.qt_interface.qt_settings.qt_spreadsheet import (
    populate_sheets_list, on_add_sheet)
from src.qt_interface.qt_styles import dark
import logging
import os


class WelcomePage(QWizardPage):
    """The welcome page describing the app."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Welcome to Invoice Buddy")
        self.setSubTitle("A financial management app that makes data entry easier")
        self.setPixmap(QWizard.LogoPixmap, QPixmap("defaults/assets/icon.ico"))

        layout = QVBoxLayout()
        self.setLayout(layout)

        welcome_note = QLabel(
            "Thank you for installing Invoice Buddy!\n\n"
            "Invoice Buddy is designed to make the invoice entry process easier. "
            "Instead of manually writing each filename and then entering the "
            "necessary data into your spreadsheet, the application takes care "
            "of it for you.")
        welcome_note.setWordWrap(True)
        layout.addWidget(welcome_note)


class MethodPage(QWizardPage):
    """The page where the user chooses recommended or custom settings."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Installation Method")
        self.setSubTitle("Choose how you would like to set up Invoice Buddy")
        self.setPixmap(QWizard.LogoPixmap, QPixmap("defaults/assets/icon.ico"))

        layout = QVBoxLayout()
        self.setLayout(layout)

        rec_note = QLabel(
            "Recommended for most users: a standard inbox and archive "
            "folder are created for you, and update checks keep you "
            "running the latest version.")
        rec_note.setWordWrap(True)
        layout.addWidget(rec_note)

        self.default_radio = QRadioButton("Recommended Settings")
        self.default_radio.setStyleSheet("padding-left: 25px;")
        self.default_radio.setChecked(True)  # Defaults to the recommended option
        layout.addWidget(self.default_radio)

        self.privacy_checkbox = QCheckBox("Disable automatic update checks")
        self.privacy_checkbox.setStyleSheet("padding-left: 50px;")
        layout.addWidget(self.privacy_checkbox)

        layout.addSpacing(20)  # Visual separation between the two options

        custom_note = QLabel(
            "Custom lets you choose your own folder paths, adjust settings, "
            "add team members, and configure sheets yourself.")
        custom_note.setWordWrap(True)
        layout.addWidget(custom_note)

        self.custom_radio = QRadioButton("Custom Settings")
        self.custom_radio.setStyleSheet("padding-left: 25px;")
        layout.addWidget(self.custom_radio)

        # Disable the privacy checkbox when Custom is selected
        self.default_radio.toggled.connect(
            lambda checked: self.privacy_checkbox.setEnabled(checked))

        # Page ID to jump to when "Default" is chosen (set by create_wizard)
        self.skip_to = None

    def nextId(self):
        if self.default_radio.isChecked() and self.skip_to is not None:
            return self.skip_to
        return super().nextId() 


class CustomPathsPage(QWizardPage):
    """Inbox and archive folder paths."""
    def __init__(self, globs, parent=None):
        super().__init__(parent)
        self.globs = globs  # Kept for when we wire the Browse buttons
        self.setTitle("Custom Paths")
        self.setSubTitle("Choose where Invoice Buddy looks for files")
        self.setPixmap(QWizard.LogoPixmap, QPixmap("defaults/assets/icon.ico"))

        layout = QVBoxLayout()
        self.setLayout(layout)

        note = QLabel(
            "Leave a field blank to use the default location.")
        note.setWordWrap(True)
        layout.addWidget(note)

        # ===== Inbox row =====
        inbox_row = QHBoxLayout()
        inbox_row.setSpacing(10)

        inbox_label = QLabel("Inbox:")
        inbox_row.addWidget(inbox_label)

        self.inbox_entry = QLineEdit()
        if globs.inbox:
            self.inbox_entry.setPlaceholderText(globs.inbox)
        else:
            self.inbox_entry.setPlaceholderText(
                os.path.normpath(load_data_path("local", "Inbox")))
        inbox_row.addWidget(self.inbox_entry)

        inbox_browse = QPushButton("Browse")
        inbox_browse.setFixedWidth(90)
        inbox_browse.clicked.connect(
            lambda: browse_directory(globs, self.inbox_entry))
        inbox_row.addWidget(inbox_browse)

        layout.addLayout(inbox_row)

        # ===== Archive row =====
        archive_row = QHBoxLayout()
        archive_row.setSpacing(10)

        archive_label = QLabel("Archive:")
        archive_row.addWidget(archive_label)

        self.archive_entry = QLineEdit()
        if globs.archive:
            self.archive_entry.setPlaceholderText(globs.archive)
        else:
            self.archive_entry.setPlaceholderText(
                os.path.normpath(load_data_path("local", "Archive")))
        archive_row.addWidget(self.archive_entry)

        archive_browse = QPushButton("Browse")
        archive_browse.setFixedWidth(90)
        archive_browse.clicked.connect(
            lambda: browse_directory(globs, self.archive_entry))
        archive_row.addWidget(archive_browse)

        layout.addLayout(archive_row)


class SheetsPage(QWizardPage):
    """Custom mode: configure the sheets Invoice Buddy writes to."""
    def __init__(self, globs, parent=None):
        super().__init__(parent)
        self.globs = globs
        self.setTitle("Sheets")
        self.setSubTitle("Choose the spreadsheets and tabs Invoice Buddy writes to")
        self.setPixmap(QWizard.LogoPixmap, QPixmap("defaults/assets/icon.ico"))

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Scrollable area holding the sheet rows
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setStyleSheet(
            "QScrollArea { background-color: transparent; border: none; }")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 10, 0, 10)
        scroll_layout.setSpacing(8)
        scroll_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area, stretch=1)

        # Redirect sheet rows into THIS wizard while it's open (modal, so safe)
        self._previous_layout = getattr(globs, "sheets_scroll_layout", None)
        globs.sheets_scroll_layout = scroll_layout

        add_button = QPushButton("+ Add New Sheet")
        add_button.clicked.connect(lambda: on_add_sheet(globs))
        layout.addWidget(add_button)

        populate_sheets_list(globs)


class BuddiesPage(QWizardPage):
    """Custom mode: optional shared folders for other people."""
    def __init__(self, globs, parent=None):
        super().__init__(parent)
        self.globs = globs
        self.setTitle("Team Members")
        self.setSubTitle("Optional: watch extra folders for family or coworkers")
        self.setPixmap(QWizard.LogoPixmap, QPixmap("defaults/assets/icon.ico"))

        layout = QVBoxLayout()
        self.setLayout(layout)

        note = QLabel(
            "Buddies allows teams or family members to manage their spreadsheets together.\n\n"
            "For example, if a family member or coworker has their own inbox set up with "
            "Invoice Buddy, add that folder here to pass on invoices or receipts to them "
            "for further processing.\n\nLeave this empty if it's just you.")
        note.setWordWrap(True)
        layout.addWidget(note)

        # Rows get inserted here
        self.buddy_container = QWidget()
        self.buddy_container_layout = QVBoxLayout(self.buddy_container)
        self.buddy_container_layout.setContentsMargins(0, 0, 0, 0)
        self.buddy_container_layout.setSpacing(8)
        self.buddy_container_layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.buddy_container)

        self.buddy_entries = []
        self.max_buddies = 3

        self.buddy_add_btn = QPushButton("+ Add Buddy")
        self.buddy_add_btn.setFixedWidth(120)
        self.buddy_add_btn.setStyleSheet(dark.browse_button)
        self.buddy_add_btn.setCursor(Qt.PointingHandCursor)
        self.buddy_add_btn.clicked.connect(lambda: self.add_buddy())
        layout.addWidget(self.buddy_add_btn)

        # Populate existing buddies from saved config
        if hasattr(globs, 'buddies') and globs.buddies:
            candidates = [(k, v) for k, v in globs.buddies.items()
                          if k != "inbox"][:self.max_buddies]
            for name, path in candidates:
                self.add_buddy()
                latest = self.buddy_entries[-1]
                latest["name_input"].setText(name)
                latest["path_input"].setText(path)

        layout.addStretch()

    def add_buddy(self):
        """Create a new buddy row: name, path, browse, remove."""
        if len(self.buddy_entries) >= self.max_buddies:
            return

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Buddy name")
        name_input.setFixedWidth(120)
        name_input.setStyleSheet(dark.line_edit)
        row_layout.addWidget(name_input)

        path_input = QLineEdit()
        path_input.setPlaceholderText("Folder path...")
        path_input.setStyleSheet(dark.line_edit)
        row_layout.addWidget(path_input)

        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(100)
        browse_btn.setStyleSheet(dark.browse_button)
        browse_btn.clicked.connect(
            lambda: browse_directory(self.globs, path_input))
        row_layout.addWidget(browse_btn)

        remove_btn = QPushButton("-")
        remove_btn.setFixedWidth(30)
        remove_btn.setStyleSheet(dark.minus_button)
        remove_btn.clicked.connect(lambda checked, r=row: self.remove_buddy(r))
        row_layout.addWidget(remove_btn)

        self.buddy_container_layout.addWidget(row)
        self.buddy_entries.append({
            "frame": row,
            "name_input": name_input,
            "path_input": path_input
        })

        if len(self.buddy_entries) >= self.max_buddies:
            self.buddy_add_btn.hide()

    def remove_buddy(self, row):
        """Remove a buddy row and clean up."""
        for entry in self.buddy_entries[:]:
            if entry["frame"] == row:
                row.deleteLater()
                self.buddy_entries.remove(entry)
                break

        if len(self.buddy_entries) < self.max_buddies:
            self.buddy_add_btn.show()


class SettingsPage(QWizardPage):
    """Custom mode: general settings checkboxes."""
    def __init__(self, globs, parent=None):
        super().__init__(parent)
        self.globs = globs
        self.setTitle("Settings")
        self.setSubTitle("Choose how Invoice Buddy behaves")
        self.setPixmap(QWizard.LogoPixmap, QPixmap("defaults/assets/icon.ico"))

        layout = QVBoxLayout()
        self.setLayout(layout)

        note = QLabel(
            "These settings can be changed anytime later from the "
            "settings panel.")
        note.setWordWrap(True)
        layout.addWidget(note)

        self.updates_checkbox = QCheckBox("Check for Updates on Startup")
        self.updates_checkbox.setChecked(globs.github_check)
        layout.addWidget(self.updates_checkbox)

        self.beta_checkbox = QCheckBox("Include Beta Updates")
        self.beta_checkbox.setChecked(globs.beta)
        layout.addWidget(self.beta_checkbox)

        self.window_checkbox = QCheckBox("Use Saved Window Placement")
        self.window_checkbox.setChecked(globs.dynamic_window_size)
        layout.addWidget(self.window_checkbox)

        layout.addStretch()


class ThankYouPage(QWizardPage):
    """The thank you page at the end of the wizard."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Thank You!")
        self.setSubTitle("Invoice Buddy is ready to use")
        self.setPixmap(QWizard.LogoPixmap, QPixmap("defaults/assets/icon.ico"))

        layout = QVBoxLayout()
        self.setLayout(layout)

        thanks_note = QLabel(
            "Setup is complete. You can revisit this wizard anytime from "
            "Help > Wizard in the title bar to reconfigure Invoice Buddy.")
        thanks_note.setWordWrap(True)
        layout.addWidget(thanks_note)


def _save_from_wizard(
        globs,
        inbox="",
        archive="",
        buddies=None,
        github_check=None,
        beta=None,
        dynamic_window_size=None):
    """Commit wizard-collected data to disk."""
    # Resolve paths: explicit value > existing > default
    new_inbox = inbox or globs.inbox or os.path.normpath(
        load_data_path("local", "Inbox"))
    new_archive = archive or globs.archive or os.path.normpath(
        load_data_path("local", "Archive"))

    # Ensure folders exist
    try:
        os.makedirs(new_inbox, exist_ok=True)
        os.makedirs(new_archive, exist_ok=True)
    except OSError as e:
        logging.error(f"Could not create wizard paths: {e}")

    # Update globs
    globs.inbox = new_inbox
    globs.archive = new_archive

    # Guarantee every sheet has a workbook to write to
    _backfill_default_workbooks(globs)

    # Merge and write paths.json
    current_paths, _ = load_paths()
    current_paths["inbox"] = new_inbox
    current_paths["archive"] = new_archive

    if buddies is not None:
        # Sanitize and validate buddy rows from the wizard
        new_buddies = {}
        buddy_counter = 0
        for entry in buddies:
            name = entry["name_input"].text().strip()[:9]
            path = entry["path_input"].text().strip()
            if name.lower() == "inbox":
                buddy_counter += 1
                name = f"inbox-{buddy_counter}"
                logging.warning("Buddy name cannot be 'inbox'. Sanitizing...")
            if name and path and os.path.isdir(path):
                new_buddies[name] = path
    else:
        _, new_buddies = load_paths()

    save_paths(globs, sources=current_paths, buddies=new_buddies)
    logging.info("Wizard paths saved.")

    # Merge and write settings.json if any settings were provided
    if github_check is not None or beta is not None or dynamic_window_size is not None:
        current_settings = load_settings()
        if github_check is not None:
            current_settings["github_check"] = github_check
        if beta is not None:
            current_settings["beta"] = beta
        if dynamic_window_size is not None:
            current_settings["dynamic_window_size"] = dynamic_window_size
        current_settings["previous_version"] = globs.current_version
        save_settings(**current_settings)
        logging.info("Wizard settings saved.")

    save_sheets(globs)


def _backfill_default_workbooks(globs):
    """Point workbook-less sheets at the OS-appropriate default spreadsheet."""
    default_name = ("default_spreadsheet.xlsx"
                    if globs.os_name.startswith("Windows")
                    else "default_spreadsheet.ods")
    default_workbook = os.path.normpath(load_data_path("local", default_name))

    for sheet in globs.sheet_data.get("sheets", []):
        if not sheet.get("workbook"):
            sheet["workbook"] = default_workbook


def create_wizard(globs):
    """Opens the wizard window."""
    # Create Wizard Window
    wizard = QWizard()
    wizard.setWindowTitle("Invoice Buddy Setup")
    wizard.resize(650, 600)

    # Force a consistent look
    wizard.setWizardStyle(QWizard.ClassicStyle)

    # "Cancel" becomes "Skip" on first run
    if globs.previous_version == "0.1.0":
        wizard.setButtonText(QWizard.CancelButton, "Skip")

    # Welcome Page
    wizard.addPage(WelcomePage())

    # Method Page
    method_page = MethodPage()
    wizard.addPage(method_page)

    # Custom Paths Page
    paths_page = CustomPathsPage(globs)
    wizard.addPage(paths_page)

    # Sheets Page
    sheets_page = SheetsPage(globs)
    wizard.addPage(sheets_page)

    # Buddies Page
    buddies_page = BuddiesPage(globs)
    wizard.addPage(buddies_page)

    # Settings Page
    settings_page = SettingsPage(globs)
    wizard.addPage(settings_page)

    # Thank You Page
    thank_you_id = wizard.addPage(ThankYouPage())

    # Set the skip target dynamically
    method_page.skip_to = thank_you_id

    # Execute Wizard
    result = wizard.exec()

    # Restore the settings panel's layout and rebuild its rows
    globs.sheets_scroll_layout = sheets_page._previous_layout
    if globs.sheets_scroll_layout is not None:
        populate_sheets_list(globs)

    # Handle wizard completion based on selection
    if result == QWizard.Accepted:
        
        if method_page.default_radio.isChecked():
            # Recommended mode: apply privacy preference
            logging.info("Recommended settings chosen")

            # Update github_check based on privacy checkbox (True = disable updates)
            globs.github_check = not method_page.privacy_checkbox.isChecked()

            # Paths: fall back to existing/default (nothing to override)
            _save_from_wizard(
                globs,
                github_check=globs.github_check)
        else:
            # Custom mode: harvest page data and save
            logging.info("Custom settings chosen")
            _save_from_wizard(
                globs,
                inbox=str(paths_page.inbox_entry.text()).strip(),
                archive=str(paths_page.archive_entry.text()).strip(),
                buddies=buddies_page.buddy_entries,
                github_check=settings_page.updates_checkbox.isChecked(),
                beta=settings_page.beta_checkbox.isChecked(),
                dynamic_window_size=settings_page.window_checkbox.isChecked())

    if result == QWizard.Rejected:
        logging.info("Wizard cancelled or skipped")
