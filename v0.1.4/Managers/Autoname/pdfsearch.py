# Managers/pdfsearch.py
import re, logging, os
from Utils.load_settings import load_company_map
from Managers.Autoname.search_helpers import extract_normalized_text, normalize_text, write_pdf_metadata, get_field_order, date_patterns
from Managers.Autoname.company_search import company_search
from Managers.Autoname.date_search import date_search
from Managers.Autoname.inv_num_search import invoice_number_search
from Managers.Autoname.card_num_search import card_number_search
from pypdf import PdfReader

def apply_auto_naming(globals, directory, file_list=None):
    """
    Master auto-namer: extracts text once per file,
    calls company/date/invoice searches sequentially,
    scrubs matches from normalized text between calls,
    and renames based on progressive logic.
    """
    # Return if no files are sent
    if not file_list:
        return 0
    
    # Create metadata dictionary
    metadata_to_write = {}

    search_dir = os.path.normpath(directory)
    if not os.path.isdir(search_dir):
        logging.error(f"Invalid directory: {search_dir}")
        return 0

    # Extract normalized texts once for all files (batch optimization)
    normalized_texts = {}
    for full_path in file_list:
        if not os.path.isfile(full_path):
            continue
        filename = os.path.basename(full_path)
        normalized = extract_normalized_text(full_path)
        normalized_texts[filename] = normalized

        logging.debug(f"Normalized text length: {len(normalized)}\n")
        logging.debug(f"\nCurrent Normalized Text: {normalized}\n")

    if not normalized_texts:
        return 0

    # Step 1: Search for companies (always, no skips)
    company_results = company_search(directory=search_dir, file_list=file_list, normalized_texts=normalized_texts)

    # Step 2: Apply company results, build initial new_parts, scrub if applied
    renamed = 0
    valid_companies = {normalize_text(c) for c in load_company_map().values()}  # For checking existing

    for full_path in file_list:
        filename = os.path.basename(full_path)
        if filename not in normalized_texts:
            continue

        # Check the identity
        identity = "Invoice"  # default fallback

        try:
            reader = PdfReader(full_path)
            if reader.metadata and "/Identity" in reader.metadata:
                identity = reader.metadata["/Identity"]
                logging.info(f"Identity read from metadata for {filename}: {identity}")
            else:
                logging.debug(f"No /Identity metadata found for {filename}, using default 'Invoice'")
        except Exception as e:
            logging.warning(f"Could not read /Identity from {filename}: {e}, using default 'Invoice'")

        # Pick apart base name from filename
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split()
        logging.info(f"Processing: {filename}")
        logging.info(f"  Original parts: {parts}")

        new_parts = parts[:]

        # Apply company if found and different/missing
        company_result = company_results.get(filename)
        if company_result:
            company, matched, keyword_tuple = company_result
            norm_company = normalize_text(company)
            if not parts or normalize_text(parts[0]) != norm_company:
                if norm_company in valid_companies:  # Safety check
                    new_parts = [company.capitalize()]
                    logging.info(f"  Applied company: {company}")

                    # Scrub all keywords from the text
                    for kw in keyword_tuple:
                        if kw.lower() in ['llc', 'inc']: continue
                        normalized_kw = normalize_text(kw)
                        if normalized_kw:
                            new_text = re.sub(
                                rf'\b{re.escape(normalized_kw)}\b', 
                                '', 
                                normalized_texts[filename])

                            if new_text != normalized_texts[filename]:
                                normalized_texts[filename] = new_text
                                logging.debug(f"  Scrubbed matched company keyword: {normalized_kw}")
                                logging.debug(f"\nCurrent Normalized Text: {normalized_texts[filename]}\n")
                                logging.debug(f"Normalized text length: {len(normalized_texts[filename])}\n")

        # Step 3: Now search for dates using updated texts
        date_results = date_search(directory=search_dir, file_list=file_list, normalized_texts=normalized_texts)

        # Apply date if we have exactly company so far
        if len(new_parts) == 1:
            date_result = date_results.get(filename)
            if date_result:
                date, matched = date_result
                new_parts.append(date)
                logging.info(f"  Applied date: {date}")

                old_length = len(normalized_texts[filename])

                # 1. Scrub the single matched date we used for naming (as before)
                if matched:
                    new_text = re.sub(rf'\b{re.escape(matched)}\b', '', normalized_texts[filename])
                    if new_text != normalized_texts[filename]:
                        normalized_texts[filename] = new_text
                        logging.debug(f"  Scrubbed matched date: {matched}")
                        logging.debug(f"  Length: {old_length} → {len(normalized_texts[filename])}")

                # 2. Exhaustively scrub ALL possible dates using all patterns
                scrubbed_any = False
                for pattern, _ in date_patterns:  # date_patterns must be in scope — see below
                    new_text = re.sub(pattern, ' ', normalized_texts[filename])  # replace with space to avoid merging words
                    if new_text != normalized_texts[filename]:
                        normalized_texts[filename] = new_text.strip()  # clean up extra spaces
                        logging.debug(f"  Scrubbed additional dates with pattern: {pattern}")
                        scrubbed_any = True

                if scrubbed_any:
                    logging.debug(f"\nCurrent Normalized Text after all date scrubs:\n{normalized_texts[filename]}\n")
                    logging.debug(f"Normalized text length after date scrubs: {len(normalized_texts[filename])}\n")

        # Step 4: Now search for invoices using updated texts
        invoice_results = invoice_number_search(directory=search_dir, file_list=file_list, normalized_texts=normalized_texts)

        # Apply invoice if we have exactly company + date
        if len(new_parts) == 2:
            invoice_result = invoice_results.get(filename)
            if invoice_result:
                invoice, matched = invoice_result
                new_parts.append(invoice)
                logging.info(f"  Applied invoice: {invoice}")
                if matched:
                    normalized_texts[filename] = re.sub(rf'\b{re.escape(matched)}\b', '', normalized_texts[filename])
                    logging.debug(f"  Scrubbed matched invoice: {matched}")

                    logging.debug(f"\nCurrent Normalized Text: {normalized_texts[filename]}\n")
                    logging.debug(f"Normalized text length: {len(normalized_texts[filename])}\n")

        # Step 5: Search for the last 4 digits of a card number if present
        card_results = card_number_search(directory=search_dir, file_list=file_list, normalized_texts=normalized_texts)

        # Get user-defined field order based on the file's Identity
        order = get_field_order(globals, identity, filename)

        # Map field names to their extracted values (only if found)
        available = {}
        if company_result:
            available["Company"] = company_result[0].strip()
        if date_results.get(filename) and date_results[filename][0]:
            available["Date"] = date_results[filename][0]
        if invoice_results.get(filename) and invoice_results[filename][0]:
            available["Invoice #"] = invoice_results[filename][0]
        if card_results.get(filename) and card_results[filename][0]:
            available["Card Number"] = card_results[filename][0]

        # Build new_parts using the user-chosen order
        # Skip any field that is empty ("") or not found
        new_parts = []
        for field in order:
            if field and field in available:
                new_parts.append(available[field])

        # If nothing new or same as original → skip rename/metadata
        if not new_parts or " ".join(new_parts) == " ".join(parts):
            logging.info(f"No changes needed for {filename}")
            continue

        new_base = " ".join(new_parts)
        new_name = new_base + ".pdf"
        new_path = os.path.join(search_dir, new_name)

        # Handle duplicates
        counter = 1
        while os.path.exists(new_path) and new_path != full_path:
            new_name = f"{new_base} ({counter}).pdf"
            new_path = os.path.join(search_dir, new_name)
            counter += 1

        # Build metadata using the same ordered values
        meta = {}
        for field in order:
            if field and field in available:
                # Normalize key (e.g. "Invoice #" → "/InvoiceNumber")
                key = f"/{field.replace(' #', 'Number').replace(' ', '')}"
                meta[key] = available[field]

        if "Card Number" in available:
            meta["/CardNumber"] = available["Card Number"]

        if meta:
            metadata_to_write[filename] = meta
            logging.debug(f"Metadata prepared for {filename}: {meta}")

        # Write metadata before rename (still using old filename)
        if filename in metadata_to_write:
            write_pdf_metadata({filename: metadata_to_write[filename]}, search_dir)
            del metadata_to_write[filename]

        # Finally rename
        try:
            os.rename(full_path, new_path)
            logging.info(f"Auto-named: {filename} → {new_name}")
            renamed += 1
        except Exception as e:
            logging.error(f"Rename failed for {filename}: {e}")

    logging.info(f"Total renamed: {renamed}")

    return renamed
