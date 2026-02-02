# Interface/Windows/inbox_window.py
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from Interface.Components.gui_actions import open_workbook, open_directory, pdf_button
from Managers.file_management import count_files
from Managers.history_manager import load_history
from Managers.file_management import move_files
from Interface.Components.gui_actions import smart_spreadsheet_button, add_file
from Interface.Components.treeview import Treeview
import os, shutil, logging, threading
import Utils.fonts as fonts
from CTkToolTip import CTkToolTip
from customtkinter import CTkImage
from PIL import Image
from send2trash import send2trash
from Utils.load_settings import load_data_path
from Utils.save_settings import save_metadata

def create_inbox(globals, inbox_tab):
    """Initiates the Inbox tab."""

    globals.inbox_dir_var = tk.StringVar(value=globals.sources['inbox'])
    globals.inbox_count_var = tk.StringVar(value=f"Files in folder: {count_files(globals.sources['inbox'], '.pdf')}")

    ctk.CTkLabel(inbox_tab, 
             textvariable=globals.inbox_count_var).pack(pady=5)

    # Tree Frame
    globals.inbox_tree = Treeview(globals, inbox_tab, get_dir=lambda: globals.sources['inbox'])

    # Frames
    process_buttons_frame = ctk.CTkFrame(inbox_tab, fg_color="transparent")
    globals.process_buttons_frame = process_buttons_frame

    # Get Icons
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

    def get_selected_files():
        """Returns a list of files which have been selected in a treeview."""
        selected_items = globals.inbox_tree.selection()
        if not selected_items:
            return []  # Empty list if no selection
        directory = globals.sources['inbox']
        return [os.path.join(directory, fname) for fname in selected_items]

    def start_pdf_thread():
        directory = globals.sources['inbox']
        file_list = get_selected_files()

        if not file_list:
            messagebox.showinfo("No Selection", "Please select one or more files before running the search.")
            logging.warning(f"PDF Search aborted. No files selected.")
            return

        logging.info(f"PDF Search starting...")

        def pdf_with_refresh():
            logging.debug(f"pdf search running in thread.")
            pdf_button(globals, directory=directory, file_list=file_list)
            globals.root.after(0, globals.update_file_counts)

        threading.Thread(target=pdf_with_refresh,
                                     daemon=True,
                                     name="PDF Search").start()

    def move_selected_to(target_dir, globals):
        """Moves selected files to another chosen directory."""
        selected_files = get_selected_files()
        save_metadata(globals)
        if not selected_files:
            messagebox.showinfo("No Selection", "Please select files to move.")
            return
        if not os.path.exists(target_dir):
            messagebox.showerror("Error", f"Target directory does not exist: {target_dir}")
            return

        moved_count = 0
        errors = []

        for src_file in selected_files:
            if not os.path.exists(src_file):
                errors.append(f"File not found: {os.path.basename(src_file)}")
                continue
            dst_file = os.path.join(target_dir, os.path.basename(src_file))
            try:
                shutil.move(src_file, dst_file)
                moved_count += 1
                logging.info(f"Moved {os.path.basename(src_file)} to {target_dir}")
            except Exception as e:
                errors.append(f"Failed to move {os.path.basename(src_file)}: {e}")

        # Refresh Treeviews and file counts
        globals.update_file_counts()
        load_history(globals.history_tree)
        if errors:
            messagebox.showerror("Move Errors", "\n".join(errors))
        else:
            messagebox.showinfo("Success", f"Moved {moved_count} files successfully!")

    # Process buttons frame (configure grid to allow dynamic columns)
    process_buttons_frame.grid_columnconfigure((0,1,2,3,4,5,6,7,8,9), weight=0)  # Up to 10 columns should be plenty
    process_buttons_frame.pack(pady=10)

    # Fixed buttons on the left (columns 0 to 3)
    add_file_button = ctk.CTkButton(process_buttons_frame, 
                                    image=globals.add_icon,
                                    text=None, 
                                    font=fonts.button_font, 
                                    width=50, 
                                    height=50,
                                    command=lambda: add_file(globals))
    add_file_button.grid(row=0, column=0, padx=5)
    ctk.CTkLabel(process_buttons_frame, text="Add").grid(row=1, column=0)
    CTkToolTip(add_file_button, message="Add new files", delay=0.6, follow=True, padx=10, pady=5)

    autoname_button = ctk.CTkButton(process_buttons_frame, 
                                    image=globals.auto_icon,
                                    text=None, 
                                    font=fonts.button_font, 
                                    width=50, 
                                    height=50,
                                    command=start_pdf_thread)
    autoname_button.grid(row=0, column=1, padx=5)
    ctk.CTkLabel(process_buttons_frame, text="Auto-name").grid(row=1, column=1)
    CTkToolTip(autoname_button, message="Auto-name selected files", delay=0.6, follow=True, padx=10, pady=5)

    enter_spreadsheet_button = ctk.CTkButton(process_buttons_frame, 
                                             image=globals.enter_icon,
                                             text=None, 
                                             font=fonts.button_font, 
                                             width=50, 
                                             height=50,
                                             command=lambda: [smart_spreadsheet_button(globals, file_list=get_selected_files()),
                                                              globals.update_file_counts()])
    enter_spreadsheet_button.grid(row=0, column=2, padx=5)
    ctk.CTkLabel(process_buttons_frame, text="Enter").grid(row=1, column=2)
    CTkToolTip(enter_spreadsheet_button, message="Enter selected items to spreadsheet", delay=0.6, follow=True, padx=10, pady=5)

    archive_button = ctk.CTkButton(process_buttons_frame, 
                                   image=globals.archive_icon,
                                   text=None, 
                                   font=fonts.button_font, 
                                   width=50, 
                                   height=50,
                                   command=lambda: [move_files(globals, globals.history_tree,
                                                              globals.inbox_dir_var.get(), globals.folder_map,
                                                              globals.oneoffs_folder, get_selected_files()),
                                                   globals.update_file_counts()])
    archive_button.grid(row=0, column=3, padx=5)
    ctk.CTkLabel(process_buttons_frame, text="Archive").grid(row=1, column=3)
    CTkToolTip(archive_button, message="Archive selected files", delay=0.6, follow=True, padx=10, pady=5)

    workbook_open_button = ctk.CTkButton(process_buttons_frame, 
                                         image=globals.workbook_icon,
                                         text=None, 
                                         font=fonts.button_font, 
                                         width=50, 
                                         height=50,
                                         command=lambda: open_workbook(globals))
    workbook_label = ctk.CTkLabel(process_buttons_frame, text="Workbook")

    directory_open_button = ctk.CTkButton(process_buttons_frame, 
                                          image=globals.inbox_folder_icon,
                                          text=None, 
                                          font=fonts.button_font, 
                                          width=50, 
                                          height=50,
                                          command=lambda: open_directory(globals.inbox))
    directory_label = ctk.CTkLabel(process_buttons_frame, text="Inbox")

    delete_button = ctk.CTkButton(process_buttons_frame, 
                                  image=globals.delete_icon,
                                  text=None, 
                                  font=fonts.button_font, 
                                  width=50, 
                                  height=50,
                                  fg_color="#8B0000", hover_color="#A00000")  # Dark red for danger
    delete_label = ctk.CTkLabel(process_buttons_frame, text="Delete")

    # Tooltips
    CTkToolTip(workbook_open_button, message="Open the workbook", delay=0.6, follow=True, padx=10, pady=5)
    CTkToolTip(directory_open_button, message="Open the inbox directory", delay=0.6, follow=True, padx=10, pady=5)
    CTkToolTip(delete_button, message="Move selected files to Trash", delay=0.6, follow=True)

    def delete_selected_to_trash(globals):
        """Safely move selected files to the system trash."""
        save_metadata(globals)
        if send2trash is None:
            messagebox.showerror("Error", "send2trash library not available — cannot delete safely.")
            return

        selected_files = get_selected_files()
        if not selected_files:
            messagebox.showinfo("No Selection", "Please select one or more files to delete.")
            return

        # Confirmation dialog
        count = len(selected_files)
        if not messagebox.askyesno("Confirm Delete",
                                   f"Move {count} file{'s' if count != 1 else ''} to the Recycle Bin/Trash?\n\n"
                                   "You can recover them later from there.",
                                   icon="warning"):
            return

        trashed_count = 0
        errors = []

        for file_path in selected_files:
            try:
                send2trash(file_path)
                trashed_count += 1
                logging.info(f"Trashed: {os.path.basename(file_path)}")
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
                logging.error(f"Failed to trash {file_path}: {e}")

        # Refresh UI
        globals.update_file_counts()

        # Feedback
        if trashed_count == len(selected_files):
            messagebox.showinfo("Success", f"Moved {trashed_count} file{'s' if trashed_count != 1 else ''} to trash.")
        elif trashed_count > 0:
            messagebox.showwarning("Partial Success", f"Trashed {trashed_count} files.\n\nFailed:\n" + "\n".join(errors))
        else:
            messagebox.showerror("Failed", "Could not move any files to trash.\n\n" + "\n".join(errors))

    # Attach command
    delete_button.configure(command=lambda: delete_selected_to_trash(globals))

    def refresh_send_buttons():
        """Clear and rebuild only the dynamic buddy buttons, then reposition fixed right buttons."""
        # --- Destroy only dynamic buddy widgets ---
        for widget in process_buttons_frame.winfo_children():
            if hasattr(widget, "is_buddy_button") or hasattr(widget, "is_buddy_label"):
                widget.destroy()

        # Get valid buddies
        valid_buddies = [(name, folder) for name, folder in globals.buddies.items()
                         if name != "inbox" and folder and os.path.isdir(folder)]

        col = 4  # After Archive

        # Create buddy buttons
        for name, folder in valid_buddies:
            btn = ctk.CTkButton(
                process_buttons_frame,
                image=globals.send_icon,
                text=None, 
                font=fonts.button_font,
                width=50,
                height=50,
                command=lambda d=folder: move_selected_to(d, globals)
            )
            btn.grid(row=0, column=col, padx=5)
            btn.is_buddy_button = True
            CTkToolTip(btn, message=f"Send selected files to {name}", delay=0.6, follow=True)

            lbl = ctk.CTkLabel(process_buttons_frame, text=name.capitalize())
            lbl.grid(row=1, column=col)
            lbl.is_buddy_label = True

            col += 1

        # Reposition fixed buttons: Workbook → Inbox → Delete (always last)
        workbook_open_button.grid(row=0, column=col, padx=5)
        workbook_label.grid(row=1, column=col)
        col += 1

        directory_open_button.grid(row=0, column=col, padx=5)
        directory_label.grid(row=1, column=col)
        col += 1

        delete_button.grid(row=0, column=col, padx=5)
        delete_label.grid(row=1, column=col)

    # Initial build
    globals.refresh_send_buttons = refresh_send_buttons
    refresh_send_buttons()