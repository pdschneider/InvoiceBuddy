# Interface/interface.py
import tkinter as tk
import customtkinter as ctk
from config import apply_theme
from src.utils.load_settings import load_data_path
from .inbox_window import create_inbox
from src.interface.components.top_bar import create_top_bar
from src.interface.settings.settings import create_settings
from src.interface.changelog import create_changelog
from src.managers.file_management import count_files
from src.utils.observers import setup_observer
from src.interface.setup.onboarding import create_onboarding_page
import logging
import os


def create_interface(globals):
    """Creates the core GUI interface."""
    # Set up main window
    logging.debug(f"Building GUI...")
    globals.root.title("Invoice Buddy")
    globals.root.withdraw()

    def draw_window():
        """Draws the window with default values."""
        screen_width = globals.root.winfo_screenwidth()
        screen_height = globals.root.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 850) // 2
        globals.root.geometry(f"900x850+{x}+{y}")

    if globals.saved_width and globals.saved_height and globals.saved_x and globals.saved_y:
        try:
            globals.root.geometry(
                f"{globals.saved_width}x{globals.saved_height}+{globals.saved_x}+{globals.saved_y}")
        except:
            draw_window()
    else:
        draw_window()

    globals.root.minsize(width=750, height=675)

    # Configure styles
    apply_theme(globals.active_theme)
    globals.root.configure(fg_color=globals.theme_dict["CTkFrame"]["fg_color"])

    # Get Icons
    try:
        globals.icon = load_data_path("config", "assets/icon.png")
        icon_image = tk.PhotoImage(file=str(globals.icon))
        globals.root.iconphoto(False, icon_image)
    except Exception as e:
        logging.error(f"Failed to load icon due to: {e}")

    # Add Navigation
    create_top_bar(globals)

    # Main Frame
    globals.main_frame = ctk.CTkFrame(globals.root)
    globals.main_frame.pack(side="left", fill="both", expand=True)

    # Inbox (Main) Page
    globals.main_page = ctk.CTkFrame(globals.main_frame)
    globals.main_page.pack(fill="both", expand=True, padx=10, pady=0)
    if not os.path.isfile(globals.workbook) or not os.path.isdir(globals.inbox) or not os.path.isdir(globals.archive):
        globals.main_page.pack_forget()
        globals.title.configure(text="Welcome!")

    # Onboarding Page
    globals.onboarding_page = ctk.CTkFrame(globals.main_frame)
    globals.onboarding_page.pack(fill="both", expand=True, padx=10, pady=0)
    if os.path.isfile(globals.workbook) and os.path.isdir(globals.inbox) and os.path.isdir(globals.archive):
        globals.onboarding_page.pack_forget()
        globals.title.configure(text="Inbox")

    # Changelog
    globals.changelog = ctk.CTkFrame(globals.main_frame)
    globals.changelog.pack_forget()

    # Settings Page
    globals.settings_page = ctk.CTkFrame(globals.main_frame)
    globals.settings_page.pack_forget()

    def create_tabs():
        """Initiates critical UI functionality."""
        create_inbox(globals, globals.main_page)
        create_settings(globals, globals.settings_page)
        create_changelog(globals, globals.changelog)
        create_onboarding_page(globals, globals.onboarding_page)

        # Display window after widgets have built
        globals.root.after(1500, lambda: [  # 1.5 seconds
            globals.root.update_idletasks(),
            globals.root.deiconify(),
            globals.root.focus_set()])

        def update_treeview(tree, extension=None):
            """
            Refreshes the custom treeview to show the correct
            current files in the directory.
            """
            tree.refresh(extension=extension)

        def update_file_counts():
            """Monitors folder changes and keeps file count labels current."""
            globals.inbox_count_var.set(
                f"Files in folder: {count_files(globals.sources['inbox'], '.pdf')}")
            if hasattr(globals, 'inbox_tree') and globals.inbox_tree:
                update_treeview(globals.inbox_tree, extension='.pdf')
            globals.root.update_idletasks()

        globals.update_file_counts = update_file_counts
        globals.observers = {}
        if globals.inbox:
            globals.observers['inbox'] = setup_observer(
                globals,
                globals.inbox,
                key='inbox')
            globals.update_file_counts()

    # Creates tabs then shows the window
    create_tabs()
