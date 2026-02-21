# Managers/Autoname/date_search.py
import logging, re, os
from Utils.load_settings import load_company_map
from Managers.Autoname.search_helpers import extract_normalized_text, date_patterns

def date_search(companies=None, directory=None, file_list=None, normalized_texts=None):
    """
    Returns dict: {original_filename: (date_str, matched_date) or None}
    Always searches regardless of current filename.
    Does NOT rename.
    """
    if not file_list:
        return {}

    company_map = load_company_map()
    search_companies = companies if companies else list(company_map.values())

    search_dir = directory.strip() if directory else None

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

            found = None
            matched_date = None
            for pattern, formatter in date_patterns:
                match = re.search(pattern, normalized)
                if match:
                    formatted = formatter(match)
                    if formatted and formatted.count('-') == 2:
                        found = formatted
                        matched_date = match.group(0)
                        break

            results[filename] = (found, matched_date) if found else None

        logging.info(f"Date search results: {results}")
        return results

    except Exception as e:
        logging.error(f"Error in date_search: {e}")
        return {}
