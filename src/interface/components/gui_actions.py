# src/interface/components/gui_actions.py
import os
import logging
from tkinter import messagebox
from src.managers.autoname.pdfsearch import apply_auto_naming
from src.managers.data_processing import (parse_invoices, parse_credit_cards,
                                          parse_sheet_qt)
from src.managers.file_management import archive_files
from src.managers.import_export import export_history, import_history
from src.utils.save_settings import save_metadata
from src.utils.save_qt import save_metadata as save_qt_metadata
from src.utils.toast import show_toast
from PySide6.QtWidgets import QMessageBox


def pdf_button(globs, companies=None, directory=None, file_list=None):
    """One-click auto-naming — all logic in apply_auto_naming."""
    # Save metadata first
    if globs.legacy_mode:
        save_metadata(globs)
    else:
        save_qt_metadata(globs)

    if not file_list:
        if not globs.legacy_mode:
            QMessageBox.information(
                globs.window,
                "Nothing Selected",
                "Please select one or more files to auto-name.",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
        else:
            messagebox.showinfo("Nothing Selected", "Please select one or more files to auto-name.")
        return
    
    new_file_list = []
    if not globs.legacy_mode:
        for file in file_list:
            new_file_list.append(os.path.normpath(os.path.join(globs.inbox, file)))
        file_list = new_file_list

    logging.debug(f"Attempting to auto-name files: {file_list}")

    search_dir = os.path.normpath(directory or globs.sources['inbox'])
    changes = apply_auto_naming(globs, search_dir, file_list)

    if changes == 0:
        if not globs.legacy_mode:
            QMessageBox.information(
                globs.window,
                "Nothing to Do",
                "Files already properly named or no matches found in file contents.",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
        else:
            messagebox.showinfo("Nothing to Do", "Files already properly named or no matches found in file contents.")
    else:
        if not globs.legacy_mode:
            QMessageBox.information(
                globs.window,
                "Complete!",
                f"Auto-Name Complete! Updated {changes} file(s).",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
        else:
            messagebox.showinfo("Complete", f"Auto-Name Complete. Updated {changes} file(s).")

    if globs.legacy_mode:
        globs.root.after(100, globs.update_file_counts)


def parse_to_spreadsheet(globs, file_type, file_list=None):
    """
    Dispatch to the correct parser (Invoices or Credit Cards).
    The parsers already know where to read/write, so we only pass:
        • globs
        • globs.history_tree (for UI refresh)
        • optional file_list
    """
    # Save metadata first
    if globs.legacy_mode:
        save_metadata(globs)
    else:
        save_qt_metadata(globs)

    parsers = {
        "Invoices":     parse_invoices,
        "Credit Cards": parse_credit_cards,}

    if file_type not in parsers:
        show_toast(globs, f"Unsupported file type: {file_type}", _type="error")
        logging.error(f"Unsupported file type: {file_type}")
        return

    # Call the selected parser with the exact signature it expects
    parsers[file_type](globs, globs.history_tree, file_list)


def smart_spreadsheet_button(globs, file_list=None):
    """
    One button to rule them all.
    Looks at each file's Identity metadata (or in-memory tag) and sends:
      - "Invoice"  → parse_invoices
      - "Card"     → parse_credit_cards
      - "Purchase" → skipped (or warn)
    """
    # Save metadata first
    if globs.legacy_mode:
        save_metadata(globs)
    else:
        save_qt_metadata(globs)

    if not file_list:
        show_toast(globs, "Please select one or more files to enter.")
        return

    if globs.legacy_mode:
        # Split files by type
        invoices = []
        cards = []
        purchases = []
        unknown = []

        for full_path in file_list:
            filename = os.path.basename(full_path)
            file_type = globs.file_identity.get(filename, "Invoice")  # default to Invoice if untagged

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
            parse_invoices(globs, globs.history_tree, invoices)
        if cards:
            parse_credit_cards(globs, globs.history_tree, cards)

        # Feedback
        total = len(file_list)
        processed = len(invoices) + len(cards)
        skipped = len(purchases) + len(unknown)

        if skipped == 0 and (os.path.isfile(globs.workbook) or os.path.isfile(globs.workbook_var.get().strip())):
            show_toast(globs, f"Entered {processed} files into the spreadsheet.")
        elif skipped != 0 and (os.path.isfile(globs.workbook) or os.path.isfile(globs.workbook_var.get().strip())):
            show_toast(globs,
                f"Entered {processed} files.\n"
                f"Skipped {skipped} files (tagged as Purchase or unknown).")
        else:
            show_toast(globs, f"No valid workbook path. Skipping entering data.", _type="error")
            logging.warning(f"No valid workbook path. Skipping entering data.")
    else:
        # Qt: group files by sheet name
        sheet_groups = {}

        for full_path in file_list:
            filename = os.path.basename(full_path)
            sheet_name = globs.file_identity.get(filename, "")
            if not sheet_name:
                sheets = globs.sheet_data.get("sheets", [])
                sheet_name = sheets[0].get("name", "Sheet") if sheets else "Sheet"
            if sheet_name not in sheet_groups:
                sheet_groups[sheet_name] = []
            sheet_groups[sheet_name].append(full_path)

        logging.info(f"Qt dispatch groups: {sheet_groups}")

        # Dispatch to parse_sheet_qt for each sheet
        for sheet_name, files in sheet_groups.items():
            parse_sheet_qt(globs, sheet_name, files)

        # Show completion toast
        show_toast(globs, f"Entered {len(file_list)} files to {len(sheet_groups)} sheets!")


def invoice_button(globs, file_list=None):
    """Initiates the parse_invoices function to enter invoice data to the spreadsheet."""
    parse_to_spreadsheet(globs, "Invoices", file_list)


def credit_button(globs, file_list=None):
    """Initiates the parse_credit_cards function to enter credit card data to the spreadsheet."""
    parse_to_spreadsheet(globs, "Credit Cards", file_list)


def move_button(globs):
    """Initiates archive_files and moves the files associated with selected treeview rows to their destination folders."""
    # Save metadata first
    if globs.legacy_mode:
        save_metadata(globs)
    else:
        save_qt_metadata(globs)
    selected_items = globs.history_tree.selection()
    if not selected_items:
        show_toast(globs, "No files selected to move.")
        return

    groups = {}
    for item_id in selected_items:
        values = globs.history_tree.item(item_id)['values']
        src_folder = values[1]
        filename = values[0]
        file_type = values[3]
        key = (src_folder, file_type)
        if key not in groups:
            groups[key] = []
        groups[key].append(os.path.join(src_folder), filename)

    if not groups:
        show_toast(globs, "No valid files found to move.")
        return

    for (directory, file_type), file_list in groups.items():
        archive_files(globs, globs.history_tree, directory, file_type, globs.folder_map, globs.oneoffs_folder, file_list)


def export_button(globs):
    """Initiates export_history to export the current history log to a chosen location."""
    # Save metadata first
    if globs.legacy_mode:
        save_metadata(globs)
    else:
        save_qt_metadata(globs)
    export_history(globs.history_tree)


def import_button(globs):
    """Initiates import_history and imports a previously exported log into the History tab's treeview."""
    # Save metadata first
    if globs.legacy_mode:
        save_metadata(globs)
    else:
        save_qt_metadata(globs)
    import_history(globs.history_tree)
