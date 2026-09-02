# src/managers/autoname/inv_num_search.py
import re
import os
import logging
from src.managers.autoname.search_helpers import extract_normalized_text


def invoice_number_search(directory=None, file_list=None, normalized_texts=None):
    """
    Returns dict: {original_filename: (inv_str, matched_inv) or None}
    Always searches regardless of current filename.
    Does NOT rename.
    """
    if not file_list:
        return {}

    search_dir = directory.strip() if directory else None

    # Patterns adjusted for lowercase text (no IGNORECASE)
    triggers = [

        # 1: Finds the word 'order' followed by an optional '#', a colon ':', then 8-30 lowercase letters or digits
        r'order\s*#?\s*:\s*([a-z0-9]{8,30})',

        # 2: Finds 'invoice' or 'inv', then 'no', 'no.', 'number', or '#', an optional colon ':' or hash '#',
        # then 3-20 lowercase letters, digits, hyphens, or underscores
        r'(?:invoice|inv)\s*(?:no\.?|number|#)\s*[:#]?\s*([a-z0-9\-_]{3,20})',

        # 3: Finds 'invoice' followed by whitespace, then optionally 'no' or 'no.', an optional colon or hash,
        # and captures 1+ lowercase letters, digits, hyphens, and underscores with no lenth limit
        r'invoice\s+no?\.?\s*[:#]?\s*([a-z0-9\-_]+)',

        # 4: Finds 'invoice' (word boundary enforced) then an optional label 'nbr', 'nbr.', 'no', 'no.',
        # 'number', or '#', then an optional ':' or '.' and 4 or more numerical digits
        r'\binvoice\s*(?:nbr\.?|no\.?|number|#)?\s*[:.]?\s*([0-9]{4,})',

        # 5: Finds 'inv' or 'invoice' (word boundary enforced), an optional label 'no', 'no.', 'number', '#', ':',
        # or a combination of '#' and ':', then captures 3 or more numerical digits
        r'\binv(?:oice)?\b\s*(?:no\.?|number|#|[:#])?\s*([0-9]{3,})',

        # 6: Finds 'trans' or 'transaction' followed by an optional '#', then an optional ':' or '#', and
        # captures 8-12 digits followed by a word boundary
        r'(?:trans(?:action)?\s*#?\s*[:#]?\s*)([0-9]{8,12})\b',

        # 7: Finds 'invoice' followed by whitespace, then the literal word 'number', an optional ':' or '#',
        # and captures 1+ lowercase letters, digits, hyphens, or underscores with no length limit
        r'invoice\s+number\s*[:#]?\s*([a-z0-9\-_]+)',

        # 8: Finds 'transaction', 'txn', or 'trans' (word boundary enforced), then an optional 'number', '#',
        # 'no', 'no.', or 'id', an optional separator (colon, hash, or period), and captures 12-18 digits
        # not followed by a slash and then more digits, protecting against matching dates
        r'\b(?:transaction|txn|trans)\b\s*(?:number|#|no\.?|id)?\s*[:#.]?\s*(\d{12,18})\b(?!\s*[/-]\d)',

        # 9: Finds 'order' followed by whitespace, the literal word 'number', an optional colon or hash, then
        # captures 1+ digits with no minimum or maximum length
        r'order\s+number\s*[:#]?\s*([0-9]+)',

        # 10: Finds 'invoice' with an optional '#', the letters 'wa', then exactly 5 digits, then an optional date
        # pattern in M/D/YYYY or MM/DD/YYYY format, and finally captures 3 or more digits at a word boundary
        r'invoice\s*#?\s*wa\s*\d{5}\s*(?:\d{1,2}/\d{1,2}/\d{4}|\d{2}/\d{2}/\d{4})?\s*(\d{3,})\b',

        # 11: Finds 'order' with an optional label 'id', 'number', or '#', an optional colon or equals sign, then
        # captures 10-16 digits followed by one or more hyphen-separated digit groups
        r'(?:order\s*(?:id|number|#)?\s*[:=]?\s*)([0-9]{10,16}(?:-\d+)+)\b',

        # 12: Captures a standalone 6-8 digit number if not preceded by another digit or a slash, DD-DD pattern,
        # DD/DD pattern, or 5 digits followed by a space, and isn't followed by a hyphen and 2 digits
        r'(?<![\d/])(?<!\d{2}-\d{2})(?<!\d{2}/\d{2})(?<!\d{5}\s)\b(\d{6,8})\b(?!\s*-?\s*\d{2})',

        # 13: Captures any standlone 6-8 digit number (word boundary on both sides) as long as it is not
        # immediately followed by a slash or hyphen and then 1-2 digits
        r'(?s)\b(\d{6,8})\b(?!\s*[/-]\d{1,2})',

        # 14: Finds 'invoice', an optional colon or hash, and captures a sequence that starts with 4 or more digits,
        # optionally followed by any number of lowercase letters, digits, hyphens, or underscores
        r'invoice\s*[:#]?\s*(\d{4,}[a-z0-9\-_]*)',

        # 15: Finds 'order' followed by whitespace, then 'id', an optional colon or hash, and captures 1+ lowercase
        # letters or digits with no hyphens or underscores allowed and no length limit
        r'order\s+id\s*[:#]?\s*([a-z0-9]{4,})',

        # 16: Finds 'order' and an optional '#', then captures 2+ digits
        r'order\s*#?\s*([0-9]{2,})',

        # 17: Captures a standalone 6-8 digit number (word boundaries enforced) as long as it is not followed by a
        # hyphen or a slash and another digit
        r'\b(\d{6,8})\b(?![-/]\d)',

        # 18: Finds 'sales slip', an optional '#', an optional ':' or '#', and captures 4-10 digits at a word boundary
        r'sales\s+slip\s*#?\s*[:#]?\s*(\d{4,10})\b',

        # 19: Optionally starts with 'your', then look for 'order' followed by whitespace, then 'number', 'no', 'no.',
        # 'id', or '#', then an optional 'is', ':', 'was', or '=', and captures 1-4 lowercase letters followed
        # by 5-12 digits
        r'(?:your\s+)?order\s+(?:number|no\.?|id|#)\s*(?:is|:|was|=)?\s*([a-z]{1,4}\d{5,12})\b',

        # 20: Optionally starts with 'order', then 'vs' an captures an optional single letter (upper or lowercase),
        # followed by 6-10 digits and a word boundary
        r'(?:order\s+)?vs\s*([a-zA-Z]?\d{6,10})\b',

        # 21: Finds 'id' with an optional '#', or 'order id' with an optional ':' or '#', then captures 20-32
        # hexidecimal characters (digits 0-9 and letters a-f only) at a word boundary
        r'(?:id\s*#?\s*|order\s+id\s*[:#]?\s*)([a-f0-9]{20,32})\b',

        # 22: Finds 'receipt' with an optional '#', 'no', 'no.', or 'number', an optional ':' or '#', and captures
        # either a 4-8 digit number or one optionally prefixed with '#' or '-', and optionally followed by a
        # hyphenated 4-digit number
        r'(?:receipt\s*(?:#|no\.?|number)?\s*[:#]?\s*)([#-]?\d{4,8}(?:-\d{4})?)\b'
    ]

    try:
        if search_dir and not os.path.isdir(search_dir):
            logging.error(f"Invalid directory: {search_dir}")
            return {}

        filenames = [os.path.basename(f) for f in file_list]

        results = {}

        for filename in filenames:
            full_path = os.path.join(search_dir, filename) if search_dir else None
            if full_path and not os.path.isfile(full_path):
                results[filename] = None
                continue

            if normalized_texts and filename in normalized_texts:
                normalized = normalized_texts[filename]
            else:
                if not full_path:
                    results[filename] = None
                    continue
                normalized = extract_normalized_text(full_path)

            if not normalized:
                results[filename] = None
                continue

            logging.debug(
                f"Contains 'order number': {'order number' in normalized}")

            invoice = None
            matched_inv = None
            matched_pattern = None
            for pattern in triggers:
                match = re.search(pattern, normalized)

                # Skip if match is invalid
                if match:
                    invalid_matches = ["date", "nbr", "net"]
                    if match.group(1).strip().lower() in invalid_matches:
                        logging.debug(f"Skipping invalid match: {match.group(1)}")
                        match = None

                if match:
                    candidate = match.group(1).strip().upper()
                    logging.info(
                        f"Pattern matched: {pattern} becomes candidate: {candidate}")
                    if re.match(r'^[A-Z0-9\-_]{2,20}$', candidate):
                        invoice = candidate
                        matched_inv = match.group(0)
                        matched_pattern = pattern
                        break

            if invoice:
                logging.info(
                    f"Final invoice for {filename}: {invoice} from pattern: {matched_pattern}")
            else:
                logging.info(
                    f"No valid invoice found for {filename} - checked all patterns")

            results[filename] = (invoice, matched_inv) if invoice else None

        logging.info(f"Invoice number search results: {results}")
        return results

    except Exception as e:
        logging.error(f"Error in invoice_number_search: {e}")
        return {}
