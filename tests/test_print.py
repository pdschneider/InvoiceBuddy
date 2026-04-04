import subprocess
import win32print


def query_printers_linux():
    """
    Queries for available printers on Linux.
    
        Important Variables:
            stats: Full command output
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

    print(f"Printers list: {printers}")
    return printers


def query_printers_windows():
    """
    Queries for available printers on Windows.

        Important Variables:
            raw_printers:       Dictionary of available printers
            printers:           List of available printer names
                                ex: ['HP651EC9 (HP ENVY Photo 7100 series)',
                                'Microsoft Print to PDF']
    """
    raw_printers = win32print.EnumPrinters(
        win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS,
        None, 2)

    printers = [printer['pPrinterName'] for printer in raw_printers]

    print(printers)



"""
Important commands:

- lpstat: Status information
- lp: Submits a print job
- cancel -a: Cancels all print jobs


"""