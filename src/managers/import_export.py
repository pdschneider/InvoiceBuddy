# Managers/import_export.py
from PySide6.QtWidgets import QFileDialog
from src.utils.toast import show_toast
import csv
import logging


def export_history(globals, history_tree):
    """Exports history as a csv file to the users desired location."""
    if not history_tree.get_children():
        show_toast(globals, message="No log entries to export")
        logging.warning(f"No log entries to export.")
        return

    #  Opens up a window to select the filepath for saving
    file_path, filter = QFileDialog.getSaveFileName(
        None,
        "Export",
        "",
        options=QFileDialog.Option.DontUseNativeDialog)

    if file_path:
        try:
            # Sets up a blank CSV file to start writing data to it
            with open(file_path, 'w', newline='') as csvfile:
                try:
                    writer = csv.writer(csvfile)
                    writer.writerow(["File Name",
                                     "Source Folder",
                                     "Destination Folder",
                                     "Type",
                                     "Archived",
                                     "Entered"])
                    for item_id in history_tree.get_children():
                        writer.writerow(history_tree.item(item_id)["values"])
                    show_toast(globals, message="Log exported!")
                    logging.info(f"History imported to {file_path}")

                # Shows an error if the file was partially written
                except Exception as e:
                    show_toast(globals, message="Export failed mid-write - Partial file written", _type="error")
                    logging.error(
                        f"Export failed mid-write and partial file was written due to {e}")

        # Shows an error if the file was not created
        except Exception as e:
            show_toast(globals, message="Export failed - check logs for details", _type="error")
            logging.error(f"Could not export as csv file due to {e}")


def import_history(globals, history_tree):
    """Imports a previously exported csv file to the history treeview."""
    file_path, filter = QFileDialog.getOpenFileName(
            None,
            "Import",
            "",
            "CSV files (*.csv);;All files (*.*)",
            options=QFileDialog.Option.DontUseNativeDialog)
    if file_path and file_path.lower().endswith(".csv"):
        try:
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader, None)

                # Makes sure headers row isn't empty and contains
                # the exact headers, case insensitive.
                if headers and [h.lower() for h in headers] != ["file name",
                                                                "source folder",
                                                                "destination folder",
                                                                "type",
                                                                "archived",
                                                                "entered"]:
                    show_toast(globals, message="Import Failed - Invalid headers", _type="error")
                    logging.error(
                        "Invalid CSV format. Expected headers: File Name, Source Folder, Destination Folder, Type, Archived, Entered")
                    return

                # Clear existint entries from the tree
                history_tree.delete(*history_tree.get_children())

                logged_rows = 0
                skipped_rows = 0
                for row in reader:
                    if len(row) == 6:
                        history_tree.insert("", "end", values=row)
                        logged_rows += 1

                    elif len(row) != 6:
                        logging.debug(
                            f"Could not write row due to incorrect row count: {row}")
                        skipped_rows += 1

            # Handles error and success messages in any scenario
            if logged_rows == 0:
                if skipped_rows == 0:
                    show_toast(globals, message="No data rows found in the CSV file")
                    logging.error(
                        f"No data written from CSV file at {file_path}.")
                else:
                    show_toast(globals, message="All rows have incorrect column count (expected 6)")
                    logging.error(
                        f"No rows imported from {file_path}: Skipped {skipped_rows} rows due to incorrect column count.")
            elif skipped_rows == 0:
                show_toast(globals, message="History imported successfully!")
                logging.info(
                    f"History imported from {file_path}. Imported {logged_rows} rows and skipped {skipped_rows} rows.")
            else:
                show_toast(globals, message=f"Partial Success - Imported {logged_rows} rows and skipped {skipped_rows} rows")
                logging.warning(
                    f"History imported from {file_path}. Imported {logged_rows} rows and skipped {skipped_rows} rows.")

        except Exception as e:
            show_toast(globals, message="Could not import CSV file", _type="error")
            logging.error(f"Could not import CSV file due to {e}")

    elif file_path and not file_path.lower().endswith(".csv"):
        show_toast(globals, message="File path either doesn't exist or is not a CSV")
        logging.warning(f"Attempted import filepath either doesn't exist or is not a CSV.")
