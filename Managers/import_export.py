# Managers/import_export.py
from tkinter import messagebox
from tkinter import filedialog
import datetime
import csv
import logging


def export_history(history_tree):
    """Exports history as a csv file to the users desired location."""
    if not history_tree.get_children():
        messagebox.showwarning("Warning", "No log entries to export.")
        logging.warning(f"No log entries to export.")
        return

    #  Opens up a window to save the file as a memory object called file_path
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile=f"invoice_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv")

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
                    messagebox.showinfo(
                        "Success", f"Log exported to {file_path}")
                    logging.info(f"History imported to {file_path}")

                # Shows an error if the file was partially written
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Export failed mid-write. Partial file written. {e}")
                    logging.error(
                        f"Export failed mid-write and partial file was written due to {e}")

        # Shows an error if the file was not created
        except Exception as e:
            messagebox.showerror("Export failed", f"{e}")
            logging.error(f"Could not export as csv file due to {e}")


def import_history(history_tree):
    """Imports a previously exported csv file to the history treeview."""
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
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
                    messagebox.showerror(
                        "Error", "Invalid CSV format. Expected headers: File Name, Source Folder, Destination Folder, Type, Archived, Entered")
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
                    messagebox.showerror(
                        "No Data", f"No data rows found in the CSV file at {file_path}.")
                    logging.error(
                        f"No data written from CSV file at {file_path}.")
                else:
                    messagebox.showerror(
                        "Error", f"No rows imported from {file_path}: All {skipped_rows} rows have incorrect column count (expected 6).")
                    logging.error(
                        f"No rows imported from {file_path}: Skipped {skipped_rows} rows due to incorrect column count.")
            elif skipped_rows == 0:
                messagebox.showinfo(
                    "Success", f"History imported from {file_path}. Imported {logged_rows} rows.")
                logging.info(
                    f"History imported from {file_path}. Imported {logged_rows} rows and skipped {skipped_rows} rows.")
            else:
                messagebox.showwarning(
                    "Partial Success", f"History imported from {file_path}. Imported {logged_rows} rows and skipped {skipped_rows} rows.")
                logging.warning(
                    f"History imported from {file_path}. Imported {logged_rows} rows and skipped {skipped_rows} rows.")

        except Exception as e:
            messagebox.showerror(
                "Error", f"Could not import CSV file due to {e}")
            logging.error(f"Could not import CSV file due to {e}")
    elif file_path and not file_path.lower().endswith(".csv"):
        logging.warning(f"File path is either not existant or not a CSV.")
        messagebox.showerror(
            "Error", f"File path is either not existant or not a CSV.")
