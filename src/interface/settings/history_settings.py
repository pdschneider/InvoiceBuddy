# src/interface/settings/history_settings.py
from tkinter import ttk
import customtkinter as ctk
from CTkToolTip import CTkToolTip
from src.managers.import_export import export_history, import_history
from src.managers.file_management import open_workbook, open_selected_folders
from src.managers.history_manager import load_history
import src.utils.fonts as fonts


def create_history_tab(globs, history_tab):
    """Initiates the History tab."""

    all_columns = ("File Name",
                   "Source Folder",
                   "Destination Folder",
                   "Type",
                   "Archived",
                   "Entered")

    globs.history_tree = ttk.Treeview(
        history_tab,
        columns=all_columns,
        show="headings",
        selectmode="extended")

    for col in all_columns:
        globs.history_tree.heading(col, text=col)

    globs.history_tree.column("File Name", width=250, anchor="w")
    globs.history_tree.column("Source Folder", width=100, anchor="w")
    globs.history_tree.column("Destination Folder", width=100, anchor="w")
    globs.history_tree.column("Type", width=100, anchor="w")
    globs.history_tree.column("Archived", width=50, anchor="center")
    globs.history_tree.column("Entered", width=50, anchor="center")
    globs.history_tree.pack(fill="both", expand=True, pady=5)

    def on_click(event):
        """
        Enables dynamic selection of treeview elements.

        - Click row to select
        - Click + drag to select multiple rows
        - Ctrl + A (or Ctrl + a) to select all rows
        - Click in empty space to de-select all
        """
        row = globs.history_tree.identify_row(event.y)
        if not row:
            globs.history_tree.selection_clear()
            return "break"

    globs.history_tree.bind(
        "<Button-1>", on_click)
    globs.history_tree.bind(
        "<B1-Motion>", lambda e: globs.history_tree.selection_add(globs.history_tree.identify_row(e.y)) if globs.history_tree.identify_row(e.y) else None)
    globs.history_tree.bind(
        "<Control-A>", lambda e: globs.history_tree.selection_set(globs.history_tree.get_children()))
    globs.history_tree.bind(
        "<Control-a>", lambda e: globs.history_tree.selection_set(globs.history_tree.get_children()))

    button_frame = ctk.CTkFrame(history_tab, fg_color="transparent")
    button_frame.pack(pady=10)

    directory_open_button = ctk.CTkButton(
        button_frame,
        image=globs.inbox_folder_icon,
        text=None,
        font=fonts.button_font,
        width=50,
        height=50,
        command=lambda: open_selected_folders(globs))
    directory_label = ctk.CTkLabel(button_frame, text="Inbox")
    directory_open_button.grid(row=0, column=0, padx=5)
    directory_label.grid(row=1, column=0)
    CTkToolTip(directory_open_button,
               message="Open the directories of\nselected files",
               delay=0.6,
               follow=True,
               padx=5)

    workbook_open_button = ctk.CTkButton(
        button_frame,
        image=globs.workbook_icon,
        text=None,
        font=fonts.button_font,
        width=50,
        height=50,
        command=lambda: open_workbook(globs))
    workbook_label = ctk.CTkLabel(button_frame, text="Workbook")
    workbook_open_button.grid(row=0, column=1, padx=5)
    workbook_label.grid(row=1, column=1)
    CTkToolTip(workbook_open_button,
               message="Open the workbook",
               delay=0.6,
               follow=True,
               padx=5)

    import_button = ctk.CTkButton(
        button_frame,
        image=globs.import_icon,
        text=None,
        font=fonts.button_font,
        width=50,
        height=50,
        command=lambda: import_history(globs, globs.history_tree))
    import_button.grid(row=0, column=2, padx=5)
    ctk.CTkLabel(button_frame, text="Import").grid(row=1, column=2)
    CTkToolTip(import_button,
               message="Import history file",
               delay=0.6,
               follow=True,
               padx=5)

    export_button = ctk.CTkButton(
        button_frame,
        image=globs.export_icon,
        text=None,
        font=fonts.button_font,
        width=50,
        height=50,
        command=lambda: export_history(globs, globs.history_tree))
    export_button.grid(row=0, column=3, padx=5)
    ctk.CTkLabel(button_frame, text="Export").grid(row=1, column=3)
    CTkToolTip(export_button,
               message="Export history data",
               delay=0.6,
               follow=True,
               padx=5)

    load_history(globs.history_tree)
