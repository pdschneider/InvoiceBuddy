# src/managers/file_management.py
import logging
import os
import shutil
import subprocess
from tkinter import filedialog
from send2trash import send2trash
from src.managers.history_manager import load_history, add_update_history
from src.utils.save_settings import save_metadata
from src.utils.load_settings import load_data_path
from src.utils.toast import show_toast
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMessageBox

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


def browse_file(globs, var, _type=None):
    """
    Open a file dialog to select a single file and set the variable.

        var:        Variable to change
                    ex: globs.workbook_var
    """
    if _type == "workbook":
        file_types = [("All files", "*.*"), ("XLSX files", "*.xlsx"), ("XLSM files", "*.xlsm"), ("XLST files", "*.xlst"), ("XLTM files", "*.xltm")]
    elif _type == "history":
        file_types = [("All files", "*.*"), ("CSV files", "*.csv")]
    else:
        file_types = [("All files", "*.*"), ("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
    if globs.legacy_mode:
        file_path = filedialog.askopenfilename(
            filetypes=file_types)
        if file_path:
            var.set(file_path)
            logging.info(f"Selected file: {file_path}")
    else:
        file_path, _ = QFileDialog.getOpenFileName(None, "Select File", "", "Excel Files (*.xlsx *.xlsm *.xlst *.xltm)")
        if file_path:
            var.setText(file_path)
            logging.info(f"Selected file: {file_path}")


def browse_directory(globs, var):
    """
    Open a directory dialog to select a directory and set the variable.

        var:        Variable to change
                    ex: globs.inbox_dir_var
    """
    if globs.legacy_mode:
        dir_path = filedialog.askdirectory()
    else:
        dir_path = QFileDialog.getExistingDirectory(None, "Select Folder", "")

    if dir_path:

        # Handle Tkinter variable (legacy mode)
        if hasattr(var, 'set'):
            var.set(dir_path)
        # Handle QLineEdit widget (Qt mode)
        elif hasattr(var, 'setText'):
            var.setText(dir_path)

        logging.info(f"Selected directory: {dir_path}")
        return dir_path
    else:
        logging.warning(f"No path found - returning empty string.")
        return ""


def open_workbook(globs, workbook_path=None):
    """
    Opens an Excel workbook at the specified file path.
    Falls back to globs.workbook if no path is provided.

        globs:            Global variables
        workbook_path:      Path to the workbook file (optional)
    """
    if not workbook_path:
        workbook_path = globs.workbook

    if os.path.isfile(workbook_path):
        try:
            if globs.os_name.startswith("Windows"):
                os.startfile(workbook_path)
            else:
                subprocess.run(['xdg-open', workbook_path], check=True)
        except PermissionError as e:
            show_toast(globs, f"Permission Error. Is the workbook already open?", _type="error")
            logging.error(f"Permission Error accessing {workbook_path}: {e}")
            return
        except Exception as e:
            show_toast(globs, "Failed to open workbook", _type="error")
            logging.error(f"Error opening workbook: {e}")
            return
    else:
        show_toast(globs, f"Invalid workbook path", _type="error")
        logging.error(f"Cannot open workbook. Invalid file path {workbook_path}")
        return


def add_files(globs):
    """
    Moves files to the inbox.
    
        globs:        Global variables

        files_tuple:    Tuple of selected files
                        ex: ('/home/phillip/ZZZ-Unnamed- Ice Melt V24533.pdf',
                        '/home/phillip/ZZZ-Unnamed- LED Lamp Refund.pdf')
        files_list:     List of selected files
                        ex: ['/home/phillip/ZZZ-Unnamed- Ice Melt V24533.pdf',
                        '/home/phillip/ZZZ-Unnamed- LED Lamp Refund.pdf']
    """

    # Uses path from var if saved path isn't valid
    if globs.legacy_mode:
        if not os.path.isdir(globs.inbox) and os.path.isdir(globs.inbox_dir_var.get().strip()):
            globs.inbox = globs.inbox_dir_var.get().strip()
            logging.debug(f"Inbox not a valid path. Using path from paths settings.")
    else:
        if not os.path.isdir(globs.inbox):
            logging.error(f"Unable to reach inbox folder.")
            return

    if os.path.isdir(globs.inbox):
        # Open file selection box
        if globs.legacy_mode:
            files_tuple = filedialog.askopenfilenames(
                title="Select Files", filetypes=[("PDF files", "*.pdf")], multiple=True)
        else:
            files_tuple, filter = QFileDialog.getOpenFileNames(
                None,
                "Add Files",
                "",
                "PDF Files (*.pdf)",
                options=QFileDialog.Option.DontUseNativeDialog)
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
                save_metadata(globs)

                # Copy files to the inbox
                logging.debug(f"Attempting to add files: {files_list}...")
                for file in files_list:
                        shutil.copy2(file, globs.inbox)
                logging.info(f"Added files!")

            else: # Return if nothing is selected
                return

        except Exception as e:
            for file in files_tuple:
                logging.error(f"Could not add {file} to inbox due to: {e}")
            show_toast(globs, f"Unable to add files.", _type="error")
    else:
        logging.error(f"Cannot add files to an invalid inbox path.")
        show_toast(globs, f"Unable to add file - Select a valid inbox path first", _type="error")


def open_directory(globs, directory):
    """
    Opens the directory of the current tab.
    
        directory:      Directory path to open
                        ex: globs.inbox
    """
    try:
        if not directory or not os.path.isdir(directory):
            show_toast(globs, "Invalid directory", _type="error")
            logging.error(f"Cannot open directory: Invalid path {directory}")
            return
        try:
            os.startfile(directory)
        except:
            subprocess.run(['xdg-open', directory], check=True)
        logging.info(f"Opened directory: {directory}")
    except Exception as e:
        show_toast(globs, f"Failed to open directory", _type="error")
        logging.error(f"Error opening directory {directory}: {e}")


def open_selected_folders(globs):
    """
    Opens the folders that the files at selected treeview rows are located in.
    Designed to be used in the history tab.
    
        globs:        Global variables
    """
    selected_items = globs.history_tree.selection()
    if not selected_items:
        show_toast(globs, "No items selected to open folders.")
        return
    folders = set()
    for item_id in selected_items:
        values = globs.history_tree.item(item_id)['values']
        dst_folder = values[2]
        src_folder= values[1]
        if dst_folder != "N/A" and os.path.isdir(dst_folder):
            folders.add(dst_folder)
        if not os.path.isdir(dst_folder):
            folders.add(src_folder)
    if not folders:
        show_toast(globs, "No valid folders found for selected items.")
        return
    for folder in folders:
        open_directory(globs, folder)
    logging.info(f"Opened {len(folders)} unique destination folders.")


def archive_files(globs, file_list=None):
    """
    Archives files to their end destination.

        globs:        Global variables
        file_list:      List of files from inbox view
    """
    errors = []
    moved_files = 0

    # Exit early if archive path is not valid
    if not globs.archive or not os.path.isdir(globs.archive):
        show_toast(globs, "Archive path not set or invalid!", _type="error")
        logging.error(f"Cannot archive: invalid archive root '{globs.archive}'")
        return

    # Return if no file list was given
    if not file_list:
        logging.warning(f"Nothing selected.")
        return

    # Create list of full paths
    if not globs.legacy_mode:
        new_file_list = []
        if not globs.legacy_mode:
            for file in file_list:
                new_file_list.append(os.path.normpath(os.path.join(globs.inbox, file)))
        file_list = new_file_list

    logging.debug(f"Attempting to archive files: {file_list}")

    for src_file in file_list:
        # Find the first word of the filename for folder matching
        filename = os.path.basename(src_file)
        first_word = os.path.splitext(filename)[0].split()[0].lower()

        # Get the identity from metadata via global dictionary variable
        file_type = globs.file_identity.get(src_file, "Invoice")
        logging.debug(f"File identity for {src_file}: {file_type}")

        # Find matching subfolder
        subfolder_name = next(
            (folder for words, folder in globs.folder_map.items() if first_word in words),
            globs.oneoffs_folder)
        logging.debug(f"Matched subfolder: {subfolder_name}")

        # Generate path for archive destination folder
        dst_folder = os.path.join(globs.archive, subfolder_name)
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
                src_folder=globs.inbox,
                dst_folder=dst_folder,
                file_type=file_type,
                moved=globs.user)
        except Exception as e:
            errors.append(f"Failed to move {filename} due to: {e}")
            logging.debug(f"Failed to move {filename} due to: {e}")
            continue

        # Reload Treeview
        load_history(globs.history_tree)

    if errors:
        show_toast(globs, f"Error moving some files", _type="error")
        logging.error(f"Move Errors: \n{errors}")
    elif moved_files == 0:
        show_toast(globs, f"No files moved in {globs.inbox}.", _type="error")
        logging.warning(f"No files moved in {globs.inbox}.")
    else:
        show_toast(globs, f"Archived {moved_files} files successfully!")


def send_to_trash(globs, file_list=None):
    """Safely move selected files to the system trash."""

    # Show message if no files are selected
    if not file_list:
        show_toast(globs, "Please select one or more files to delete.")
        return

    # Create list of full paths
    new_file_list = []
    if not globs.legacy_mode:
        for file in file_list:
            new_file_list.append(os.path.normpath(os.path.join(globs.inbox, file)))
    file_list = new_file_list

    logging.debug(f"Attempting to print files: {file_list}")

    # Important variables
    count = len(file_list)
    trashed_count = 0
    errors = []

    # If not on network drive, use safer deletion method
    if not globs.network_drive:
        reply = QMessageBox.question(
            globs.window,
            "Confirm Delete",
            f"Move {count} file{'s' if count != 1 else ''} to the Recycle Bin?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return False

        # Send files safely to trash
        for file_path in file_list:
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
            globs.window,
            "Confirm Delete",
            f"Permanently delete {count} file{'s' if count != 1 else ''}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return False

        # Delete files permanently
        for file_path in file_list:
            try:
                os.remove(file_path)
                trashed_count += 1
                logging.info(f"Deleted: {os.path.basename(file_path)}")
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
                logging.error(f"Failed to delete {file_path}: {e}")

    # Refresh UI
    if globs.legacy_mode:
        globs.update_file_counts()

    # Feedback
    if trashed_count == len(file_list):
        show_toast(globs,
                    f"Moved {trashed_count} file{'s' if trashed_count != 1 else ''} to trash.")
    elif trashed_count > 0:
        logging.warning(f"Trashed {trashed_count} files.\n\nFailed: \n" + "\n".join(errors))
        show_toast(globs,
                    f"Trashed {trashed_count} files - Some Failed to Trash\n",
                    _type="error")
    else:
        logging.error(
            f"Could not move any files to trash.\n\n" + "\n".join(errors))
        show_toast(globs,
                    f"Could not move any files to trash.",
                    _type="error")
    
    return True


def open_logs(globs):
    """Opens the logs folder."""
    if globs.os_name.startswith("Windows"):
        logging.debug(f"Opening logs folder on Windows...")
        os.startfile(load_data_path("cache", "logs"))
    else:
        logging.debug(f"Opening logs folder on Linux...")
        subprocess.run(
            ['xdg-open', load_data_path("cache", "logs")], check=True)


def open_config(globs):
    """Opens the settings folder."""
    if globs.os_name.startswith("Windows"):
        logging.debug(f"Opening settings folder on Windows...")
        os.startfile(load_data_path("config"))
    else:
        logging.debug(f"Opening settings folder on Linux...")
        subprocess.run(
            ['xdg-open', load_data_path("config")], check=True)
