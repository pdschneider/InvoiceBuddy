# Interface/Components/gui_actions.py
import os
import subprocess
import logging
import shutil
import threading
from PySide6.QtWidgets import QFileDialog
from Managers.Autoname.pdfsearch import apply_auto_naming
from Managers.data_processing import parse_invoices, parse_credit_cards
from Managers.file_management import move_files
from Managers.import_export import export_history, import_history
from Utils.save_settings import save_metadata
from Utils.toast import show_toast


def add_file(globals):
    """Moves a file to the inbox."""

    # Exit early if inbox is not a valid path
    if not os.path.isdir(globals.inbox) and os.path.isdir(globals.inbox_dir_var.get().strip()):
        globals.inbox = globals.inbox_dir_var.get().strip()
        logging.debug(
            f"Inbox not a valid path. Using path from paths settings.")

    # Add files if path is valid
    if os.path.isdir(globals.inbox) and os.path.isdir(globals.inbox):
        new_file, filter = QFileDialog.getOpenFileNames(
            None,
            "Attach File",
            "",
            "PDF Files (*.pdf)",
            options=QFileDialog.Option.DontUseNativeDialog)
        try:
            if new_file:
                files_list = []
                for file in new_file:
                    files_list.append(file)
                    logging.debug(f"Attempting to add files: {files_list}")

                for file in files_list:
                    filename = os.path.basename(file)
                    # Exit early if files are not .pdf format
                    if not str(file).lower().endswith(".pdf"):
                        logging.warning(f"Only PDF files can be added.")
                        show_toast(globals,
                                   "Only PDF files can be added.",
                                   _type="error")
                        return

                    # Exit early if file with the same name already exists
                    if os.path.isfile(os.path.join(globals.inbox, filename)):
                        logging.warning(f"File {file} already exists in inbox.")
                        show_toast(globals,
                                   "File already exists in inbox!",
                                   _type="error")
                        return

                for file in new_file:
                    shutil.copy2(file, globals.inbox)
                save_metadata(globals)
                logging.info(f"Added files!")

        except Exception as e:
            for file in new_file:
                logging.error(f"Could not add {file} to inbox due to: {e}")
            show_toast(globals, f"Unable to add files.", _type="error")
    else:
        logging.error(f"Cannot add files to an invalid inbox path.")
        show_toast(
            globals,
            f"Unable to add file - Select a valid inbox path first",
            _type="error")


def browse_directory(var):
    """Open a directory dialog and set the path into either QLineEdit or ctk.StringVar"""
    dir_path = QFileDialog.getExistingDirectory(
        None,
        "Choose Directory",
        "",
        options=QFileDialog.Option.DontUseNativeDialog)

    if dir_path:
        _set_value(var, dir_path)
        logging.info(f"Selected directory: {dir_path}")


def browse_file(var):
    """Open a file dialog and set the path into either QLineEdit or ctk.StringVar"""
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Browse for File",
        "",
        "Excel files (*.xlsx);;CSV files (*.csv);;All files (*.*)",
        options=QFileDialog.Option.DontUseNativeDialog)

    if file_path:
        _set_value(var, file_path)
        logging.info(f"Selected file: {file_path}")


def _set_value(var, value: str):
    """Helper that works with both QLineEdit and ctk.StringVar"""
    if hasattr(var, "setText"):           # PySide6 QLineEdit
        var.setText(value)
    elif hasattr(var, "set"):             # CustomTkinter StringVar
        var.set(value)
    else:
        logging.error(f"Unsupported variable type for browse: {type(var)}")


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
            show_toast(
                globals,
                f"Permission Error. Is the workbook already open?",
                _type="error")
            logging.error(
                f"Permission Error accessing {globals.workbook}: {e}")
            return
        except Exception as e:
            show_toast(globals, "Failed to open workbook", _type="error")
            logging.error(f"Error opening workbook {globals.workbook}: {e}")
            return
    else:
        show_toast(globals, f"Invalid workbook path", _type="error")
        logging.error(
            f"Cannot open workbook. Invalid file path {globals.workbook}")
        return


def open_directory(directory):
    """Opens the directory of the current tab."""
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
    """Opens the folders that the files at selected treeview rows are located in."""
    selected_items = globals.history_tree.selection()
    if not selected_items:
        show_toast(globals, "No items selected to open folders.")
        return
    folders = set()
    for item_id in selected_items:
        values = globals.history_tree.item(item_id)['values']
        dst_folder = values[2]
        src_folder = values[1]
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


def pdf_button(globals, companies=None, directory=None, file_list=None):
    """One-click auto-naming — all logic in apply_auto_naming."""
    save_metadata(globals)
    if not file_list:
        logging.debug("One or more files must be selected")
        return

    search_dir = os.path.normpath(directory or globals.sources['inbox'])
    changes = apply_auto_naming(globals, search_dir, file_list)

    if changes == 0:
        logging.warning("Files already properly named or no matches found in file contents")
    else:
        logging.info(f"Auto-Name Complete! Updated {changes} file(s)")

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
        "Credit Cards": parse_credit_cards}

    if file_type not in parsers:
        logging.error(f"Unsupported file type: {file_type}")
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

    def _add_in_thread(globals, file_list):
        if not file_list:
            logging.warning("Please select one or more files to enter.")
            return

        # Split files by type
        invoices = []
        cards = []
        purchases = []
        unknown = []

        for full_path in file_list:
            filename = os.path.basename(full_path)
            # default to Invoice if untagged
            file_type = globals.file_identity.get(filename, "Invoice")

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
            logging.warning(f"Entered {processed} files into the spreadsheet.")
        elif skipped != 0 and (os.path.isfile(globals.workbook) or os.path.isfile(globals.workbook_var.get().strip())):
            logging.warning(f"Skipped {skipped} files (tagged as Purchase or unknown).")
        else:
            logging.warning(f"No valid workbook path. Skipping entering data.")
    
    threading.Thread(target=_add_in_thread, args=(globals, file_list), daemon=True).start()


def invoice_button(globals, file_list=None):
    """
    Initiates the parse_invoices function
    to enter invoice data to the spreadsheet.
    """
    parse_to_spreadsheet(globals, "Invoices", file_list)


def credit_button(globals, file_list=None):
    """
    Initiates the parse_credit_cards function to
    enter credit card data to the spreadsheet.
    """
    parse_to_spreadsheet(globals, "Credit Cards", file_list)


def move_button(globals):
    """
    Initiates move_files and moves the files associated with
    selected treeview rows to their destination folders.
    """
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
        move_files(
            globals,
            globals.history_tree,
            directory,
            file_type,
            globals.folder_map,
            globals.oneoffs_folder,
            file_list)


def export_button(globals):
    """
    Initiates export_history to export the
    current historylog to a chosen location.
    """
    save_metadata(globals)
    export_history(globals, globals.history_tree)


def import_button(globals):
    """
    Initiates import_history and imports a previously
    exported log into the History tab's treeview.
    """
    save_metadata(globals)
    import_history(globals, globals.history_tree)
