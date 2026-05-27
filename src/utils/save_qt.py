# src/qt_interface/qt_settings/save_qt.py
import logging
from src.utils.save_settings import save_settings
from src.utils.load_settings import load_settings


def save_qt_settings(globals):
    """
    Save Qt-specific settings to JSON.
    Currently handles only the GitHub check setting.
    """

    # Read the checkbox states
    new_github_check = globals.github_check_checkbox.isChecked()
    new_beta = globals.beta_checkbox.isChecked()
    new_window_size = globals.window_checkbox.isChecked()
    new_printer = globals.printer_combo.currentText()
    new_legacy_mode = globals.legacy_checkbox.isChecked()

    # Update the globals object immediately
    globals.github_check = new_github_check
    globals.beta = new_beta
    globals.dynamic_window_size = new_window_size
    globals.default_printer = new_printer
    globals.legacy_mode = new_legacy_mode

    # Load current settings to merge with new value
    current_settings = load_settings()
    current_settings["github_check"] = new_github_check
    current_settings["beta"] = new_beta
    current_settings["dynamic_window_size"] = new_window_size
    current_settings["default_printer"] = new_printer
    current_settings["legacy_mode"] = new_legacy_mode

    # Save to JSON file
    try:
        save_settings(**current_settings)
        logging.info(f"Setting Saved!")

    except Exception as e:
        logging.error(f"Failed to save settings: {e}")
