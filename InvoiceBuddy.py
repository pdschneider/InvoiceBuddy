# InvoiceBuddy.py
import sys
import logging
from Utils.dependencies import check_dependencies
check_dependencies()
from Utils.startup import setup
from config import globals
from Utils.factory_reset import factory_reset
from Interface.interface import create_interface
from Utils.save_settings import save_all_settings


# Ensures settings files are usable
setup(globals)


def on_closing():
    """Closes observers when the program closes."""
    if hasattr(globals, 'observers'):
        for observer in globals.observers.values():
            if observer and observer.is_alive():
                observer.stop()
                observer.join()
    try:
        save_all_settings(globals, reject_toast=True)
    except Exception as e:
        logging.error(f"Error occurred when saving settings: {e}")
    logging.shutdown()
    globals.root.quit()
    globals.root.destroy()

if __name__ == "__main__":
    # Initialize GUI
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
            factory_reset(error)
    else:  # Not bundled
        create_interface(globals)
        globals.root.protocol("WM_DELETE_WINDOW", on_closing)
        globals.root.mainloop()
