# Interface/Components/gui_actions.py
import os, subprocess, logging
from tkinter import messagebox
from src.managers.autoname.pdfsearch import apply_auto_naming
from src.managers.data_processing import parse_invoices, parse_credit_cards
from src.managers.file_management import archive_files
from src.managers.import_export import export_history, import_history
from src.utils.save_settings import save_metadata
from src.utils.toast import show_toast


def pdf_button(globals, companies=None, directory=None, file_list=None):
    """One-click auto-naming — all logic in apply_auto_naming."""
    save_metadata(globals)
    if not file_list:
        messagebox.showinfo("Nothing Selected", "Please select one or more files to auto-name.")
        return

    search_dir = os.path.normpath(directory or globals.sources['inbox'])
    changes = apply_auto_naming(globals, search_dir, file_list)

    if changes == 0:
        messagebox.showinfo("Nothing to Do", "Files already properly named or no matches found in file contents.")
    else:
        messagebox.showinfo("Complete", f"Auto-Name Complete. Updated {changes} file(s).")

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
        show_toast(globals, f"Unsupported file type: {file_type}", _type="error")
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
        show_toast(globals, f"No valid workbook path. Skipping entering data.", _type="error")
        logging.warning(f"No valid workbook path. Skipping entering data.")

def invoice_button(globals, file_list=None):
    """Initiates the parse_invoices function to enter invoice data to the spreadsheet."""
    parse_to_spreadsheet(globals, "Invoices", file_list)
    
def credit_button(globals, file_list=None):
    """Initiates the parse_credit_cards function to enter credit card data to the spreadsheet."""
    parse_to_spreadsheet(globals, "Credit Cards", file_list)

def move_button(globals):
    """Initiates archive_files and moves the files associated with selected treeview rows to their destination folders."""
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
        archive_files(globals, globals.history_tree, directory, file_type, globals.folder_map, globals.oneoffs_folder, file_list)

def export_button(globals):
    """Initiates export_history to export the current history log to a chosen location."""
    save_metadata(globals)
    export_history(globals.history_tree)

def import_button(globals):
    """Initiates import_history and imports a previously exported log into the History tab's treeview."""
    save_metadata(globals)
    import_history(globals.history_tree)
