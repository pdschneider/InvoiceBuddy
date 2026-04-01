# Utils/setup.py
import logging
import sys
import os
import json
import csv
import hashlib
from logging.handlers import TimedRotatingFileHandler
from src.utils.load_settings import load_data_path, load_settings
from src.utils.vars import create_vars
from src.utils.icons import load_icons


def setup(globals):
    """Initiate setup sequence."""
    setup_logging()
    logging.info(f"Python Version: {sys.version}")
    logging.info(f"Invoice Buddy Version: {globals.current_version}")
    setup_company_map()
    setup_folder_maps()
    setup_settings()
    setup_paths()
    make_legacy_compatible()
    setup_spreadsheet()
    setup_history()
    setup_themes()
    company_map_check()
    folder_maps_check()
    create_vars(globals)
    load_icons(globals)


def setup_logging():
    """
    Sets up logging for both the log file as well as standard console output.
    """
    logging.getLogger().handlers.clear()
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Silence Dependencies
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
            logs_dir, "invoicebuddy.log"), when="midnight", backupCount=50)
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


def setup_folder_maps():
    try:
        folder_map = load_data_path("config", "folder_maps.json")
        with open(folder_map, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check for type error
        for key, subfolder in data["maps"].items():
            test = os.path.join(".", subfolder)

        changed = False

        # Check to make sure dicts are present
        if "maps" not in data:
            data["maps"] = {}
            changed = True
            logging.info("Added missing 'maps' key to folder_maps.json")

        # Write to file
        if changed:
            with open(folder_map, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            changed = False

        # Write to file
        if changed:
            with open(folder_map, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

    except json.JSONDecodeError as e:
        logging.error(
            f"Invalid json synatax: {e} | Replacing corrupted folder_maps file with default.")
        os.remove(folder_map)
        load_data_path("config", "folder_maps.json")
    except TypeError as e:
        logging.error(
            f"Invalid json structure: {e} | Replacing corrupted folder_maps file with default.")
        os.remove(folder_map)
        load_data_path("config", "folder_maps.json")
    except Exception as e:
        logging.error(f"Unable to load folder map due to {e}")


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

        # Check to make sure paths are valid
        if not os.path.isfile(data["history_path"]):
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
        if not os.path.exists(data["sources"]["inbox"]):
            logging.warning(f"Inbox is not a valid path.")
            data["sources"]["inbox"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect path 'inbox'")
        if not os.path.exists(data["sources"]["workbook"]):
            logging.warning(f"Workbook is not a valid path.")
            data["sources"]["workbook"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect path 'workbook'")
        if not os.path.exists(data["sources"]["archive"]):
            logging.warning(f"Archive is not a valid path.")
            data["sources"]["archive"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect path 'archive'")

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


def setup_history():
    """
    Initializes the history file with headers in the app's designated folder.
    """
    headers = ["File Name",
               "Source Folder",
               "Destination Folder",
               "Type",
               "Archived",
               "Entered"]
    history_file = load_data_path("local", "history.csv")

    # Create the file if it does not exist
    if not os.path.exists(history_file):
        with open(history_file, 'w', encoding='utf-8', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        logging.info(f"Created new history file with headers: {history_file}")
        return

    # Read the first line:
    with open(history_file, 'r', encoding='utf-8') as f:
        first_line = f.readline().rstrip('\n')

    # Expected first line
    expected = ','.join(headers)

    if first_line == expected:
        logging.debug("History file headers are correct.")
        return

    # If headers are wrong, fix them
    logging.warning(f"Wrong headers found. Fixing... (found: {first_line!r})")

    # Read everything except the first line
    with open(history_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[1:]

    # Write the correct header and re-add the rest of the file
    with open(history_file, 'w', encoding='utf=8', newline="") as h:
        h.write(expected + "\n")
        h.writelines(lines)
    logging.info(f"Headers fixed successfully")


def setup_themes():
    """Replaces theme files if they are different from the current version."""
    try:
        themes = ["themes/cosmic_sky.json",
                  "themes/pastel_green.json",
                  "themes/trojan_red.json",
                  "themes/dark_cloud.json",
                  "themes/soft_light.json"]

        for theme in themes:
            try:
                # Read the contents of the default path and hash it
                default_theme_path = load_data_path(
                    "config", theme, default=True)
                with open(default_theme_path, 'r', encoding='utf-8') as f:
                    default_theme_file = f.read()
                hashed_default_theme_file = hashlib.md5(
                    default_theme_file.encode()).hexdigest()
                if not hashed_default_theme_file:
                    logging.warning(f"No hash for default {theme} found.")

                # Read the contents of the current user's path and hash it
                user_theme_path = load_data_path("config", theme)
                with open(user_theme_path, 'r', encoding='utf-8') as f:
                    user_theme_file = f.read()
                hashed_user_theme_file = hashlib.md5(
                    user_theme_file.encode()).hexdigest()
                if not hashed_user_theme_file:
                    logging.warning(f"No has for user's {theme} found.")

            except Exception as e:
                logging.warning(f"Unable to hash {theme} due to: {e}")
                return

            # Compare hashes, remove and replace old file if different
            if hashed_default_theme_file != hashed_user_theme_file:
                try:
                    if os.path.isfile(load_data_path("config", theme)):
                        logging.debug(f"Removing old {theme}...")
                        os.remove(load_data_path("config", theme))
                    logging.info(f"Updating {theme}...")
                    load_data_path("config", theme, default=True)

                except Exception as e:
                    logging.warning(f"Unable to update {theme} to: {e}")
                    return

    except Exception as e:
        logging.error(f"Could not hash theme files due to: {e}")
        return


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


def folder_maps_check():
    """
    Checks if folder map is different from
    user's folder map, prompts for change.
    """
    try:
        # Read the contents of the default folder_maps path and hash it
        default_folder_path = load_data_path(
            "config", "folder_maps.json", default=True)
        with open(default_folder_path, 'r') as f:
            default_folder_file = f.read()
        hashed_default_folder_map = hashlib.md5(
            default_folder_file.encode()).hexdigest()

        # Read the contents of the current user's folder_maps path and hash it
        user_folder_path = load_data_path("config", "folder_maps.json")
        with open(user_folder_path, 'r') as f:
            user_folder_file = f.read()
        hashed_user_folder_map = hashlib.md5(
            user_folder_file.encode()).hexdigest()

    except Exception as e:
        logging.warning(f"Unable to hash folder_maps.json files due to: {e}")
        return

    if hashed_default_folder_map != hashed_user_folder_map:
        try:
            if os.path.isfile(load_data_path("config", "folder_maps.json")):
                logging.debug(f"Removing old folder map...")
                os.remove(load_data_path("config", "folder_maps.json"))
            logging.info(f"Updating folder map...")
            load_data_path("config", "folder_maps.json", default=True)

        except Exception as e:
            logging.warning(f"Unable to update folder map due to: {e}")


def make_legacy_compatible():
    """
    Reads legacy entries in files and converts
    them to the modern format usable in recent versions.
    """
    try:
        # Load folder_maps.json
        folder_maps_path = load_data_path("config", "folder_maps.json")
        with open(folder_maps_path, 'r', encoding='utf-8') as f:
            folder_data = json.load(f)

        # Load paths.json
        paths = load_data_path("config", "paths.json")
        with open(paths, 'r', encoding='utf-8') as f:
            paths_data = json.load(f)

        # Get archive path from both files
        archive_path = folder_data.get("bases", {}).get("archive", "")
        new_archive_path = paths_data.get("sources", {}).get("archive", "")

        # Skip if archive path is empty or falsy in either file
        if not archive_path or new_archive_path:
            return

        # Load paths.json
        paths_file = load_data_path("config", "paths.json")
        with open(paths_file, 'r', encoding='utf-8') as f:
            paths_data = json.load(f)

        changed = False

        # Ensure "sources" exists
        if "sources" not in paths_data:
            paths_data["sources"] = {}
            changed = True
            logging.info("Added missing 'sources' key to paths.json")

        # Add/update archive key only if it's not already there or different
        current_archive = paths_data["sources"].get("archive", "")
        if current_archive != archive_path:
            paths_data["sources"]["archive"] = archive_path
            changed = True
            logging.info(
                f"Added/updated archive path in paths.json: {archive_path}")

        # Save if changes were made
        if changed:
            with open(paths_file, 'w', encoding='utf-8') as f:
                json.dump(paths_data, f, indent=4)

    except json.JSONDecodeError as e:
        logging.error(
            f"JSON decode error in folder_maps.json or paths.json: {e}")
    except Exception as e:
        logging.error(f"Failed to set up archive path: {e}")
