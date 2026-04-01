#Utils/dependencies.py
import ctypes
import platform
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

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
    else:
        print(f"Windows user - dependency check skipped.")
