# Interface/Settings/general_settings.py
from tkinter import messagebox
import customtkinter as ctk
from src.utils.save_settings import save_all_settings
from src.managers.printers import query_printers
from PySide6.QtWidgets import QMessageBox
import src.utils.fonts as fonts
from CTkToolTip import CTkToolTip
import subprocess
import logging
import sys


def create_general_settings_tab(globals, settings_tab):
    """
    Create the Settings tab for configuring paths and advanced settings.

    Args:
        globals (globals): The global configuration
        object containing UI variables and settings.
    """

    ctk.CTkLabel(settings_tab,
                 font=fonts.title_font,
                 text="General"
                 ).pack(pady=20, fill="x", anchor="center", padx=10)

    # Theme Frame
    theme_frame = ctk.CTkFrame(settings_tab,
                               bg_color="transparent",
                               fg_color="transparent")
    theme_frame.pack(fill="x", pady=10, padx=10)

    # Theme List
    themes_dict = [{"label": "Cosmic Sky", "theme": "cosmic_sky"},
                   {"label": "Pastel Green", "theme": "pastel_green"},
                   {"label": "Trojan Red", "theme": "trojan_red"},
                   {"label": "Dark Cloud", "theme": "dark_cloud"},
                   {"label": "Soft Light", "theme": "soft_light"}]
    theme_labels = [entry["label"] for entry in themes_dict]
    label_to_theme = {entry["label"]: entry["theme"] for entry in themes_dict}

    theme_label_var = ctk.StringVar()

    def update_theme_var(*args):
        selected_label = theme_label_var.get()
        theme_name = label_to_theme.get(selected_label, "Cosmic Sky")
        globals.theme_var.set(theme_name)

    theme_label_var.trace("w", update_theme_var)

    initial_theme = globals.theme_var.get()
    initial_label = next(
        (label for label,
         theme in label_to_theme.items() if theme == initial_theme), "Cosmic Sky")
    theme_label_var.set(initial_label)

    ctk.CTkLabel(theme_frame,
                 text=None,
                 image=globals.theme_icon).pack(side="left", padx=6, pady=0)

    ctk.CTkLabel(theme_frame,
                 text="Theme",
                 font=fonts.heading_font).pack(side="left", padx=(0, 12))

    ctk.CTkComboBox(theme_frame,
                    variable=theme_label_var,
                    values=theme_labels,
                    state="readonly",
                    width=150).pack(side="left")
    
    ctk.CTkLabel(theme_frame,
                 text="*Requires restart",
                 font=fonts.body_font).pack(side="left", padx=6, pady=0)
    
    # Printer Selection Frame
    printer_frame = ctk.CTkFrame(settings_tab,
                                bg_color="transparent",
                                fg_color="transparent")
    printer_frame.pack(fill="x", pady=10, padx=10)

    ctk.CTkLabel(printer_frame,
                text=None,
                image=globals.printer_icon).pack(side="left", padx=6, pady=0)

    ctk.CTkLabel(printer_frame,
                text="Printer",
                font=fonts.heading_font).pack(side="left", padx=(0, 12))

    ctk.CTkComboBox(printer_frame,
                    variable=globals.default_printer_var,
                    values=query_printers(),
                    state="readonly",
                    width=150).pack(side="left")
    
    # Version Check
    version_frame = ctk.CTkFrame(settings_tab,
                                 bg_color="transparent",
                                 fg_color="transparent")
    version_frame.pack(fill="x", pady=10, padx=10)

    ctk.CTkLabel(version_frame,
                 text=None,
                 image=globals.notification_icon).pack(side="left", padx=6, pady=0)

    version_check_label = ctk.CTkLabel(version_frame,
                                    text="Check for Updates",
                                    font=fonts.heading_font)
    version_check_label.pack(side="left", padx=(0, 12))
    CTkToolTip(version_check_label,
               message="When on, pings github for the\nthe latest version of Pearl\non startup",
               delay=0.8,
               follow=True,
               padx=10,
               pady=5)

    ctk.CTkCheckBox(version_frame,
                    variable=globals.github_check_var,
                    onvalue=True,
                    text=None,
                    width=0,
                    offvalue=False).pack(side="left")
    
    ctk.CTkLabel(version_frame,
                 text="*Requires restart",
                 font=fonts.body_font).pack(side="left", padx=6, pady=0)

    # Save Button Frame
    save_button_frame = ctk.CTkFrame(settings_tab, fg_color="transparent")
    save_button_frame.pack(pady=10)

    ctk.CTkButton(save_button_frame,
                  text="Save Settings",
                  command=lambda: save_button(globals)).pack()

    def save_button(globals):
        """Saves and prompts for restart if required."""
        prompt_restart = False
        if globals.github_check != globals.github_check_var.get():
            prompt_restart = True
        elif globals.active_theme != globals.theme_var.get():
            prompt_restart = True
        save_all_settings(globals)

        if prompt_restart:
            if globals.qt_mode:
                reply = QMessageBox.question(
                    None,
                    "Restart Pearl?",
                    f"Would you like to restart Pearl to apply all changes?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes)
                if reply == QMessageBox.StandardButton.Yes:
                    subprocess.Popen(globals.app_path)
                    sys.exit(0)
            else:
                    reply = messagebox.askyesno(
                        parent=globals.root,
                        title="Restart Pearl",
                        message="Would you like restart Pearl to apply all changes?")
                    if reply:
                        try:
                            subprocess.Popen(globals.app_path)
                        except Exception as e:
                            logging.error(f"Unable to open program due to: {e}")
                        sys.exit(0)
