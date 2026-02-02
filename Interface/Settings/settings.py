# Interface/Settings/settings.py
import customtkinter as ctk
from Interface.Settings.general_settings import create_general_settings_tab
from Interface.Settings.about_settings import create_about_tab
from Interface.Settings.history_settings import create_history_tab
from Interface.Settings.paths_settings import create_paths_settings_tab
from Interface.Settings.advanced_settings import create_advanced_tab
from Interface.Settings.spreadsheet_settings import create_spreadsheet_settings_tab

def create_settings(globals, settings_frame):
    """
    Creates the settings tab and initializes widgets.

            Parameters:
                    globals: Global variables
                    settings_frame: The main frame which holds the settings Tabview
    """

    # Notebook tabs for settings
    globals.notebook = ctk.CTkTabview(settings_frame)
    globals.notebook.pack(fill="both", expand=True, padx=20, pady=20)

    def create_settings_tabs():
        """Initiates the settings Tabview and passes global variables."""
        general_tab = globals.notebook.add("General")
        paths_tab = globals.notebook.add("Paths")
        spreadsheet_tab = globals.notebook.add("Spreadsheet")
        history_tab = globals.notebook.add("History")
        advanced_tab = globals.notebook.add("Advanced")
        about_tab = globals.notebook.add("About")
        create_general_settings_tab(globals, general_tab)
        create_paths_settings_tab(globals, paths_tab)
        create_spreadsheet_settings_tab(globals, spreadsheet_tab)
        create_history_tab(globals, history_tab)
        create_advanced_tab(globals, advanced_tab)
        create_about_tab(globals, about_tab)

    create_settings_tabs()
