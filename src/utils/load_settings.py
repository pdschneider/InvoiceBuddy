# src/utils/load_settings.py
from pypdf import PdfReader
import logging
import platform
import os
import sys
import json
import shutil


def load_data_path(direct=None, filename=None, default=False):
    """
    Get the path to a writable data folder or a specific file,
    copying bundled default files if needed.
    """
    # ==================== DEFAULT FILES ====================
    default_files = [
        "settings.json", "company_map.json", "categories.json", "ledger.json",
        "paths.json", "default_spreadsheet.xlsx", "default_spreadsheet.ods",
        "assets/icon.png", "assets/add-1.png", "assets/add-2.png", "assets/add-3.png",
        "assets/archive.png", "assets/auto.png", "assets/card-1.png", "assets/card-2.png",
        "assets/cards-1.png", "assets/cards-2.png", "assets/delete-1.png", "assets/delete-2.png",
        "assets/delete-3.png", "assets/delete-4.png", "assets/inbox-1.png", "assets/inbox-2.png",
        "assets/invoice-1.png", "assets/invoice-2.png", "assets/invoice-3.png", "assets/mail.png",
        "assets/pen-1.png", "assets/pen-2.png", "assets/pencil.png", "assets/settings.png",
        "assets/toggle.png", "assets/workbook-1.png", "assets/workbook-2.png", "assets/send.png",
        "assets/download.png", "assets/upload.png", "assets/money-1.png", "assets/money-2.png",
        "assets/money-bag.png", "assets/theme.png", "assets/preferences.png", "assets/note.png",
        "assets/settings-2.png", "assets/printer-1.png", "assets/printer-2.png", "assets/window-size.png",
        "assets/notification-1.png", "assets/notification-2.png", "assets/notification-3.png",
        "sheets.json", "counterparties.json",
        "assets/github-light.svg", "assets/github.svg", "assets/codeberg.svg",
        "assets/github-light.png", "assets/github.png", "assets/codeberg.png"
    ]

    # ==================== DETECT RUN MODE ====================
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller
        is_bundled = True
        bundle_root = sys._MEIPASS

    elif "__compiled__" in globals():
        # Nuitka (onefile or standalone)
        is_bundled = True
        try:
            module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # src/utils/
            bundle_root = os.path.dirname(module_dir)  # root (where defaults/ lives)
        except Exception:
            bundle_root = os.path.dirname(sys.executable)

    else:
        # === DEVELOPMENT MODE ===
        is_bundled = False
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # src/utils/
        dev_base_dir = os.path.dirname(base_dir)  # project root

    # ==================== SET bundled_dir and data_dir ====================
    if is_bundled:
        bundled_dir = os.path.normpath(os.path.join(bundle_root, "defaults"))

        # Persistent directory for user data
        if direct == "config":
            if platform.system() == "Windows":
                persistent_dir = os.path.normpath(os.path.join(os.getenv("APPDATA"), "InvoiceBuddy"))
            else:
                persistent_dir = os.path.normpath(os.path.expanduser("~/.config/InvoiceBuddy"))
        elif direct == "local":
            if platform.system() == "Windows":
                persistent_dir = os.path.normpath(os.path.join(os.getenv("LOCALAPPDATA"), "InvoiceBuddy"))
            else:
                persistent_dir = os.path.normpath(os.path.expanduser("~/.local/share/InvoiceBuddy"))
            default_files = ["default_spreadsheet.xlsx", "default_spreadsheet.ods",
                             "counterparties.json", "categories.json",
                             "ledger.json"]
        else:  # cache or main
            if platform.system() == "Windows":
                persistent_dir = os.path.normpath(
                    os.path.join(os.getenv("LOCALAPPDATA"), "InvoiceBuddy", "Cache"))
            else:
                persistent_dir = os.path.normpath(os.path.expanduser("~/.cache/InvoiceBuddy"))
            default_files = []

        data_dir = persistent_dir

        # Create persistent dir + subdirs
        try:
            os.makedirs(persistent_dir, exist_ok=True)
            if any(f.startswith("assets/") for f in default_files):
                os.makedirs(os.path.join(persistent_dir, "assets"), exist_ok=True)
            if not os.access(persistent_dir, os.W_OK):
                raise PermissionError(f"No write permission for {persistent_dir}")
        except Exception as e:
            logging.error(f"Error creating persistent directory: {e}")
            raise

    else:
        # === DEVELOPMENT ===
        data_dir = os.path.normpath(os.path.join(dev_base_dir, "data"))
        bundled_dir = os.path.normpath(os.path.join(dev_base_dir, "defaults"))

        # Create dev data dir + subdirs
        try:
            os.makedirs(data_dir, exist_ok=True)
            if any(f.startswith("assets/") for f in default_files):
                os.makedirs(os.path.join(data_dir, "assets"), exist_ok=True)
            if not os.access(data_dir, os.W_OK):
                raise PermissionError(f"No write permission for {data_dir}")
        except Exception as e:
            logging.error(f"Error creating data directory: {e}")
            raise

    # ==================== COPY DEFAULT FILES IF MISSING ====================
    for default_file in default_files:
        src = os.path.normpath(os.path.join(bundled_dir, default_file))
        dst = os.path.normpath(os.path.join(data_dir, default_file))
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                logging.info(f"Copied default file: {default_file}")
            except Exception as e:
                logging.error(f"Failed to copy {default_file}: {e}")

    # ==================== RETURN REQUESTED PATH ====================
    if default:
        return os.path.normpath(os.path.join(bundled_dir, filename)) if filename else bundled_dir
    else:
        return os.path.normpath(os.path.join(data_dir, filename)) if filename else data_dir


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


def load_sheets():
    """Load sheet definitions from sheets.json."""
    try:
        file_path = os.path.normpath(load_data_path("config", "sheets.json"))
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Error: sheets.json not found in data folder")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding sheets.json: {e}")
        return []


# File metadata
METADATA_KEYS = {
    "/Counterparty": "Counterparty",
    "/Date": "Date",
    "/Amount": "Amount",
    "/Category": "Category",
    "/Subcategory": "Subcategory",
    "/Description": "Description",
    "/CardNumber": "Card Number",
    "/InvoiceNumber": "Invoice Number",
    "/Net": "Terms (Net)",
    "/Tax": "Tax",
}


def read_file_metadata(filepath):
    """Reads auto-name metadata keys from a PDF, skipping missing ones."""
    fields = {}
    try:
        reader = PdfReader(filepath)
        if reader.metadata:
            for key, label in METADATA_KEYS.items():
                value = reader.metadata.get(key)
                if value:
                    fields[label] = str(value)
    except Exception:
        pass
    return fields


def load_counterparties():
    """Load counterparties from counterparties.json."""
    try:
        file_path = os.path.normpath(load_data_path("local", "counterparties.json"))
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Error: counterparties.json not found")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding counterparties.json: {e}")
        return {}


def load_categories():
    """Load categories from categories.json."""
    try:
        file_path = os.path.normpath(load_data_path("local", "categories.json"))
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Error: categories.json not found")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding categories.json: {e}")
        return {}


def load_ledger():
    """Load accounts and transactions from ledger.json."""
    try:
        file_path = os.path.normpath(load_data_path("local", "ledger.json"))
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Error: ledger.json not found")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding ledger.json: {e}")
        return {}
