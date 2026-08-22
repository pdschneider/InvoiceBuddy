# src/utils/save_settings.py
import logging
import json
import os
from src.utils.load_settings import (load_settings,
                                 load_paths,
                                 load_folder_map,
                                 load_data_path)
from src.managers.history_manager import load_history
from pypdf import PdfReader, PdfWriter
from config import apply_theme
from src.utils.toast import show_toast


def save_all_settings(globs, reject_toast=False, reject_metadata=False):
    """
    Save all settings to JSON files and update globs.

    Args:
        globs (globs): The global configuration
        object containing UI variables and settings.
    """

    def _gather_buddy_info(globs):
        """Collect current buddy name → path from the UI entries."""
        buddy_map = {}
        buddy_counter = 0
        for entry in globs.buddy_entries:  # ← Use the UI list
            name = entry["name_var"].get().strip()[:9]
            if name == "inbox":
                buddy_counter += 1
                name = f"inbox-{buddy_counter}"
                logging.warning(
                    f"Buddy name cannot be 'inbox'. Sanitizing....")
            path = entry["path_var"].get().strip()
            # Only save if both name and path are filled
            if name and path and os.path.isdir(path):
                buddy_map[name] = path
        return buddy_map

    if not reject_metadata:
        save_metadata(globs)

    if hasattr(globs, "archive_path_var"):
        save_folder_map(globs)

    # Save Spreadsheet Specs
    save_spreadsheet_specs(globs)

    # Sources from UI
    new_sources = {
        "inbox": globs.inbox_dir_var.get().strip() or globs.inbox,
        "workbook": globs.workbook_var.get().strip() or globs.workbook,
        "archive": globs.archive_path_var.get().strip() or globs.archive}
    if not os.path.isdir(new_sources["inbox"]):
        logging.debug(f"Inbox is not a valid path. Sanitizing...")
        new_sources["inbox"] = ""
    if not os.path.isfile(new_sources["workbook"]):
        logging.debug(f"Workbook is not a valid path. Sanitizing...")
        new_sources["workbook"] = ""

    buddy_map = _gather_buddy_info(globs)

    save_paths(globs, sources=new_sources, buddies=buddy_map)

    # Load current settings
    settings = load_settings()
    current_logging_level = globs.logging_level_var.get()
    current_active_theme = globs.theme_var.get()
    current_history_path = globs.history_var.get()
    current_default_printer = globs.default_printer_var.get()
    logging_level = current_logging_level
    current_github_check = globs.github_check_var.get()
    current_beta = globs.beta_var.get()
    current_dynamic_window_size = globs.dynamic_window_size_var.get()
    current_legacy_mode = globs.legacy_mode_var.get()

    # Save Window Placement
    if globs.root.state() != "zoomed":  # don't save if maximized
        try:
            current_width = globs.root.winfo_width()
            current_height = globs.root.winfo_height()
            current_horizontal_placement = globs.root.winfo_x()
            current_vertical_placement = globs.root.winfo_y()
        except Exception as e:
            logging.debug(f"Could not save window placement due to {e}")
            return
    else:
        return

    # Save settings with updated logging levels
    save_settings(
        logging_level=logging_level,
        active_theme=current_active_theme,
        history_path=current_history_path,
        saved_width=current_width,
        saved_height=current_height,
        saved_x=current_horizontal_placement,
        saved_y=current_vertical_placement,
        default_printer=current_default_printer,
        github_check = current_github_check,
        beta=current_beta,
        dynamic_window_size=current_dynamic_window_size,
        legacy_mode=current_legacy_mode)

    # Refresh globs
    globs.refresh_globs()

    # Update UI with fresh spreadsheet specs
    globs.sheet_invoices_var.set(globs.sheet_invoices)
    globs.sheet_CreditCards_var.set(globs.sheet_CreditCards)
    globs.sheet_PurchaseOrders_var.set(globs.sheet_PurchaseOrders)
    globs.table_InvoiceTable_var.set(globs.table_InvoiceTable)
    globs.table_CreditCards_var.set(globs.table_CreditCards)
    globs.table_PurchaseOrders_var.set(globs.table_PurchaseOrders)
    globs.invoice_starting_row_var.set(globs.invoice_starting_row)
    globs.card_starting_row_var.set(globs.card_starting_row)
    globs.po_starting_row_var.set(globs.po_starting_row)
    globs.invoice_starting_column_var.set(globs.invoice_starting_column)
    globs.card_starting_column_var.set(globs.card_starting_column)
    globs.po_starting_column_var.set(globs.po_starting_column)
    globs.invoice_com_a_var.set(globs.invoice_component_a)
    globs.invoice_com_b_var.set(globs.invoice_component_b)
    globs.invoice_com_c_var.set(globs.invoice_component_c)
    globs.invoice_com_d_var.set(globs.invoice_component_d)
    globs.card_com_a_var.set(globs.card_component_a)
    globs.card_com_b_var.set(globs.card_component_b)
    globs.card_com_c_var.set(globs.card_component_c)
    globs.card_com_d_var.set(globs.card_component_d)
    globs.po_com_a_var.set(globs.po_component_a)
    globs.po_com_b_var.set(globs.po_component_b)
    globs.po_com_c_var.set(globs.po_component_c)
    globs.po_com_d_var.set(globs.po_component_d)

    # Reload settings to update globs
    settings = load_settings()
    globs.logging_level_var.set(settings["logging_level"])
    globs.theme_var.set(settings["active_theme"])

    # Update paths from folder_maps.json
    folder_map, oneoffs_folder = load_folder_map()
    sources, buddies = load_paths()
    globs.folder_map = folder_map
    globs.oneoffs_folder = oneoffs_folder
    globs.sources = sources
    if os.path.isfile(globs.history_path):
        globs.history_var.set(globs.history_path)
    else:
        globs.history_var.set("")
        logging.warning(f"History path is not a valid file path.")
    logging.root.setLevel(getattr(logging, settings["logging_level"]))

    # Apply new theme
    if globs.legacy_mode:
        apply_theme(current_active_theme)

    load_history(globs.history_tree)

    # Configure labels
    configure_labels(globs)

    if hasattr(globs, "refresh_send_buttons"):
        try:
            globs.refresh_send_buttons()
        except Exception as e:
            logging.error(f"Failed to refresh inbox send buttons: {e}")

    # Show success toast
    if not reject_toast:
        show_toast(globs, "Saved!")
    logging.info(f"Settings saved successfully!")


def save_paths(globs, sources=None, buddies=None):
    """
    Save updates to paths.json and immediately update the live globs object.

    Args:
        globs: The globs instance (required)
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

        # Update the live globs object
        globs.sources = full_data["sources"]
        globs.buddies = full_data["buddies"]
        globs.inbox = full_data["sources"].get("inbox", "")
        globs.workbook = full_data["sources"].get("workbook", "")
        globs.archive = full_data["sources"].get("archive", "")

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
    except Exception as e:
        logging.error(f"Error saving settings to {file_path}: {e}")


def save_spreadsheet_specs(globs):
    """
    Save the current spreadsheet sheet and table names to spreadsheet.json.
    """
    file_path = os.path.normpath(load_data_path("config", "spreadsheet.json"))

    data = {
        "sheet_invoices": globs.sheet_invoices_var.get().strip() or "Invoices",
        "sheet_CreditCards": globs.sheet_CreditCards_var.get().strip() or "Credit Cards",
        "sheet_PurchaseOrders": globs.sheet_PurchaseOrders_var.get().strip() or "Purchase Orders",
        "table_InvoiceTable": globs.table_InvoiceTable_var.get().strip() or "InvoiceTable",
        "table_CreditCards": globs.table_CreditCards_var.get().strip() or "CreditCards",
        "table_PurchaseOrders": globs.table_PurchaseOrders_var.get().strip() or "POTable",
        "invoice_starting_row": globs.invoice_starting_row_var.get() or 3,
        "card_starting_row": globs.card_starting_row_var.get() or 3,
        "po_starting_row": globs.po_starting_row_var.get() or 0,
        "invoice_starting_column": globs.invoice_starting_column_var.get() or 1,
        "card_starting_column": globs.card_starting_column_var.get() or 1,
        "po_starting_column": globs.po_starting_column_var.get() or 1,
        "invoice_icon": globs.invoice_icon_path or "assets/invoice-1.png",
        "card_icon": globs.card_icon_path or "assets/card-1.png",
        "po_icon": globs.po_icon_path or "assets/invoice-2.png",
        "invoice_component_a": globs.invoice_com_a_var.get() or "",
        "invoice_component_b": globs.invoice_com_b_var.get() or "",
        "invoice_component_c": globs.invoice_com_c_var.get() or "",
        "invoice_component_d": globs.invoice_com_d_var.get() or "",
        "card_component_a": globs.card_com_a_var.get() or "",
        "card_component_b": globs.card_com_b_var.get() or "",
        "card_component_c": globs.card_com_c_var.get() or "",
        "card_component_d": globs.card_com_d_var.get() or "",
        "po_component_a": globs.po_com_a_var.get() or "",
        "po_component_b": globs.po_com_b_var.get() or "",
        "po_component_c": globs.po_com_c_var.get() or "",
        "po_component_d": globs.po_com_d_var.get() or ""
        }

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save spreadsheet.json: {e}")


def save_folder_map(globs):
    """
    Save the user-selected archive path back to folder_maps.json.
    """
    file_path = os.path.normpath(load_data_path("config", "folder_maps.json"))
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

    except FileNotFoundError:
        logging.error(f"folder_maps.json not found at {file_path}")
    except Exception as e:
        logging.error(f"Failed to save folder_maps.json: {e}")


def save_metadata(globs):
    """Save file identities to PDF metadata."""
    if hasattr(globs, "file_identity") and globs.file_identity:
        inbox_dir = globs.sources.get("inbox", "")
        if os.path.isdir(inbox_dir):
            try:
                saved_count = 0
                for filename, identity_type in globs.file_identity.items():
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
                        logging.warning(
                            f"Could not save identity to {filename}: {e}")
                logging.info(
                    f"Saved identity metadata to {saved_count} PDF files.")
            except ImportError:
                logging.warning(
                    "pypdf not available — skipping PDF metadata save.")
            except Exception as e:
                logging.error(f"Error saving PDF identities: {e}")


def configure_labels(globs):
    if globs.invoice_sheet_label:
        globs.invoice_sheet_label.configure(
            text=globs.sheet_invoices or globs.sheet_invoices_var)
    if globs.card_sheet_label:
        globs.card_sheet_label.configure(
            text=globs.sheet_CreditCards or globs.sheet_CreditCards_var)
    if globs.po_sheet_label:
        globs.po_sheet_label.configure(
            text=globs.sheet_PurchaseOrders or globs.sheet_PurchaseOrders_var)
