# Managers/history_manager.py
import logging
import csv
import os
from Utils.load_settings import load_history_path

headers = ["File Name",
           "Source Folder",
           "Destination Folder",
           "Type",
           "Archived",
           "Entered"]


def load_history(history_tree):
    """
    Loads history from the history.csv file,
    return default headers if file doesn't exist.
    """
    path = load_history_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Create a new history file with headers if missing
        if not os.path.isfile(path):
            with open(path, "w", newline="", encoding="utf-8") as history:
                writer = csv.writer(history)
                writer.writerow(headers)
            logging.info(f"Created a new history file at {path}")
        # Write headers if file is empty
        if os.path.isfile(path) and os.path.getsize(path) == 0:
                    with open(path, "w", newline="", encoding="utf-8") as history:
                        writer = csv.writer(history)
                        writer.writerow(headers)
                    logging.info(
                         f"Added headers to empty history file at {path}")
        # Loads data into the treeview
        history_tree.delete(*history_tree.get_children())
        with open(path, "r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    if len(row) == 6:
                        history_tree.insert("", "end", values=tuple(row))
                    else:
                        logging.warning(
                            f"Skipping invalid row in history.csv: {row}")
        logging.debug(
            f"Loaded {len(history_tree.get_children())} entries from {path}")
    except Exception as e:
            logging.error(f"Could not load history file due to: {e}")


def add_update_history(filename, src_folder, dst_folder=None, file_type=None, moved=None, entered=None):
    """
    Adds or updates a history entry.
    Only changes fields that are provided (not None).
    """
    path = load_history_path()
    rows = []

    # Read existing CSV
    if os.path.isfile(path) and path.lower().endswith("csv"):
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

    # Ensure headers exist
    if not rows or rows[0] != headers:
        rows = [headers] + (rows if rows else [])

    # Find existing row
    row_index = None
    for i in range(1, len(rows)):
        if len(rows[i]) > 0 and rows[i][0] == filename:
            row_index = i
            break

    if row_index is not None:
        # Update existing row — preserve old values unless new one provided
        current = rows[row_index]
        # Pad short rows
        while len(current) < 6:
            current.append("")

        new_row = [
            filename,                                      # column 0
            src_folder if src_folder is not None else current[1],
            dst_folder if dst_folder is not None else current[2],
            file_type if file_type is not None else current[3],
            moved if moved is not None else current[4],
            entered if entered is not None else current[5]]
        rows[row_index] = new_row
        logging.debug(f"Updated history entry for {filename}")
    else:
        # New entry — use defaults where nothing provided
        new_row = [
            filename,
            src_folder or "",           # or raise error if required?
            dst_folder or "N/A",
            file_type or "",            # or raise error if required?
            moved or "No",
            entered or "No"]
        rows.append(new_row)
        logging.debug(f"Added new history entry for {filename}")

    # Write back
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        logging.info(f"Successfully updated history.csv for {filename}")
    except Exception as e:
        logging.error(f"Failed to update history.csv for {filename}: {e}")
