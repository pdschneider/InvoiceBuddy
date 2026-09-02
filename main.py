# main.py
import sys
import logging
from src.utils.dependencies import check_dependencies
check_dependencies()
from src.utils.startup import setup
from config import globs
from src.utils.factory_reset import factory_reset_config
from src.interface.interface import create_interface
from src.utils.save_settings import save_all_settings
from src.qt_interface.qt_interface import create_qt_interface


# Ensures settings files are usable
setup(globs)


def on_closing():
    """Closes observers when the program closes."""
    try:
        if hasattr(globs, 'observers'):
            for observer in globs.observers.values():
                if observer and observer.is_alive():
                    observer.stop()
                    observer.join(timeout=10.0)
        logging.debug(f"Observers successfully shut down!")
    except Exception as e:
        logging.error(f"Unable to shut down observers due to: {e}")
    try:
        if globs.legacy_mode:
            save_all_settings(globs, reject_toast=True)
    except Exception as e:
        logging.error(f"Error occurred when saving settings: {e}")

    # Properly shut down
    logging.debug(f"Shutting down...")
    if globs.legacy_mode:
        globs.root.withdraw()
        globs.root.quit()
        globs.root.destroy()
    else:
        globs.app.quit()
    logging.shutdown()

if __name__ == "__main__":
    # Initialize GUI
    if not globs.legacy_mode:
        create_qt_interface(globs)
        sys.exit(globs.app.exec())
    else:
        if getattr(sys, 'frozen', False):  # If bundled
            try:
                create_interface(globs)
                globs.root.protocol("WM_DELETE_WINDOW", on_closing)
                globs.root.mainloop()
            except Exception as error:
                if globs.root:
                    try:
                        globs.root.quit()
                        globs.root.destroy()
                    except Exception as e:
                        logging.error(
                            f"Unable to destroy window during exception: {e}")
                factory_reset_config(globs, error)
        else:  # Not bundled
            create_interface(globs)
            globs.root.protocol("WM_DELETE_WINDOW", on_closing)
            globs.root.mainloop()
