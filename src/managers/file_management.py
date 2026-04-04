# Managers/file_management.py
import logging
import os
import shutil
import subprocess
from tkinter import filedialog
from src.managers.history_manager import load_history, add_update_history
from src.utils.save_settings import save_metadata
from src.utils.toast import show_toast

move_log = []


def count_files(directory, extension=None):
    """
    Count files in the given directory, optionally filtering by extension.

        directory:      The folder path to count files
        extension:      Filter by extension (ex: '.pdf')
    """
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        if extension:
            files = [f for f in files if f.lower().endswith(extension)]
        return len(files)
    except Exception as e:
        logging.error(f"Error counting files in {directory}: {e}")
        return 0


def browse_file(var, _type=None):
    """
    Open a file dialog to select a single file and set the variable.

        var:        Variable to change
                    ex: globals.workbook_var
    """
    if _type == "workbook":
        file_types = [("All files", "*.*"), ("XLSX files", "*.xlsx"), ("XLSM files", "*.xlsm"), ("XLST files", "*.xlst"), ("XLTM files", "*.xltm")]
    elif _type == "history":
        file_types = [("All files", "*.*"), ("CSV files", "*.csv")]
    else:
        file_types = [("All files", "*.*"), ("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
    file_path = filedialog.askopenfilename(
        filetypes=file_types)
    if file_path:
        var.set(file_path)
        logging.info(f"Selected file: {file_path}")


def browse_directory(var):
    """
    Open a directory dialog to select a directory and set the variable.

        var:        Variable to change
                    ex: globals.inbox_dir_var
    """
    dir_path = filedialog.askdirectory()
    if dir_path:
        var.set(dir_path)
        logging.info(f"Selected directory: {dir_path}")


def open_workbook(globals):
    """
    Opens the Excel workbook at the initiated file path.
    
        globals:        Global variables
    """
    if os.path.isfile(globals.workbook):
        try:
            if globals.os_name.startswith("Windows"):
                os.startfile(globals.workbook)
            else:
                subprocess.run(['xdg-open', globals.workbook], check=True)
        except PermissionError as e:
            show_toast(globals, f"Permission Error. Is the workbook already open?", _type="error")
            logging.error(f"Permission Error accessing {globals.workbook}: {e}")
            return
        except Exception as e:
            show_toast(globals, "Failed to open workbook", _type="error")
            logging.error(f"Error opening workbook: {e}")
            return
    else:
        show_toast(globals, f"Invalid workbook path", _type="error")
        logging.error(f"Cannot open workbook. Invalid file path {globals.workbook}")
        return


def add_files(globals):
    """
    Moves files to the inbox.
    
        globals:        Global variables

        files_tuple:    Tuple of selected files
                        ex: ('/home/phillip/ZZZ-Unnamed- Ice Melt V24533.pdf',
                        '/home/phillip/ZZZ-Unnamed- LED Lamp Refund.pdf')
        files_list:     List of selected files
                        ex: ['/home/phillip/ZZZ-Unnamed- Ice Melt V24533.pdf',
                        '/home/phillip/ZZZ-Unnamed- LED Lamp Refund.pdf']
    """
    # Uses path from var if saved path isn't valid
    if not os.path.isdir(globals.inbox) and os.path.isdir(globals.inbox_dir_var.get().strip()):
        globals.inbox = globals.inbox_dir_var.get().strip()
        logging.debug(f"Inbox not a valid path. Using path from paths settings.")

    if os.path.isdir(globals.inbox):
        # Open file selection box
        files_tuple = filedialog.askopenfilenames(
            title="Select Files", filetypes=[("PDF files", "*.pdf")], multiple=True)
        try:
            if files_tuple:
                files_list = []
                # Convert tuple into list of file paths
                for file in files_tuple:
                    # Ignore non-.pdf files
                    if file.lower().endswith(".pdf"):
                        files_list.append(file)
                    else:
                        logging.warning(f"Only PDF files can be added.")

                # Save metadata to retain identities before inbox rebuilds
                save_metadata(globals)

                # Copy files to the inbox
                logging.debug(f"Attempting to add files: {files_list}...")
                for file in files_list:
                        shutil.copy2(file, globals.inbox)
                logging.info(f"Added files!")

            else: # Return if nothing is selected
                return

        except Exception as e:
            for file in files_tuple:
                logging.error(f"Could not add {file} to inbox due to: {e}")
            show_toast(globals, f"Unable to add files.", _type="error")
    else:
        logging.error(f"Cannot add files to an invalid inbox path.")
        show_toast(globals, f"Unable to add file - Select a valid inbox path first", _type="error")


def open_directory(directory):
    """
    Opens the directory of the current tab.
    
        directory:      Directory path to open
                        ex: globals.inbox
    """
    try:
        if not directory or not os.path.isdir(directory):
            show_toast(globals, "Invalid directory", _type="error")
            logging.error(f"Cannot open directory: Invalid path {directory}")
            return
        try:
            os.startfile(directory)
        except:
            subprocess.run(['xdg-open', directory], check=True)
        logging.info(f"Opened directory: {directory}")
    except Exception as e:
        show_toast(globals, f"Failed to open directory", _type="error")
        logging.error(f"Error opening directory {directory}: {e}")


def open_selected_folders(globals):
    """
    Opens the folders that the files at selected treeview rows are located in.
    Designed to be used in the history tab.
    
        globals:        Global variables
    """
    selected_items = globals.history_tree.selection()
    if not selected_items:
        show_toast(globals, "No items selected to open folders.")
        return
    folders = set()
    for item_id in selected_items:
        values = globals.history_tree.item(item_id)['values']
        dst_folder = values[2]
        src_folder= values[1]
        if dst_folder != "N/A" and os.path.isdir(dst_folder):
            folders.add(dst_folder)
        if not os.path.isdir(dst_folder):
            folders.add(src_folder)
    if not folders:
        show_toast(globals, "No valid folders found for selected items.")
        return
    for folder in folders:
        open_directory(folder)
    logging.info(f"Opened {len(folders)} unique destination folders.")


def archive_files(globals, file_list=None):
    """
    Archives files to their end destination.

        globals:        Global variables
        file_list:      List of files from inbox view
    """
    errors = []
    moved_files = 0

    # Exit early if archive path is not valid
    if not globals.archive or not os.path.isdir(globals.archive):
        show_toast(globals, "Archive path not set or invalid!", _type="error")
        logging.error(f"Cannot archive: invalid archive root '{globals.archive}'")
        return

    # Return if no file list was given
    if not file_list:
        logging.warning(f"Nothing selected.")
        return

    for src_file in file_list:
        # Find the first word of the filename for folder matching
        filename = os.path.basename(src_file)
        first_word = os.path.splitext(filename)[0].split()[0].lower()

        # Get the identity from metadata via global dictionary variable
        file_type = globals.file_identity.get(src_file, "Invoice")
        logging.debug(f"File identity for {src_file}: {file_type}")

        # Find matching subfolder
        subfolder_name = next(
            (folder for words, folder in globals.folder_map.items() if first_word in words),
            globals.oneoffs_folder)
        logging.debug(f"Matched subfolder: {subfolder_name}")

        # Generate path for archive destination folder
        dst_folder = os.path.join(globals.archive, subfolder_name)
        logging.debug(f"Destination folder: {dst_folder}")

        # Create the destination folder if it doesn't already exist
        if not os.path.isdir(dst_folder):
            os.mkdir(dst_folder)

        # Generate the full path for the file in its new location
        dst_file = os.path.join(dst_folder, filename)

        # Skip copy if file already exists in destination folder
        if os.path.exists(dst_file):
            logging.warning(f"File {filename} already in destination folder. Skipping...")
            continue

        # Move files to their archived location
        try:
            shutil.move(src_file, dst_file)
            moved_files += 1
            add_update_history(
                filename=filename,
                src_folder=globals.inbox,
                dst_folder=dst_folder,
                file_type=file_type,
                moved=globals.user)
        except Exception as e:
            errors.append(f"Failed to move {filename} due to: {e}")
            logging.debug(f"Failed to move {filename} due to: {e}")
            continue

        # Reload Treeview
        load_history(globals.history_tree)

    if errors:
        show_toast(globals, f"Error moving some files", _type="error")
        logging.error("Move Errors", "\n".join(errors))
    elif moved_files == 0:
        show_toast(globals, f"No files moved in {globals.inbox}.", _type="error")
        logging.warning("No Files", f"No files moved in {globals.inbox}.")
    else:
        show_toast(globals, f"Archived {moved_files} files successfully!")
