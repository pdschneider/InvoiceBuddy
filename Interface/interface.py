# Interface/interface.py
import tkinter as tk
import customtkinter as ctk
from config import apply_theme
from Utils.load_settings import load_data_path
from .Windows.inbox_window import create_inbox
from Interface.Components.top_bar import create_top_bar
from Interface.Settings.settings import create_settings
from Interface.Windows.changelog import create_changelog
from Managers.file_management import count_files
from Utils.observers import setup_observer
from Interface.Windows.onboarding import create_onboarding_page
import logging, os
from customtkinter import CTkImage
from PIL import Image

def create_interface(globals):
    """Creates the core GUI interface."""
    # Set up main window
    globals.root = ctk.CTk()
    globals.root.title("Invoice Buddy")

    def draw_window():
        screen_width = globals.root.winfo_screenwidth()
        screen_height = globals.root.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 850) // 2
        globals.root.geometry(f"900x850+{x}+{y}")

    if globals.saved_width and globals.saved_height and globals.saved_x and globals.saved_y:
        try:
            globals.root.geometry(f"{globals.saved_width}x{globals.saved_height}+{globals.saved_x}+{globals.saved_y}")
        except:
            draw_window()
    else:
        draw_window()
    globals.root.minsize(width=500, height=500)

    # Log GUI path
    logging.debug(f"CustomTkinter package path: {ctk.__file__}")

    # Configure styles
    apply_theme(globals.active_theme)
    globals.root.configure(fg_color=globals.theme_dict["CTkFrame"]["fg_color"])

    # Get Icons
    globals.icon = load_data_path("config", "assets/icon.png")
    icon_image = tk.PhotoImage(file=str(globals.icon))
    globals.root.iconphoto(False, icon_image)

    def load_icons():
        """Loads icons."""
        globals.add_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/add-2.png")),
        dark_image=Image.open(load_data_path("config", "assets/add-2.png")),
        size=(40, 40))

        globals.auto_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/auto.png")),
        dark_image=Image.open(load_data_path("config", "assets/auto.png")),
        size=(40, 40))
        
        globals.enter_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/pen-2.png")),
        dark_image=Image.open(load_data_path("config", "assets/pen-2.png")),
        size=(40, 40))

        globals.archive_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/archive.png")),
        dark_image=Image.open(load_data_path("config", "assets/archive.png")),
        size=(40, 40))

        globals.workbook_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/workbook-1.png")),
        dark_image=Image.open(load_data_path("config", "assets/workbook-1.png")),
        size=(40, 40))

        globals.inbox_folder_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/inbox-1.png")),
        dark_image=Image.open(load_data_path("config", "assets/inbox-1.png")),
        size=(40, 40))

        globals.delete_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/delete-4.png")),
        dark_image=Image.open(load_data_path("config", "assets/delete-4.png")),
        size=(40, 40))

        globals.send_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/send.png")),
        dark_image=Image.open(load_data_path("config", "assets/send.png")),
        size=(40, 40))

        globals.settings_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/settings.png")),
        dark_image=Image.open(load_data_path("config", "assets/settings.png")),
        size=(40, 40))

        globals.import_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/upload.png")),
        dark_image=Image.open(load_data_path("config", "assets/upload.png")),
        size=(40, 40))

        globals.export_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/download.png")),
        dark_image=Image.open(load_data_path("config", "assets/download.png")),
        size=(40, 40))

        globals.inbox_icon = CTkImage(
        light_image=Image.open(load_data_path("config", "assets/mail.png")),
        dark_image=Image.open(load_data_path("config", "assets/mail.png")),
        size=(40, 40))

        globals.invoice_icon = CTkImage(
        light_image=Image.open(load_data_path("config", globals.invoice_icon_path)),
        dark_image=Image.open(load_data_path("config", globals.invoice_icon_path)),
        size=(30, 30))

        globals.card_icon = CTkImage(
        light_image=Image.open(load_data_path("config", globals.card_icon_path)),
        dark_image=Image.open(load_data_path("config", globals.card_icon_path)),
        size=(30, 30))

        globals.po_icon = CTkImage(
        light_image=Image.open(load_data_path("config", globals.po_icon_path)),
        dark_image=Image.open(load_data_path("config", globals.po_icon_path)),
        size=(30, 30))

    load_icons()

    # Add Navigation
    create_top_bar(globals)

    # Main Frame
    globals.main_frame = ctk.CTkFrame(globals.root)
    globals.main_frame.pack(side="left", fill="both", expand=True)

    # Inbox (Main) Page
    globals.main_page = ctk.CTkFrame(globals.main_frame)
    globals.main_page.pack(fill="both", expand=True, padx=10, pady=0)
    if not os.path.isfile(globals.workbook) or not os.path.isdir(globals.inbox) or not os.path.isdir(globals.archive_path):
        globals.main_page.pack_forget()
        globals.title.configure(text="Welcome!")
        globals.inbox_button.configure(state="disabled")
        globals.settings_button.configure(state="disabled")

    # Onboarding Page
    globals.onboarding_page = ctk.CTkFrame(globals.main_frame)
    globals.onboarding_page.pack(fill="both", expand=True, padx=10, pady=0)
    if os.path.isfile(globals.workbook) and os.path.isdir(globals.inbox) and os.path.isdir(globals.archive_path):
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
        globals.file_var = tk.StringVar(value=globals.workbook)
        globals.logging_level_var = tk.StringVar(value=globals.logging_level)
        globals.theme_var = tk.StringVar(value=globals.active_theme)
        globals.history_var = tk.StringVar(value=globals.history_path)
        globals.inbox_dir_var = tk.StringVar(value=globals.inbox)
        globals.workbook_var = tk.StringVar(value=globals.workbook)
        globals.sheet_invoices_var = tk.StringVar(value=globals.sheet_invoices)
        globals.sheet_CreditCards_var = tk.StringVar(value=globals.sheet_CreditCards)
        globals.sheet_PurchaseOrders_var = tk.StringVar(value=globals.sheet_PurchaseOrders)
        globals.table_InvoiceTable_var = tk.StringVar(value=globals.table_InvoiceTable)
        globals.table_CreditCards_var = tk.StringVar(value=globals.table_CreditCards)
        globals.table_PurchaseOrders_var = tk.StringVar(value=globals.table_PurchaseOrders)
        globals.invoice_starting_row_var = tk.IntVar(value=globals.invoice_starting_row)
        globals.card_starting_row_var = tk.IntVar(value=globals.card_starting_row)
        globals.po_starting_row_var = tk.IntVar(value=globals.po_starting_row)
        globals.archive_path_var = tk.StringVar(value=globals.archive_path)
        globals.invoice_starting_column_var = tk.IntVar(value=globals.invoice_starting_column)
        globals.card_starting_column_var = tk.IntVar(value=globals.card_starting_column)
        globals.po_starting_column_var = tk.IntVar(value=globals.po_starting_column)

        create_inbox(globals, globals.main_page)
        create_settings(globals, globals.settings_page)
        create_changelog(globals, globals.changelog)
        create_onboarding_page(globals, globals.onboarding_page)

        def update_treeview(tree, extension=None):
            """Refreshes a custom treeview to show the correct current files in the directory."""
            tree.refresh(extension=extension)

        def update_file_counts():
            """Monitors folder changes and keeps file count labels current."""
            globals.inbox_count_var.set(f"Files in folder: {count_files(globals.sources['inbox'], '.pdf')}")
            if hasattr(globals, 'inbox_tree') and globals.inbox_tree:
                update_treeview(globals.inbox_tree, extension='.pdf')
            globals.root.update_idletasks()

        globals.update_file_counts = update_file_counts
        globals.observers = {}
        if globals.sources["inbox"]:
            globals.observers['inbox'] = setup_observer(globals, globals.inbox, key='inbox')
        globals.update_file_counts()

    create_tabs()

