# Managers/Autoname/card_num_search.py
import re, os, logging
from Managers.Autoname.search_helpers import extract_normalized_text

def card_number_search(directory=None, file_list=None, normalized_texts=None):
    """
    Returns dict: {original_filename: (card_num_str, matched_str) or None}
    Always searches regardless of current filename or identity.
    Handles OCR errors like O→0, L→1 in the captured digits.
    Does NOT rename.
    """
    if not file_list:
        return {}

    search_dir = directory.strip() if directory else None

    # Patterns
    triggers = [

    # 1. Highest priority: Masked format with x's/* (now tolerates 'j' in last-4)
    r'(?:c/c#|cc#|visa|mastercard|credit|chip|payment)\s*[:#]?[\s-]*[x*]{8,16}\s*([0-9~olIj]{4})\b',

    # 2. ccard style (unchanged — no need for 'j' here)
    r'(?:payment|ccard|credit\s*card)\s*[:#]?\s*ccard[o ]?([0-9~ol]{4})\b',

    # 3. visa chip + mask
    r'(?:uisa|visa|mastercard)\s*chip\s*(x{8,16})\s*([0-9~ol]{4})\b',
    r'(?:visa|visaj|mastercard|amex|discover)\s*(?:ending\s*in|ending\s*with|last\s*4|xxxx)\s*([0-9ol]{4})\b',
    r'(?:visa|mastercard|amex|discover)\s*\*{3,}\s*([0-9ol]{4})\b',
    r'(?:card\s*(?:number|#))\s*[:#]?\s*([0-9ol]{4})\b',
    r'(?:chip\s*\(visa\)|visa|credit)\s*\*{3,}\s*([0-9ol]{4})\b',
    r'(?:mastercard|mc|visa|amex|discover|card)\s*[-–—:,]?\s*(\d{4})\b',
    r'(?:visa|mastercard|amex|discover|card)?\s*(?:[#*xX]{4}\s*){3}([0-9olIj]{4})\b',

    # 4. Common c/c# or card # + mask (now also tolerates 'j')
    r'(?:c/c#|cc#|card\s*#?|visa\s*(?:credit)?)\s*[:#]?\s*(?:x{8,16}|\*{{8,16}|[x*\.]{8,16})\s*([0-9~olIj]{4})\b',

    # 5. visa nearby + mask (kept strict — no 'j' tolerance to avoid junk)
    r'(?:visa|mastercard).*?(?:x{8,16}|\*{{8,16}|[*x.]{8,16})\s*([0-9ol]{4})\b',

    # 6. Payment keywords + mask (kept strict)
    r'(?:visa|mastercard|credit|payment|charged?|c/c#).*?(x{8,16}|xxxxxxxxxxxx|\*{{8,16})\s*([0-9ol]{4})\b',

    # 7. Loose fallback mask (kept strict — no 'j')
    r'(?:x{8,16}|\*{{8,16}|[*x]{12,16})\s*([0-9ol]{4})\b',

    # 8. Original safety net (kept strict)
    r'(visa|mastercard)\s*[: ]?\s*(x{8,16}|\*{{8,16})\s*([0-9ol]{4})'
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

            logging.debug(f"Contains 'visa' or 'mastercard': {'visa' in normalized or 'mastercard' in normalized}")

            card_num = None
            matched_card = None
            matched_pattern = None
            for pattern in triggers:
                match = re.search(pattern, normalized)
                if match:
                    # Capture the "digits" group (last group in most patterns)
                    candidate = match.groups()[-1].strip().lower()
                    logging.info(f"Pattern matched: {pattern} → raw candidate: {candidate}")

                    # Fix OCR errors: O→0, L→1, I→1 (add more if needed)
                    candidate = candidate.replace('o', '0').replace('l', '1').replace('i', '1')

                    # Validate: Exactly 4 digits now?
                    if re.match(r'^\d{4}$', candidate):
                        card_num = candidate.upper()  # Upper for consistency, though digits are same
                        matched_card = match.group(0)  # Full match for scrubbing
                        matched_pattern = pattern
                        break  # First valid wins

            if card_num:
                logging.info(f"Final card number for {filename}: {card_num} from pattern: {matched_pattern}")
            else:
                logging.info(f"No valid card number found for {filename} - checked all patterns")

            results[filename] = (card_num, matched_card) if card_num else None

        logging.info(f"Card number search results: {results}")
        return results

    except Exception as e:
        logging.error(f"Error in card_number_search: {e}")
        return {}
