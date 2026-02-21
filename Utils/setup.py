# Utils/setup.py
import logging, os, json, csv, shutil, hashlib
from logging.handlers import TimedRotatingFileHandler
from Utils.load_settings import load_data_path, load_settings, load_default_data_path
import tkinter as tk
from tkinter import messagebox

def setup():
    setup_logging()
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

def setup_logging():
    """Sets up logging for both the log file as well as standard console output."""
    logging.getLogger().handlers.clear() # Clears output destinations
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Silence Dependencies
    logging.getLogger('pdfplumber').setLevel(logging.WARNING)
    logging.getLogger('pdfminer').setLevel(logging.WARNING)
    logging.getLogger('pdfminer.six').setLevel(logging.WARNING)
    logging.getLogger('watchdog').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

    # Sets up logs folder
    logs_dir = os.path.join(load_data_path(direct="cache"), "logs")
    os.makedirs(logs_dir, exist_ok=True) # Creates the logs folder if it doesn't exist

    # Sets up logging to files
    logfile_handler = TimedRotatingFileHandler(os.path.join(logs_dir, "invoicebuddy.log"), when="midnight", backupCount=50)
    logfile_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logging.getLogger().addHandler(logfile_handler)

    # Loads correct logging level from settings
    try:
        settings = load_settings()
        logging.root.setLevel(getattr(logging, settings.get("logging_level", "INFO")))
    except:
        logging.warning(f"logging level variable in settings file is unconforming. Sanitizing...")
        setup_settings()
        settings = load_settings()
        logging.root.setLevel(getattr(logging, settings.get("logging_level", "INFO")))

    logging.info(f"File and console logging initialized.")

def setup_company_map():
    try:
        company_map = load_data_path("config", "company_map.json")
        with open(company_map, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.debug(f"company map loaded successfully from {company_map}")
        if "company_map" not in data:
            data["company_map"] = {}
            logging.info(f"Added missing 'company_map' key to company_map.json")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid json synatax {e}. Replacing corrupted company_map file with default.")
        os.remove(company_map)
        company_map = load_data_path("config", "company_map.json")
    except TypeError as e:
        logging.error(f"Invalid json structure: {e} | Replacing corrupted company_map file with default.")
        os.remove(company_map)
        company_map = load_data_path("config", "company_map.json")
    except Exception as e:
        logging.error(f"Unable to load company map due to {e}")

def setup_folder_maps():
    try:
        logging.debug(f"attempting to retrieve folder maps filepath...")
        folder_map = load_data_path("config", "folder_maps.json")
        with open(folder_map, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.debug(f"folder map loaded successfully from {folder_map}")

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
        logging.error(f"Invalid json synatax: {e} | Replacing corrupted folder_maps file with default.")
        os.remove(folder_map)
        load_data_path("config", "folder_maps.json")
    except TypeError as e:
        logging.error(f"Invalid json structure: {e} | Replacing corrupted folder_maps file with default.")
        os.remove(folder_map)
        load_data_path("config", "folder_maps.json")
    except Exception as e:
        logging.error(f"Unable to load folder map due to {e}")

def setup_settings():
    try:
        settings = load_data_path("config", "settings.json")
        with open(settings, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.debug(f"settings loaded successfully from {settings}")

        changed = False

        # Check to make sure keys are present
        if "logging_level" not in data:
            data["logging_level"] = "INFO"
            changed = True
            logging.info("Added missing 'logging_level' key to settings.json")
        if "active_theme" not in data:
            data["active_theme"] = "cosmic_sky"
            changed = True
            logging.info(f"Adding missing 'active_theme' key to settings.json")
        if "history_path" not in data:
            data["history_path"] = ""
            changed = True
            logging.info(f"Added missing 'history_path' key to settings.json")
        if "saved_width" not in data:
            data["saved_width"] = 0
            changed = True
            logging.info("Added missing 'saved_width' key to settings.json")
        if "saved_height" not in data:
            data["saved_height"] = 0
            changed = True
            logging.info(f"Adding missing 'saved_height' key to settings.json")
        if "saved_x" not in data:
            data["saved_x"] = 0
            changed = True
            logging.info(f"Added missing 'saved_x' key to settings.json")
        if "saved_y" not in data:
            data["saved_y"] = 0
            changed = True
            logging.info(f"Added missing 'saved_y' key to settings.json")

        # Check to make sure keys are the correct type
        if not isinstance(data["logging_level"], str):
            logging.warning(f"Current type of value for logging level: {type(data["logging_level"])}")
            data["logging_level"] = "INFO"
            changed = True
            logging.info(f"Sanitizing incorrect type 'logging_level'")
        if not isinstance(data["active_theme"], str):
            logging.warning(f"Current type of value for active theme: {type(data["active_theme"])}")
            data["active_theme"] = "cosmic_sky"
            changed = True
            logging.info(f"Sanitizing incorrect type 'active_theme'")
        if not isinstance(data["history_path"], str):
            logging.warning(f"Current type of value for history path: {type(data["history_path"])}")
            data["history_path"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect type 'history_path'")
        if not isinstance(data["saved_width"], int):
            logging.warning(f"Current type of value for saved width: {type(data["saved_width"])}")
            data["saved_width"] = 0
            changed = True
            logging.info(f"Sanitizing incorrect type 'saved_width'")
        if not isinstance(data["saved_height"], int):
            logging.warning(f"Current type of value for saved height: {type(data["saved_height"])}")
            data["saved_height"] = 0
            changed = True
            logging.info(f"Sanitizing incorrect type 'saved_height'")
        if not isinstance(data["saved_x"], int):
            logging.warning(f"Current type of value for saved x position: {type(data["saved_x"])}")
            data["saved_x"] = 0
            changed = True
            logging.info(f"Sanitizing incorrect type 'saved_x'")
        if not isinstance(data["saved_y"], int):
            logging.warning(f"Current type of value for saved y position: {type(data["saved_y"])}")
            data["saved_y"] = 0
            changed = True
            logging.info(f"Sanitizing incorrect type 'saved_y'")
        
        # Check to make sure logging level and theme are acceptable values
        accepted_logging_values = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        accepted_themes = ["cosmic_sky", "pastel_green", "trojan_red", "dark_cloud", "soft_light"]
        if data["logging_level"] not in accepted_logging_values:
            data["logging_level"] = "INFO"
            changed = True
            logging.info("Fixed nonconforming value for 'logging_level' key in settings.json")
        if data["active_theme"] not in accepted_themes:
            data["active_theme"] = "cosmic_sky"
            changed = True
            logging.info(f"Adding missing 'active_theme' key to settings.json")

        # Check to make sure paths are valid
        logging.debug(f"History path: {data["history_path"]}")
        if not os.path.isfile(data["history_path"]):
            logging.warning(f"History Path not a valid path. Defaulting to default history file.")
            try:
                data["history_path"] = load_data_path("local", "history.csv")
            except Exception as e:
                logging.warning(f"Unable to set up default history file. Sanitizing to empty path...")
                data["history_path"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect type 'history_path'")

        # Write to file
        if changed:
            with open(settings, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

    except json.JSONDecodeError as e:
        logging.error(f"Invalid json synatax {e}. Replacing corrupted file with default.")
        os.remove(settings)
        load_data_path("config", "settings.json")
    except TypeError as e:
        logging.error(f"Invalid json structure: {e} | Replacing corrupted settings file with default.")
        os.remove(settings)
        load_data_path("config", "settings.json")
    except Exception as e:
        logging.error(f"Unable to load settings due to {e}")

def setup_paths():
    try:
        paths = load_data_path("config", "paths.json")
        with open(paths, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.debug(f"paths loaded successfully from {paths}")

        changed = False

        # Check to make sure dicts are present
        if "sources" not in data:
            data["sources"] = {}
            changed = True
            logging.info("Added missing 'sources' key to paths.json")
        if "buddies" not in data:
            data["buddies"] = {}
            changed = True
            logging.info(f"Adding missing 'buddies' key to paths.json")
        
        # Check to make sure keys are present
        if "inbox" not in data.get("sources", {}):
            data["sources"]["inbox"] = ""
            changed = True
            logging.info(f"Added missing 'inbox' under sources")
        if "workbook" not in data.get("sources", {}):
            data["sources"]["workbook"] = ""
            changed = True
            logging.info(f"Added missing 'workbook' under sources")

        # Write new data to the file
        if changed:
            with open(paths, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            changed = False

        # Check to make sure keys are the correct type
        if not isinstance(data["sources"]["inbox"], str):
            logging.debug(f"Current type of value in inbox: {type(data["sources"]["inbox"])}")
            data["sources"]["inbox"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect type 'inbox' under sources")
        if not isinstance(data["sources"]["workbook"], str):
            logging.debug(f"Current type of value in workbook: {type(data["sources"]["workbook"])}")
            data["sources"]["workbook"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect type 'workbook' under sources")

        # Check to make sure paths are valid
        logging.info(f"Inbox: {data["sources"]["inbox"]}")
        if not os.path.exists(data["sources"]["inbox"]):
            logging.warning(f"Inbox is not a valid path.")
            data["sources"]["inbox"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect path 'inbox'")
        logging.info(f"Workbook: {data["sources"]["workbook"]}")
        if not os.path.exists(data["sources"]["workbook"]):
            logging.warning(f"Workbook is not a valid path.")
            data["sources"]["workbook"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect path 'workbook'")
        
        # Write new data to the file again
        if changed:
            with open(paths, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

    except json.JSONDecodeError as e:
        logging.error(f"Invalid json synatax: {e} | Replacing corrupted paths file with default.")
        os.remove(paths)
        load_data_path("config", "paths.json")
    except TypeError as e:
        logging.error(f"Invalid json structure: {e} | Replacing corrupted paths file with default.")
        os.remove(paths)
        load_data_path("config", "paths.json")
    except Exception as e:
        logging.error(f"Unable to load paths due to {e}")

def setup_spreadsheet():
    try:
        spreadsheet = load_data_path("config", "spreadsheet.json")
        with open(spreadsheet, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.debug(f"spreadsheet data loaded successfully from {spreadsheet}")

        # Check to make sure keys are present
        if "sheet_invoices" not in data or not isinstance(data["sheet_invoices"], str):
            data["sheet_invoices"] = "Invoices"
            changed = True
            logging.info("Added missing or incorrectly typed 'sheet_invoices' key to spreadsheet.json")
        if "sheet_CreditCards" not in data or not isinstance(data["sheet_CreditCards"], str):
            data["sheet_CreditCards"] = "Credit Cards"
            changed = True
            logging.info("Added missing or incorrectly typed 'Credit Cards' key to spreadsheet.json")
        if "sheet_PurchaseOrders" not in data or not isinstance(data["sheet_PurchaseOrders"], str):
            data["sheet_Purchase Orders"] = "Purchase Orders"
            changed = True
            logging.info("Added missing or incorrectly typed 'Purchase Orders' key to spreadsheet.json")
        if "table_InvoiceTable" not in data or not isinstance(data["table_InvoiceTable"], str):
            data["table_InvoiceTable"] = "InvoiceTable"
            changed = True
            logging.info("Added missing or incorrectly typed 'table_InvoiceTable' key to spreadsheet.json")
        if "table_CreditCards" not in data or not isinstance(data["table_CreditCards"], str):
            data["table_CreditCards"] = "CreditCards"
            changed = True
            logging.info("Added missing or incorrectly typed 'table_CreditCards' key to spreadsheet.json")
        if "table_PurchaseOrders" not in data or not isinstance(data["table_PurchaseOrders"], str):
            data["table_PurchaseOrders"] = "POTable"
            changed = True
            logging.info("Added missing or incorrectly typed 'table_PurchaseOrders' key to spreadsheet.json")
        if "invoice_starting_row" not in data or not isinstance(data["invoice_starting_row"], str):
            data["invoice_starting_row"] = 4
            changed = True
            logging.info("Added missing or incorrectly typed 'invoice_starting_row' key to spreadsheet.json")
        if "card_starting_row" not in data or not isinstance(data["card_starting_row"], str):
            data["card_starting_row"] = 10
            changed = True
            logging.info("Added missing or incorrectly typed 'card_starting_row' key to spreadsheet.json")
        if "po_starting_row" not in data or not isinstance(data["po_starting_row"], str):
            data["po_starting_row"] = 0
            changed = True
            logging.info("Added missing or incorrectly typed 'po_starting_row' key to spreadsheet.json")
        if "invoice_icon" not in data or not isinstance(data["invoice_icon"], str):
            data["invoice_icon"] = "assets/invoice-1.png"
            changed = True
            logging.info("Added missing or incorrectly typed 'invoice_icon' key to spreadsheet.json")
        if "card_icon" not in data or not isinstance(data["card_icon"], str):
            data["card_icon"] = "assets/card-1.png"
            changed = True
            logging.info("Added missing or incorrectly typed 'card_icon' key to spreadsheet.json")
        if "po_icon" not in data or not isinstance(data["po_icon"], str):
            data["po_icon"] = "assets/invoice-2.png"
            changed = True
            logging.info("Added missing or incorrectly typed 'card_icon' key to spreadsheet.json")
        if "invoice_component_a" not in data or not isinstance(data["invoice_component_a"], str):
            data["invoice_component_a"] = "Company"
            changed = True
            logging.info("Added missing or incorrectly typed 'invoice_component_a' key to spreadsheet.json")
        if "invoice_component_b" not in data or not isinstance(data["invoice_component_b"], str):
            data["invoice_component_b"] = "Date"
            changed = True
            logging.info("Added missing or incorrectly typed 'invoice_component_b' key to spreadsheet.json")
        if "invoice_component_c" not in data or not isinstance(data["invoice_component_c"], str):
            data["invoice_component_c"] = "Invoice #"
            changed = True
            logging.info("Added missing or incorrectly typed 'invoice_component_c' key to spreadsheet.json")
        if "invoice_component_d" not in data or not isinstance(data["invoice_component_d"], str):
            data["invoice_component_d"] = ""
            changed = True
            logging.info("Added missing or incorrectly typed 'invoice_component_d' key to spreadsheet.json")
        if "card_component_a" not in data or not isinstance(data["card_component_a"], str):
            data["card_component_a"] = "Company"
            changed = True
            logging.info("Added missing or incorrectly typed 'card_component_a' key to spreadsheet.json")
        if "card_component_b" not in data or not isinstance(data["card_component_b"], str):
            data["card_component_b"] = "Date"
            changed = True
            logging.info("Added missing or incorrectly typed 'card_component_b' key to spreadsheet.json")
        if "card_component_c" not in data or not isinstance(data["card_component_c"], str):
            data["card_component_c"] = "Invoice #"
            changed = True
            logging.info("Added missing or incorrectly typed 'card_component_c' key to spreadsheet.json")
        if "card_component_d" not in data or not isinstance(data["card_component_d"], str):
            data["card_component_d"] = ""
            changed = True
            logging.info("Added missing or incorrectly typed 'card_component_d' key to spreadsheet.json")
        if "po_component_a" not in data or not isinstance(data["po_component_a"], str):
            data["po_component_a"] = "Company"
            changed = True
            logging.info("Added missing or incorrectly typed 'po_component_a' key to spreadsheet.json")
        if "po_component_b" not in data or not isinstance(data["po_component_b"], str):
            data["po_component_b"] = "Date"
            changed = True
            logging.info("Added missing or incorrectly typed 'po_component_b' key to spreadsheet.json")
        if "po_component_c" not in data or not isinstance(data["po_component_c"], str):
            data["po_component_c"] = "Invoice #"
            changed = True
            logging.info("Added missing or incorrectly typed 'po_component_c' key to spreadsheet.json")
        if "po_component_d" not in data or not isinstance(data["po_component_d"], str):
            data["po_component_d"] = ""
            changed = True
            logging.info("Added missing or incorrectly typed 'po_component_d' key to spreadsheet.json")

        # Write to file
        if changed:
            with open(spreadsheet, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

    except json.JSONDecodeError as e:
        logging.error(f"Invalid json synatax: {e} | Replacing corrupted spreadsheet file with default.")
        os.remove(spreadsheet)
        spreadsheet = load_data_path("config", "spreadsheet.json")
    except TypeError as e:
        logging.error(f"Invalid json structure: {e} | Replacing corrupted spreadsheet file with default.")
        os.remove(spreadsheet)
        spreadsheet = load_data_path("config", "spreadsheet.json")
    except Exception as e:
        logging.error(f"Unable to load spreadsheet data due to {e}")

def setup_history():
    """Initializes the history file with headers in the app's designated folder."""
    headers = ["File Name", "Source Folder", "Destination Folder", "Type", "Archived", "Entered"]
    history_file = load_data_path("local", "history.csv")

    # Create the file if it does not exist
    if not os.path.exists(history_file):
        with open(history_file, 'w', encoding='utf-8', newline="") as f:
            writer = csv.writer(f)
            writer.writerows(headers)
        logging.info(f"Created new history file with headers: {history_file}")
        return

    # Read the first line:
    with open(history_file, 'r', encoding='utf-8') as f:
        first_line = f.readline().rstrip('\n')
    
    # Expected first line
    expected = ','.join(f'"{h}"' for h in headers)

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
    try:
        themes = ["themes/cosmic_sky.json", 
                    "themes/pastel_green.json", 
                    "themes/trojan_red.json", 
                    "themes/dark_cloud.json", 
                    "themes/soft_light.json"]
        theme_directory = os.path.normpath(load_data_path("config", "themes"))
        theme_keys = ["CTk", 
                      "CTkFont", 
                      "CTkFrame", 
                      "CTkLabel", 
                      "CTkButton", 
                      "CTkEntry", 
                      "CTkCheckBox", 
                      "CTkRadioButton", 
                      "CTkComboBox", 
                      "CTkTextbox", 
                      "CTkScrollbar", 
                      "CTkSegmentedButton", 
                      "CTkTabview", 
                      "DropdownMenu", 
                      "CTkScrollableFrame", 
                      "CTkToplevel",
                      "CTkSlider"]
        total_themes = []
        for theme in themes:
            current_theme = os.path.normpath(load_data_path("config", theme))
            with open(current_theme, 'r', encoding='utf-8') as f:
                data = json.load(f)
            total_themes.append(theme)
            for key in theme_keys:
                if key not in data:
                    shutil.rmtree(theme_directory)
                    load_data_path("config", theme_directory)
                    logging.info(f"Theme missing {key}, loading default themes.")
                    return
        logging.debug(f"Successfully loaded themes: {total_themes}")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid json synatax: {e} | Replacing corrupted theme files with defaults.")
        shutil.rmtree(theme_directory)
        theme_directory = os.path.normpath(load_data_path("config", "themes"))
    except TypeError as e:
        logging.error(f"Invalid json structure: {e} | Replacing corrupted theme files with defaults.")
        shutil.rmtree(theme_directory)
        theme_directory = os.path.normpath(load_data_path("config", "themes"))
    except Exception as e:
        logging.error(f"Unable to load themes due to {e}")

def company_map_check():
    """Checks if company map is different from user's company map, prompts for change."""
    try:

        # Read the contents of the default company_map path and hash it
        default_company_path = load_default_data_path("config", "company_map.json")
        with open(default_company_path, 'r') as f:
            default_company_file = f.read()
        hashed_default_company_map = hashlib.md5(default_company_file.encode()).hexdigest()
        logging.debug(f"Default company map hash: {hashed_default_company_map}")

        # Read the contents of the current user's company_map path and hash it
        user_company_path = load_data_path("config", "company_map.json")
        with open(user_company_path, 'r') as f:
            user_company_file = f.read()
        hashed_user_company_map = hashlib.md5(user_company_file.encode()).hexdigest()
        logging.debug(f"User company map hash: {hashed_user_company_map}")

    except Exception as e:
        logging.warning(f"Unable to hash company_map.json files due to: {e}")
        return

    if hashed_default_company_map != hashed_user_company_map:
        try:
            root = tk.Tk()
            root.withdraw()
            answer = messagebox.askyesno(parent=root, 
                                title="Update Company Map?" ,
                                message="Updated company database available. Would you like to update?")
            if answer:
                if os.path.isfile(load_data_path("config", "company_map.json")):
                    logging.debug(f"Removing old company map...")
                    os.remove(load_data_path("config", "company_map.json"))
                logging.info(f"Updating company map...")
                load_default_data_path("config", "company_map.json")
            else:
                logging.info(f"Not updating company map.")
            root.destroy()
        except Exception as e:
            logging.warning(f"Unable to update company map due to: {e}")
    else:
        logging.info(f"Company map already at current version!")

def folder_maps_check():
    """Checks if folder map is different from user's folder map, prompts for change."""
    try:
        # Read the contents of the default folder_maps path and hash it
        default_folder_path = load_default_data_path("config", "folder_maps.json")
        with open(default_folder_path, 'r') as f:
            default_folder_file = f.read()
        hashed_default_folder_map = hashlib.md5(default_folder_file.encode()).hexdigest()
        logging.debug(f"Default folder map hash: {hashed_default_folder_map}")

        # Read the contents of the current user's folder_maps path and hash it
        user_folder_path = load_data_path("config", "folder_maps.json")
        with open(user_folder_path, 'r') as f:
            user_folder_file = f.read()
        hashed_user_folder_map = hashlib.md5(user_folder_file.encode()).hexdigest()
        logging.debug(f"User folder map hash: {hashed_user_folder_map}")

    except Exception as e:
        logging.warning(f"Unable to hash folder_maps.json files due to: {e}")
        return

    if hashed_default_folder_map != hashed_user_folder_map:
        try:
            root = tk.Tk()
            root.withdraw()
            answer = messagebox.askyesno(parent=root, 
                                title="Update Folder Map?" ,
                                message="Updated folder database available. Would you like to update?")
            if answer:
                if os.path.isfile(load_data_path("config", "folder_maps.json")):
                    logging.debug(f"Removing old folder map...")
                    os.remove(load_data_path("config", "folder_maps.json"))
                logging.info(f"Updating folder map...")
                load_default_data_path("config", "folder_maps.json")
            else:
                logging.info(f"Not updating folder map.")
            root.destroy()
        except Exception as e:
            logging.warning(f"Unable to update folder map due to: {e}")
    else:
        logging.info(f"Folder map already at current version!")

def make_legacy_compatible():
    """Reads legacy entries in files and converts them to the modern format usable in recent versions."""
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

        # Skip if archive path is empty or falsy
        if not archive_path:
            logging.debug("No archive path defined in folder_maps.json → skipping")
            return
        
        if new_archive_path:
            logging.debug(f"Archive path already found in paths.json → skipping")
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
            logging.info(f"Added/updated archive path in paths.json: {archive_path}")

        # Save if changes were made
        if changed:
            with open(paths_file, 'w', encoding='utf-8') as f:
                json.dump(paths_data, f, indent=4)
            logging.debug("paths.json updated successfully")

    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in folder_maps.json or paths.json: {e}")
    except Exception as e:
        logging.error(f"Failed to set up archive path: {e}")
