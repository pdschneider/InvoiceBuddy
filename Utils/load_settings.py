# Utils/load_settings.py
import logging
import platform
import os
import sys
import json
import shutil


def load_data_path(direct=None, filename=None, default=False):
    """
    Get the path to a writable data folder or a specific file,
    copying bundled files if needed.

    Parameters:
        direct = The file type to specify its directory,
        either configuration, persistent user data, or logs
        filename = The file name being accessed
        default = If the default folder is requested
    """
    os_name = platform.platform()
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
                     "assets/invoice-3.png",
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
                     "assets/money-1.png",
                     "assets/money-2.png",
                     "assets/money-bag.png",
                     "assets/theme.png",
                     "assets/preferences.png",
                     "assets/note.png",
                     "assets/settings-2.png",
                     "themes/cosmic_sky.json",
                     "themes/pastel_green.json",
                     "themes/trojan_red.json",
                     "themes/dark_cloud.json",
                     "themes/soft_light.json"]
    # Get base dir from __file__
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dev_base_dir = os.path.dirname(base_dir)

    # Running in development
    if os.path.exists(os.path.join(dev_base_dir, 'InvoiceBuddy.py')):
        data_dir = os.path.normpath(os.path.join(dev_base_dir, "data"))
        bundled_dir = os.path.normpath(os.path.join(dev_base_dir, "defaults"))

        # Checks if any file has themes/ or assets/ path
        try:
            os.makedirs(data_dir, exist_ok=True)
            if any("themes/" in f for f in default_files):
                themes_dir = os.path.join(data_dir, "themes")
                os.makedirs(themes_dir, exist_ok=True)
            if any("assets/" in f for f in default_files):
                assets_dir = os.path.join(data_dir, "assets")
                os.makedirs(assets_dir, exist_ok=True)
            if not os.access(data_dir, os.W_OK):
                raise PermissionError(f"No write permission for {data_dir}")
        except Exception as e:
            logging.error(f"Error creating data directory: {e}")
            raise

    # Running as bundled executable
    else:
        # Determine bundle root
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # PyInstaller
            bundle_root = sys._MEIPASS
        else:
            # Nuitka or other - assume similar to dev, go up from base_dir
            bundle_root = os.path.dirname(base_dir)

            # Safety check: climb up until we find a likely root
            max_climb = 5  # Prevent infinite loop
            climb_count = 0
            while not os.path.exists(os.path.join(bundle_root, "defaults")) and climb_count < max_climb:
                bundle_root = os.path.dirname(bundle_root)
                climb_count += 1
            if climb_count == max_climb:
                logging.warning(
                    "Could not find bundle root automatically - defaults may not copy.")

        bundled_dir = os.path.normpath(os.path.join(bundle_root, "defaults"))

        # Set persistent_dir based on direct
        if direct == "config":
            if os_name.startswith("Windows"):
                persistent_dir = os.path.normpath(
                    os.path.join(os.getenv("APPDATA"), "InvoiceBuddy"))
            else:
                persistent_dir = os.path.normpath(
                    os.path.expanduser("~/.config/InvoiceBuddy"))
                if not os_name.startswith("Linux"):
                    logging.warning("OS not found. Defaulting to Linux paths.")
        elif direct == "local":
            if os_name.startswith("Windows"):
                persistent_dir = os.path.normpath(
                    os.path.join(os.getenv("LOCALAPPDATA"), "InvoiceBuddy"))
            else:
                persistent_dir = os.path.normpath(
                    os.path.expanduser("~/.local/share/InvoiceBuddy"))
                if not os_name.startswith("Linux"):
                    logging.warning("OS not found. Defaulting to Linux paths.")
            default_files = []  # No defaults for local?
        else:  # cache
            if os_name.startswith("Windows"):
                persistent_dir = os.path.normpath(
                    os.path.join(
                        os.getenv("LOCALAPPDATA"), "InvoiceBuddy", "Cache"))
            else:
                persistent_dir = os.path.normpath(
                    os.path.expanduser("~/.cache/InvoiceBuddy"))
                if not os_name.startswith("Linux"):
                    logging.warning("OS not found. Defaulting to Linux paths.")
            default_files = []  # No defaults for cache?

        # Create persistent dir and subdirs
        try:
            os.makedirs(persistent_dir, exist_ok=True)
            if any("themes/" in f for f in default_files):
                themes_dir = os.path.join(persistent_dir, "themes")
                os.makedirs(themes_dir, exist_ok=True)
            if any("assets/" in f for f in default_files):
                assets_dir = os.path.join(persistent_dir, "assets")
                os.makedirs(assets_dir, exist_ok=True)
            if not os.access(persistent_dir, os.W_OK):
                raise PermissionError(
                    f"No write permission for {persistent_dir}")
        except Exception as e:
            logging.error(f"Error creating persistent data directory: {e}")
            raise

        data_dir = persistent_dir

    # Copy defaults (common to both dev and bundled)
    for default_file in default_files:
        bundled_file = os.path.normpath(
            os.path.join(bundled_dir, default_file))
        persistent_file = os.path.normpath(
            os.path.join(data_dir, default_file))
        if os.path.exists(bundled_file) and not os.path.exists(persistent_file):
            try:
                os.makedirs(os.path.dirname(persistent_file), exist_ok=True)
                logging.info(
                    f"Copying {default_file} from {bundled_file} to {persistent_file}")
                shutil.copy(bundled_file, persistent_file)
            except Exception as e:
                logging.error(f"Error copying {default_file}: {e}")

    if not default:
        return os.path.normpath(
            os.path.join(data_dir, filename)) if filename else data_dir
    else:
        return os.path.normpath(
            os.path.join(bundled_dir, filename)) if filename else bundled_dir


def load_spreadsheet_specs():
    """Get the spreadsheet data such as table and sheet names."""
    try:
        file_path = os.path.normpath(
            load_data_path("config", "spreadsheet.json"))
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
        file_path = os.path.normpath(
            load_data_path("config", "company_map.json"))
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
        return settings.get(
            "history_path", load_data_path("local", "history.csv"))


def load_folder_map():
    """
    Load folder_map from folder_maps.json and
    return (folder_map, oneoffs_folder).
    """
    try:
        # Load subfolders from folder_maps
        file_path = os.path.normpath(
            load_data_path("config", "folder_maps.json"))
        with open(file_path, 'r') as f:
            subfolder_data = json.load(f)

        # Load archive from paths.json
        file_path = os.path.normpath(load_data_path("config", "paths.json"))
        with open(file_path, 'r') as f:
            archive_path_data = json.load(f)

        try:
            archive_path = archive_path_data["sources"]["archive"]
        except:
            logging.warning(
                "Archive path not loaded properly in load_folder_map, sanitizing...")
            archive_path = ""

        folder_map = {}
        # All vendors now live under the single archive folder
        for key_str, subfolder in subfolder_data['maps'].items():
            tuple_key = tuple(key_str.split(','))
            full_path = os.path.join(archive_path, subfolder)
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
        raise json.JSONDecodeError(
            f"Invalid folder_maps.json: {e}", e.doc, e.pos)
    except KeyError as e:
        logging.error(f"Missing required key in folder_maps.json: {e}")
        raise KeyError(f"Missing key in folder_maps.json: {e}")


def load_paths():
    """Load user-specific paths like inbox and workbook."""
    try:
        file_path = os.path.normpath(load_data_path("config", "paths.json"))
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
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Error: settings.json not found in data folder")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding settings.json: {e}")
        return {}
