# Interface/Components/top_bar.py
import customtkinter as ctk
import tkinter as tk
from CTkToolTip import CTkToolTip
from Utils.load_settings import load_data_path

def create_top_bar(globals):
    """
    Creates the top bar for navigation.

            Parameters:
                    globals: Global variables

            Returns:
                    top_bar: The top_bar frame and its child widgets
    """
    def toggle_inbox():
        globals.main_page.pack(fill="both", expand=True, padx=10, pady=0)
        globals.changelog.pack_forget()
        globals.settings_page.pack_forget()
        globals.main_page.tkraise()
        globals.title.configure(text="Inbox")

    def toggle_settings():
        """Shows and hides the settings window when the button is clicked."""
        globals.settings_page.pack(fill="both", expand=True, padx=10, pady=0)
        globals.changelog.pack_forget()
        globals.main_page.pack_forget()
        globals.settings_page.tkraise()
        globals.title.configure(text="Settings")

    # Main top bar
    top_bar = ctk.CTkFrame(globals.root, height=55, corner_radius=0)
    globals.top_bar = top_bar
    top_bar.pack(side="top", fill="x")
    top_bar.pack_propagate(False)

    # Inbox button (left)
    globals.inbox_button = ctk.CTkButton(
        top_bar,
        image=globals.inbox_icon,
        text=None,
        width=45,
        height=45)
    globals.inbox_button.pack(side="left", padx=10, pady=5)
    globals.inbox_button.configure(command=toggle_inbox)
    CTkToolTip(globals.inbox_button, message="Inbox", delay=0.6, follow=True, padx=10, pady=5)

    # Title / App name (center)
    title = ctk.CTkLabel(
        top_bar,
        text="",
        font=ctk.CTkFont(size=20, weight="bold"))
    globals.title = title
    globals.title.pack(side="left", expand=True)

    # Settings gear (right)
    globals.settings_button = ctk.CTkButton(
        top_bar,
        image=globals.settings_icon,
        text=None,
        width=45,
        height=45)
    globals.settings_button.pack(side="right", padx=10, pady=0)
    globals.settings_button.configure(command=toggle_settings)
    CTkToolTip(globals.settings_button, message="Settings", delay=0.6, follow=True, padx=10, pady=5)

    return top_bar