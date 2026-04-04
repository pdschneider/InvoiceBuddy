# Interface/Windows/inbox_window.py
import customtkinter as ctk
from PySide6.QtWidgets import QMessageBox
from src.interface.components.gui_actions import (pdf_button)
from src.managers.file_management import count_files
from src.managers.history_manager import load_history
from src.managers.file_management import archive_files, add_files, open_workbook, open_directory
from src.interface.components.gui_actions import smart_spreadsheet_button
from src.managers.printers import print_selected_files
from src.interface.components.treeview import Treeview
import src.utils.fonts as fonts
from CTkToolTip import CTkToolTip
from send2trash import send2trash
from src.utils.save_settings import save_metadata
from src.utils.toast import show_toast
import os
import shutil
import logging
import threading


def create_inbox(globals, inbox_tab):
    """
    Initiates the Inbox tab.
    
        globals:        Global variables
        inbox_tab:      Frame to hold inbox
                        ex: globals.main_page
    """

    globals.inbox_dir_var = ctk.StringVar(value=globals.inbox)
    globals.inbox_count_var = ctk.StringVar(value=f"Files in folder: {count_files(globals.inbox, '.pdf')}")

    ctk.CTkLabel(inbox_tab,
                 textvariable=globals.inbox_count_var).pack(pady=5)

    # Tree Frame
    globals.inbox_tree = Treeview(globals, inbox_tab, get_dir=lambda: globals.inbox)

    # Frames
    process_buttons_frame = ctk.CTkFrame(inbox_tab, fg_color="transparent")
    globals.process_buttons_frame = process_buttons_frame

    def get_selected_files():
        """Returns a list of files which have been selected in a treeview."""
        selected_items = globals.inbox_tree.selection()
        if not selected_items:
            return []  # Empty list if no selection
        directory = globals.inbox
        return [os.path.join(directory, fname) for fname in selected_items]

    def start_pdf_thread():
        """Starts the pdf search process in a thread."""
        directory = globals.inbox
        file_list = get_selected_files()

        # Exit early if no files are selected
        if not file_list:
            show_toast(globals, "Please select one or more files before running the search.")
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

        # Return early if nothing is selected
        if not selected_files:
            show_toast(globals, "Please select files to move.")
            return

        # Return early if target directory does not exist
        if not os.path.isdir(target_dir):
            logging.error(f"Target directory does not exist: {target_dir}")
            show_toast(globals, "Target directory does not exist", _type="error")
            return

        moved_count = 0
        errors = []

        for src_file in selected_files:
            # Skip if file is not found in the inbox
            if not os.path.isfile(src_file):
                errors.append(f"File not found: {os.path.basename(src_file)}")
                continue

            # Generate destination path
            dst_file = os.path.join(target_dir, os.path.basename(src_file))

            # Skip moving file if one already exists with that name
            if os.path.isfile(dst_file):
                errors.append(f"Filename already exists in target directory: {dst_file}")
                continue

            # Move files
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
            logging.error(
                "Move Errors - some files may have invalid paths or already exist in target directory")
            logging.error(f"Errors: {errors}")
            show_toast(
                globals,
                "Some files may have invalid paths or already exist in target directory",
                _type="error")
        else:
            show_toast(globals, f"Moved {moved_count} files successfully!")

    # Process buttons frame (configure grid to allow dynamic columns)
    process_buttons_frame.grid_columnconfigure(
        (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=0)
    process_buttons_frame.pack(pady=10)

    # Fixed buttons on the left (columns 0 to 3)
    add_file_button = ctk.CTkButton(process_buttons_frame,
                                    image=globals.add_icon,
                                    text=None,
                                    font=fonts.button_font,
                                    width=50,
                                    height=50,
                                    command=lambda: add_files(globals))
    add_file_button.grid(row=0, column=0, padx=5)
    ctk.CTkLabel(process_buttons_frame, text="Add").grid(row=1, column=0)
    CTkToolTip(add_file_button,
               message="Add new files",
               delay=0.6,
               follow=True,
               padx=10,
               pady=5)

    autoname_button = ctk.CTkButton(process_buttons_frame,
                                    image=globals.auto_icon,
                                    text=None,
                                    font=fonts.button_font,
                                    width=50,
                                    height=50,
                                    command=start_pdf_thread)
    autoname_button.grid(row=0, column=1, padx=5)
    ctk.CTkLabel(process_buttons_frame, text="Auto-name").grid(row=1, column=1)
    CTkToolTip(autoname_button,
               message="Auto-name selected files",
               delay=0.6,
               follow=True,
               padx=10,
               pady=5)

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
                                   command=lambda: [archive_files(globals, get_selected_files())])

    archive_button.grid(row=0, column=3, padx=5)
    ctk.CTkLabel(process_buttons_frame, text="Archive").grid(row=1, column=3)
    CTkToolTip(archive_button, message="Archive selected files", delay=0.6, follow=True, padx=10, pady=5)

    print_button = ctk.CTkButton(process_buttons_frame,
                                   image=globals.print_icon,
                                   text=None,
                                   font=fonts.button_font,
                                   width=50,
                                   height=50,
                                   command=lambda: [print_selected_files(globals, get_selected_files())])

    print_button.grid(row=0, column=4, padx=5)
    ctk.CTkLabel(process_buttons_frame, text="Print").grid(row=1, column=4)
    CTkToolTip(print_button, message="Print selected files", delay=0.6, follow=True, padx=10, pady=5)

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
                                  fg_color="#8B0000", hover_color="#A00000")
    delete_label = ctk.CTkLabel(process_buttons_frame, text="Delete")

    # Tooltips
    CTkToolTip(workbook_open_button,
               message="Open the workbook",
               delay=0.6,
               follow=True,
               padx=10,
               pady=5)
    CTkToolTip(directory_open_button,
               message="Open the inbox directory",
               delay=0.6,
               follow=True,
               padx=10,
               pady=5)
    CTkToolTip(delete_button,
               message="Move selected files to Trash",
               delay=0.6,
               follow=True)

    def delete_selected_to_trash(globals):
        """Safely move selected files to the system trash."""
        save_metadata(globals)
        selected_files = get_selected_files()

        # Show message if no files are selected
        if not selected_files:
            show_toast(globals, "Please select one or more files to delete.")
            return

        # Important variables
        count = len(selected_files)
        trashed_count = 0
        errors = []

        # If not on network drive, use safer deletion method
        if not globals.network_drive:
            reply = QMessageBox.question(
                None,
                "Confirm Delete",
                f"Move {count} file{'s' if count != 1 else ''} to the Recycle Bin?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.No:
                return

            # Send files safely to trash
            for file_path in selected_files:
                try:
                    send2trash(file_path)
                    trashed_count += 1
                    logging.info(f"Trashed: {os.path.basename(file_path)}")
                except Exception as e:
                    errors.append(f"{os.path.basename(file_path)}: {str(e)}")
                    logging.error(f"Failed to trash {file_path}: {e}")

        # If on network drive, fall back to permanent deletion method
        else:
            reply = QMessageBox.question(
                None,
                "Confirm Delete",
                f"Permanently delete {count} file{'s' if count != 1 else ''}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.No:
                return

            # Delete files permanently
            for file_path in selected_files:
                try:
                    os.remove(file_path)
                    trashed_count += 1
                    logging.info(f"Deleted: {os.path.basename(file_path)}")
                except Exception as e:
                    errors.append(f"{os.path.basename(file_path)}: {str(e)}")
                    logging.error(f"Failed to delete {file_path}: {e}")

        # Refresh UI
        globals.update_file_counts()

        # Feedback
        if trashed_count == len(selected_files):
            show_toast(globals,
                       f"Moved {trashed_count} file{'s' if trashed_count != 1 else ''} to trash.")
        elif trashed_count > 0:
            logging.warning(f"Trashed {trashed_count} files.\n\nFailed: \n" + "\n".join(errors))
            show_toast(globals,
                       f"Trashed {trashed_count} files - Some Failed to Trash\n",
                       _type="error")
        else:
            logging.error(
                f"Could not move any files to trash.\n\n" + "\n".join(errors))
            show_toast(globals,
                       f"Could not move any files to trash.",
                       _type="error")

    # Attach command
    delete_button.configure(command=lambda: delete_selected_to_trash(globals))

    def refresh_send_buttons():
        """
        Clear and rebuild only the dynamic buddy buttons,
        then reposition fixed right buttons.
        """
        # --- Destroy only dynamic buddy widgets ---
        for widget in process_buttons_frame.winfo_children():
            if hasattr(widget, "is_buddy_button") or hasattr(widget, "is_buddy_label"):
                widget.destroy()

        # Get valid buddies
        valid_buddies = [(name, folder) for name, folder in globals.buddies.items()
                         if name != "inbox" and folder and os.path.isdir(folder)]

        col = 5  # After Print

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
            CTkToolTip(btn,
                       message=f"Send selected files to {name}",
                       delay=0.6,
                       follow=True)

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
