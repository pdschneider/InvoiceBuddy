# src/managers/data_processing.py
import os
import copy
import logging
import traceback
import msoffcrypto
from io import BytesIO
from tkinter import simpledialog
from openpyxl import load_workbook
from src.managers.history_manager import load_history, add_update_history
from src.utils.save_qt import save_metadata
from src.utils.toast import show_toast
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.teletype import extractText
from odf.text import P


def parse_spreadsheet(globs, file_list=None):
    """Directs spreadsheet parsing."""
    save_metadata(globs)

    if not file_list:
        show_toast(globs, "Please select one or more files to enter.")
        return

    sheet_groups = {}

    for full_path in file_list:
        filename = os.path.basename(full_path)
        sheet_name = globs.file_identity.get(filename, "")
        if not sheet_name:
            sheets = globs.sheet_data.get("sheets", [])
            sheet_name = sheets[0].get("name", "Sheet") if sheets else "Sheet"
        if sheet_name not in sheet_groups:
            sheet_groups[sheet_name] = []
        sheet_groups[sheet_name].append(full_path)

    logging.info(f"Qt dispatch groups: {sheet_groups}")

    # Dispatch to the correct parsing function for each sheet
    for sheet_name, files in sheet_groups.items():
        sheet_config = next(
            (s for s in globs.sheet_data.get("sheets", []) if s.get("name") == sheet_name),
            None
        )
        workbook_path = sheet_config.get("workbook", "") if sheet_config else ""

        if workbook_path.lower().endswith(".ods"):
            parse_ods(globs, sheet_name, files)
        else:
            parse_sheet_qt(globs, sheet_name, files)

    # Show completion toast
    show_toast(globs, f"Entered {len(file_list)} files to {len(sheet_groups)} sheets!")


def get_ods_cell(table, row_num, col_num):
    """
    Returns the TableCell at 1-based (row_num, col_num), or None if
    the logical position doesn't exist or is empty space.
    Handles ODF's number-rows/columns-repeated sparse-grid compression.
    """
    row_idx = 0
    for row in table.getElementsByType(TableRow):
        row_count = int(row.getAttribute('numberrowsrepeated') or 1)
        if row_idx <= row_num - 1 < row_idx + row_count:
            # Skip rows that are pure repetition (no children = empty filler)
            if row_count > 1 and not row.hasChildNodes():
                return None
            col_idx = 0
            for cell in row.getElementsByType(TableCell):
                cell_count = int(cell.getAttribute('numbercolumnsrepeated') or 1)
                if col_idx <= col_num - 1 < col_idx + cell_count:
                    # Guard against the massive empty tail cells LibreOffice appends
                    if cell_count >= 1024 and not cell.hasChildNodes():
                        return None
                    return cell
                col_idx += cell_count
            return None
        row_idx += row_count
    return None


def _insert_element(parent, child, ref):
    """Inserts child before ref, or appends if ref is None."""
    if ref is not None:
        parent.insertBefore(child, ref)
    else:
        parent.appendChild(child)


def get_or_create_ods_row(table, row_num):
    """
    Returns a writable physical TableRow for 1-based row_num.
    Creates missing rows, splits repeated filler spans, and splits
    repeated styled rows (with children) so a write hits ONE row.
    """
    rows = table.getElementsByType(TableRow)

    row_idx = 0
    for i, row in enumerate(rows):
        rep = int(row.getAttribute('numberrowsrepeated') or 1)
        if row_idx <= row_num - 1 < row_idx + rep:
            if rep > 1 and not row.hasChildNodes():
                # Filler span (no children) - split into discrete empty rows
                before = (row_num - 1) - row_idx
                after = (row_idx + rep) - row_num
                style = row.getAttribute('stylename')
                ref = rows[i + 1] if i + 1 < len(rows) else None

                safe_remove_child(table, row)

                def _clone_row(count):
                    r = TableRow()
                    if count > 1:
                        r.setAttribute('numberrowsrepeated', str(count))
                    if style:
                        r.setAttribute('stylename', style)
                    return r

                if before > 0:
                    _insert_element(table, _clone_row(before), ref)
                if style:
                    row.setAttribute('stylename', style)
                row.setAttribute('numberrowsrepeated', '1')
                _insert_element(table, row, ref)
                if after > 0:
                    _insert_element(table, _clone_row(after), ref)
                return row

            if rep > 1:
                # Styled repeated row (HAS children) - split with deepcopies
                before = (row_num - 1) - row_idx
                after = (row_idx + rep) - row_num
                ref = rows[i + 1] if i + 1 < len(rows) else None

                # Detach FIRST - copies must never be made from an attached element
                safe_remove_child(table, row)
                row.setAttribute('numberrowsrepeated', '1')

                # Build BOTH copies while the row is detached, then sever
                # any lingering linkage pointers on the copies
                segs = []
                for count in (before, after):
                    if count > 0:
                        seg = copy.deepcopy(row)
                        seg.setAttribute('numberrowsrepeated', str(count))
                        seg.parentNode = None
                        seg.nextSibling = None
                        seg.previousSibling = None
                        segs.append((count, seg))

                # Re-insert: before-segment, the row itself, after-segment
                for count, seg in segs:
                    if count == before and before > 0:
                        _insert_element(table, seg, ref)
                _insert_element(table, row, ref)
                for count, seg in segs:
                    if count == after and after > 0:
                        _insert_element(table, seg, ref)
                return row

            return row
        row_idx += rep

    # Row is beyond the grid - append rows until it exists,
    # inheriting the style of the last physical row (keeps colored bands going)
    inherit_style = rows[-1].getAttribute('stylename') if rows else None
    new_row = None
    for _ in range(row_num - row_idx):
        new_row = TableRow()
        if inherit_style:
            new_row.setAttribute('stylename', inherit_style)
        table.appendChild(new_row)
    return new_row


def safe_remove_child(parent, child):
    """
    Removes child from parent. If the element was never registered in odfpy's
    document cache (true for anything we inserted ourselves — appendChild/
    insertBefore skip registration, but removeChild demands it), bypass the
    cache bookkeeping entirely instead of crashing.
    """
    doc = parent.ownerDocument
    if doc is not None and child in doc.element_dict.get(child.qname, []):
        # Registered element: use odfpy's own, cache-consistent path
        parent.removeChild(child)
    else:
        # Our own unregistered element: unhook siblings and parent manually
        parent.childNodes.remove(child)
        if child.nextSibling is not None:
            child.nextSibling.previousSibling = child.previousSibling
        if child.previousSibling is not None:
            child.previousSibling.nextSibling = child.nextSibling
        child.nextSibling = child.previousSibling = None
        child.parentNode = None


def set_ods_cell(row, col_num, value):
    """
    Writes value to the logical cell at 1-based col_num within this physical row,
    splitting repeated spans and padding with new cells so the write always lands.
    Returns True if written, False on unexpected failure.
    """
    cells = row.getElementsByType(TableCell)
    total_cols = sum(int(c.getAttribute('numbercolumnsrepeated') or 1) for c in cells)

    # Target beyond physical space - pad with empty styled cells first
    if col_num > total_cols:
        pad_style = cells[-1].getAttribute('stylename') if cells else None
        for _ in range(col_num - total_cols):
            c = TableCell()
            if pad_style:
                c.setAttribute('stylename', pad_style)
            row.appendChild(c)
        cells = row.getElementsByType(TableCell)

    col_idx = 0
    for i, cell in enumerate(cells):
        rep = int(cell.getAttribute('numbercolumnsrepeated') or 1)
        if not (col_idx <= col_num - 1 < col_idx + rep):
            col_idx += rep
            continue

        # Found the span covering our target column - split it
        before = (col_num - 1) - col_idx
        after = (col_idx + rep) - col_num
        style = cell.getAttribute('stylename')
        ref = cells[i + 1] if i + 1 < len(cells) else None

        safe_remove_child(row, cell)

        def _clone(rep_count, text=None):
            c = TableCell(numbercolumnsrepeated=str(rep_count)) if rep_count > 1 else TableCell()
            if style:
                c.setAttribute('stylename', style)
            if text is not None:
                c.setAttribute('valuetype', 'string')
                c.addElement(P(text=text))
            return c

        if before > 0:
            _insert_element(row, _clone(before, None), ref)
        _insert_element(row, _clone(1, value), ref)   # the actual write target
        if after > 0:
            _insert_element(row, _clone(after, None), ref)
        return True

    return False


def parse_ods(globs, sheet_name, file_list=None):
    """Handles entering data to a .ods spreadsheet (odfpy backend)."""

    # Exit early if no files are selected
    if not file_list:
        show_toast(globs, "Please select one or more files to enter.")
        return

    # Get sheet config (name, color, workbook path, first row/column, column order)
    sheet_config = next(
        (s for s in globs.sheet_data.get("sheets", []) if s.get("name") == sheet_name),
        None
    )

    # Exit if sheet name is not found in sheet config
    if not sheet_config:
        logging.error(f"Sheet '{sheet_name}' not found in sheet definitions.")
        return

    workbook_path = sheet_config.get("workbook", "")
    if not os.path.isfile(workbook_path):
        show_toast(globs, f"No valid workbook for sheet '{sheet_name}'.", _type="error")
        return

    # Dispatcher misroute guard
    if not workbook_path.lower().endswith(".ods"):
        logging.error(f"parse_ods called for non-.ods workbook: {workbook_path}")
        return

    try:
        base_names = [os.path.basename(f) for f in file_list]

        doc = load(workbook_path)
        tables = doc.spreadsheet.getElementsByType(Table)
        logging.debug(f"Available Sheets: {[t.getAttribute('name') for t in tables]}")

        table = next(
            (t for t in tables if t.getAttribute('name') == sheet_config.get("sheet_name", sheet_name)),
            None
        )
        if not table:
            logging.warning(f"{sheet_name} not found in workbook.")
            show_toast(globs, message=f"{sheet_name} not in workbook")
            return

        logging.debug(f"Sheet Name: {table.getAttribute('name')}")

        starting_row = sheet_config.get("first_row", 3)
        starting_column = sheet_config.get("first_column", 1)
        columns_to_check = 5

        def is_empty(r, c):
            """A logical cell is 'empty' if it doesn't exist or has no text."""
            cell = get_ods_cell(table, r, c)
            return cell is None or extractText(cell).strip() == ""

        # Walk down past any rows with content in the checked window
        while not all(
            is_empty(starting_row, col)
            for col in range(starting_column, starting_column + columns_to_check)):
            starting_row += 1

        for full_file_name in base_names:
            # Advance to the next empty row (skip rows filled by earlier iterations)
            while not all(
                is_empty(starting_row, col)
                for col in range(starting_column, starting_column + columns_to_check)):
                starting_row += 1

            base_name = os.path.splitext(full_file_name)[0]
            portions = base_name.split()

            row = get_or_create_ods_row(table, starting_row)
            if not row:
                logging.warning(
                    f"No physical row at {starting_row} in '{sheet_name}' - skipping file '{full_file_name}'")
                continue

            for offset, portion in enumerate(portions):
                written = set_ods_cell(row, starting_column + offset, portion.strip())
                if not written:
                    logging.warning(
                        f"No physical space at ({starting_row}, {starting_column + offset}) "
                        f"in '{sheet_name}' - skipped portion '{portion}'")

            starting_row += 1

        if os.access(workbook_path, os.W_OK):
            doc.save(workbook_path)
            logging.info(f"Saved {len(base_names)} entries to '{sheet_name}' in {workbook_path}")
        else:
            logging.warning(f"Permission denied to write to {workbook_path}")

    except Exception as e:
        logging.error(f"ods sheet parsing error for '{sheet_name}': {e}")
        logging.error(traceback.format_exc())
        show_toast(globs, message=f"Error: '{sheet_name}': {e}", _type="error")


def parse_sheet_qt(globs, sheet_name, file_list=None):
    """
    Qt-mode parser: writes filename data to a user-defined sheet.
    Reads sheet config (workbook, starting row/col, column order) from sheet_data.
    """

    # Exit early if no files are selected
    if not file_list:
        show_toast(globs, "Please select one or more files to enter.")
        return

    # Get sheet config (name, color, workbook path, first row/column, column order)
    sheet_config = None
    for sheet in globs.sheet_data.get("sheets", []):
        if sheet.get("name") == sheet_name:
            sheet_config = sheet
            logging.debug(f"Sheet Config: {sheet_config}")
            break

    # Exit if sheet name is not found in sheet config
    if not sheet_config:
        logging.error(f"Sheet '{sheet_name}' not found in sheet definitions.")
        return

    workbook_path = sheet_config.get("workbook", "")
    if not os.path.isfile(workbook_path):
        show_toast(globs, f"No valid workbook for sheet '{sheet_name}'.", _type="error")
        return

    # Use correct workbook
    if not globs.legacy_mode:
        globs.workbook = workbook_path

    # Extract workbook to memory object and return if empty
    wb = encryption_handler(globs)
    if not wb:
        return

    # Ensure chosen sheet name is in workbook sheet names
    wb_sheets = wb.sheetnames
    logging.debug(f"Available Sheets: {wb_sheets}")
    if sheet_name not in wb_sheets:
        logging.warning(f"{sheet_name} not found in workbook.")
        show_toast(globs, message=f"{sheet_name} not in workbook")
        return

    try:
        base_names = [os.path.basename(f) for f in file_list]
        sheet = wb[sheet_config.get("sheet_name", sheet_name)]
        logging.debug(f"Sheet Name: {sheet}")

        starting_row = sheet_config.get("first_row", 3)
        starting_column = sheet_config.get("first_column", 1)
        column_order = sheet_config.get("column_order", ["Company", "Date", "Invoice #", ""])

        columns_to_check = 5

        while not all(
            sheet.cell(row=starting_row, column=col).value is None
            for col in range(starting_column, starting_column + columns_to_check)):
            starting_row += 1

        for full_file_name in base_names:
            while not all(
                sheet.cell(row=starting_row, column=col).value is None
                for col in range(starting_column, starting_column + columns_to_check)):
                starting_row += 1

            base_name = os.path.splitext(full_file_name)[0]
            portions = base_name.split()

            for j, portion in enumerate(portions, start=starting_column):
                sheet.cell(row=starting_row, column=j, value=portion.strip())

            starting_row += 1

        if os.access(workbook_path, os.W_OK):
            wb.save(workbook_path)
            logging.info(f"Saved {len(base_names)} entries to '{sheet_name}' in {workbook_path}")
        else:
            logging.warning(f"Permission denied to write to {workbook_path}")

    except Exception as e:
        logging.error(f"Qt sheet parsing error for '{sheet_name}': {e}")
        show_toast(globs, message=f"Error: '{sheet_name}': {e}", _type="error")


def paths_check(globs):
    """Ensures that the workbook is writable and inbox path is valid."""
    try:
        # Check if inbox path is valid
        if os.path.isdir(globs.inbox):
            pass
        elif os.path.isdir(globs.inbox_dir_var.get().strip()):
            globs.inbox = globs.inbox_dir_var.get().strip()
        else:
            logging.warning(f"Inbox path not valid - Skipping entering data.")
            return False

        # Check if workbook path is valid
        if os.path.isfile(globs.workbook):
            pass
        elif os.path.isfile(globs.workbook_var.get().strip()):
            globs.workbook = globs.workbook_var.get().strip()
        else:
            logging.warning(f"Workbook path not valid - Skipping entering data.")
            return False

        # Ensure workbook has writable filesystem permissions
        # This only checks for general filesystem permissions,
        # NOT file locks such as when another user has the spreadhseet open.
        if os.access(globs.workbook, os.W_OK):
            pass
        else:
            logging.error(f"Permission denied to write to workbook via filesystem permissions.")
            return False
        
        # Return True only if checks pass
        return True

    except Exception as e:
        logging.error(f"Unable to check paths due to: {e}")
        return False


def encryption_handler(globs):
    """
    Returns a wb object and handles encrypted workbooks.
    
        is_encrypted:   True if workbook is password protected, else False
        wb:             Workbook object in memory
    """
    is_encrypted = False

    try:
        # Check to see if workbook is encrypted
        with open(globs.workbook, "rb") as f:
            workbook_file = msoffcrypto.OfficeFile(f)
            is_encrypted = workbook_file.is_encrypted()

        # Handle password entry if workbook is encrypted
        if is_encrypted:
            password = simpledialog.askstring(
                "Password Required",
                "Enter the password for the encrypted workbook:",
                show='*')
            if password:
                decrypted = BytesIO()
                try:
                    with open(globs.workbook, 'rb') as f:
                        file = msoffcrypto.OfficeFile(f)
                        file.load_key(password=password)
                        file.decrypt(decrypted)
                except:
                    logging.error(f"Password failed.")
                    return False

                # Return if password entry failed
                if is_encrypted:
                    logging.error(f"Decryption failed.")
                    show_toast(globs, message="Decryption failed - wrong password?")
                    return False

                # Return decrypted workbook
                decrypted.seek(0)
                wb = load_workbook(decrypted)
                return wb

            else: # If password is not entered
                logging.info(f"Exited password entry.")
                return False
        else: # If not encrypted
            wb = load_workbook(globs.workbook)
            return wb
    except Exception as e:
        logging.error(f"Unable to generate workbook object due to: {e}")
        return False


def parse_invoices(globs, history_tree, file_list=None):
    """
    Writes filename data to the Invoices sheet of the workbook,
    respecting a configurable starting column.

        globs:        Global variables
        history_tree:   Tkinter treeview
        file_list:      list of filepath strings from the inbox view
                        ex: ['/home/phillip/Phillip Inbox/03-04-26 109215.pdf']

        base_names:     A list of base names for each entry in file_list
                        ex: ['03-04-26 109215.pdf']
    """
    # Return if inbox or workbook paths are not valid
    if not paths_check(globs):
        return

    # Return if file list is empty
    if not file_list:
        show_toast(globs, "Please select one or more files to enter.")
        return

    # Generate wb object, return if empty
    wb = encryption_handler(globs)
    if not wb:
        return

    try:
        base_names = [os.path.basename(f) for f in file_list]

        # Generate sheet object
        sheet = wb[globs.sheet_invoices]

        # Set starting row
        if globs.invoice_starting_row and isinstance(globs.invoice_starting_row, int):
            current_row = globs.invoice_starting_row
        else:
            current_row = 1
            logging.error(
                f"Could not read invoice starting row. Defaulting to 1.")

        # Set starting column
        if globs.invoice_starting_column and isinstance(globs.invoice_starting_column, int):
            starting_column = globs.invoice_starting_column
        else:
            starting_column = 1
            logging.error(
                "Could not read invoice starting column. Defaulting to 1.")

        columns_to_check = 5  # If any of these columns are not empty, skip row

        # Find the first fully empty row starting from current_row
        while not all(
            sheet.cell(row=current_row, column=col).value is None
            for col in range(starting_column, starting_column + columns_to_check)):
            current_row += 1
        logging.info(
            f"First available row: {current_row} (starting at column {starting_column})")

        # Process each file
        for full_file_name in base_names:
            # Double-check row is empty before writing
            while not all(sheet.cell(row=current_row, column=col).value is None for col in range(starting_column, starting_column + columns_to_check)):
                current_row += 1

            # Create list based on filename, separated by spaces
            base_name = os.path.splitext(full_file_name)[0]
            portions = base_name.split()

            # Write each portion starting at the defined column (in memory)
            for j, portion in enumerate(portions, start=starting_column):
                sheet.cell(row=current_row, column=j, value=portion.strip())

            current_row += 1  # Move to next row for next file

        # Update history for all processed files
        for full_file_name in base_names:
            add_update_history(
                filename=full_file_name,
                src_folder=globs.inbox,
                file_type="Invoices",
                entered=globs.user)

        # Save workbook
        if os.access(globs.workbook, os.W_OK):
            wb.save(globs.workbook)

            # Refresh history treeview
            load_history(history_tree)
        else:
            logging.warning(f"Permission denied to write to {globs.workbook}")
            raise PermissionError(
                f"Permission denied to write to {globs.workbook}")

    except Exception as e:
        logging.error(f"{globs.invoice_sheet_label} processing error: {e}")


def parse_credit_cards(globs, history_tree, file_list=None):
    """
    Writes filename data to the Credit Cards sheet of the workbook,
    respecting a configurable starting column.

        globs:        Global variables
        history_tree:   Tkinter treeview
        file_list:      list of filepaths from the inbox view
    """
    # Return if inbox or workbook paths are not valid
    if not paths_check(globs):
        return

    # Return if file list is empty
    if not file_list:
        show_toast(globs, "Please select one or more files to enter.")
        return

    # Generate wb object, return if empty
    wb = encryption_handler(globs)
    if not wb:
        return

    try:
        base_names = [os.path.basename(f) for f in file_list]

        # Generate sheet object
        sheet = wb[globs.sheet_CreditCards]

        # Starting row (fallback to 3)
        if globs.card_starting_row and isinstance(globs.card_starting_row, int):
            current_row = globs.card_starting_row
        else:
            current_row = 3


        # Starting column (fallback to 1)
        if globs.card_starting_column and isinstance(globs.card_starting_column, int):
            starting_column = globs.card_starting_column
        else:
            starting_column = 1

        columns_to_check = 3 # Ensure at least the first 3 columns are empty

        # Find the first fully empty row starting from current_row
        while not all(
            sheet.cell(row=current_row, column=col).value is None
            for col in range(starting_column, starting_column + columns_to_check)):
            current_row += 1
        logging.info(
            f"First available row: {current_row} (starting at column {starting_column})")

        # Process each file
        for full_file_name in base_names:
            # Double-check row is empty before writing
            while not all(
                sheet.cell(row=current_row, column=col).value is None
                for col in range(starting_column, starting_column + columns_to_check)):
                current_row += 1

            # Generate a list split by spaces in filename
            base_name = os.path.splitext(full_file_name)[0]
            portions = base_name.split()

            # Write each portion starting at the defined column
            for j, portion in enumerate(portions, start=starting_column):
                sheet.cell(row=current_row, column=j, value=portion.strip())

            current_row += 1  # Move to next row for next file

        # Update history for all processed files
        for full_file_name in base_names:
            add_update_history(
                filename=full_file_name,
                src_folder=globs.inbox,
                file_type="Credit Cards",
                entered=globs.user)

        # Save workbook
        if os.access(globs.workbook, os.W_OK):
            wb.save(globs.workbook)
            logging.info(f"Saved workbook to {globs.workbook}")

            # Refresh history treeview
            load_history(history_tree)
        else:
            logging.warning("Permission denied to write to workbook.")
            raise PermissionError(
                f"Permission denied to write to {globs.workbook}")

    except Exception as e:
        logging.error(f"{globs.card_sheet_label} processing error: {e}")
