# Interface/Settings/advanced_settings.py
import customtkinter as ctk
from Utils.save_settings import save_all_settings
from Utils.load_settings import load_data_path
from Interface.Components.gui_actions import open_directory
import Utils.fonts as fonts
from CTkToolTip import CTkToolTip
import logging
import os
import subprocess


def create_advanced_tab(globals, advanced_frame):
    """
    Creates the advanced tab and initializes widgets.

        Parameters:
                globals: Global variables
                about_frame: The main frame of the about tab
    """

    ctk.CTkLabel(advanced_frame,
                 font=fonts.title_font,
                 text="Advanced"
                 ).pack(pady=20, fill="x", anchor="center", padx=10)

    # Logging Frame
    logging_frame = ctk.CTkFrame(advanced_frame,
                                 bg_color="transparent",
                                 fg_color="transparent")
    logging_frame.pack(anchor="w", pady=5)

    ctk.CTkLabel(logging_frame,
                 text=None,
                 image=globals.preferences_icon).grid(
                     row=0, column=0, padx=6, sticky="w")

    logging_label = ctk.CTkLabel(logging_frame,
                                 text="Logging Level",
                                 font=fonts.heading_font)
    logging_label.grid(row=0, column=1, padx=5, sticky="w")

    CTkToolTip(
        logging_label,
        message="Sets Logging Level\nDebug: Very Verbose\nInfo: General Info & Failures\nWarning: Warnings/Errors/Failures\nError: Errors/System Failures\nCritical: Only System Failures",
        delay=0.6,
        follow=True,
        padx=10,
        pady=5)

    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    col = 2
    for level in levels:
        ctk.CTkRadioButton(
            logging_frame,
            text=level,
            value=level,
            variable=globals.logging_level_var
            ).grid(row=0, column=col, padx=5, sticky="w")
        col += 1

    def open_logs():
        """Opens the logs folder."""
        if globals.os_name.startswith("Windows"):
            logging.debug(f"Opening logs folder on Windows...")
            os.startfile(load_data_path("cache", "logs"))
        else:
            logging.debug(f"Opening logs folder on Linux...")
            subprocess.run(
                ['xdg-open', load_data_path("cache", "logs")], check=True)

    def open_config():
        """Opens the settings folder."""
        if globals.os_name.startswith("Windows"):
            logging.debug(f"Opening settings folder on Windows...")
            os.startfile(load_data_path("config"))
        else:
            logging.debug(f"Opening settings folder on Linux...")
            subprocess.run(
                ['xdg-open', load_data_path("config")], check=True)

    # Folders Frame
    folders_frame = ctk.CTkFrame(advanced_frame,
                              bg_color="transparent",
                              fg_color="transparent")
    folders_frame.pack(anchor="w", pady=5)

    ctk.CTkLabel(folders_frame,
                 text=None,
                 image=globals.note_icon).pack(side="left", padx=6, pady=0)

    ctk.CTkLabel(folders_frame,
                 text="Open Logs",
                 font=fonts.heading_font).pack(side="left", padx=(0, 12))

    logs_button = ctk.CTkButton(folders_frame,
                                text="Logs",
                                width=20,
                                command=lambda: open_logs())
    logs_button.pack(side="left", padx=(0, 12))

    ctk.CTkLabel(folders_frame,
                 text=None,
                 image=globals.config_icon).pack(side="left", padx=6, pady=0)

    ctk.CTkLabel(folders_frame,
                 text="Open Config",
                 font=fonts.heading_font).pack(side="left", padx=(0, 12))
    
    open_config_button = ctk.CTkButton(folders_frame,
                                text="Config",
                                width=20,
                                command=lambda: open_config())
    open_config_button.pack(side="left", padx=(0, 12))

    # Save Button Frame
    save_button_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
    save_button_frame.pack(pady=10)

    ctk.CTkButton(save_button_frame,
                  text="Save Settings",
                  command=lambda: save_all_settings(globals)).pack()
