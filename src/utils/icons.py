# src/utils/icons.py
from PySide6.QtGui import QIcon
import logging
from src.utils.load_settings import load_data_path


def load_qt_icons(globs):
    """Loads QT icons."""
    try:
        if globs.os_name.startswith("Linux"):
            globs.github_icon = QIcon(load_data_path("config", "assets/github.svg"))
            globs.github_light_icon = QIcon(load_data_path("config", "assets/github-light.svg"))
            globs.codeberg_icon = QIcon(load_data_path("config", "assets/codeberg.svg"))
        else:
            globs.github_icon = QIcon(load_data_path("config", "assets/github.png"))
            globs.github_light_icon = QIcon(load_data_path("config", "assets/github-light.png"))
            globs.codeberg_icon = QIcon(load_data_path("config", "assets/codeberg.png"))

        globs.mail_icon = QIcon(load_data_path("config", "assets/mail.png"))

    except Exception as e:
        logging.error(f"Failed to load icons due to: {e}")
