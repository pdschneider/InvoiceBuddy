#Utils/dependencies.py
import ctypes
import platform
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import pytesseract
import getpass
import os
import webbrowser

def check_dependencies():
    if platform.platform().startswith("Linux"):
        try:
            ctypes.CDLL("libxcb-cursor.so.0", mode=ctypes.RTLD_GLOBAL)
            return
        except Exception as e:
            print(f"PySide6 initialization failed due to: {e}")
            root = tk.Tk()
            root.withdraw()
            answer = messagebox.askyesno(
                parent=root,
                title=f"Essential Dependency Missing",
                message=f"The libxcb-cursor0 dependency is missing. Would you like to install it?"
            )
            download_cmd = """
                        #!/bin/bash

                        set -euo pipefail

                        read -p "Missing dependency: libxb-cursor0 - Install? [Y/n] " choice
                        if [[ "$choice" =~ ^[Yy]?$ ]]; then
                            sudo apt update
                            sudo apt install -y libxcb-cursor0
                            echo ""
                            echo "Dependency successfully installed! Re-launch Pearl to begin."
                            read -r dummy
                            exit 0
                        else
                            exit 0
                        fi
                        """

            if answer:
                try:
                    subprocess.Popen([
                        "gnome-terminal",
                        "--",
                        "bash", "-c",
                        f"{download_cmd}"
                    ])
                except Exception as e:
                    print(f"Error: {e}")
                    try:
                        subprocess.Popen(["x-terminal-emulator", "-e", "bash", "-c", download_cmd])
                    except Exception as e:
                        print(f"Error: {e}")

            root.destroy()
            sys.exit(0)

    else:  # Pytesseract download for Windows users
        username = getpass.getuser()
        download_url = "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe"

        if os.path.isfile(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        elif os.path.isfile(f'C:\\Users\\{username}\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'):
            pytesseract.pytesseract.tesseract_cmd = f'C:\\Users\\{username}\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'

        try:
            print(f"Pytesseract Version: {pytesseract.get_tesseract_version()}")
            download_needed = False
        except:
            print(f"OCR not yet installed - prompting for download.")
            download_needed = True

        if download_needed:
            root = tk.Tk()
            root.withdraw()
            answer = messagebox.askyesno(
                parent=root,
                title=f"Dependency Missing",
                message=f"Pytesseract is missing, which is required for OCR. Would you like to install it?")

            if answer:
                try:
                    webbrowser.open(url=download_url)
                except Exception as e:
                    print(f"Error: {e}")

            root.destroy()
            sys.exit(0)
