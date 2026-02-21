# Interface/Settings/advanced_settings.py
import customtkinter as ctk
from Utils.save_settings import save_all_settings
from Utils.load_settings import load_data_path
from Interface.Components.gui_actions import open_directory
import Utils.fonts as fonts
from CTkToolTip import CTkToolTip

def create_advanced_tab(globals, advanced_frame):
    """
    Creates the advanced tab and initializes widgets.

            Parameters:
                    globals: Global variables
                    about_frame: The main frame of the about tab
    """

    ctk.CTkLabel(advanced_frame, 
                 font=fonts.title_font,
                 text="Advanced").pack(pady=20, fill="x", anchor="center", padx=10)

    # Advanced Settings
    logging_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
    logging_frame.pack(anchor="w", pady=10, padx=10)

    logging_label = ctk.CTkLabel(logging_frame, 
             text="Logging Level:")
    logging_label.grid(row=1, column=0, padx=5, sticky="w")
    CTkToolTip(logging_label, message="Sets Logging Level\nDebug: Very Verbose\nInfo: General Info & Failures\nWarning: Warnings/Errors/Failures\nError: Errors/System Failures\nCritical: Only System Failures", delay=0.6, follow=True, padx=10, pady=5)

    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    col = 1
    for level in levels:
        ctk.CTkRadioButton(logging_frame, 
                       text=level, 
                       value=level, 
                       variable=globals.logging_level_var).grid(row=1, column=col, padx=5, sticky="w")
        col += 1

    logs_button_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
    logs_button_frame.pack()

    logs_button = ctk.CTkButton(logs_button_frame, text="Show Logs", command=lambda: open_directory(load_data_path("cache", "logs")))
    logs_button.pack(pady=10)
    CTkToolTip(logs_button, message="Open the logs directory", delay=0.6, follow=True, padx=10, pady=5)

    # Save Button Frame
    save_button_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
    save_button_frame.pack(pady=10)

    ctk.CTkButton(save_button_frame, 
               text="Save Settings", 
               command=lambda: save_all_settings(globals)).pack()
