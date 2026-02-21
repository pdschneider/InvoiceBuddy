# Managers/Autoname/company_search.py
import logging, os, re
from Utils.load_settings import load_company_map
from Managers.Autoname.search_helpers import extract_normalized_text, normalize_text

def company_search(companies=None, directory=None, file_list=None, normalized_texts=None):
    """
    Returns dict: {original_filename: (company_name, matched_keyword) or None}
    Always searches regardless of current filename.
    Does NOT rename or handle duplicates.
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
        logging.info(f"Processing {len(filenames)} selected PDF files for company name")

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

            # Search text for any company keyword and return the company name and matched keyword if found
            matched_keyword = None
            company = None
            for keyword_tuple, comp in company_map.items():
                for keyword in keyword_tuple:
                    if keyword.lower() in ['llc', 'inc']:
                        continue
                    normalized_keyword = normalize_text(keyword)
                    match = re.search(rf'\b{re.escape(normalized_keyword)}\b', normalized)
                    if match:
                        company = comp
                        matched_keyword = match.group(0)
                        results[filename] = (company, matched_keyword, keyword_tuple) if company else None
                        break
                if company:
                    break

            results[filename] = (company, matched_keyword, keyword_tuple) if company else None

        logging.info(f"Company search results: {results}")
        return results

    except Exception as e:
        logging.error(f"Error in company_search: {e}")
        return {}