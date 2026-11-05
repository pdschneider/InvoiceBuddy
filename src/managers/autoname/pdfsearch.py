# src/managers/autoname/pdfsearch.py
import re
import logging
import os
from src.utils.load_settings import load_company_map
from src.managers.autoname.search_helpers import (extract_normalized_text,
                                              normalize_text,
                                              write_pdf_metadata,
                                              date_patterns)
from src.managers.autoname.company_search import company_search
from src.managers.autoname.date_search import date_search
from src.managers.autoname.inv_num_search import invoice_number_search
from src.managers.autoname.card_num_search import card_number_search
from src.utils.save import save_metadata, ensure_uuid
from PySide6.QtWidgets import QMessageBox
from pypdf import PdfReader
from datetime import datetime


def apply_auto_naming(globs, directory, file_list=None, force=False):
    """
    Master auto-namer: extracts text once per file,
    calls company/date/invoice searches sequentially,
    scrubs matches from normalized text between calls,
    and renames based on progressive logic.

    When force=True, PDF metadata is overwritten and the
    filename is regenerated.

    When force=False, only blank PDF metadata is written and
    the filename is not changed.
    """

    # Save metadata first
    save_metadata(globs)

    # Return if no files are sent
    if not file_list and force:
        QMessageBox.information(
            globs.window,
            "Nothing Selected",
            "Please select one or more files to auto-name.",
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok
        )
        return 0, {}

    # Make File List Work for PySide6
    new_file_list = []
    for file in file_list:
        new_file_list.append(os.path.normpath(os.path.join(globs.inbox, file)))
    file_list = new_file_list

    logging.debug(f"Attempting to auto-name files: {file_list}")

    search_dir = os.path.normpath(directory or globs.sources['inbox'])

    # Create metadata & dates dictionaries
    metadata_to_write = {}
    applied_dates = {}

    search_dir = os.path.normpath(directory)
    if not os.path.isdir(search_dir):
        logging.error(f"Invalid directory: {search_dir}")
        return 0, {}

    # Extract normalized texts once for all files (batch optimization)
    normalized_texts = {}
    for full_path in file_list:
        if not os.path.isfile(full_path):
            continue
        filename = os.path.basename(full_path)
        
        # Check AutoNamed flag BEFORE extracting text (if not forcing)
        if not force:
            try:
                reader = PdfReader(full_path)
                if (reader.metadata or {}).get("/AutoNamed"):
                    logging.info(f"Skipping {filename}: already auto-named (pre-scan)")
                    continue
            except Exception:
                pass
        
        normalized = extract_normalized_text(full_path)
        normalized_texts[filename] = normalized
        logging.debug(f"Normalized text length: {len(normalized)}\n")

    if not normalized_texts:
        return 0, {}

    # Step 1: Search for companies (always, no skips)
    counterparty_results = company_search(
        directory=search_dir,
        file_list=file_list,
        normalized_texts=normalized_texts)

    # Step 2: Apply counterparty results, build initial new_parts, scrub if applied
    renamed = 0
    valid_companies = {normalize_text(c) for c in load_company_map().values()}

    for full_path in file_list:
        filename = os.path.basename(full_path)
        if filename not in normalized_texts:
            continue

        # Determine identity and check AutoNamed flag
        identity = ""
        existing = {}
        try:
            reader = PdfReader(full_path)
            existing = reader.metadata or {}
            if existing.get("/Sheet"):
                identity = str(existing["/Sheet"])
                logging.info(f"Sheet identity for {filename}: {identity}")
        except Exception as e:
            logging.warning(f"Could not read metadata from {filename}: {e}")

        if not identity:
            identity = globs.sheet_data.get("sheets", [{}])[0].get("name", "")
            logging.info(f"No /Sheet metadata for {filename}, defaulting to first sheet: {identity}")

        # Pick apart base name from filename
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split()
        logging.info(f"Processing: {filename}")
        logging.info(f"  Original parts: {parts}")

        new_parts = parts[:]

        # Apply counterparty if found and different/missing
        counterparty_result = counterparty_results.get(filename)
        if counterparty_result:
            counterparty, matched, keyword_tuple = counterparty_result
            norm_counterparty = normalize_text(counterparty)
            if not parts or normalize_text(parts[0]) != norm_counterparty:
                if norm_counterparty in valid_companies:  # Safety check
                    new_parts = [counterparty.capitalize()]
                    logging.info(f"  Applied counterparty: {counterparty}")

                    # Scrub all keywords from the text
                    for kw in keyword_tuple:
                        if kw.lower() in ['llc', 'inc']:
                            continue
                        normalized_kw = normalize_text(kw)
                        if normalized_kw:
                            new_text = re.sub(
                                rf'\b{re.escape(normalized_kw)}\b',
                                '',
                                normalized_texts[filename])

                            if new_text != normalized_texts[filename]:
                                normalized_texts[filename] = new_text
                                logging.debug(
                                    f"  Scrubbed matched counterparty keyword: {normalized_kw}")
                                logging.debug(
                                    f"\nCurrent Normalized Text: {normalized_texts[filename]}\n")
                                logging.debug(
                                    f"Normalized text length: {len(normalized_texts[filename])}\n")

        # Step 3: Now search for dates using updated texts
        date_results = date_search(
            directory=search_dir,
            file_list=file_list,
            normalized_texts=normalized_texts)

        # Apply date if we have exactly counterparty so far
        if len(new_parts) == 1:
            date_result = date_results.get(filename)
            if date_result:
                date, matched = date_result
                new_parts.append(date)
                applied_dates[filename] = date
                logging.info(f"  Applied date: {date}")

                old_length = len(normalized_texts[filename])

                # 1. Scrub the single matched date we used for naming (as before)
                if matched:
                    new_text = re.sub(rf'\b{re.escape(matched)}\b', '', normalized_texts[filename])
                    if new_text != normalized_texts[filename]:
                        normalized_texts[filename] = new_text
                        logging.debug(f"  Scrubbed matched date: {matched}")
                        logging.debug(f"  Length: {old_length} becomes {len(normalized_texts[filename])}")

                # 2. Exhaustively scrub ALL possible dates using all patterns
                scrubbed_any = False
                for pattern, fmt in date_patterns:
                    def _guarded(match, fmt=fmt):
                        return ' ' if fmt(match) else match.group(0)
                    new_text = re.sub(pattern, _guarded, normalized_texts[filename])
                    if new_text != normalized_texts[filename]:
                        normalized_texts[filename] = new_text.strip()
                        logging.debug(
                            f"  Scrubbed additional dates with pattern: {pattern}")
                        scrubbed_any = True

                if scrubbed_any:
                    logging.debug(
                        f"\nCurrent Normalized Text after all date scrubs: \n{normalized_texts[filename]}\n")
                    logging.debug(
                        f"Normalized text length after date scrubs: {len(normalized_texts[filename])}\n")

        # Step 4: Now search for invoices using updated texts
        invoice_results = invoice_number_search(
            directory=search_dir,
            file_list=file_list,
            normalized_texts=normalized_texts)

        # Apply invoice if we have exactly company + date
        if len(new_parts) == 2:
            invoice_result = invoice_results.get(filename)
            if invoice_result:
                invoice, matched = invoice_result
                new_parts.append(invoice)
                logging.info(f"  Applied invoice: {invoice}")
                if matched:
                    normalized_texts[filename] = re.sub(
                        rf'\b{re.escape(matched)}\b', '', normalized_texts[filename])
                    logging.debug(f"  Scrubbed matched invoice: {matched}")

                    logging.debug(
                        f"\nCurrent Normalized Text: {normalized_texts[filename]}\n")
                    logging.debug(
                        f"Normalized text length: {len(normalized_texts[filename])}\n")

        # Step 5: Search for the last 4 digits of a card number if present
        card_results = card_number_search(
            directory=search_dir,
            file_list=file_list,
            normalized_texts=normalized_texts)

        # Get user-defined field order based on the file's Identity
        meta_order = ["", "", "", ""]
        order = ["", "", "", ""]
        sheets = globs.sheet_data.get("sheets", [])
        for s in sheets:
            if s.get("name") == identity:
                order = s.get("column_order", ["Counterparty", "Date", "Invoice Number", ""])
                if s.get("separate_filename") and s.get("filename_order"):
                    order = s.get("filename_order", [])
                break

        # Map field names to their extracted values (only if found)
        available = {}
        if counterparty_result:
            available["Counterparty"] = counterparty_result[0].strip()
        if date_results.get(filename) and date_results[filename][0]:
            available["Date"] = date_results[filename][0]
        if invoice_results.get(filename) and invoice_results[filename][0]:
            available["Invoice Number"] = invoice_results[filename][0]
        if card_results.get(filename) and card_results[filename][0]:
            available["Card Number"] = card_results[filename][0]

        # Fill in any fields already present in PDF metadata (e.g. set in the editor)
        try:
            reader = PdfReader(full_path)
            existing = reader.metadata or {}
            pdf_key_map = {
                "/Counterparty": "Counterparty",
                "/Date": "Date",
                "/Amount": "Amount",
                "/Category": "Category",
                "/Subcategory": "Subcategory",
                "/Description": "Description",
                "/InvoiceNumber": "Invoice Number",
                "/CardNumber": "Card Number",
            }
            for pdf_key, field in pdf_key_map.items():
                if field not in available and existing.get(pdf_key):
                    available[field] = str(existing[pdf_key])
        except Exception as e:
            logging.warning(f"Could not merge existing metadata for {filename}: {e}")

        # Pull stored counterparty data (Category/Subcategory/Description)
        counterparty_name = available.get("Counterparty")
        if counterparty_name:
            record = globs.counterparties.get(counterparty_name, {})
            record_map = {
                "Category": "Category",
                "Subcategory": "Subcategory",
                "Description": "Description",
            }
            for field, record_key in record_map.items():
                if field not in available and record.get(record_key):
                    available[field] = record[record_key]
                    logging.info(f"  Auto-filled {field} from counterparty record")

        # Build new_parts using the user-chosen order
        # Skip any field that is empty ("") or not found
        new_parts = []
        for field in order:
            if field and field in available:
                new_parts.append(available[field])

        # Rename only if the built name differs from the current one
        if not new_parts or " ".join(new_parts) == " ".join(parts):
            logging.info(f"No rename needed for {filename} (writing metadata)")
            # fall through to metadata write

        new_base = " ".join(new_parts)
        new_name = new_base + ".pdf"
        new_path = os.path.join(search_dir, new_name)

        # Handle duplicates
        counter = 1
        while os.path.exists(new_path) and new_path != full_path:
            new_name = f"{new_base} ({counter}).pdf"
            new_path = os.path.join(search_dir, new_name)
            counter += 1

        # Build metadata from all available fields (force overwrites all, drop-in fills blanks only)
        meta = {}
        for field, value in available.items():
            key = f"/{field.replace(' #', 'Number').replace(' ', '')}"
            if not force and existing.get(key):
                continue  # field already populated
            meta[key] = value

        # Write AutoNamed flag to metadata
        meta["/AutoNamed"] = "True"
        if existing.get("/UUID"):
            meta["/UUID"] = str(existing["/UUID"])
        ensure_uuid(meta)

        if meta:
            metadata_to_write[filename] = meta
            logging.debug(f"Metadata prepared for {filename}: {meta}")

        # Write metadata before rename (still using old filename)
        if filename in metadata_to_write:
            write_pdf_metadata(
                {filename: metadata_to_write[filename]}, search_dir)
            del metadata_to_write[filename]

        # File rename (force only)
        if force:
            try:
                os.rename(full_path, new_path)
                logging.info(f"Auto-named: {filename} becomes {new_name}")
                renamed += 1
            except Exception as e:
                logging.error(f"Rename failed for {filename}: {e}")

        logging.debug(f"{filename} | order={order} | available={list(available.keys())}")

    if renamed:
        logging.info(f"Total renamed: {renamed}")

    return renamed, applied_dates


def pdf_button(globs, companies=None, directory=None, file_list=None, force=False, show_dialogs=True):
    """One-click auto-naming — all logic in apply_auto_naming."""

    # Apply auto-naming and return number of changed files and dates
    search_dir = os.path.normpath(directory or globs.sources['inbox'])
    changes, applied_dates = apply_auto_naming(globs, search_dir, file_list, force=force)
    logging.debug(f"Applied Dates: {applied_dates}")

    # Determine today's date and create empty list for any future dates
    today = datetime.now().date()
    future_dates = []
    old_dates = []

    # Parse dates to see if any are past the current date
    for filename, date_str in applied_dates.items():
        try:
            parsed = datetime.strptime(date_str, "%m-%d-%y").date()
            if parsed > today:
                future_dates.append((filename, date_str))
            elif (today - parsed).days > 365:
                old_dates.append((filename, date_str))
        except ValueError:
            logging.warning(f"Could not parse date '{date_str}' for {filename}")

    # Return early if dialogs are not shown
    if not show_dialogs:
        return changes, applied_dates

    # Display a messagebox
    if changes == 0 and force:
        QMessageBox.information(
            globs.window,
            "Nothing to Do",
            "Files already properly named or no matches found in file contents.",
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok
        )
    elif future_dates and old_dates and force:
        QMessageBox.information(
            globs.window,
            "Complete!",
            f"Auto-Name Complete! Updated {changes} file(s).\nCaution: {len(future_dates)} files have dates later than today's date and {len(old_dates)} files have dates more than a year old.\nIt might be a good idea to check if these are correct!",
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok
        )
    elif future_dates and force:
        QMessageBox.information(
            globs.window,
            "Complete!",
            f"Auto-Name Complete! Updated {changes} file(s).\nCaution: {len(future_dates)} files have dates later than today's date.\nIt might be a good idea to check if these are correct!",
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok
        )
    elif old_dates and force:
        QMessageBox.information(
            globs.window,
            "Complete!",
            f"Auto-Name Complete! Updated {changes} file(s).\nCaution: {len(old_dates)} files have dates more than a year old.\nIt might be a good idea to check if these are correct!",
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok
        )
    else:
        if force:
            QMessageBox.information(
                globs.window,
                "Complete!",
                f"Auto-Name Complete! Updated {changes} file(s).",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )

    return changes, applied_dates
