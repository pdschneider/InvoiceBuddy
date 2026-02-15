# Managers/pdfsearch.py
import pdfplumber, re, logging, os
from Utils.load_settings import load_company_map
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("OCR libraries (pdf2image/pytesseract) not found. Fallback disabled.")

def normalize_text(text):
    """Normalize text by removing commas, extra spaces, and converting to lowercase."""
    text = text.replace(',', '')  #  Remove commas
    return ' '.join(text.split()).lower() #  Returns normalized text

def extract_text_with_ocr(full_path):
    """Fallback OCR: Convert PDF to images and extract text page-by-page."""
    if not OCR_AVAILABLE:
        logging.warning(f"OCR not available for {full_path}. Skipping fallback.")
        return ""
    try:
        images = convert_from_path(full_path)  #  Convert PDF to list of images
        full_text = ""
        for image in images:
            text = pytesseract.image_to_string(image)
            if text.strip():  #  If text found, append and continue
                full_text += text + " "
        logging.debug(f"Full PDF text with OCR: {full_text}")
        return full_text
    except Exception as e:
        logging.error(f"OCR error on {full_path}: {e}")
        return ""

def company_search(companies=None, directory=None, file_list=None):
    """
    Returns dict: {original_filename: "SuggestedCompany.pdf" or None}
    Skips if file already starts with a known company.
    Does NOT rename.
    """
    if not file_list:
        return {}

    company_map = load_company_map()
    search_companies = companies if companies else list(company_map.values())
    valid_companies = {normalize_text(c) for c in search_companies}

    search_dir = directory.strip()

    try:
        if not os.path.isdir(search_dir):
            logging.error(f"Invalid directory: {search_dir}")
            return {}

        logging.info(f"Processing {len(file_list)} selected PDF files for company name")

        filenames = [os.path.basename(f) for f in file_list]

        results = {}

        for filename in filenames:
            full_path = os.path.join(search_dir, filename)
            if not os.path.isfile(full_path):
                results[filename] = None
                continue

            base_name = os.path.splitext(filename)[0]
            parts = base_name.split()

            # Skip if already starts with known company
            if parts and normalize_text(parts[0]) in valid_companies:
                results[filename] = None
                continue

            text = ""
            try:
                with pdfplumber.open(full_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text
                        if len(text) > 5000:
                            break
            except Exception as e:
                logging.warning(f"pdfplumber failed on {filename}: {e}")

            if not text.strip():
                text = extract_text_with_ocr(full_path)
                logging.debug(f"Full PDF text with OCR: {text}")
            
            def get_company_from_keywords(text):
                """Search text for any company keyword and return the company name if found."""
                if not text:
                    return None

                normalized = normalize_text(text)

                for keyword_tuple, company in company_map.items():
                    for keyword in keyword_tuple:
                        if keyword.lower() in ['llc', 'inc']:
                            continue
                        normalized_keyword = normalize_text(keyword)
                        if re.search(rf'\b{re.escape(normalized_keyword)}\b', normalized):
                            return company

                return None

            company = get_company_from_keywords(text)
            if company:
                suggested = f"{company.capitalize()}.pdf"
                # Handle duplicates
                counter = 0
                test = suggested
                while os.path.exists(os.path.join(search_dir, test)):
                    counter += 1
                    test = f"{company.capitalize()} {counter}.pdf"
                results[filename] = test
            else:
                results[filename] = None

        logging.info(f"Company search results: {results}")
        return results

    except Exception as e:
        logging.error(f"Error in company_search: {e}")
        return {}

def date_search(companies=None, directory=None, file_list=None):
    """
    Returns dict: {original_filename: "MM-DD-YY" or None}
    Only suggests date if filename has exactly one word and it's a known company.
    Does NOT rename.
    """
    if not file_list:
        return {}

    company_map = load_company_map()
    search_companies = companies if companies else list(company_map.values())
    valid_companies = {normalize_text(c) for c in search_companies}

    search_dir = directory.strip()

    month_map = {
        'jan': '01', 'january': '01', 'feb': '02', 'february': '02',
        'mar': '03', 'march': '03', 'apr': '04', 'april': '04',
        'may': '05', 'jun': '06', 'june': '06', 'jul': '07', 'july': '07',
        'aug': '08', 'august': '08', 'sep': '09', 'september': '09',
        'oct': '10', 'october': '10', 'nov': '11', 'november': '11',
        'dec': '12', 'december': '12'
    }

    date_patterns = [
            (r'\b(\d{4})-(\d{2})-(\d{2})\b', lambda m: f"{m.group(2)}-{m.group(3)}-{m.group(1)[-2:]}"),
            (r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', lambda m: f"{m.group(1).zfill(2)}-{m.group(2).zfill(2)}-{m.group(3)[-2:]}"),
            (r'\b(\d{2})-([A-Za-z]{3})-(\d{4})\b', lambda m: f"{month_map.get(m.group(2).lower(), '')}-{m.group(1)}-{m.group(3)[-2:]}" if month_map.get(m.group(2).lower()) else None),
            (r'\b(\d{1,2})\.(\d{1,2})\.(\d{2})\b', lambda m: f"{m.group(1).zfill(2)}-{m.group(2).zfill(2)}-{m.group(3)}"),
            (r'\b([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})\b', lambda m: f"{month_map.get(m.group(1).lower(), '')}-{m.group(2).zfill(2)}-{m.group(3)[-2:]}" if month_map.get(m.group(1).lower()) else None),
            (r'\b([A-Za-z]+)\s+(\d{1,2})\s+(\d{4})\b', lambda m: f"{month_map.get(m.group(1).lower(), '')}-{m.group(2).zfill(2)}-{m.group(3)[-2:]}" if month_map.get(m.group(1).lower()) else None),
            (r'\b([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?\s*,?\s*(\d{4})\b', lambda m: f"{month_map.get(m.group(1).lower(), '')}-{m.group(2).zfill(2)}-{m.group(3)[-2:]}" if month_map.get(m.group(1).lower()) else None),
            (r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b', lambda m: f"{m.group(1).zfill(2)}-{m.group(2).zfill(2)}-{m.group(3).zfill(4)[-2:]}"),
        ]

    try:
        if not os.path.isdir(search_dir):
            logging.error(f"Invalid directory: {search_dir}")
            return {}

        results = {}

        for full_path in file_list:
            filename = os.path.basename(full_path)
            base_name = os.path.splitext(filename)[0]
            parts = base_name.split()

            # Only if exactly one word and it's a known company
            if len(parts) != 1 or normalize_text(parts[0]) not in valid_companies:
                results[filename] = None
                continue

            text = ""
            try:
                with pdfplumber.open(full_path) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text() or ""
                        text += t + " "
            except Exception as e:
                logging.warning(f"pdfplumber failed on {filename}: {e}")

            if not text.strip():
                text = extract_text_with_ocr(full_path)

            normalized = normalize_text(text)
            found = None
            for pattern, formatter in date_patterns:
                match = re.search(pattern, normalized, re.IGNORECASE)
                if match:
                    formatted = formatter(match)
                    if formatted and formatted.count('-') == 2:
                        found = formatted
                        break

            results[filename] = found

        logging.info(f"Date search results: {results}")
        return results

    except Exception as e:
        logging.error(f"Error in date_search: {e}")
        return {}

def invoice_number_search(directory, file_list=None):
    """
    Returns dict: {original_filename: "INV12345" or None}
    Only suggests if filename has exactly two words: Company MM-DD-YY
    Does NOT rename.
    """
    if not file_list:
        return {}

    search_dir = directory.strip()

    triggers = [
    # Looks for "order #:" or "order:" followed by a long alphanumeric code (8–30 chars)
    r'order\s*#?\s*:\s*([A-Za-z0-9]{8,30})',

    # Matches "invoice" or "inv" followed by optional "no.", "number", "#", then captures the next identifier
    r'(?:invoice|inv)\s*(?:no\.?|number|#)\s*[:#]?\s*([A-Za-z0-9\-_]{3,20})',

    # Catches "invoice no." (with optional period) followed by any short alphanumeric code
    r'invoice\s+no?\.?\s*[:#]?\s*([A-Za-z0-9\-_]+)',

    # Specifically targets "invoice" followed by "nbr.", "no.", "number", or "#", then a number
    # Handles cases like "Invoice Nbr.: 009660" — requires at least 4 digits
    r'\binvoice\s*(?:nbr\.?|no\.?|number|#)?\s*[:.]?\s*([0-9]{4,})',

    # Strong pattern for "inv" or "invoice" (whole word) with optional label, captures pure numbers (3+ digits)
    # Reliable for most clean "Invoice # 12345" or "Inv 678" formats
    r'\binv(?:oice)?\b\s*(?:no\.?|number|#|[:#])?\s*([0-9]{3,})',

    # Matches "invoice number" followed by any alphanumeric code
    r'invoice\s+number\s*[:#]?\s*([A-Za-z0-9\-_]+)',

    # Looks for "order number" followed by digits only
    r'order\s+number\s*[:#]?\s*([0-9]+)',

    # Looks for "invoice #" or just "invoice" followed by a number, skips a date if present, and captures
    # only a number 3 digits or more while ignoring "wa" and zip codes
    r'invoice\s*#?\s*wa\s*\d{5}\s*(?:\d{1,2}/\d{1,2}/\d{4}|\d{2}/\d{2}/\d{4})?\s*(\d{3,})\b',

    # Fallback: finds the first standalone 6–8 digit number anywhere in the document
    r'(?s)\b(\d{6,8})\b(?!\s*[/-]\d{1,2})',

    # Catches "invoice" optionally followed by ":" or "#", then a number (at least 4 digits)
    r'invoice\s*[:#]?\s*(\d{4,}[A-Za-z0-9\-_]*)',

    # Looks for "order id" followed by alphanumeric code
    r'order\s+id\s*[:#]?\s*([A-Za-z0-9]+)',

    # Catches "order #" followed by digits only
    r'order\s*#?\s*([0-9]+)',

    # Very cautious fallback: 6–8 digit number not looking like a date or zip
    # Tries to avoid obvious false positives like partial dates or postal codes
    r'(?<![\d/])(?<!\d{2}-\d{2})(?<!\d{2}/\d{2})(?<!\d{5}\s)\b(\d{6,8})\b(?!\s*-?\s*\d{2})',

    # Last-resort fallback: any standalone 6–8 digit number not followed by date-like pattern
    r'\b(\d{6,8})\b(?![-/]\d)'
]

    results = {}

    for full_path in file_list:
        filename = os.path.basename(full_path)
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split()

        # Only if exactly two parts and second is date
        if len(parts) != 2 or not re.match(r'^\d{2}-\d{2}-\d{2}$', parts[1]):
            results[filename] = None
            continue

        text = ""
        try:
            with pdfplumber.open(full_path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    text += t + "\n"
        except Exception:
            pass

        if not text.strip():
            text = extract_text_with_ocr(full_path)

        if not text.strip():
            results[filename] = None
            continue

        normalized = normalize_text(text)
        logging.info(f"Normalized text length: {len(normalized)} | Contains 'order number': {'order number' in normalized}")
        invoice = None
        for pattern in triggers:
            match = re.search(pattern, normalized, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip().upper()
                logging.info(f"Pattern matched: {pattern} → candidate: {candidate}")
                if re.match(r'^[A-Z0-9\-_]{2,20}$', candidate):
                    invoice = candidate
                    matched_pattern = pattern
                    break
        if invoice:
            logging.info(f"Final invoice: {invoice} from pattern: {matched_pattern}")
        else:
            logging.info("No valid invoice found - checked all patterns")
        results[filename] = invoice

    logging.info(f"Invoice number search results: {results}")
    return results

def apply_auto_naming(directory, file_list=None):
    """
    Master auto-namer: extracts text once from the real file,
    applies company → date → invoice all from the same text.
    Renames only once at the end.
    """
    if not file_list:
        return 0

    search_dir = directory.strip()
    if not os.path.isdir(search_dir):
        logging.error(f"Invalid directory: {search_dir}")
        return 0

    renamed = 0

    for full_path in file_list:
        filename = os.path.basename(full_path)
        base = os.path.splitext(filename)[0]
        parts = base.split()
        logging.info(f"Processing: {filename}")
        logging.info(f"  Original parts: {parts}")

        # Extract text ONCE from the actual current file
        text = ""
        try:
            with pdfplumber.open(full_path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    logging.debug(f"Full PDF text: {t}")
                    text += t + " "
        except Exception:
            text = extract_text_with_ocr(full_path)
            logging.debug(f"Full PDF text with OCR: {text}")

        if not text.strip():
            text = extract_text_with_ocr(full_path)
            logging.warning(f"No matches found in extracted text from {filename} — skipping")
            logging.debug(f"Full file contents with OCR: {text}")

        normalized = normalize_text(text)
        logging.debug(f"Normalized Text: \n{normalized}\n")

        new_parts = parts[:]

        # 1. Try to find company (even if filename already looks good)
        company = None
        for keyword_tuple, comp in load_company_map().items():
            for kw in keyword_tuple:
                if kw.lower() in ['llc', 'inc']: continue
                if re.search(rf'\b{re.escape(normalize_text(kw))}\b', normalized):
                    company = comp
                    break
            if company: break

        if company and (not parts or normalize_text(parts[0]) != normalize_text(company)):
            new_parts = [company.capitalize()]

        month_map = {
            'jan': '01', 'january': '01', 'feb': '02', 'february': '02',
            'mar': '03', 'march': '03', 'apr': '04', 'april': '04',
            'may': '05', 'jun': '06', 'june': '06', 'jul': '07', 'july': '07',
            'aug': '08', 'august': '08', 'sep': '09', 'september': '09',
            'oct': '10', 'october': '10', 'nov': '11', 'november': '11',
            'dec': '12', 'december': '12'
        }

        date_patterns = [
            (r'\b(\d{4})-(\d{2})-(\d{2})\b', lambda m: f"{m.group(2)}-{m.group(3)}-{m.group(1)[-2:]}"),
            (r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', lambda m: f"{m.group(1).zfill(2)}-{m.group(2).zfill(2)}-{m.group(3)[-2:]}"),
            (r'\b(\d{2})-([A-Za-z]{3})-(\d{4})\b', lambda m: f"{month_map.get(m.group(2).lower(), '')}-{m.group(1)}-{m.group(3)[-2:]}" if month_map.get(m.group(2).lower()) else None),
            (r'\b(\d{1,2})\.(\d{1,2})\.(\d{2})\b', lambda m: f"{m.group(1).zfill(2)}-{m.group(2).zfill(2)}-{m.group(3)}"),
            (r'\b([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})\b', lambda m: f"{month_map.get(m.group(1).lower(), '')}-{m.group(2).zfill(2)}-{m.group(3)[-2:]}" if month_map.get(m.group(1).lower()) else None),
            (r'\b([A-Za-z]+)\s+(\d{1,2})\s+(\d{4})\b', lambda m: f"{month_map.get(m.group(1).lower(), '')}-{m.group(2).zfill(2)}-{m.group(3)[-2:]}" if month_map.get(m.group(1).lower()) else None),
            (r'\b([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?\s*,?\s*(\d{4})\b', lambda m: f"{month_map.get(m.group(1).lower(), '')}-{m.group(2).zfill(2)}-{m.group(3)[-2:]}" if month_map.get(m.group(1).lower()) else None),
            (r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b', lambda m: f"{m.group(1).zfill(2)}-{m.group(2).zfill(2)}-{m.group(3).zfill(4)[-2:]}"),
        ]

        # 2. Try to find date
        date = None
        for pattern, formatter in date_patterns:  # reuse your date_patterns from date_search
            match = re.search(pattern, normalized, re.IGNORECASE)
            if match:
                formatted = formatter(match)
                if formatted and formatted.count('-') == 2:
                    date = formatted
                    break

        if date and len(new_parts) == 1:  # only add if we have company
            new_parts.append(date)

        # 3. Try to find invoice number
        invoice = None

        triggers = [
    # Looks for "order #:" or "order:" followed by a long alphanumeric code (8–30 chars)
    r'order\s*#?\s*:\s*([A-Za-z0-9]{8,30})',

    # Matches "invoice" or "inv" followed by optional "no.", "number", "#", then captures the next identifier
    r'(?:invoice|inv)\s*(?:no\.?|number|#)\s*[:#]?\s*([A-Za-z0-9\-_]{3,20})',

    # Catches "invoice no." (with optional period) followed by any short alphanumeric code
    r'invoice\s+no?\.?\s*[:#]?\s*([A-Za-z0-9\-_]+)',

    # Specifically targets "invoice" followed by "nbr.", "no.", "number", or "#", then a number
    # Handles cases like "Invoice Nbr.: 009660" — requires at least 4 digits
    r'\binvoice\s*(?:nbr\.?|no\.?|number|#)?\s*[:.]?\s*([0-9]{4,})',

    # Strong pattern for "inv" or "invoice" (whole word) with optional label, captures pure numbers (3+ digits)
    # Reliable for most clean "Invoice # 12345" or "Inv 678" formats
    r'\binv(?:oice)?\b\s*(?:no\.?|number|#|[:#])?\s*([0-9]{3,})',

    # Matches "invoice number" followed by any alphanumeric code
    r'invoice\s+number\s*[:#]?\s*([A-Za-z0-9\-_]+)',

    # Looks for "order number" followed by digits only
    r'order\s+number\s*[:#]?\s*([0-9]+)',

    # Looks for "invoice #" or just "invoice" followed by a number, skips a date if present, and captures
    # only a number 3 digits or more while ignoring "wa" and zip codes
    r'invoice\s*#?\s*wa\s*\d{5}\s*(?:\d{1,2}/\d{1,2}/\d{4}|\d{2}/\d{2}/\d{4})?\s*(\d{3,})\b',

    # Fallback: finds the first standalone 6–8 digit number anywhere in the document
    r'(?s)\b(\d{6,8})\b(?!\s*[/-]\d{1,2})',

    # Catches "invoice" optionally followed by ":" or "#", then a number (at least 4 digits)
    r'invoice\s*[:#]?\s*(\d{4,}[A-Za-z0-9\-_]*)',

    # Looks for "order id" followed by alphanumeric code
    r'order\s+id\s*[:#]?\s*([A-Za-z0-9]+)',

    # Catches "order #" followed by digits only
    r'order\s*#?\s*([0-9]+)',

    # Very cautious fallback: 6–8 digit number not looking like a date or zip
    # Tries to avoid obvious false positives like partial dates or postal codes
    r'(?<![\d/])(?<!\d{2}-\d{2})(?<!\d{2}/\d{2})(?<!\d{5}\s)\b(\d{6,8})\b(?!\s*-?\s*\d{2})',

    # Last-resort fallback: any standalone 6–8 digit number not followed by date-like pattern
    r'\b(\d{6,8})\b(?![-/]\d)'
]
        
        for pattern in triggers:
            match = re.search(pattern, normalized, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip().upper()
                if re.match(r'^[A-Z0-9\-_]{2,20}$', candidate):
                    invoice = candidate
                    break

        if invoice and len(new_parts) == 2:  # only add if we have company + date
            new_parts.append(invoice)

        # Build final name
        if new_parts == parts:
            logging.info(f"  No changes needed for {filename}")
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

        try:
            os.rename(full_path, new_path)
            logging.info(f"Auto-named: {filename} → {new_name}")
            renamed += 1
        except Exception as e:
            logging.error(f"Rename failed: {filename} → {e}")

    logging.info(f"Total renamed: {renamed}")
    return renamed
