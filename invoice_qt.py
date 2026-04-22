import sys
import logging
from src.utils.dependencies import check_dependencies
check_dependencies()
from src.qt_interface.qt_interface import create_interface
from config import globals
from src.utils.startup import setup


setup(globals)

globals.qt_mode = True

if __name__ == "__main__":
    # Initialize GUI
    create_interface(globals)
    sys.exit(globals.app.exec())
