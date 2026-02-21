# Managers/Autoname/search_helpers.py
import logging, pdfplumber, os
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("OCR libraries (pdf2image/pytesseract) not found. Fallback disabled.")

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
    (r'\b(\d{2})-([a-z]{3})-(\d{4})\b', lambda m: f"{month_map.get(m.group(2), '')}-{m.group(1)}-{m.group(3)[-2:]}" if month_map.get(m.group(2)) else None),
    (r'\b(\d{1,2})\.(\d{1,2})\.(\d{2})\b', lambda m: f"{m.group(1).zfill(2)}-{m.group(2).zfill(2)}-{m.group(3)}"),
    (r'\b([a-z]+)\s+(\d{1,2})\s+(\d{4})\b', lambda m: f"{month_map.get(m.group(1), '')}-{m.group(2).zfill(2)}-{m.group(3)[-2:]}" if month_map.get(m.group(1)) else None),
    (r'\b([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?\s*(\d{4})\b', lambda m: f"{month_map.get(m.group(1), '')}-{m.group(2).zfill(2)}-{m.group(3)[-2:]}" if month_map.get(m.group(1)) else None),
    (r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b', lambda m: f"{m.group(1).zfill(2)}-{m.group(2).zfill(2)}-{m.group(3).zfill(4)[-2:]}"),
]

def normalize_text(text):
    """Normalize text by removing commas, extra spaces, and converting to lowercase."""
    text = text.replace(',', '')  # Remove commas
    return ' '.join(text.split()).lower()  # Returns normalized text

def extract_text_with_ocr(full_path):
    """Fallback OCR: Convert PDF to images and extract text page-by-page."""
    if not OCR_AVAILABLE:
        logging.warning(f"OCR not available for {full_path}. Skipping fallback.")
        return ""
    try:
        images = convert_from_path(full_path)  # Convert PDF to list of images
        full_text = ""
        for image in images:
            text = pytesseract.image_to_string(image)
            if text.strip():  # If text found, append and continue
                full_text += text + " "
        logging.debug(f"Full PDF text with OCR: {full_text}")
        return full_text
    except Exception as e:
        logging.error(f"OCR error on {full_path}: {e}")
        return ""

def extract_normalized_text(full_path):
    """Extract and normalize text from a single PDF file."""
    text = ""
    try:
        with pdfplumber.open(full_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
                if len(text) > 5000:
                    break
    except Exception as e:
        logging.warning(f"pdfplumber failed on {os.path.basename(full_path)}: {e}")
        text = extract_text_with_ocr(full_path)

    if not text.strip():
        logging.warning(f"No text extracted from {os.path.basename(full_path)} Trying OCR...")
        text = extract_text_with_ocr(full_path)

    
    return normalize_text(text)

def write_pdf_metadata(file_metadata_dict: dict[str, dict], inbox_dir: str):
    """file_metadata_dict: {filename: {"Company": "Acme", "InvoiceDate": "2025-01-15", ...}}"""
    import os
    from pypdf import PdfReader, PdfWriter
    updated = 0
    for filename, new_fields in file_metadata_dict.items():
        path = os.path.join(inbox_dir, filename)
        if not os.path.isfile(path):
            continue
        try:
            reader = PdfReader(path)
            writer = PdfWriter()
            writer.append(reader)               # copies all pages + forms + attachments etc.
            meta = reader.metadata or {}
            meta.update(new_fields)             # merge / overwrite
            writer.add_metadata(meta)
            with open(path, "wb") as f:
                writer.write(f)
            updated += 1
        except Exception as e:
            logging.warning(f"Metadata write failed {filename}: {e}")
    logging.info(f"Updated metadata on {updated} files")
    return updated

def get_field_order(globals, identity="Invoice", filename=None):
    """Returns list of field names in user-chosen order for this identity."""
    if identity == "Invoice":
        return [
            globals.invoice_com_a_var.get().strip(),
            globals.invoice_com_b_var.get().strip(),
            globals.invoice_com_c_var.get().strip(),
            globals.invoice_com_d_var.get().strip(),
        ]
    elif identity == "Card":
        return [
            globals.card_com_a_var.get().strip(),
            globals.card_com_b_var.get().strip(),
            globals.card_com_c_var.get().strip(),
            globals.card_com_d_var.get().strip(),
        ]
    elif identity == "Purchase":
        return [
            globals.po_com_a_var.get().strip(),
            globals.po_com_b_var.get().strip(),
            globals.po_com_c_var.get().strip(),
            globals.po_com_d_var.get().strip(),
        ]
    else:
        # Fallback — use invoice order or log warning
        logging.warning(f"Unknown identity '{identity}' for {filename}, falling back to Invoice order")
        return [
            globals.invoice_com_a_var.get().strip(),
            globals.invoice_com_b_var.get().strip(),
            globals.invoice_com_c_var.get().strip(),
            globals.invoice_com_d_var.get().strip(),
        ]
