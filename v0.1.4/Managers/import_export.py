# Managers/import_export.py
from tkinter import messagebox, filedialog
import datetime, csv, logging

def export_history(history_tree):
    """Exports history as a csv file to the users desired location."""
    if not history_tree.get_children(): #  Checks to see if the history_tree has any rows, or is empty
        messagebox.showwarning("Warning", "No log entries to export.")
        logging.warning(f"No log entries to export.")
        return

    #  Opens up a window to save the file as a memory object (a string) called file_path
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                            filetypes=[("CSV files", "*.csv")], 
                                            initialfile=f"invoice_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv")

    if file_path: #  Checks if file_path is not empty, as in the user chose a file path
        try:
            with open(file_path, 'w', newline='') as csvfile: #  Sets up a blank CSV file to start writing data to it
                try:
                    writer = csv.writer(csvfile) #  Opens the new file in memory in write mode
                    writer.writerow(["File Name", "Source Folder", "Destination Folder", "Type", "Moved", "Entered"]) #  Assigns headers to file
                    for item_id in history_tree.get_children(): #  Iterates through history_tree's list of rows
                        writer.writerow(history_tree.item(item_id)["values"]) #  Writes rows to file, "values" is a key reflecting tree information
                    messagebox.showinfo("Success", f"Log exported to {file_path}")
                    logging.info(f"History imported to {file_path}")
                except: #  Shows an error if the file was partially written
                    messagebox.showerror("Error", f"Export failed mid-write. Partial file written. {e}")
                    logging.error(f"Export failed mid-write and partial file was written due to {e}")
        except Exception as e: #  Shows an error if the file was not created
            messagebox.showerror("Export failed", f"{e}")
            logging.error(f"Could not export as csv file due to {e}")

def import_history(history_tree):
    """Imports a previously exported csv file to the history treeview."""
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path and file_path.lower().endswith(".csv"): 
        try:
            with open(file_path, 'r', newline='') as csvfile: #  Opens the selected CSV file in read mode and assigns to csvfile variable
                reader = csv.reader(csvfile) #  Creates a reader object for the csvfile
                headers = next(reader, None)  #  Makes sure the headers row isn't written to the tree

                #  Makes sure headers row isn't empty and contains the exact headers, case insensitive. If different, it triggers an error.
                if headers and [h.lower() for h in headers] != ["file name", "source folder", "destination folder", "type", "moved", "entered"]:
                    messagebox.showerror("Error", "Invalid CSV format. Expected headers: File Name, Source Folder, Destination Folder, Type, Moved, Entered")
                    logging.error(f"Invalid CSV format. Expected headers: File Name, Source Folder, Destination Folder, Type, Moved, Entered")
                    return

                history_tree.delete(*history_tree.get_children()) #  Clear existing entries from tkinter's tree

                logged_rows = 0 #  Defines logged_rows variable for counting successes
                skipped_rows = 0 #  Defines skipped_rows variable for counting errors
                for row in reader: #  Loops through each row in the csv file 
                    if len(row) == 6:  #  Ensure row has all 6 columns, skips rows with more or less than 6 columns
                        history_tree.insert("", "end", values=row) #  Writes each row into the history_tree, appending to the bottom of the tree view
                        logged_rows += 1
                    elif len(row) != 6: #  Displays an error message if rows are not 6
                        logging.debug(f"Could not write row due to incorrect row count: {row}")
                        skipped_rows += 1

            if logged_rows == 0: #  Handles error and success messages in any scenario
                if skipped_rows == 0:
                    messagebox.showerror("No Data", f"No data rows found in the CSV file at {file_path}.")
                    logging.error(f"No data written from CSV file at {file_path}.")
                else:
                    messagebox.showerror("Error", f"No rows imported from {file_path}: All {skipped_rows} rows have incorrect column count (expected 6).")
                    logging.error(f"No rows imported from {file_path}: Skipped {skipped_rows} rows due to incorrect column count.")
            elif skipped_rows == 0:
                messagebox.showinfo("Success", f"History imported from {file_path}. Imported {logged_rows} rows.")
                logging.info(f"History imported from {file_path}. Imported {logged_rows} rows and skipped {skipped_rows} rows.")
            else:
                messagebox.showwarning("Partial Success", f"History imported from {file_path}. Imported {logged_rows} rows and skipped {skipped_rows} rows.")
                logging.warning(f"History imported from {file_path}. Imported {logged_rows} rows and skipped {skipped_rows} rows.")

        except Exception as e:
            messagebox.showerror("Error", f"Could not import CSV file due to {e}")
            logging.error(f"Could not import CSV file due to {e}")
    elif file_path and not file_path.lower().endswith(".csv"):
        logging.warning(f"File path is either not existant or not a CSV.")
        messagebox.showerror("Error", f"File path is either not existant or not a CSV.")
