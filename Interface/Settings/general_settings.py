# Interface/Settings/general_settings.py
import tkinter as tk
import customtkinter as ctk
from Utils.save_settings import save_all_settings
import Utils.fonts as fonts

def create_general_settings_tab(globals, settings_tab):
    """
    Create the Settings tab for configuring paths and advanced settings.

    Args:
        globals (globals): The global configuration object containing UI variables and settings.
    """
    ctk.CTkLabel(settings_tab, 
                 font=fonts.title_font,
                 text="General").pack(pady=20, fill="x", anchor="center", padx=10)

    # Theme Frame
    theme_frame = ctk.CTkFrame(settings_tab, fg_color="transparent")
    theme_frame.pack(fill="x", pady=10, padx=10)

    # Theme List
    themes_dict = [{"label": "Cosmic Sky", "theme": "cosmic_sky"}, 
                   {"label": "Pastel Green", "theme": "pastel_green"}, 
                   {"label": "Trojan Red", "theme": "trojan_red"},
                   {"label": "Dark Cloud", "theme": "dark_cloud"}, 
                   {"label": "Soft Light", "theme": "soft_light"}]
    theme_labels = [entry["label"] for entry in themes_dict]
    label_to_theme = {entry["label"]: entry["theme"] for entry in themes_dict}

    label_var = tk.StringVar()

    def update_theme_var(*args):
        selected_label = label_var.get()
        theme_name = label_to_theme.get(selected_label, "Cosmic Sky")
        globals.theme_var.set(theme_name)

    label_var.trace("w", update_theme_var)

    initial_theme = globals.theme_var.get()
    initial_label = next((label for label, theme in label_to_theme.items() if theme == initial_theme), "Cosmic Sky")
    label_var.set(initial_label)

    ctk.CTkLabel(theme_frame, 
    text="Theme:").pack(side="left", padx=(0, 12))

    ctk.CTkComboBox(theme_frame,
        variable=label_var,
        values=theme_labels,
        state="readonly",
        width=150).pack(side="left")

    # Save Button Frame
    save_button_frame = ctk.CTkFrame(settings_tab, fg_color="transparent")
    save_button_frame.pack(pady=10)

    ctk.CTkButton(save_button_frame, 
               text="Save Settings", 
               command=lambda: save_all_settings(globals)).pack()
