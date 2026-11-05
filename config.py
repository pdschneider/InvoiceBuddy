# config
import platform
import getpass
import os
import sys
import hashlib
import threading
import customtkinter as ctk
from version import __version__
from PySide6.QtWidgets import QApplication, QMainWindow
from src.utils.load_settings import (
    load_settings, load_data_path, load_paths,
    load_sheets, load_counterparties, load_categories
)


# Globs Class
class Globs:
    """A class to hold all configuration and UI variables for InvoiceBuddy."""
    def __init__(self):
        """Initialize settings from load_settings"""
        self.refresh_globs()
        self.refresh_counterparties()
        self.refresh_categories()
        self.observers = {}

        # Current Version
        self.current_version = __version__

        # Global Variables
        self.os_name = platform.system()
        self.user = getpass.getuser()
        self.hashed_user = hashlib.md5(self.user.encode()).hexdigest()

        # Bundled Flags
        self.pyinstaller_bundle = getattr(sys, 'frozen', False)
        self.is_bundled = self.pyinstaller_bundle

        # Folder mappings and paths
        self.sources, self.buddies = load_paths()

        # PySide6 Widgets
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.mailbox = NotImplemented
        self.preview_pane = None
        self.preview_placeholder = None
        self.pill_bar = None
        self.pill_layout = None
        self.pdf_viewer = None
        self.github_check_checkbox = None
        self.beta_checkbox = None
        self.window_checkbox = None
        self.printer_combo = None  # The combobox that stores the printer value
        self.logging_level_box = None
        self.inbox_entry_box = None
        self.archive_entry_box = None
        self.spreadsheet_toggle = None
        self.dim_overlay = None
        self.autoname_curtain = None
        self.active_source_dialog = None
        self.file_menu = None
        self.rebuild_file_menu = None
        self.transaction_editor = None
        self.page_stack = None
        self.selected_file = None
        self.place_curtain = None

        # PySide6 Inbox
        self.files = []  # ALL filenames without extensions in inbox
        self.checked_files = None  # ONLY the filenames of checked entries

        # App Path
        self.app_path = get_executable_path()
        self.app_type = None

        # Locks
        self.edit_lock = threading.Lock()

        # UI variables
        self.root = ctk.CTk(className="invoice-buddy")
        self.notebook = None
        self.main_frame = None
        self.main_page = None
        self.changelog = None
        self.settings_page = None
        self.onboarding_page = None
        self.send_buttons_frame = None
        self.refresh_send_buttons = None
        self.process_buttons_frame = None
        self.title = None
        self.file_identity = {}
        self.theme_dict = None
        self.theme_path = None
        self.inbox_button = None
        self.settings_button = None
        self.invoice_sheet_label = None
        self.card_sheet_label = None
        self.po_sheet_label = None

        # Icons
        self.icon = None
        self.inbox_icon = None
        self.settings_icon = None
        self.add_icon = None
        self.auto_icon = None
        self.enter_icon = None
        self.archive_icon = None
        self.inbox_folder_icon = None
        self.workbook_icon = None
        self.delete_icon = None
        self.send_icon = None
        self.import_icon = None
        self.export_icon = None
        self.theme_icon = None
        self.preferences_icon = None
        self.note_icon = None
        self.config_icon = None
        self.garbage_icon = None
        self.print_icon = None
        self.printer_icon = None
        self.notification_icon = None
        self.windows_icon = None
        self.github_icon = None
        self.github_light_icon = None
        self.codeberg_icon = None
        self.mail_icon = None

        # Treeview Icons
        self.invoice_icon = None
        self.card_icon = None
        self.po_icon = None

        # Flags
        self.edit_flag = None
        self.network_drive = False

        # Inbox Temporary Vars
        self.inbox_dir_var = ""
        self.buddy_pairs = []
        self.max_buddies = 3
        self.buddy_frames = []
        self.buddy_entries = []

        # Counts for Watchdog
        self.inbox_count_var = None
        self.update_file_counts = None

    def refresh_counterparties(self):
        """Refreshes counterparties from counterparties json file."""
        counterparties = load_counterparties()
        self.counterparties = counterparties.get("counterparties", {})

    def refresh_categories(self):
        """Refreshes categories from categories json file."""
        categories = load_categories()
        self.categories = categories.get("categories", {})

    def refresh_globs(self):
        """Refreshes settings from settings file and a lot more"""
        settings = load_settings()
        sources, buddies = load_paths()
        self.sheet_data = load_sheets()

        # Settings
        self.logging_level = settings.get("logging_level", "INFO")
        self.active_theme = settings.get("active_theme", "cosmic_sky")
        self.history_path = settings.get("history_path", load_data_path("local", "history.csv"))
        self.saved_width = settings.get("saved_width", 850)
        self.saved_height = settings.get("saved_height", 850)
        self.saved_x = settings.get("saved_x", -1)
        self.saved_y = settings.get("saved_y", -1)
        self.default_printer = settings.get("default_printer", "")
        self.github_check = settings.get("github_check", False)
        self.beta = settings.get("beta", False)
        self.dynamic_window_size = settings.get("dynamic_window_size", True)
        self.legacy_mode = settings.get("legacy_mode", False)
        self.previous_version = settings.get("previous_version", "0.1.0")
        self.simple_entry = settings.get("simple_entry", False)
        self.google_auth = settings.get("google_auth", False)

        # Paths
        self.inbox = sources.get("inbox", "")
        self.workbook = sources.get("workbook", "")
        self.archive = sources.get("archive", "")

        # Variables not stored directly in a file
        self.current_folder = self.inbox


def get_executable_path():
    """Get the correct path to the app file."""
    
    script_path = os.path.abspath(sys.argv[0])

    # Check if AppImage
    if 'APPIMAGE' in os.environ:
        print(f"Path to executable (AppImage): {os.environ['APPIMAGE']}")
        return os.environ['APPIMAGE']
    
    # Check if .deb
    elif script_path.startswith("/usr/bin/invoice-buddy") or script_path.startswith("/usr/local/bin/invoice-buddy"):
        print(f"Path to executable (.deb/system): {os.path.realpath(sys.executable)} | Path to script: {script_path}")
        return script_path

    # Check if running as an .exe
    elif platform.platform().startswith("Windows") and ('onefile' in sys.executable.lower() or '_MEIPASS' in sys.executable):
        print(f"Path to executable (frozen / Inno Setup): {sys.executable} | Path to Script: {script_path}")
        return script_path
    
    # Fallback to Development Mode
    else:
        print(f"Path to executable: {script_path}")
        return [sys.executable, script_path]

globs = Globs()
