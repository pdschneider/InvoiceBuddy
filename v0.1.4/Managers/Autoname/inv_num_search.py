# Managers/Autoname/inv_num_search.py
import re, os, logging
from Managers.Autoname.search_helpers import extract_normalized_text

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
        r'order\s*#?\s*:\s*([a-z0-9]{8,30})',
        r'(?:invoice|inv)\s*(?:no\.?|number|#)\s*[:#]?\s*([a-z0-9\-_]{3,20})',
        r'invoice\s+no?\.?\s*[:#]?\s*([a-z0-9\-_]+)',
        r'\binvoice\s*(?:nbr\.?|no\.?|number|#)?\s*[:.]?\s*([0-9]{4,})',
        r'\binv(?:oice)?\b\s*(?:no\.?|number|#|[:#])?\s*([0-9]{3,})',
        r'(?:trans(?:action)?\s*#?\s*[:#]?\s*)([0-9]{8,12})\b',
        r'invoice\s+number\s*[:#]?\s*([a-z0-9\-_]+)',
        r'\b(?:transaction|txn|trans)\b\s*(?:number|#|no\.?|id)?\s*[:#.]?\s*(\d{12,18})\b(?!\s*[/-]\d)',
        r'order\s+number\s*[:#]?\s*([0-9]+)',
        r'invoice\s*#?\s*wa\s*\d{5}\s*(?:\d{1,2}/\d{1,2}/\d{4}|\d{2}/\d{2}/\d{4})?\s*(\d{3,})\b',
        r'(?:order\s*(?:id|number|#)?\s*[:=]?\s*)([0-9]{10,16}(?:-\d+)+)\b',
        r'(?s)\b(\d{6,8})\b(?!\s*[/-]\d{1,2})',
        r'invoice\s*[:#]?\s*(\d{4,}[a-z0-9\-_]*)',
        r'order\s+id\s*[:#]?\s*([a-z0-9]+)',
        r'order\s*#?\s*([0-9]+)',
        r'(?<![\d/])(?<!\d{2}-\d{2})(?<!\d{2}/\d{2})(?<!\d{5}\s)\b(\d{6,8})\b(?!\s*-?\s*\d{2})',
        r'\b(\d{6,8})\b(?![-/]\d)',
        r'sales\s+slip\s*#?\s*[:#]?\s*(\d{4,10})\b',
        r'(?:your\s+)?order\s+(?:number|no\.?|id|#)\s*(?:is|:|was|=)?\s*([a-z]{1,4}\d{5,12})\b',
        r'(?:order\s+)?vs\s*([a-zA-Z]?\d{6,10})\b',
        r'(?:id\s*#?\s*|order\s+id\s*[:#]?\s*)([a-f0-9]{20,32})\b',
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

            logging.debug(f"Contains 'order number': {'order number' in normalized}")

            invoice = None
            matched_inv = None
            matched_pattern = None
            for pattern in triggers:
                match = re.search(pattern, normalized)
                if match:
                    candidate = match.group(1).strip().upper()
                    logging.info(f"Pattern matched: {pattern} → candidate: {candidate}")
                    if re.match(r'^[A-Z0-9\-_]{2,20}$', candidate):
                        invoice = candidate
                        matched_inv = match.group(0)
                        matched_pattern = pattern
                        break

            if invoice:
                logging.info(f"Final invoice for {filename}: {invoice} from pattern: {matched_pattern}")
            else:
                logging.info(f"No valid invoice found for {filename} - checked all patterns")

            results[filename] = (invoice, matched_inv) if invoice else None

        logging.info(f"Invoice number search results: {results}")
        return results

    except Exception as e:
        logging.error(f"Error in invoice_number_search: {e}")
        return {}
