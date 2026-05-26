# src/qt_interface/qt_settings/save_qt.py

import logging
from src.utils.save_settings import save_settings
from src.utils.load_settings import load_settings


def save_qt_settings(globals):
    """
    Save Qt-specific settings to JSON.
    Currently handles only the GitHub check setting.
    """

    # 1. Read the checkbox state
    new_github_check = globals.github_check_checkbox.isChecked()

    # 2. Check if anything actually changed
    if new_github_check == globals.github_check:
        logging.info("No changes detected in General settings.")
        return

    # 3. Update the globals object immediately
    globals.github_check = new_github_check

    # 4. Load current settings to merge with new value
    current_settings = load_settings()
    current_settings["github_check"] = new_github_check

    # 5. Save to JSON file
    try:
        save_settings(**current_settings)
        logging.info(f"GitHub check setting saved: {new_github_check}")

        # Optional: Print confirmation (since no toasts in Qt version)
        print(f"✓ Settings saved! GitHub check: {'ON' if new_github_check else 'OFF'}")

    except Exception as e:
        logging.error(f"Failed to save settings: {e}")
        print(f"✗ Error saving settings: {e}")
