# Interface/Settings/about_settings.py
import webbrowser
import customtkinter as ctk
import src.utils.fonts as fonts
from src.interface.setup.setup_wizard import create_wizard


def create_about_tab(globals, about_tab):
    """
    Creates the about tab and initializes widgets.

        Parameters:
                globals: Global variables
                about_frame: The main frame of the about tab
    """
    ctk.CTkLabel(about_tab,
                 font=fonts.title_font,
                 text="About"
                 ).pack(pady=20, fill="x", anchor="center", padx=10)

    ctk.CTkLabel(
        about_tab,
        justify="left",
        text="Invoice Buddy is your helper to automate the invoice entry process.\n\n"
        "The program does three things:\n\n"
        "1) Automatically detects invoice data from each file and writes it to the filename.\n"
        "2) Writes that data to a spreadsheet.\n"
        "3) Moves processed files to their proper folder for archival.\n\n"
        "Files are separated into three categories: Invoices, Credit Card Receipts, and Purchase Orders.\n\n"
        "Always look over generated content to ensure its accuracy before continuing."
        ).pack(padx=5, pady=5)

    ctk.CTkLabel(about_tab,
                 text=f"Current Version: {globals.current_version}",
                 anchor="center").pack(fill="x", pady=20, padx=10)

    buttons_frame = ctk.CTkFrame(about_tab, fg_color="transparent")
    buttons_frame.pack(padx=10, pady=10)

    ctk.CTkButton(
        buttons_frame,
        text="View Changelog",
        command=lambda: show_changelog()).grid(row=0, column=0, padx=5)

    ctk.CTkButton(buttons_frame,
                  text="Open Wizard",
                  command=lambda: create_wizard(globals)).grid(
                      row=0, column=1, padx=5)
    
    github_button = ctk.CTkButton(buttons_frame,
                                  text="View Github",
                                  command=lambda: webbrowser.open(
                                      url="https://github.com/pdschneider/InvoiceBuddy"))
    github_button.grid(row=0, column=2, padx=5)

    def show_changelog():
        """Brings up the changelog window."""
        pages = [globals.settings_page, globals.main_page, globals.onboarding_page]
        for page in pages:
            page.pack_forget()
        globals.changelog.pack(fill="both", expand=True, padx=10, pady=0)
        globals.title.configure(text="Changelog")
