# src/interface/settings/settings.py
import customtkinter as ctk
from src.interface.settings.general_settings import create_general_settings_tab
from src.interface.settings.about_settings import create_about_tab
from src.interface.settings.history_settings import create_history_tab
from src.interface.settings.paths_settings import create_paths_settings_tab
from src.interface.settings.advanced_settings import create_advanced_tab
from src.interface.settings.spreadsheet_settings import create_spreadsheet_settings_tab


def create_settings(globs, settings_frame):
    """
    Creates the settings tab and initializes widgets.

        Parameters:
                globs: Global variables
                settings_frame: The main frame =
                which holds the settings Tabview
    """

    # Notebook tabs for settings
    globs.notebook = ctk.CTkTabview(settings_frame)
    globs.notebook.pack(fill="both", expand=True, padx=20, pady=20)

    def create_settings_tabs():
        """Initiates the settings Tabview and passes global variables."""
        general_tab = globs.notebook.add("General")
        paths_tab = globs.notebook.add("Paths")
        spreadsheet_tab = globs.notebook.add("Spreadsheet")
        history_tab = globs.notebook.add("History")
        advanced_tab = globs.notebook.add("Advanced")
        about_tab = globs.notebook.add("About")
        create_general_settings_tab(globs, general_tab)
        create_paths_settings_tab(globs, paths_tab)
        create_spreadsheet_settings_tab(globs, spreadsheet_tab)
        create_history_tab(globs, history_tab)
        create_advanced_tab(globs, advanced_tab)
        create_about_tab(globs, about_tab)

    create_settings_tabs()
