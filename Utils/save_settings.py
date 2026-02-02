# Utils/save_settings.py
import logging, json, os
from Utils.load_settings import load_settings, load_paths, load_folder_map, load_data_path, load_spreadsheet_specs
from Managers.history_manager import load_history
from pypdf import PdfReader, PdfWriter
from config import apply_theme

def save_all_settings(globals):
    """
    Save all settings to JSON files and update globals.

    Args:
        globals (globals): The global configuration object containing UI variables and settings.
    """

    def _gather_buddy_info(globals):
        """Collect current buddy name → path from the UI entries."""
        buddy_map = {}
        for entry in globals.buddy_entries:  # ← Use the UI list
            name = entry["name_var"].get().strip()[:9]
            path = entry["path_var"].get().strip()
            if name and path and os.path.isdir(path):  # Only save if both are filled
                buddy_map[name] = path
        return buddy_map

    save_metadata(globals)

    if hasattr(globals, "archive_path_var"):
        save_folder_map(globals)

    # Save Spreadsheet Specs
    save_spreadsheet_specs(globals)

    # Sources from UI
    new_sources = {
        "inbox": globals.inbox_dir_var.get().strip() or globals.inbox,
        "workbook": globals.workbook_var.get().strip() or globals.workbook}
    if not os.path.isdir(new_sources["inbox"]):
        logging.debug(f"Inbox is not a valid path. Sanitizing...")
        new_sources["inbox"] = ""
    if not os.path.isfile(new_sources["workbook"]):
        logging.debug(f"Workbook is not a valid path. Sanitizing...")
        new_sources["workbook"] = ""

    buddy_map = _gather_buddy_info(globals)

    save_paths(globals, sources=new_sources, buddies=buddy_map)

    # Load current settings
    settings = load_settings()
    current_logging_level = globals.logging_level_var.get()
    current_active_theme = globals.theme_var.get()
    current_history_path = globals.history_var.get()
    logging_level = current_logging_level

    # Save Window Placement
    logging.debug(f"Root state: {globals.root.state()}")
    if globals.root.state() != "zoomed":  # don't save if maximized
        try:
            current_width = globals.root.winfo_width()
            current_height = globals.root.winfo_height()
            current_horizontal_placement = globals.root.winfo_x()
            current_vertical_placement = globals.root.winfo_y()

            logging.debug(f"Saving via winfo: {current_width}x{current_height}"
                        f"+{current_horizontal_placement}+{current_vertical_placement}")
        except Exception as e:
            logging.debug(f"Could not save window placement due to {e}")
            return
    else:
        return

    # Save settings with updated logging levels
    save_settings(
        logging_level = logging_level,
        active_theme = current_active_theme, 
        history_path = current_history_path,
        saved_width = current_width,
        saved_height = current_height,
        saved_x = current_horizontal_placement,
        saved_y = current_vertical_placement)

    # Refresh globals
    globals.refresh_globals()

    # Update UI with fresh spreadsheet specs
    globals.sheet_invoices_var.set(globals.sheet_invoices)
    globals.sheet_CreditCards_var.set(globals.sheet_CreditCards)
    globals.sheet_PurchaseOrders_var.set(globals.sheet_PurchaseOrders)
    globals.table_InvoiceTable_var.set(globals.table_InvoiceTable)
    globals.table_CreditCards_var.set(globals.table_CreditCards)
    globals.table_PurchaseOrders_var.set(globals.table_PurchaseOrders)
    globals.invoice_starting_row_var.set(globals.invoice_starting_row)
    globals.card_starting_row_var.set(globals.card_starting_row)
    globals.po_starting_row_var.set(globals.po_starting_row)
    globals.invoice_starting_column_var.set(globals.invoice_starting_column)
    globals.card_starting_column_var.set(globals.card_starting_column)
    globals.po_starting_column_var.set(globals.po_starting_column)

    # Reload settings to update globals
    settings = load_settings()
    globals.logging_level_var.set(settings["logging_level"])
    globals.theme_var.set(settings["active_theme"])

    # Update paths from folder_maps.json
    folder_map, oneoffs_folder = load_folder_map()
    sources, buddies = load_paths()
    globals.folder_map = folder_map
    globals.oneoffs_folder = oneoffs_folder
    globals.sources = sources
    if os.path.isfile(globals.history_path):
        globals.history_var.set(globals.history_path)
        logging.debug(f"History path saved correctly.")
    else:
        globals.history_var.set("")
        logging.warning(f"History path is not a valid file path.")
    logging.root.setLevel(getattr(logging, settings["logging_level"]))

    # Apply new theme
    apply_theme(current_active_theme)

    load_history(globals.history_tree)

    if hasattr(globals, "refresh_send_buttons"):
        try:
            globals.refresh_send_buttons()
        except Exception as e:
            logging.error(f"Failed to refresh inbox send buttons: {e}")

def save_paths(globals, sources=None, buddies=None):
    """
    Save updates to paths.json and immediately update the live Globals object.

    Args:
        globals: The Globals instance (required)
        sources: Dict with updates for inbox/workbook (optional)
        buddies: Dict with buddy name → path updates (optional)
    """
    file_path = load_data_path("config", "paths.json")
    try:
        # Load current data
        current_sources, current_buddies = load_paths()

        full_data = {
            "sources": current_sources.copy(),
            "buddies": current_buddies.copy()
        }

        # Apply updates if provided
        if sources is not None:
            full_data["sources"].update(sources)
        if buddies is not None:
            full_data["buddies"] = buddies

        # Write to disk
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=4)

        logging.info(f"Saved paths to {file_path}")

        # Update the live Globals object — now safe because we have the real one
        globals.sources = full_data["sources"]
        globals.buddies = full_data["buddies"]
        globals.inbox = full_data["sources"].get("inbox", "")
        globals.workbook = full_data["sources"].get("workbook", "")

    except Exception as e:
        logging.error(f"Failed to save paths.json: {e}")

def save_settings(**kwargs):
    """Save settings to settings.json."""
    settings = load_settings()
    settings.update(kwargs)
    file_path = os.path.normpath(load_data_path("config", "settings.json"))
    try:
        with open(file_path, 'w') as f:
            json.dump(settings, f, indent=4)
        logging.info(f"Saving settings to: {file_path}")
    except Exception as e:
        logging.error(f"Error saving settings to {file_path}: {e}")

def save_spreadsheet_specs(globals):
    """Save the current spreadsheet sheet and table names to spreadsheet.json."""
    file_path = os.path.normpath(load_data_path("config", "spreadsheet.json"))
    
    data = {
        "sheet_invoices": globals.sheet_invoices_var.get().strip() or "Invoices",
        "sheet_CreditCards": globals.sheet_CreditCards_var.get().strip() or "Credit Cards",
        "sheet_PurchaseOrders": globals.sheet_PurchaseOrders_var.get().strip() or "Purchase Orders",
        "table_InvoiceTable": globals.table_InvoiceTable_var.get().strip() or "InvoiceTable",
        "table_CreditCards": globals.table_CreditCards_var.get().strip() or "CreditCards",
        "table_PurchaseOrders": globals.table_PurchaseOrders_var.get().strip() or "POTable",
        "invoice_starting_row": globals.invoice_starting_row_var.get() or 3,
        "card_starting_row": globals.card_starting_row_var.get() or 3,
        "po_starting_row": globals.po_starting_row_var.get() or 0,
        "invoice_starting_column": globals.invoice_starting_column_var.get() or 1,
        "card_starting_column": globals.card_starting_column_var.get() or 1,
        "po_starting_column": globals.po_starting_column_var.get() or 1}
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Spreadsheet specifications saved to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save spreadsheet.json: {e}")

def save_folder_map(globals):
    """
    Save the user-selected archive path back to folder_maps.json.
    """
    file_path = os.path.normpath(load_data_path("config", "folder_maps.json"))
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if os.path.isdir(globals.archive_path_var.get().strip()):
            new_archive = globals.archive_path_var.get().strip()
        else:
            logging.warning(f"Archive path invalid Sanitizing...")
            new_archive = ""

        if not new_archive:
            logging.warning("Archive path is empty — not saving.")
            return

        # Normalize and ensure trailing separator
        normalized_archive = os.path.normpath(new_archive)
        if not normalized_archive.endswith(os.sep):
            normalized_archive += os.sep

        old_archive = data['bases']['archive']
        data['bases']['archive'] = normalized_archive

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        logging.info(f"Updated archive path in folder_maps.json: {old_archive} → {normalized_archive}")

        # Update the live globals immediately (redundant but safe)
        globals.archive_path = normalized_archive

    except FileNotFoundError:
        logging.error(f"folder_maps.json not found at {file_path}")
    except Exception as e:
        logging.error(f"Failed to save folder_maps.json: {e}")

def save_metadata(globals):
    # Save file identities to PDF metadata
    if hasattr(globals, "file_identity") and globals.file_identity:
        inbox_dir = globals.sources.get("inbox", "")
        if os.path.isdir(inbox_dir):
            try:
                saved_count = 0
                for filename, identity_type in globals.file_identity.items():
                    filepath = os.path.join(inbox_dir, filename)
                    if not os.path.isfile(filepath):
                        continue
                    try:
                        reader = PdfReader(filepath)
                        writer = PdfWriter()
                        for page in reader.pages:
                            writer.add_page(page)
                        if reader.metadata:
                            writer.add_metadata(reader.metadata)
                        writer.add_metadata({"/Identity": identity_type})
                        with open(filepath, "wb") as f:
                            writer.write(f)
                        saved_count += 1
                    except Exception as e:
                        logging.warning(f"Could not save identity to {filename}: {e}")
                logging.info(f"Saved identity metadata to {saved_count} PDF files.")
            except ImportError:
                logging.warning("pypdf not available — skipping PDF metadata save.")
            except Exception as e:
                logging.error(f"Error saving PDF identities: {e}")
    logging.info(f"Settings saved successfully.")
