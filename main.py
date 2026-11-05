# main
import sys
from src.utils.dependencies import check_dependencies
check_dependencies()
from src.utils.startup import setup
from config import globs
from src.utils.factory_reset import factory_reset_config
from src.interface.interface import create_qt_interface
from src.interface.setup_wizard import create_wizard
from packaging import version


# Ensures settings files are usable
setup(globs)


# Trigger wizard if first time using the app
if version.parse(globs.previous_version) == version.parse("0.1.0"):
    create_wizard(globs)


if __name__ == "__main__":
    # Initialize GUI
    try:
        create_qt_interface(globs)
        sys.exit(globs.app.exec())
    except Exception as error:
        factory_reset_config(globs, error)
