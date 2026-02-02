# InvoiceBuddy.py
# v0.1.0

# Sets up logging and settings files
from Utils.setup import setup
setup()

from config import globals
from Utils.factory_reset import factory_reset
from Interface.interface import create_interface
from Utils.save_settings import save_all_settings
import sys

def on_closing():
    """Closes observers when the program closes."""
    if hasattr(globals, 'observers'): #  Checks if hasattr has the attribute 'observers' for watchdog
        for observer in globals.observers.values(): #  If observers exists, loops through its values
            if observer and observer.is_alive(): #  For each observer, checks that observer isn't None and is active
                observer.stop() #  If an observer is alive, it stops it
                observer.join() #  After stopping, waits for the observers thread to finish
    try:
        save_all_settings(globals)
    except:
        pass
    globals.root.destroy() #  Closes the main graphical window of the program

# Initialize GUI
if getattr(sys, 'frozen', False):
    try:
        create_interface(globals) # Create the interface, passing the globals object
        globals.root.protocol("WM_DELETE_WINDOW", on_closing) #  Closes the entire program, makes sure on_closing processes runs first
        globals.root.mainloop()
    except Exception as error:
        if globals.root:
            try:
                globals.root.destroy()
            except:
                pass
        factory_reset(error)
else:
    create_interface(globals) # Create the interface, passing the globals object
    globals.root.protocol("WM_DELETE_WINDOW", on_closing) # Closes the entire program, makes sure on_closing processes runs first
    globals.root.mainloop()

"""
Changelog:

- Initial Release
- Normalized button icons
- Application runs through initial checks and cleans settings files if corrupted or missing values
- Draws window in the center of the screen if saved screen dimensions are missing or 0
- Removed broken regenerate workbook buttons and revert history button
- Sanitized settings pages to eliminate saving nonconforming values
- Silenced CTkImage warnings
- Ensures all file opening or path selection can only choose working paths
- Application automatically creates new folders if one doesn't exist when archiving
- Added onboarding page for application start under empty or invalid path conditions
- Added welcome document
- Fixed workbook and inbox not opening on Windows

"""