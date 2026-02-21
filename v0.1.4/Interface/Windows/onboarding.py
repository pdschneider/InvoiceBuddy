# Interface/setup_window.py
import customtkinter as ctk
import Utils.fonts as fonts
import shutil, logging, os
from Interface.Components.gui_actions import browse_file, browse_directory
from Utils.save_settings import save_all_settings
from Utils.load_settings import load_data_path
from Utils.observers import setup_observer

def create_onboarding_page(globals, onboarding_page):
    """
    Creates the tab to display setup instructions for new users.

            Parameters:
                    globals: Global variables
                    onboarding_page: The main frame of the setup window
    """

    hello_frame = ctk.CTkFrame(onboarding_page, fg_color="transparent")
    hello_frame.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(hello_frame, 
                text="Welcome to Invoice Buddy!", 
                font=fonts.title_font,
                anchor="center").pack(fill="x", pady=20, padx=10)

    ctk.CTkLabel(hello_frame, 
                 justify="center", 
                 text=f"Invoice Buddy is an application that makes entering spreadsheet data easier.\n\n" \
                        f"To use Invoice Buddy, you must first choose an inbox and a workbook path.\n\n" \
                        f"Your inbox is where you will add files to process.\n\n" \
                        f"The workbook is the spreadsheet file you will be entering data.\n\n" \
                        f"You will also need to choose an archive path for storing files after processing.\n\n" \
                        f"Only choose the 'top-level' archive path. The application will create subfolders for you.\n\n" \
                        f"Have fun!").pack(fill="both", expand=True, padx=10, pady=10)

    # Paths Frame
    paths_frame = ctk.CTkFrame(onboarding_page, fg_color="transparent")
    paths_frame.pack(fill="both", expand=True, padx=10, pady=10)
    paths_frame.grid_columnconfigure(1, weight=1)

    # Workbook
    ctk.CTkLabel(paths_frame, 
                 font=fonts.heading_font,
                 text="Workbook:").grid(row=0, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(paths_frame, 
             textvariable=globals.workbook_var).grid(row=0, column=1, padx=(0, 10), sticky="ew")

    ctk.CTkButton(paths_frame, 
               text="Browse", 
               width=140,
               command=lambda: browse_file(globals.workbook_var)).grid(row=0, column=2, pady=5)
    
    # Inbox
    ctk.CTkLabel(paths_frame,
                 font=fonts.heading_font, 
                 text="Inbox:").grid(row=1, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(paths_frame, 
             textvariable=globals.inbox_dir_var).grid(row=1, column=1, padx=(0, 10), sticky="ew")

    ctk.CTkButton(paths_frame, 
               text="Browse", 
               width=140,
               command=lambda: [browse_directory(globals.inbox_dir_var), globals.update_file_counts()]).grid(row=1, column=2, pady=5)

    # Archive
    ctk.CTkLabel(paths_frame,
                 font=fonts.heading_font, 
                 text="Archive:").grid(row=2, column=0, padx=(20, 10), sticky="w")

    ctk.CTkEntry(paths_frame, 
             textvariable=globals.archive_path_var).grid(row=2, column=1, padx=(0, 10), sticky="ew")

    ctk.CTkButton(paths_frame, 
               text="Browse", 
               width=140,
               command=lambda: [browse_directory(globals.archive_path_var)]).grid(row=2, column=2, pady=5)
 
    # Buttons Frame
    buttons_frame = ctk.CTkFrame(onboarding_page, fg_color="transparent")
    buttons_frame.pack(fill="x", padx=10, pady=10)

    ctk.CTkButton(buttons_frame, 
                text="Continue", 
                command= lambda: continue_to_inbox()).pack(padx=5, pady=5)

    def continue_to_inbox():
        """Forgets setup and settings pages to return the user to a clean chat page"""
        save_all_settings(globals)
        globals.title.configure(text="Inbox")
        globals.inbox_button.configure(state="normal")
        globals.settings_button.configure(state="normal")
        setup_observer(globals, globals.inbox, key='inbox')

        try:
            src_dir = os.path.normpath(load_data_path("local", "Welcome to Invoice Buddy.pdf"))
            shutil.copy2(src_dir, globals.inbox)
        except Exception as e:
            logging.error(f"Cannot load welcome file due to: {e}")

        globals.settings_page.pack_forget()
        globals.onboarding_page.pack_forget()
        globals.main_page.pack(fill="both", expand=True, padx=10, pady=0)
