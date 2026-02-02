# Utils/setup.py
import logging, os, json, csv, shutil
from logging.handlers import TimedRotatingFileHandler
from Utils.load_settings import load_data_path, load_settings

def setup():
    setup_logging()
    setup_company_map()
    setup_folder_maps()
    setup_settings()
    setup_paths()
    setup_spreadsheet()
    setup_history()
    setup_themes()

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
        if "bases" not in data:
            data["bases"] = {}
            changed = True
            logging.info(f"Adding missing 'bases' key to folder_maps.json")

        # Check to make sure keys are present
        if "archive" not in data.get("bases", {}):
            data["bases"]["archive"] = ""
            changed = True
            logging.info(f"Added missing 'archive' under bases")

        # Write to file
        if changed:
            with open(folder_map, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            changed = False

        # Check to make sure keys are the correct type
        if not isinstance(data["bases"]["archive"], str):
            logging.warning(f"Current type of value for archive: {type(data["bases"]["archive"])}")
            data["bases"]["archive"] = ""
            changed = True
            logging.info(f"Sanitizing incorrect type 'archive' under bases")

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
            logging.info("Added missing 'logging_level' key to settings.json")
        if "saved_height" not in data:
            data["saved_height"] = 0
            changed = True
            logging.info(f"Adding missing 'active_theme' key to settings.json")
        if "saved_x" not in data:
            data["saved_x"] = 0
            changed = True
            logging.info(f"Added missing 'history_path' key to settings.json")
        if "saved_y" not in data:
            data["saved_y"] = 0
            changed = True
            logging.info(f"Added missing 'history_path' key to settings.json")

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
        logging.info(f"History path: {data["history_path"]}")
        if not os.path.exists(data["history_path"]):
            logging.warning(f"History Path not a valid path.")
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
            json.load(f)
        logging.debug(f"spreadsheet data loaded successfully from {spreadsheet}")
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
    headers = ["File Name", "Source Folder", "Destination Folder", "Type", "Moved", "Entered"]
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
