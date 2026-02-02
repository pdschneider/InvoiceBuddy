# Utils/load_settings.py
import logging, platform, os, sys, json, shutil
import customtkinter as ctk

def load_data_path(direct=None, filename=None):
    """
    Get the path to a writable data folder or a specific file, copying bundled files if needed.

        Parameters:
                direct = The file type to specify its directory, either configuration, persistent user data, or logs
                filename = The file name being accessed
    """
    default_files = ["settings.json", 
                        "company_map.json", 
                        "folder_maps.json", 
                        "FY26-Blank_Workbook.xlsx",
                        "paths.json",
                        "spreadsheet.json",
                        "assets/icon.png",
                        "assets/add-1.png",
                        "assets/add-2.png",
                        "assets/add-3.png",
                        "assets/archive.png",
                        "assets/auto.png",
                        "assets/card-1.png",
                        "assets/card-2.png",
                        "assets/cards-1.png",
                        "assets/cards-2.png",
                        "assets/delete-1.png",
                        "assets/delete-2.png",
                        "assets/delete-3.png",
                        "assets/delete-4.png",
                        "assets/inbox-1.png",
                        "assets/inbox-2.png",
                        "assets/invoice-1.png",
                        "assets/invoice-2.png",
                        "assets/invoice.3.png",
                        "assets/mail.png",
                        "assets/pen-1.png",
                        "assets/pen-2.png",
                        "assets/pencil.png",
                        "assets/settings.png",
                        "assets/toggle.png",
                        "assets/workbook-1.png",
                        "assets/workbook-2.png",
                        "assets/send.png",
                        "assets/download.png",
                        "assets/upload.png",
                        "themes/cosmic_sky.json", 
                        "themes/pastel_green.json", 
                        "themes/trojan_red.json", 
                        "themes/dark_cloud.json", 
                        "themes/soft_light.json"]
    if getattr(sys, 'frozen', False):
        logging.debug(f"Program has been bundled with Pyinstaller")
        if direct == "config":
            if platform.system().startswith("Windows"):
                persistent_dir = os.path.normpath(os.path.join(os.getenv("APPDATA"), "InvoiceBuddy"))
            else:
                persistent_dir = os.path.normpath(os.path.expanduser("~/.config/InvoiceBuddy"))
        elif direct == "local":
            if platform.system().startswith("Windows"):
                persistent_dir = os.path.normpath(os.path.join(os.getenv("LOCALAPPDATA"), "InvoiceBuddy"))
            else:
                persistent_dir = os.path.normpath(os.path.expanduser("~/.local/share/InvoiceBuddy"))
            default_files = ["users.json",
                             "history.csv",
                             "Welcome to Invoice Buddy.pdf"]
        else:
            if platform.system().startswith("Windows"):
                persistent_dir = os.path.normpath(os.path.join(os.getenv("LOCALAPPDATA"), "InvoiceBuddy", "Cache"))
            else:
                persistent_dir = os.path.normpath(os.path.expanduser("~/.cache/InvoiceBuddy"))
            default_files = []

        # Checks if any file has themes/ or assets/ path
        try:
            os.makedirs(persistent_dir, exist_ok=True)
            if "themes/" in str(default_files):
                themes_dir = os.path.join(persistent_dir, "themes")
                os.makedirs(themes_dir, exist_ok=True)
            if "assets/" in str(default_files):
                assets_dir = os.path.join(persistent_dir, "assets")
                os.makedirs(assets_dir, exist_ok=True)
            if not os.access(persistent_dir, os.W_OK):
                raise PermissionError(f"No write permission for {persistent_dir}")
        except Exception as e:
            logging.error(f"Error creating persistent data directory: {e}")
            raise
        bundled_dir = os.path.normpath(os.path.join(sys._MEIPASS, "defaults"))
        for default_file in default_files:
            bundled_file = os.path.normpath(os.path.join(bundled_dir, default_file))
            persistent_file = os.path.normpath(os.path.join(persistent_dir, default_file))
            if os.path.exists(bundled_file) and not os.path.exists(persistent_file):
                try:
                    logging.info(f"Copying {default_file} from {bundled_file} to {persistent_file}")
                    shutil.copy(bundled_file, persistent_file)
                except Exception as e:
                    logging.error(f"Error copying {default_file}: {e}")
        data_dir = persistent_dir
    else:  #  Running in development
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.normpath(os.path.join(base_dir, "data"))
        defaults_dir = os.path.normpath(os.path.join(base_dir, "defaults"))

        # Checks if any file has themes/ or assets/ path
        try:
            os.makedirs(data_dir, exist_ok=True)
            if "themes/" in str(default_files):
                themes_dir = os.path.join(data_dir, "themes")
                os.makedirs(themes_dir, exist_ok=True)
            if "assets/" in str(default_files):
                assets_dir = os.path.join(data_dir, "assets")
                os.makedirs(assets_dir, exist_ok=True)
            if not os.access(data_dir, os.W_OK):
                raise PermissionError(f"No write permission for {persistent_dir}")
        except Exception as e:
            logging.error(f"Error creating persistent data directory: {e}")
            raise

        # Loads defaults
        for default_file in default_files:
            bundled_file = os.path.normpath(os.path.join(defaults_dir, default_file))
            persistent_file = os.path.normpath(os.path.join(data_dir, default_file))

            if os.path.exists(bundled_file) and not os.path.exists(persistent_file):
                try:
                    logging.info(f"Copying {default_file} from {bundled_file} to {persistent_file}")
                    shutil.copy(bundled_file, persistent_file)
                except Exception as e:
                    logging.error(f"Error copying {default_file}: {e}")
        try:
            os.makedirs(data_dir, exist_ok=True)
            if not os.access(data_dir, os.W_OK):
                raise PermissionError(f"No write permission for {data_dir}")
        except Exception as e:
            logging.error(f"Error creating data directory: {e}")
            raise
    return os.path.normpath(os.path.join(data_dir, filename)) if filename else data_dir

def load_spreadsheet_specs():
    """Get the spreadsheet data such as table and sheet names."""
    try:
        file_path = os.path.normpath(load_data_path("config", "spreadsheet.json"))
        logging.debug(f"Loading spreadsheet data from: {file_path}")
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Error: spreadsheet.json not found in data folder")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding spreadsheet.json: {e}")
        return {}

def load_company_map():
    """Load company_map from company_map.json."""
    try:
        file_path = os.path.normpath(load_data_path("config", "company_map.json"))
        logging.debug(f"Loading company_map.json from: {file_path}")
        with open(file_path, 'r') as f:
            data = json.load(f)
            return {tuple(k.split(',')): v for k, v in data['company_map'].items()}
    except FileNotFoundError:
        logging.error("Error: company_map.json not found in data folder")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding company_map.json: {e}")
        return {}

def load_users_path():
    """Get the path for users.json."""
    return os.path.normpath(load_data_path("local", "users.json"))

def load_history_path():
    """Fetches the history CSV file."""
    settings = load_settings()
    if not settings.get("history_path", load_data_path("local", "history.csv")):
        return os.path.normpath(load_data_path("local", "history.csv"))
    else:
        return settings.get("history_path", load_data_path("local", "history.csv"))

def load_folder_map():
    """Load folder_map from folder_maps.json and return (folder_map, oneoffs_folder)."""
    try:
        file_path = os.path.normpath(load_data_path("config", "folder_maps.json"))
        logging.debug(f"Loading folder_maps.json from: {file_path}")
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        try:
            archive_path = os.path.normpath(data['bases']['archive'])
        except:
            logging.warning(f"Archive path not loaded properly in load_folder_map, sanitizing...")
            archive_path = ""

        folder_map = {}
        # All vendors (former facility + utility) now live under the single archive folder
        for key_str, subfolder in data['maps'].items():
            tuple_key = tuple(key_str.split(','))
            full_path = os.path.join(archive_path, subfolder)
            logging.debug(f"Full path to folder_maps: {full_path}")
            logging.debug(f"Archive Path: {archive_path}")
            logging.debug(f"Archive subfolder: {subfolder}")
            folder_map[tuple_key] = os.path.normpath(full_path)

        # One-offs → Miscellaneous subfolder inside the archive
        miscellaneous_path = os.path.join(archive_path, "Miscellaneous")
        oneoffs_folder = os.path.normpath(miscellaneous_path)

        return folder_map, oneoffs_folder

    except FileNotFoundError:
        logging.error(f"folder_maps.json not found at: {file_path}")
        raise FileNotFoundError(f"folder_maps.json not found at: {file_path}")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding folder_maps.json: {e}")
        raise json.JSONDecodeError(f"Invalid folder_maps.json: {e}", e.doc, e.pos)
    except KeyError as e:
        logging.error(f"Missing required key in folder_maps.json: {e}")
        raise KeyError(f"Missing key in folder_maps.json: {e}")

def load_paths():
    """Load user-specific paths like inbox and workbook."""
    try:
        file_path = os.path.normpath(load_data_path("config", "paths.json"))
        logging.debug(f"Loading paths.json from: {file_path}")
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        sources = data["sources"]
        buddies = data["buddies"]
        return sources, buddies

    except FileNotFoundError:
        logging.error(f"paths.json not found at: {file_path}")
        raise FileNotFoundError(f"paths.json not found at: {file_path}")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding paths.json: {e}")
        raise json.JSONDecodeError(f"Invalid paths.json: {e}", e.doc, e.pos)

def load_settings():
    """Load settings from settings.json in the data folder."""
    try:
        file_path = os.path.normpath(load_data_path("config", "settings.json"))
        logging.debug(f"Loading settings from: {file_path}")
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Error: settings.json not found in data folder")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding settings.json: {e}")
        return {}
