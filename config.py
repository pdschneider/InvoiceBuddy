# config.py
import platform, getpass, os, sys, hashlib, json, logging
import customtkinter as ctk
from Utils.load_settings import load_settings, load_data_path, load_folder_map, load_paths, load_spreadsheet_specs

# Globals Class
class Globals:
    """A class to hold all configuration and UI variables for InvoiceBuddy."""
    def __init__(self):
        """Initialize settings from load_settings"""
        self.refresh_globals()
        self.observers = {}

        # Current Version
        self.current_version = "v0.1.2"

        # Global Variables
        self.os_name = platform.system()
        self.user = getpass.getuser()
        self.hashed_user = hashlib.md5(self.user.encode()).hexdigest()

        # Bundled Flags
        self.pyinstaller_bundle = getattr(sys, 'frozen', False)
        self.is_bundled = self.pyinstaller_bundle

        # Folder mappings and paths from folder_maps.json
        self.sources, self.buddies = load_paths()

        # UI variables
        self.root = None
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

        self.icons_list = ["assets/invoice-1.png",
                            "assets/invoice-2.png",
                            "assets/invoice-3.png",
                            "assets/card-1.png",
                            "assets/card-2.png",
                            "assets/cards-1.png",
                            "assets/cards-2.png",
                            "assets/money-1.png",
                            "assets/money-2.png",
                            "assets/money-bag.png",]

        self.invoice_icon = None
        self.card_icon = None
        self.po_icon = None

        # Flags
        self.edit_flag = None
        self.network_drive = False

        # Trees
        self.inbox_tree = None
        self.history_tree = None

        # Temporary UI Variables
        self.workbook_var = ""
        self.history_var = ""

        # Inbox Temporary Vars
        self.inbox_dir_var = ""
        self.buddy_pairs = []
        self.max_buddies = 3
        self.buddy_frames = []
        self.buddy_entries = []

        self.logging_level_var = None
        self.theme_var = None
        self.archive_path_var = None

        self.sheet_invoices_var = None
        self.sheet_CreditCards_var = None
        self.sheet_PurchaseOrders_var = None
        self.table_InvoiceTable_var = None
        self.table_CreditCards_var = None
        self.table_PurchaseOrders_var = None
        self.invoice_starting_row_var = None
        self.card_starting_row_var = None
        self.po_starting_row_var = None
        self.invoice_starting_column_var = None
        self.card_starting_column_var = None
        self.po_starting_column_var = None

        # Counts for Watchdog
        self.inbox_count_var = None

    def refresh_globals(self):
        """Refreshes settings from settings file"""
        settings = load_settings()
        sources, buddies = load_paths()
        spreadsheet_specs = load_spreadsheet_specs()
        self.folder_map, self.oneoffs_folder = load_folder_map()

        # Settings
        self.logging_level = settings.get("logging_level", "INFO")
        self.active_theme = settings.get("active_theme", "cosmic_sky")
        self.history_path = settings.get("history_path", load_data_path("local", "history.csv"))
        self.saved_width = settings.get("saved_width", 850)
        self.saved_height = settings.get("saved_height", 850)
        self.saved_x = settings.get("saved_x", -1)
        self.saved_y = settings.get("saved_y", -1)

        # Paths
        self.inbox = sources.get("inbox", "")
        self.workbook = sources.get("workbook", "")

        # Folder Maps
        data = json.load(open(os.path.normpath(load_data_path("config", "folder_maps.json")), 'r'))
        self.archive_path = os.path.normpath(data['bases']['archive'])

        # Spreadsheet
        self.sheet_invoices = spreadsheet_specs.get("sheet_invoices", "Invoices")
        self.sheet_CreditCards = spreadsheet_specs.get("sheet_CreditCards", "Credit Cards")
        self.sheet_PurchaseOrders = spreadsheet_specs.get("sheet_PurchaseOrders", "Purchase Orders")
        self.table_InvoiceTable = spreadsheet_specs.get("table_InvoiceTable", "InvoiceTable")
        self.table_PurchaseOrders = spreadsheet_specs.get("table_PurchaseOrders", "POTable")
        self.table_CreditCards = spreadsheet_specs.get("table_CreditCards", "CreditCards")
        self.invoice_starting_row = spreadsheet_specs.get("invoice_starting_row", 3)
        self.card_starting_row = spreadsheet_specs.get("card_starting_row", 3)
        self.po_starting_row = spreadsheet_specs.get("po_starting_row", 0)
        self.invoice_starting_column = spreadsheet_specs.get("invoice_starting_column", 1)
        self.card_starting_column = spreadsheet_specs.get("card_starting_column", 1)
        self.po_starting_column = spreadsheet_specs.get("po_starting_column", 1)
        self.invoice_icon_path = spreadsheet_specs.get("invoice_icon", "assets/invoice-1.png")
        self.card_icon_path = spreadsheet_specs.get("card_icon", "assets/card-1.png")
        self.po_icon_path = spreadsheet_specs.get("po_icon", "assets/invoice-2.png")

def apply_theme(name: str) -> None:
    """Loads the user's chosen theme and applies it to ctk widgets."""
    try:
        globals.theme_path = os.path.normpath(os.path.join(load_data_path(direct="config"), f"themes/{globals.active_theme}.json"))
        try:
            with open(globals.theme_path, 'r') as f:
                globals.theme_dict = json.load(f)
        except:
            logging.warning(f"Unable to load theme into dictionary.")
        ctk.set_default_color_theme(globals.theme_path)
        logging.debug(f"CTk theme found at: {globals.theme_path}")
    except Exception as e:
        logging.warning(f"Could not retrieve CTk active theme due to: {e}")

globals = Globals()
