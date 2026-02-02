# Interface/Settings/about_settings.py
import customtkinter as ctk
import Utils.fonts as fonts

def create_about_tab(globals, about_tab):
    """
    Creates the about tab and initializes widgets.

            Parameters:
                    globals: Global variables
                    about_frame: The main frame of the about tab
    """
    ctk.CTkLabel(about_tab, 
                 font=fonts.title_font,
                 text="About").pack(pady=20, fill="x", anchor="center", padx=10)

    ctk.CTkLabel(about_tab,
                 justify="left",
                 text="Invoice Buddy is your helper to automate the invoice entry process.\n\n" \
                    "The program does three things:\n\n" \
                    "1) Automatically detects invoice data from each file and writes it to the filename.\n" \
                    "2) Writes that data to a spreadsheet.\n" \
                    "3) Moves processed files to their proper folder for archival.\n\n" \
                    "Files are separated into three categories: Invoices, Credit Card Receipts, and Purchase Orders.\n\n" \
                    "Always look over generated content to ensure its accuracy before continuing.").pack(padx=5, pady=5)

    ctk.CTkLabel(about_tab, 
             text=f"Current Version: {globals.current_version}", 
             anchor="center").pack(fill="x", pady=20, padx=10)

    buttons_frame = ctk.CTkFrame(about_tab, fg_color="transparent")
    buttons_frame.pack(padx=10, pady=10)

    ctk.CTkButton(buttons_frame, text="View Changelog", command= lambda: show_changelog()).grid(row=0, column=1, padx=5)

    def show_changelog():
        """Brings up the changelog window."""
        globals.main_page.pack_forget()
        globals.settings_page.pack_forget()
        globals.changelog.pack(fill="both", expand=True, padx=10, pady=0)
        globals.title.configure(text="Changelog")
