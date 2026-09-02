# src/qt_interface/qt_settings/save_qt.py
from src.utils.save_settings import save_settings, save_paths
from src.utils.load_settings import load_settings, load_paths
from src.utils.load_settings import load_data_path
from pypdf import PdfReader, PdfWriter
import json
import logging
import os


def save_qt_settings(globs):
    """
    Save Qt-specific settings to JSON.
    Currently handles only the GitHub check setting.
    """

    # Read settings states
    new_github_check = globs.github_check_checkbox.isChecked()
    new_beta = globs.beta_checkbox.isChecked()
    new_window_size = globs.window_checkbox.isChecked()
    new_printer = globs.printer_combo.currentText()
    new_legacy_mode = globs.legacy_checkbox.isChecked()
    new_logging_level = globs.logging_level_box.currentText().upper()

    # Read Inbox Path
    if str(globs.inbox_entry_box.text()):
        new_inbox = str(globs.inbox_entry_box.text())
    elif globs.inbox:
        new_inbox = globs.inbox
    else:
        new_inbox = str(globs.inbox_entry_box.placeholderText())
    if not os.path.isdir(new_inbox):
        try:
            os.makedirs(new_inbox)
        except Exception as e:
            logging.error(f"Unable to make inbox path due to: {e}")

    # Read Archive Path
    if str(globs.archive_entry_box.text()):
        new_archive = str(globs.archive_entry_box.text())
    elif globs.archive:
        new_archive = globs.archive
    else:
        new_archive = str(globs.archive_entry_box.placeholderText())
    if not os.path.isdir(new_archive):
        try:
            os.makedirs(new_archive)
        except Exception as e:
            logging.error(f"Unable to make archive path due to: {e}")

    # Update the globs object immediately
    globs.github_check = new_github_check
    globs.beta = new_beta
    globs.dynamic_window_size = new_window_size
    globs.default_printer = new_printer
    globs.legacy_mode = new_legacy_mode
    globs.logging_level = new_logging_level
    globs.inbox = new_inbox
    globs.archive = new_archive

    # Load current settings to merge with new values
    current_settings = load_settings()
    current_settings["github_check"] = new_github_check
    current_settings["beta"] = new_beta
    current_settings["dynamic_window_size"] = new_window_size
    current_settings["default_printer"] = new_printer
    current_settings["legacy_mode"] = new_legacy_mode
    current_settings["logging_level"] = new_logging_level
    current_settings["previous_version"] = globs.current_version

    # Load current paths to merge with new values
    current_paths, current_buddies = load_paths()
    current_paths["inbox"] = new_inbox
    current_paths["archive"] = new_archive

    # Gather buddy entries from Qt UI
    new_buddies = {}
    buddy_counter = 0
    for entry in globs.buddy_entries:
        name = entry["name_input"].text().strip()[:9]
        path = entry["path_input"].text().strip()

        if name.lower() == "inbox":
            buddy_counter += 1
            name = f"inbox-{buddy_counter}"
            logging.warning("Buddy name cannot be 'inbox'. Sanitizing...")

        if name and path and os.path.isdir(path):
            new_buddies[name] = path

    # Save to JSON files
    try:
        save_settings(**current_settings)
        save_paths(globs, sources=current_paths, buddies=new_buddies)
        logging.info(f"Setting Saved!")
    except Exception as e:
        logging.error(f"Failed to save settings: {e}")

    # Clear text boxes and update placeholders to show saved values
    globs.inbox_entry_box.clear()
    globs.inbox_entry_box.setPlaceholderText(globs.inbox)

    globs.archive_entry_box.clear()
    globs.archive_entry_box.setPlaceholderText(globs.archive)

    # Save sheet definitions
    save_sheets(globs)


def save_sheets(globs):
    """Save sheet definitions to sheets.json."""
    
    try:
        file_path = load_data_path("config", "sheets.json")
        with open(file_path, 'w') as f:
            json.dump(globs.sheet_data, f, indent=2)
        logging.info(f"Saved {len(globs.sheet_data.get('sheets', []))} sheet definitions.")
    except Exception as e:
        logging.error(f"Failed to save sheets.json: {e}")


def save_metadata(globs):
    """Save sheet assignments to PDF metadata as /Sheet."""

    inbox_dir = globs.inbox
    if not hasattr(globs, "file_identity") or not globs.file_identity:
        return
    if not os.path.isdir(inbox_dir):
        return

    saved_count = 0
    for filename, sheet_name in globs.file_identity.items():
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
