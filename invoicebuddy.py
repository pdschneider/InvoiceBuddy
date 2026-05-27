# invoicebuddy.py
import sys
import logging
from src.utils.dependencies import check_dependencies
check_dependencies()
from src.utils.startup import setup
from config import globals
from src.utils.factory_reset import factory_reset_config
from src.interface.interface import create_interface
from src.utils.save_settings import save_all_settings
from src.qt_interface.qt_interface import create_qt_interface


# Ensures settings files are usable
setup(globals)


def on_closing():
    """Closes observers when the program closes."""
    try:
        if hasattr(globals, 'observers'):
            for observer in globals.observers.values():
                if observer and observer.is_alive():
                    observer.stop()
                    observer.join(timeout=10.0)
        logging.debug(f"Observers successfully shut down!")
    except Exception as e:
        logging.error(f"Unable to shut down observers due to: {e}")
    try:
        if globals.legacy_mode:
            save_all_settings(globals, reject_toast=True)
    except Exception as e:
        logging.error(f"Error occurred when saving settings: {e}")
    
    # Properly shut down
    logging.debug(f"Shutting down...")
    if globals.legacy_mode:
        globals.root.withdraw()
        globals.root.quit()
        globals.root.destroy()
    else:
        globals.app.quit()
    logging.shutdown()

if __name__ == "__main__":
    # Initialize GUI
    if not globals.legacy_mode:
        create_qt_interface(globals)
        sys.exit(globals.app.exec())
    else:
        if getattr(sys, 'frozen', False):  # If bundled
            try:
                create_interface(globals)
                globals.root.protocol("WM_DELETE_WINDOW", on_closing)
                globals.root.mainloop()
            except Exception as error:
                if globals.root:
                    try:
                        globals.root.quit()
                        globals.root.destroy()
                    except Exception as e:
                        logging.error(
                            f"Unable to destroy window during exception: {e}")
                factory_reset_config(globals, error)
        else:  # Not bundled
            create_interface(globals)
            globals.root.protocol("WM_DELETE_WINDOW", on_closing)
            globals.root.mainloop()
