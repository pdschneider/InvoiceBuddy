import subprocess
import platform
import logging
import os
from PySide6.QtWidgets import QMessageBox
if platform.platform().startswith("Windows"):
    import win32print
    import win32api


def print_selected_files(globals, filenames=None):
    """
    Prints selected files on either Windows or Linux.

        Arguments:
            globals:    Global variables
            filenames:  Files to print
    """
    # Return early if not files are selected
    success = None
    if not filenames:
        return
    
    try:
        if platform.platform().startswith("Linux"):
            reply = QMessageBox.question(
                    None,
                    "Print?",
                    "Would you like to print selected files?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                success = print_on_linux(globals, filenames)
            else:
                return
            if success:
                QMessageBox.information(
                    None,
                    "Print Succeeded",
                    "Print successful!",
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
                return
            else:
                QMessageBox.warning(
                    None,
                    "Print Failed",
                    "Unable to print.",
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
        else:
            reply = QMessageBox.question(
                    None,
                    "Print?",
                    "Would you like to print selected files?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                success = print_on_windows(globals, filenames)
            else:
                return
            if success:
                QMessageBox.information(
                    None,
                    "Print Succeeded",
                    "Print successful!",
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
                return
            else:
                QMessageBox.warning(
                    None,
                    "Print Failed",
                    "Unable to print.",
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
            return False
    except Exception as e:
        logging.error(f"Could not print due to: {e}")


def print_on_linux(globals, filenames):
    """
    Prints selected documents on Linux systems.

        Important Variables:
            globals:        Global variables
            filenames:      Files to print
                            ex: ['/home/phillip/Phillip Inbox/4012 2.pdf']
    """
    try:
        for file in filenames:
            if not os.path.isfile(file):
                logging.warning(f"File not found: {file}")
                continue
            subprocess.run(args=["lp", f"{file}", "-d", f"{globals.default_printer}"])
        return True
    except Exception as e:
        logging.error(f"Unable to print due to: {e}")
        return False


def print_on_windows(globals, filenames):
    """
    Prints selected documents on Windows systems.

        Arguments:
            globals:        Global variables
            filenames:      Files to print
    """
    # Check to make sure printer is available
    try:
        handle = win32print.OpenPrinter(globals.default_printer)
        win32print.ClosePrinter(handle)
    except Exception as e:
        logging.error(f"Printer not is not available: {e}")
        return False
    
    try:
        for file in filenames:
            if not os.path.isfile(file):
                logging.warning(f"File not found: {file}")
                continue
            win32api.ShellExecute(
                0,
                "print",
                file,
                f'/d:"{globals.default_printer}"',
                os.path.dirname(file) or ".",
                0)
        return True
    except Exception as e:
        logging.error(f"Failed to print due to: {e}")
        return False
    


def query_printers():
    """Chooses the correct OS to query printers from."""
    if platform.platform().startswith("Linux"):
        return query_printers_linux()
    else:
        return query_printers_windows()


def query_printers_linux():
    """
    Queries for available printers on Linux.
    
        Important Variables:
            stats: Full command output
            printers: List of available printers
                     ex: ['ENVY_Photo_7100',
                     'HP_ENVY_Photo_7100_series_651EC9',
                     'HP_ENVY_Photo_7100_series_651EC9@HP3024A9651EC9.local']
    """
    stats = subprocess.run(args=["lpstat", "-a"],
                           text=True,
                           capture_output=True,
                           timeout=5)

    printer_list = stats.stdout.splitlines()

    printers= []
    for line in printer_list:
        line = line.split()[0]
        if not line.startswith("reason"):
            printers.append(line)

    return printers


def query_printers_windows():
    """
    Queries for available printers on Windows.

        Important Variables:
            raw_printers:       Verbose dictionary of available printers
            printers:           List of available printer names
                                ex: ['HP651EC9 (HP ENVY Photo 7100 series)',
                                'Microsoft Print to PDF']
    """
    raw_printers = win32print.EnumPrinters(
        win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS,
        None, 2)

    printers = [printer['pPrinterName'] for printer in raw_printers]

    return printers


"""
Important commands:

- lpstat: Status information
- lp: Submits a print job
- cancel -a: Cancels all print jobs

"""