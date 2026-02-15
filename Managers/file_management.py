# Managers/file_management.py
import logging, os, shutil
from tkinter import messagebox
from Managers.history_manager import load_history, add_update_history
from Utils.toast import show_toast

move_log = []

def count_files(directory, extension=None):
    """Count files in the given directory, optionally filtering by extension."""
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        if extension:
            files = [f for f in files if f.lower().endswith(extension)]
        return len(files)
    except Exception as e:
        logging.error(f"Error counting files in {directory}: {e}")
        return 0

def move_files(globals, history_tree, directory, folder_map, oneoffs_folder, file_list=None):
    """Moves files from one directory to another."""
    errors = []
    moved_files = 0
    archive_root = globals.archive.strip()
    logging.debug(f"Using archive_root: {archive_root}")

    if not archive_root or not os.path.isdir(archive_root):
        show_toast(globals, "Archive path not set or invalid!", _type="error")
        logging.error(f"Cannot archive: invalid archive root '{archive_root}'")
        return

    if file_list is None:
        file_list = [os.path.join(directory, filename) for filename in os.listdir(directory) if os.path.isfile(os.path.join(directory, filename))]
    
    for src_file in file_list:
        filename = os.path.basename(src_file)
        first_word = os.path.splitext(filename)[0].split()[0].lower()
        logging.debug(f"First word of the filename: {first_word}")

        file_type = globals.file_identity.get(src_file, "Invoice")  # default to Invoice if untagged
        logging.debug(f"File identity for {src_file}: {file_type}")

        # Find matching subfolder
        subfolder_name = next(
            (folder for words, folder in folder_map.items() if first_word in words),
            oneoffs_folder
        )
        logging.debug(f"Matched subfolder: {subfolder_name}")

        dst_folder = os.path.join(archive_root, subfolder_name)
        logging.debug(f"Destination folder: {dst_folder}")
        logging.debug(f"Miscellaneous folder: {oneoffs_folder}")

        # Create the destination folder if it doesn't already exist
        if not os.path.isdir(dst_folder):
            os.mkdir(dst_folder)

        dst_file = os.path.join(dst_folder, filename)
        try:
            shutil.move(src_file, dst_file)
            moved_files += 1
            add_update_history(filename=filename, src_folder=globals.inbox, dst_folder=dst_folder, file_type=file_type, moved=globals.user)
        except Exception as e:
            errors.append(f"Failed to move {filename} due to: {e}")
            logging.debug(f"Failed to move {filename} due to: {e}")
            continue

        # Reload Treeview
        load_history(history_tree)

    if errors:
        show_toast(globals, f"Error moving some files", _type="error")
        logging.error("Move Errors", "\n".join(errors))
    elif moved_files == 0:
        show_toast(globals, f"No files moved in {directory}.", _type="error")
        logging.warning("No Files", f"No files moved in {directory}.")
    else:
        show_toast(globals, f"Archived {moved_files} files successfully!")
