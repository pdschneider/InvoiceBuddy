# src/utils/setup.py
import logging
import sys
import os
import json
import hashlib
import platform
from logging.handlers import TimedRotatingFileHandler
from src.utils.load_settings import load_data_path, load_settings
from src.connections.updater import version_check


def setup(globs):
    """Initiate setup sequence."""
    setup_logging()
    logging.info(f"Python Version: {sys.version}")
    logging.info(f"Invoice Buddy Version: {globs.current_version}")
    if globs.github_check:
        version_check(globs)
    setup_company_map()
    setup_settings()
    setup_paths()
    setup_spreadsheet()
    company_map_check()
    get_executable_path(globs)


def setup_logging():
    """
    Sets up logging for both the log file as well as standard console output.
    """
    logging.getLogger().handlers.clear()
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Silence Dependencies
    logging.getLogger('webbrowser').setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger('pdfplumber').setLevel(logging.WARNING)
    logging.getLogger('pdfminer').setLevel(logging.WARNING)
    logging.getLogger('pdfminer.six').setLevel(logging.WARNING)
    logging.getLogger('watchdog').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

    # Sets up logs folder
    logs_dir = os.path.join(load_data_path(direct="cache"), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Sets up logging to files
    logfile_handler = TimedRotatingFileHandler(
        os.path.join(
            logs_dir, "invoicebuddy.log"), when="midnight", backupCount=30)
    logfile_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logging.getLogger().addHandler(logfile_handler)

    # Loads correct logging level from settings
    try:
        settings = load_settings()
        logging.root.setLevel(
            getattr(logging, settings.get("logging_level", "INFO")))
    except:
        logging.warning(
            f"logging level variable in settings file is unconforming. Sanitizing...")
        setup_settings()
        settings = load_settings()
        logging.root.setLevel(
            getattr(logging, settings.get("logging_level", "INFO")))

    logging.debug(f"File and console logging initialized.")


def setup_company_map():
    try:
        company_map = load_data_path("config", "company_map.json")
        with open(company_map, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if "company_map" not in data:
            data["company_map"] = {}
            logging.info(
                f"Added missing 'company_map' key to company_map.json")
    except json.JSONDecodeError as e:
        logging.error(
            f"Invalid json synatax {e}. Replacing corrupted company_map file with default.")
        os.remove(company_map)
        company_map = load_data_path("config", "company_map.json")
    except TypeError as e:
        logging.error(
            f"Invalid json structure: {e} | Replacing corrupted company_map file with default.")
        os.remove(company_map)
        company_map = load_data_path("config", "company_map.json")
    except Exception as e:
        logging.error(f"Unable to load company map due to {e}")


def setup_settings():
    try:
        settings = load_data_path("config", "settings.json")
        with open(settings, 'r', encoding='utf-8') as f:
            data = json.load(f)

        changed = False

        # Accepted string values
        accepted_logging_values = ["DEBUG",
                                   "INFO",
                                   "WARNING",
                                   "ERROR",
                                   "CRITICAL"]
        accepted_themes = ["cosmic_sky",
                           "pastel_green",
                           "trojan_red",
                           "dark_cloud",
                           "soft_light"]

        # Check to make sure keys are present
        if "logging_level" not in data or not isinstance(data["logging_level"], str) or data["logging_level"] not in accepted_logging_values:
            data["logging_level"] = "INFO"
            changed = True
            logging.info(
                "Added missing or nonconforming 'logging_level' key to settings.json")
        if "active_theme" not in data or not isinstance(data["active_theme"], str) or data["active_theme"] not in accepted_themes:
            data["active_theme"] = "cosmic_sky"
            changed = True
            logging.info(
                f"Adding missing or nonconforming 'active_theme' key to settings.json")
        if "history_path" not in data or not isinstance(data["history_path"], str):
            data["history_path"] = ""
            changed = True
            logging.info(
                f"Added missing or nonconforming 'history_path' key to settings.json")
        if "saved_width" not in data or not isinstance(data["saved_width"], int):
            data["saved_width"] = 0
            changed = True
            logging.info(
                "Added missing or nonconforming'saved_width' key to settings.json")
        if "saved_height" not in data or not isinstance(data["saved_height"], int):
            data["saved_height"] = 0
            changed = True
            logging.info(
                f"Adding missing or nonconforming 'saved_height' key to settings.json")
        if "saved_x" not in data or not isinstance(data["saved_x"], int):
            data["saved_x"] = 0
            changed = True
            logging.info(
                f"Added missing or nonconforming 'saved_x' key to settings.json")
        if "saved_y" not in data or not isinstance(data["saved_y"], int):
            data["saved_y"] = 0
            changed = True
            logging.info(
                f"Added missing or nonconforming 'saved_y' key to settings.json")
        if "default_printer" not in data or not isinstance(data["default_printer"], str):
            data["default_printer"] = ""
            changed = True
            logging.info(
                f"Added missing or nonconforming 'default_printer' key to settings.json")
        if "github_check" not in data or not isinstance(data["github_check"], bool):
            data["github_check"] = False
            changed = True
            logging.info(
                f"Added missing or nonconforming 'github_check' key to settings.json")
        if "beta" not in data or not isinstance(data["beta"], bool):
            data["beta"] = False
            changed = True
            logging.info(
                f"Added missing or nonconforming 'beta' key to settings.json")
        if "dynamic_window_size" not in data or not isinstance(data["dynamic_window_size"], bool):
            data["dynamic_window_size"] = True
            changed = True
            logging.info(
                f"Added missing or nonconforming 'dynamic_window_size' key to settings.json")
        if "legacy_mode" not in data or not isinstance(data["legacy_mode"], bool) or data.get("legacy_mode", True) == True:
            data["legacy_mode"] = False
            changed = True
            logging.info(
                f"Added missing or nonconforming 'legacy_mode' key to settings.json")
        if ("previous_version" not in data) or not isinstance(data["previous_version"], str):
            data["previous_version"] = "0.1.0"
            changed = True
            logging.info(
                f"Added missing or nonconforming 'previous_version' key to settings.json")
        if "simple_entry" not in data or not isinstance(data["simple_entry"], bool):
            data["simple_entry"] = False
            changed = True
            logging.info(
                f"Added missing or nonconforming 'simple_entry' key to settings.json")
        if "google_auth" not in data or not isinstance(data["google_auth"], bool):
            data["google_auth"] = False
            changed = True
            logging.info(
                f"Added missing or nonconforming 'google_auth' key to settings.json")

        # Check to make sure paths are valid
        if not os.path.isfile(data["history_path"]) and data["history_path"]:
            logging.warning(
                f"History Path not a valid path. Defaulting to default history file.")
            try:
                data["history_path"] = load_data_path("local", "history.csv")
            except Exception as e:
                logging.warning(
                    f"Unable to set up default history file. Sanitizing to empty path...")
                data["history_path"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect type 'history_path'")

        # Write to file
        if changed:
            with open(settings, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

    except json.JSONDecodeError as e:
        logging.error(
            f"Invalid json synatax {e}. Replacing corrupted file with default.")
        os.remove(settings)
        load_data_path("config", "settings.json")
    except TypeError as e:
        logging.error(
            f"Invalid json structure: {e} | Replacing corrupted settings file with default.")
        os.remove(settings)
        load_data_path("config", "settings.json")
    except Exception as e:
        logging.error(f"Unable to load settings due to {e}")


def setup_paths():
    try:
        paths = load_data_path("config", "paths.json")
        with open(paths, 'r', encoding='utf-8') as f:
            data = json.load(f)

        changed = False

        # Check to make sure dicts are present
        if "sources" not in data or not isinstance(data["sources"], dict):
            data["sources"] = {}
            changed = True
            logging.info("Added missing or invalid 'sources' key to paths.json")
        if "buddies" not in data or not isinstance(data["buddies"], dict):
            data["buddies"] = {}
            changed = True
            logging.info(f"Adding missing or invalid 'buddies' key to paths.json")

        # Write new data to the file
        if changed:
            with open(paths, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            changed = False

        # Check to make sure keys are present
        if "inbox" not in data.get("sources", {}):
            data["sources"]["inbox"] = ""
            changed = True
            logging.info(f"Added missing 'inbox' under sources")
        if "workbook" not in data.get("sources", {}):
            data["sources"]["workbook"] = ""
            changed = True
            logging.info(f"Added missing 'workbook' under sources")
        if "archive" not in data.get("sources", {}):
            data["sources"]["archive"] = ""
            changed = True
            logging.info(f"Added missing 'archive' under sources")

        # Write new data to the file
        if changed:
            with open(paths, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            changed = False

        # Check to make sure paths are valid
        if data["sources"]["inbox"] and not os.path.exists(data["sources"]["inbox"]):
            logging.warning(f"Inbox is not a valid path.")
            data["sources"]["inbox"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect path 'inbox'")
        if data["sources"]["workbook"] and not os.path.exists(data["sources"]["workbook"]):
            logging.warning(f"Workbook is not a valid path.")
            data["sources"]["workbook"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect path 'workbook'")
        if data["sources"]["archive"] and not os.path.exists(data["sources"]["archive"]):
            logging.warning(f"Archive is not a valid path.")
            data["sources"]["archive"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect path 'archive'")

        # Backfill blank inbox/archive with default locations
        if not data["sources"]["inbox"]:
            data["sources"]["inbox"] = os.path.normpath(
                load_data_path("local", "Inbox"))
            changed = True
            logging.info("Blank inbox path defaulted")
        if not data["sources"]["archive"]:
            data["sources"]["archive"] = os.path.normpath(
                load_data_path("local", "Archive"))
            changed = True
            logging.info("Blank archive path defaulted")

        # Create the folders if they don't exist
        for key in ["inbox", "archive"]:
            folder = data["sources"][key]
            if folder and not os.path.isdir(folder):
                os.makedirs(folder, exist_ok=True)

        # Write new data to the file again
        if changed:
            with open(paths, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

    except json.JSONDecodeError as e:
        logging.error(
            f"Invalid json synatax: {e} | Replacing corrupted paths file with default.")
        os.remove(paths)
        load_data_path("config", "paths.json")
    except TypeError as e:
        logging.error(
            f"Invalid json structure: {e} | Replacing corrupted paths file with default.")
        os.remove(paths)
        load_data_path("config", "paths.json")
    except Exception as e:
        logging.error(f"Unable to load paths due to {e}")


def setup_spreadsheet():
    try:
        spreadsheet = load_data_path("config", "spreadsheet.json")
        with open(spreadsheet, 'r', encoding='utf-8') as f:
            data = json.load(f)
        changed = False

        # Check to make sure keys are present
        if "sheet_invoices" not in data or not isinstance(data["sheet_invoices"], str):
            data["sheet_invoices"] = "Invoices"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'sheet_invoices' key to spreadsheet.json")
        if "sheet_CreditCards" not in data or not isinstance(data["sheet_CreditCards"], str):
            data["sheet_CreditCards"] = "Credit Cards"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'Credit Cards' key to spreadsheet.json")
        if "sheet_PurchaseOrders" not in data or not isinstance(data["sheet_PurchaseOrders"], str):
            data["sheet_Purchase Orders"] = "Purchase Orders"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'Purchase Orders' key to spreadsheet.json")
        if "table_InvoiceTable" not in data or not isinstance(data["table_InvoiceTable"], str):
            data["table_InvoiceTable"] = "InvoiceTable"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'table_InvoiceTable' key to spreadsheet.json")
        if "table_CreditCards" not in data or not isinstance(data["table_CreditCards"], str):
            data["table_CreditCards"] = "CreditCards"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'table_CreditCards' key to spreadsheet.json")
        if "table_PurchaseOrders" not in data or not isinstance(data["table_PurchaseOrders"], str):
            data["table_PurchaseOrders"] = "POTable"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'table_PurchaseOrders' key to spreadsheet.json")

        # Rows
        if "invoice_starting_row" not in data or not isinstance(data["invoice_starting_row"], int):
            data["invoice_starting_row"] = 4
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'invoice_starting_row' key to spreadsheet.json")
        if "card_starting_row" not in data or not isinstance(data["card_starting_row"], int):
            data["card_starting_row"] = 10
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'card_starting_row' key to spreadsheet.json")
        if "po_starting_row" not in data or not isinstance(data["po_starting_row"], int):
            data["po_starting_row"] = 0
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'po_starting_row' key to spreadsheet.json")

        # Columns
        if "invoice_starting_column" not in data or not isinstance(data["invoice_starting_column"], int):
            data["invoice_starting_column"] = 1
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'invoice_starting_column' key to spreadsheet.json")
        if "card_starting_column" not in data or not isinstance(data["card_starting_column"], int):
            data["card_starting_column"] = 11
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'card_starting_column' key to spreadsheet.json")
        if "po_starting_column" not in data or not isinstance(data["po_starting_column"], int):
            data["po_starting_column"] = 1
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'po_starting_column' key to spreadsheet.json")

        if "invoice_icon" not in data or not isinstance(data["invoice_icon"], str):
            data["invoice_icon"] = "assets/invoice-1.png"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'invoice_icon' key to spreadsheet.json")
        if "card_icon" not in data or not isinstance(data["card_icon"], str):
            data["card_icon"] = "assets/card-1.png"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'card_icon' key to spreadsheet.json")
        if "po_icon" not in data or not isinstance(data["po_icon"], str):
            data["po_icon"] = "assets/invoice-2.png"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'card_icon' key to spreadsheet.json")
        if "invoice_component_a" not in data or not isinstance(data["invoice_component_a"], str):
            data["invoice_component_a"] = "Company"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'invoice_component_a' key to spreadsheet.json")
        if "invoice_component_b" not in data or not isinstance(data["invoice_component_b"], str):
            data["invoice_component_b"] = "Date"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'invoice_component_b' key to spreadsheet.json")
        if "invoice_component_c" not in data or not isinstance(data["invoice_component_c"], str):
            data["invoice_component_c"] = "Invoice #"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'invoice_component_c' key to spreadsheet.json")
        if "invoice_component_d" not in data or not isinstance(data["invoice_component_d"], str):
            data["invoice_component_d"] = ""
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'invoice_component_d' key to spreadsheet.json")
        if "card_component_a" not in data or not isinstance(data["card_component_a"], str):
            data["card_component_a"] = "Company"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'card_component_a' key to spreadsheet.json")
        if "card_component_b" not in data or not isinstance(data["card_component_b"], str):
            data["card_component_b"] = "Date"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'card_component_b' key to spreadsheet.json")
        if "card_component_c" not in data or not isinstance(data["card_component_c"], str):
            data["card_component_c"] = "Invoice #"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'card_component_c' key to spreadsheet.json")
        if "card_component_d" not in data or not isinstance(data["card_component_d"], str):
            data["card_component_d"] = ""
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'card_component_d' key to spreadsheet.json")
        if "po_component_a" not in data or not isinstance(data["po_component_a"], str):
            data["po_component_a"] = "Company"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'po_component_a' key to spreadsheet.json")
        if "po_component_b" not in data or not isinstance(data["po_component_b"], str):
            data["po_component_b"] = "Date"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'po_component_b' key to spreadsheet.json")
        if "po_component_c" not in data or not isinstance(data["po_component_c"], str):
            data["po_component_c"] = "Invoice #"
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'po_component_c' key to spreadsheet.json")
        if "po_component_d" not in data or not isinstance(data["po_component_d"], str):
            data["po_component_d"] = ""
            changed = True
            logging.info(
                "Added missing or incorrectly typed 'po_component_d' key to spreadsheet.json")

        # Write to file
        if changed:
            with open(spreadsheet, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

    except json.JSONDecodeError as e:
        logging.error(
            f"Invalid json synatax: {e} | Replacing corrupted spreadsheet file with default.")
        os.remove(spreadsheet)
        spreadsheet = load_data_path("config", "spreadsheet.json")
    except TypeError as e:
        logging.error(
            f"Invalid json structure: {e} | Replacing corrupted spreadsheet file with default.")
        os.remove(spreadsheet)
        spreadsheet = load_data_path("config", "spreadsheet.json")
    except Exception as e:
        logging.error(f"Unable to load spreadsheet data due to {e}")


def company_map_check():
    """
    Checks if company map is different from
    user's company map, prompts for change.
    """
    try:

        # Read the contents of the default company_map path and hash it
        default_company_path = load_data_path(
            "config", "company_map.json", default=True)
        with open(default_company_path, 'r') as f:
            default_company_file = f.read()
        hashed_default_company_map = hashlib.md5(
            default_company_file.encode()).hexdigest()

        # Read the contents of the current user's company_map path and hash it
        user_company_path = load_data_path("config", "company_map.json")
        with open(user_company_path, 'r') as f:
            user_company_file = f.read()
        hashed_user_company_map = hashlib.md5(
            user_company_file.encode()).hexdigest()

    except Exception as e:
        logging.warning(f"Unable to hash company_map.json files due to: {e}")
        return

    if hashed_default_company_map != hashed_user_company_map:
        try:
            if os.path.isfile(load_data_path("config", "company_map.json")):
                logging.debug(f"Removing old company map...")
                os.remove(load_data_path("config", "company_map.json"))
            logging.info(f"Updating company map...")
            load_data_path("config", "company_map.json", default=True)

        except Exception as e:
            logging.warning(f"Unable to update company map due to: {e}")


def get_executable_path(globs):
    """Get the correct path to the app file."""
    
    # Script path (ex: /usr/bin/spawn)
    script_path = os.path.abspath(sys.argv[0])  # Run From (pwd + binary name)
    script_path_2 = sys.executable  # Actual Binary Path

    # Check if AppImage
    if 'APPIMAGE' in os.environ:
        globs.app_type = "AppImage"
        globs.app_path = os.environ['APPIMAGE']
        logging.debug(f"Path to executable (AppImage): {globs.app_path}")
        logging.debug(f"App Type: {globs.app_type}")
        return os.environ['APPIMAGE']
    
    # Check if .deb
    elif (script_path_2.startswith("/usr/bin/invoice-buddy") or
          script_path_2.startswith("/usr/local/bin/invoice-buddy") or
          script_path_2.startswith("/usr/lib/invoice-buddy")
          ) or (script_path.startswith("/usr/bin/invoice-buddy") or
                script_path.startswith("/usr/local/bin/invoice-buddy") or
                script_path.startswith("/usr/lib/invoice-buddy")):
        globs.app_type = "Deb"
        globs.app_path = script_path
        logging.debug(f"Path to executable (.deb/system): {os.path.realpath(sys.executable)} | Path to script: {script_path_2}")
        logging.debug(f"App Type: {globs.app_type}")
        return script_path_2

    # Check if running as an .exe
    elif platform.platform().startswith("Windows") and (getattr(sys, 'frozen', False) or '__compiled__' in dir(sys.modules.get('__main__', {})) or 'onefile' in sys.executable.lower() or '_MEIPASS' in sys.executable):
        globs.app_type = "Exe"
        globs.app_path = script_path
        logging.debug(f"Path to executable (frozen / Inno Setup): {sys.executable} | Path to Script: {script_path}")
        logging.debug(f"App Type: {globs.app_type}")
        return script_path
    
    # Fallback to Development Mode
    else:
        globs.app_type = "Development"
        globs.app_path = [sys.executable, script_path]
        logging.debug(f"Path to executable: {script_path}")
        logging.debug(f"App Type: {globs.app_type}")
        return [sys.executable, script_path]
