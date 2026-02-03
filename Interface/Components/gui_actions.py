# Interface/Components/gui_actions.py
import os, subprocess, logging, shutil
from tkinter import messagebox, filedialog
from Managers.pdfsearch import apply_auto_naming
from Managers.data_processing import parse_invoices, parse_credit_cards
from Managers.file_management import move_files
from Managers.history_manager import revert_moves
from Managers.import_export import export_history, import_history
from Utils.save_settings import save_metadata
from Utils.toast import show_toast

def add_file(globals):
    """Moves a file to the inbox."""
    if not os.path.isdir(globals.inbox) and os.path.isdir(globals.inbox_dir_var.get().strip()):
        globals.inbox = globals.inbox_dir_var.get().strip()
        logging.debug(f"Inbox not a valid path. Using path from paths settings.")
    if os.path.isdir(globals.inbox) and os.path.isdir(globals.inbox):
        new_file = filedialog.askopenfilenames(title="Select Files", filetypes=[("PDF files", "*.pdf")], multiple=True)
        try:
            if new_file:
                files_list = []
                for file in new_file:
                    files_list.append(file)
                    logging.debug(f"Attempting to add files: {files_list}")
                for file in files_list:
                    if not file.lower().endswith(".pdf"):
                        logging.warning(f"Only PDF files can be added.")
                        messagebox.showerror(parent=globals.root, title="Unable to Add File", message="Only PDF files can be added.")
                        return
                for file in new_file:
                        save_metadata(globals)
                        shutil.copy2(file, globals.inbox)
                logging.info(f"Added files!")
        except Exception as e:
            for file in new_file:
                logging.error(f"Could not add {file} to inbox due to: {e}")
            messagebox.showerror(parent=globals.root, title="Unable to Add File", message="Unable to add files.")
    else:
        logging.error(f"Cannot add files to an invalid inbox path.")
        messagebox.showwarning(parent=globals.root, title="Unable to Add File", message="Select a valid inbox path first.")

def browse_file(var):
    """Open a file dialog to select a file and set the variable."""
    file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*"), ("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
    if file_path:
        var.set(file_path)
        logging.info(f"Selected file: {file_path}")

def browse_directory(var):
    """Open a directory dialog to select a directory and set the variable."""
    dir_path = filedialog.askdirectory()
    if dir_path:
        var.set(dir_path)
        logging.info(f"Selected directory: {dir_path}")

def open_workbook(globals):
    """Opens the Excel workbook at the initiated file path."""
    if os.path.isfile(globals.workbook):
        try:
            if globals.os_name.startswith("Windows"):
                os.startfile(globals.workbook)
            else:
                subprocess.run(['xdg-open', globals.workbook], check=True)
            logging.info(f"Opened workbook: {globals.workbook}")
        except PermissionError as e:
            messagebox.showerror("Error", f"Permission Error. Is the workbook already open?\n {e}")
            logging.error(f"Permission Error. Is the workbook already open?\n {e}")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open workbook {globals.workbook}: {e}")
            logging.error(f"Error opening workbook {globals.workbook}: {e}")
            return
    else:
        messagebox.showerror("Error", f"Cannot open workbook. Invalid file path: {globals.workbook}")
        logging.error(f"Cannot open workbook. Invalid file path {globals.workbook}")
        return

def open_directory(directory):
    """Opens the directory of the current tab."""
    try:
        if not directory or not os.path.isdir(directory):
            messagebox.showerror("Error", f"Invalid directory: {directory}")
            logging.error(f"Cannot open directory: Invalid path {directory}")
            return
        try:
            os.startfile(directory)
        except:
            subprocess.run(['xdg-open', directory], check=True)
        logging.info(f"Opened directory: {directory}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open directory {directory}: {e}")
        logging.error(f"Error opening directory {directory}: {e}")

def open_selected_folders(globals):
    """Opens the folders that the files at selected treeview rows are located in."""
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

def revert_button(history_tree):
    """Initiates the reversion of selected files which have been moved or entered into the spreadsheet."""
    revert_moves(history_tree)

def pdf_button(globals, companies=None, directory=None, file_list=None):
    """One-click auto-naming — all logic in apply_auto_naming."""
    save_metadata(globals)
    if not file_list:
        show_toast(globals, "Please select one or more files to auto-name.")
        return

    search_dir = os.path.normpath(directory or globals.sources['inbox'])
    changes = apply_auto_naming(search_dir, file_list)

    if changes == 0:
        show_toast(globals, "Files already properly named or no matches found in file contents.")
    else:
        show_toast(globals, f"Auto-Name Complete. Updated {changes} file(s).")

    globals.root.after(100, globals.update_file_counts)

def parse_to_spreadsheet(globals, file_type, file_list=None):
    """
    Dispatch to the correct parser (Invoices or Credit Cards).
    The parsers already know where to read/write, so we only pass:
        • globals
        • globals.history_tree (for UI refresh)
        • optional file_list
    """
    save_metadata(globals)
    parsers = {
        "Invoices":     parse_invoices,
        "Credit Cards": parse_credit_cards,}

    if file_type not in parsers:
        messagebox.showerror("Error", f"Unsupported file type: {file_type}")
        return

    # Call the selected parser with the exact signature it expects
    parsers[file_type](globals, globals.history_tree, file_list)

def smart_spreadsheet_button(globals, file_list=None):
    """
    One button to rule them all.
    Looks at each file's Identity metadata (or in-memory tag) and sends:
      - "Invoice"  → parse_invoices
      - "Card"     → parse_credit_cards
      - "Purchase" → skipped (or warn)
    """
    save_metadata(globals)

    if not file_list:
        show_toast(globals, "Please select one or more files to enter.")
        return

    # Split files by type
    invoices = []
    cards = []
    purchases = []
    unknown = []

    for full_path in file_list:
        filename = os.path.basename(full_path)
        file_type = globals.file_identity.get(filename, "Invoice")  # default to Invoice if untagged

        if file_type == "Invoice":
            invoices.append(full_path)
        elif file_type == "Card":
            cards.append(full_path)
        elif file_type == "Purchase":
            purchases.append(full_path)
        else:
            unknown.append(full_path)

    # Run the appropriate parsers
    if invoices:
        parse_invoices(globals, globals.history_tree, invoices)
    if cards:
        parse_credit_cards(globals, globals.history_tree, cards)

    # Feedback
    total = len(file_list)
    processed = len(invoices) + len(cards)
    skipped = len(purchases) + len(unknown)

    if skipped == 0 and (os.path.isfile(globals.workbook) or os.path.isfile(globals.workbook_var.get().strip())):
        show_toast(globals, f"Entered {processed} files into the spreadsheet.")
    elif skipped != 0 and (os.path.isfile(globals.workbook) or os.path.isfile(globals.workbook_var.get().strip())):
        show_toast(globals,
            f"Entered {processed} files.\n"
            f"Skipped {skipped} files (tagged as Purchase or unknown).")
    else:
        messagebox.showwarning("Warning", f"No valid workbook path. Skipping entering data.")
        logging.warning(f"No valid workbook path. Skipping entering data.")

def invoice_button(globals, file_list=None):
    """Initiates the parse_invoices function to enter invoice data to the spreadsheet."""
    parse_to_spreadsheet(globals, "Invoices", file_list)
    
def credit_button(globals, file_list=None):
    """Initiates the parse_credit_cards function to enter credit card data to the spreadsheet."""
    parse_to_spreadsheet(globals, "Credit Cards", file_list)

def move_button(globals):
    """Initiates move_files and moves the files associated with selected treeview rows to their destination folders."""
    save_metadata(globals)
    selected_items = globals.history_tree.selection()
    if not selected_items:
        show_toast(globals, "No files selected to move.")
        return

    groups = {}
    for item_id in selected_items:
        values = globals.history_tree.item(item_id)['values']
        src_folder = values[1]
        filename = values[0]
        file_type = values[3]
        key = (src_folder, file_type)
        if key not in groups:
            groups[key] = []
        groups[key].append(os.path.join(src_folder), filename)

    if not groups:
        show_toast(globals, "No valid files found to move.")
        return

    for (directory, file_type), file_list in groups.items():
        move_files(globals, globals.history_tree, directory, file_type, globals.folder_map, globals.oneoffs_folder, file_list)

def export_button(globals):
    """Initiates export_history to export the current history log to a chosen location."""
    save_metadata(globals)
    export_history(globals.history_tree)

def import_button(globals):
    """Initiates import_history and imports a previously exported log into the History tab's treeview."""
    save_metadata(globals)
    import_history(globals.history_tree)
