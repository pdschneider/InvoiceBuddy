# Interface/Windows/history_window.py
from tkinter import ttk
import tkinter as tk
import customtkinter as ctk
from customtkinter import CTkImage
from CTkToolTip import CTkToolTip
from PIL import Image
from Interface.Components.gui_actions import open_selected_folders, open_workbook
from Managers.import_export import export_history, import_history
from Managers.history_manager import load_history
from Utils.load_settings import load_data_path
import Utils.fonts as fonts

def create_history_tab(globals, history_tab):
    """Initiates the History tab."""

    # Get Icons
    globals.workbook_icon = CTkImage(
    light_image=Image.open(load_data_path("config", "assets/workbook-1.png")),
    dark_image=Image.open(load_data_path("config", "assets/workbook-1.png")),
    size=(40, 40))

    globals.inbox_folder_icon = CTkImage(
    light_image=Image.open(load_data_path("config", "assets/inbox-1.png")),
    dark_image=Image.open(load_data_path("config", "assets/inbox-1.png")),
    size=(40, 40))

    globals.import_icon = CTkImage(
    light_image=Image.open(load_data_path("config", "assets/upload.png")),
    dark_image=Image.open(load_data_path("config", "assets/upload.png")),
    size=(40, 40))

    globals.export_icon = CTkImage(
    light_image=Image.open(load_data_path("config", "assets/download.png")),
    dark_image=Image.open(load_data_path("config", "assets/download.png")),
    size=(40, 40))

    all_columns = ("File Name", "Source Folder", "Destination Folder", "Type", "Moved", "Entered")

    globals.history_tree = ttk.Treeview(history_tab, columns=all_columns, show="headings", selectmode="extended")

    for col in all_columns:
        globals.history_tree.heading(col, text=col)

    globals.history_tree.column("File Name", width=250, anchor="w")
    globals.history_tree.column("Source Folder", width=100, anchor="w")
    globals.history_tree.column("Destination Folder", width=100, anchor="w")
    globals.history_tree.column("Type", width=100, anchor="w")
    globals.history_tree.column("Moved", width=50, anchor="center")
    globals.history_tree.column("Entered", width=50, anchor="center")
    globals.history_tree.pack(fill="both", expand=True, pady=5)

    def on_click(event):
        """
        Enables dynamic selection of treeview elements.

        - Click row to select
        - Click + drag to select multiple rows
        - Ctrl + A (or Ctrl + a) to select all rows
        - Click in empty space to de-select all
        """
        row = globals.history_tree.identify_row(event.y)
        if not row:
            globals.history_tree.selection_clear()
            return "break"

    globals.history_tree.bind("<Button-1>", on_click)
    globals.history_tree.bind("<B1-Motion>", lambda e: globals.history_tree.selection_add(globals.history_tree.identify_row(e.y)) if globals.history_tree.identify_row(e.y) else None)
    globals.history_tree.bind("<Control-A>", lambda e: globals.history_tree.selection_set(globals.history_tree.get_children()))
    globals.history_tree.bind("<Control-a>", lambda e: globals.history_tree.selection_set(globals.history_tree.get_children()))

    button_frame = ctk.CTkFrame(history_tab, fg_color="transparent")
    button_frame.pack(pady=10)

    directory_open_button = ctk.CTkButton(button_frame, 
                                            image=globals.inbox_folder_icon,
                                            text=None, 
                                            font=fonts.button_font, 
                                            width=50, 
                                            height=50,
                                            command=lambda: open_selected_folders(globals.history_tree))
    directory_label = ctk.CTkLabel(button_frame, text="Inbox")
    directory_open_button.grid(row=0, column=0, padx=5)
    directory_label.grid(row=1, column=0)
    CTkToolTip(directory_open_button, message="Open the directories of\nselected files", delay=0.6, follow=True, padx=5)

    workbook_open_button = ctk.CTkButton(button_frame, 
                                         image=globals.workbook_icon,
                                         text=None, 
                                         font=fonts.button_font, 
                                         width=50, 
                                         height=50,
                                         command=lambda: open_workbook(globals))
    workbook_label = ctk.CTkLabel(button_frame, text="Workbook")
    workbook_open_button.grid(row=0, column=1, padx=5)
    workbook_label.grid(row=1, column=1)
    CTkToolTip(workbook_open_button, message="Open the workbook", delay=0.6, follow=True, padx=5)

    import_button = ctk.CTkButton(button_frame, 
                                    image=globals.import_icon,
                                    text=None, 
                                    font=fonts.button_font, 
                                    width=50, 
                                    height=50,
                                    command=lambda: import_history(globals.history_tree))
    import_button.grid(row=0, column=2, padx=5)
    ctk.CTkLabel(button_frame, text="Import").grid(row=1, column=2)
    CTkToolTip(import_button, message="Import history file", delay=0.6, follow=True, padx=5)

    export_button = ctk.CTkButton(button_frame, 
                                    image=globals.export_icon,
                                    text=None, 
                                    font=fonts.button_font, 
                                    width=50, 
                                    height=50,
                                    command=lambda: export_history(globals.history_tree))
    export_button.grid(row=0, column=3, padx=5)
    ctk.CTkLabel(button_frame, text="Export").grid(row=1, column=3)
    CTkToolTip(export_button, message="Export history data", delay=0.6, follow=True, padx=5)

    load_history(globals.history_tree)
