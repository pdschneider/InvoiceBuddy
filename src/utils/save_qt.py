# src/qt_interface/qt_settings/save_qt.py
from src.utils.save_settings import save_settings, save_paths
from src.utils.load_settings import load_settings, load_paths
from src.utils.load_settings import load_data_path
from pypdf import PdfReader, PdfWriter
import json
import logging
import os


def save_qt_settings(globals):
    """
    Save Qt-specific settings to JSON.
    Currently handles only the GitHub check setting.
    """

    # Read settings states
    new_github_check = globals.github_check_checkbox.isChecked()
    new_beta = globals.beta_checkbox.isChecked()
    new_window_size = globals.window_checkbox.isChecked()
    new_printer = globals.printer_combo.currentText()
    new_legacy_mode = globals.legacy_checkbox.isChecked()
    new_logging_level = globals.logging_level_box.currentText().upper()

    # Read Inbox Path
    if str(globals.inbox_entry_box.text()):
        new_inbox = str(globals.inbox_entry_box.text())
    elif globals.inbox:
        new_inbox = globals.inbox
    else:
        new_inbox = str(globals.inbox_entry_box.placeholderText())
    if not os.path.isdir(new_inbox):
        try:
            os.makedirs(new_inbox)
        except Exception as e:
            logging.error(f"Unable to make inbox path due to: {e}")

    # Read Archive Path
    if str(globals.archive_entry_box.text()):
        new_archive = str(globals.archive_entry_box.text())
    elif globals.archive:
        new_archive = globals.archive
    else:
        new_archive = str(globals.archive_entry_box.placeholderText())
    if not os.path.isdir(new_archive):
        try:
            os.makedirs(new_archive)
        except Exception as e:
            logging.error(f"Unable to make archive path due to: {e}")

    # Update the globals object immediately
    globals.github_check = new_github_check
    globals.beta = new_beta
    globals.dynamic_window_size = new_window_size
    globals.default_printer = new_printer
    globals.legacy_mode = new_legacy_mode
    globals.logging_level = new_logging_level
    globals.inbox = new_inbox
    globals.archive = new_archive

    # Load current settings to merge with new values
    current_settings = load_settings()
    current_settings["github_check"] = new_github_check
    current_settings["beta"] = new_beta
    current_settings["dynamic_window_size"] = new_window_size
    current_settings["default_printer"] = new_printer
    current_settings["legacy_mode"] = new_legacy_mode
    current_settings["logging_level"] = new_logging_level

    # Load current paths to merge with new values
    current_paths, current_buddies = load_paths()
    current_paths["inbox"] = new_inbox
    current_paths["archive"] = new_archive

    # Save to JSON files
    try:
        save_settings(**current_settings)
        save_paths(globals, sources=current_paths, buddies=current_buddies)
        logging.info(f"Setting Saved!")
    except Exception as e:
        logging.error(f"Failed to save settings: {e}")

    # Save sheet definitions
    save_sheets(globals)


def save_sheets(globals):
    """Save sheet definitions to sheets.json."""
    
    try:
        file_path = load_data_path("config", "sheets.json")
        with open(file_path, 'w') as f:
            json.dump(globals.sheet_data, f, indent=2)
        logging.info(f"Saved {len(globals.sheet_data.get('sheets', []))} sheet definitions.")
    except Exception as e:
        logging.error(f"Failed to save sheets.json: {e}")


def save_metadata(globals):
    """Save sheet assignments to PDF metadata as /Sheet."""

    inbox_dir = globals.inbox
    if not hasattr(globals, "file_identity") or not globals.file_identity:
        return
    if not os.path.isdir(inbox_dir):
        return

    saved_count = 0
    for filename, sheet_name in globals.file_identity.items():
        filepath = os.path.join(inbox_dir, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            reader = PdfReader(filepath)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            if reader.metadata:
                writer.add_metadata(reader.metadata)
            writer.add_metadata({"/Sheet": sheet_name})
            with open(filepath, "wb") as f:
                writer.write(f)
            saved_count += 1
        except Exception as e:
            logging.warning(f"Could not save /Sheet to {filename}: {e}")

    logging.info(f"Saved /Sheet metadata to {saved_count} PDF files.")
