# src/interface/interface.py
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


def create_interface(globs):
    """Creates the core GUI interface."""
    # Set up main window
    logging.debug(f"Building GUI...")
    globs.root.title("Invoice Buddy")
    globs.root.withdraw()

    def draw_window():
        """Draws the window with default values."""
        screen_width = globs.root.winfo_screenwidth()
        screen_height = globs.root.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 850) // 2
        globs.root.geometry(f"900x850+{x}+{y}")

    if globs.saved_width and globs.saved_height and globs.saved_x and globs.saved_y and globs.dynamic_window_size:
        try:
            globs.root.geometry(
                f"{globs.saved_width}x{globs.saved_height}+{globs.saved_x}+{globs.saved_y}")
        except:
            draw_window()
    else:
        draw_window()

    globs.root.minsize(width=750, height=675)

    # Configure styles
    apply_theme(globs.active_theme)
    globs.root.configure(fg_color=globs.theme_dict["CTkFrame"]["fg_color"])

    # Get Icons
    try:
        globs.icon = load_data_path("config", "assets/icon.png")
        icon_image = tk.PhotoImage(file=str(globs.icon))
        globs.root.iconphoto(False, icon_image)
    except Exception as e:
        logging.error(f"Failed to load icon due to: {e}")

    # Add Navigation
    create_top_bar(globs)

    # Main Frame
    globs.main_frame = ctk.CTkFrame(globs.root)
    globs.main_frame.pack(side="left", fill="both", expand=True)

    # Inbox (Main) Page
    globs.main_page = ctk.CTkFrame(globs.main_frame)
    globs.main_page.pack(fill="both", expand=True, padx=10, pady=0)
    if not os.path.isfile(globs.workbook) or not os.path.isdir(globs.inbox) or not os.path.isdir(globs.archive):
        globs.main_page.pack_forget()
        globs.title.configure(text="Welcome!")

    # Onboarding Page
    globs.onboarding_page = ctk.CTkFrame(globs.main_frame)
    globs.onboarding_page.pack(fill="both", expand=True, padx=10, pady=0)
    if os.path.isfile(globs.workbook) and os.path.isdir(globs.inbox) and os.path.isdir(globs.archive):
        globs.onboarding_page.pack_forget()
        globs.title.configure(text="Inbox")

    # Changelog
    globs.changelog = ctk.CTkFrame(globs.main_frame)
    globs.changelog.pack_forget()

    # Settings Page
    globs.settings_page = ctk.CTkFrame(globs.main_frame)
    globs.settings_page.pack_forget()

    def create_tabs():
        """Initiates critical UI functionality."""
        create_inbox(globs, globs.main_page)
        create_settings(globs, globs.settings_page)
        create_changelog(globs, globs.changelog)
        create_onboarding_page(globs, globs.onboarding_page)

        # Display window after widgets have built
        globs.root.after(1500, lambda: [  # 1.5 seconds
            globs.root.update_idletasks(),
            globs.root.deiconify(),
            globs.root.focus_set()])

        def update_treeview(tree, extension=None):
            """
            Refreshes the custom treeview to show the correct
            current files in the directory.
            """
            tree.refresh(extension=extension)

        def update_file_counts():
            """Monitors folder changes and keeps file count labels current."""
            if globs.inbox:
                globs.inbox_count_var.set(
                    f"Files in folder: {count_files(globs.inbox, '.pdf')}")
                if hasattr(globs, 'inbox_tree') and globs.inbox_tree:
                    update_treeview(globs.inbox_tree, extension='.pdf')
                globs.root.update_idletasks()

        globs.update_file_counts = update_file_counts
        globs.observers = {}
        if globs.inbox:
            globs.observers['inbox'] = setup_observer(
                globs,
                globs.inbox,
                key='inbox')
            globs.update_file_counts()

    # Creates tabs then shows the window
    create_tabs()
