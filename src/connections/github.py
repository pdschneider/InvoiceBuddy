# Connections/github.py
import requests
import logging
import webbrowser
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon
import sys
from src.utils.load_settings import load_data_path


def version_check(globals):
    """Checks to see which version is most recent."""

    def ver_tuple(v):
        """Turn "0.3.4-beta" into (0, 3, 4) for correct comparison."""
        v = v.replace("-beta", "").strip()
        try:
            return tuple(int(x) for x in v.split("."))
        except:
            return (0, 0, 0)   # safety

    # Determine Endpoint & Headers
    repo = "pdschneider/InvoiceBuddy"
    if globals.beta:
        print(f"Beta updates active. Using beta channel.")
        url = f"https://api.github.com/repos/{repo}/releases"
    else:
        print(f"Beta updates not active. Using stable channel.")
        url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {"Accept": "application/vnd.github+json"}

    try:
        # Query github for the version
        if globals.beta:
            response = requests.get(url, headers=headers, params={"per_page": 10}, timeout=10)
        else:
            response = requests.get(url, headers=headers, timeout=10)

        # Gracefully exit if status code is not 200
        if response.status_code != 200:
            logging.warning(
                f"Unable to fetch latest version | Status Code: {response.status_code}")
            return

        # Parse just the version number from data
        if globals.beta:
            data = response.json()[0]
        else:
            data = response.json()
        globals.latest_version = data["tag_name"].replace('v', '')

        # Determine if newest version is in beta
        beta = "-beta" in globals.latest_version

        # Pull html and changelog from latest release
        latest_version_url = data["html_url"]
        assets = data["assets"]
        changelog = str(data["body"])

        # Specify changelog not available if empty
        if not changelog:
            changelog = "Changelog not available."

        # Remove markdown elements from changelog
        changelog = changelog.replace("###", "").replace("##", "")

        # print(f"\n\nChangelog: {changelog}\n\n")  # <-- Prints Changelog

        # Exit if assets is not available
        if not assets:
            logging.warning(f"Unable to locate download URLs.")
            return

        # Declare download variables
        windows_download_url = None
        linux_download_url = None

        # print(f"{data}")  # <-- Prints entire output

        globals.app_type = "Deb"

        # Locate the correct file
        for asset in assets:
            download_url = asset["browser_download_url"]
            # print(f"DOWNLOAD URL: {download_url}")  # <-- Prints Download URL
            if download_url.endswith(".AppImage") and globals.app_type == "AppImage":
                linux_download_url = download_url
                break
            elif download_url.endswith(".deb") and globals.app_type == "Deb":
                linux_download_url = download_url
                break
            elif download_url.endswith(".exe"):
                windows_download_url = download_url
                break
        
        if not linux_download_url and not windows_download_url:
            logging.warning(f"No new version found.")
            return

        # Gracefully exit if the latest version is still not found
        if not globals.latest_version:
            logging.warning(f"Latest version not found.")
            return

        # Is current version in beta?
        if "-beta" in globals.current_version:
            current_beta = True
        else:
            current_beta = False

        # Convert to numeric tuples so 0.3.9 < 0.3.10 works correctly
        current_comp = ver_tuple(globals.current_version)
        latest_comp = ver_tuple(globals.latest_version)

        # Check if this is the latest version
        if not globals.beta:
            should_update = current_comp < latest_comp
        else:
            # Beta users get next beta OR stable upgrade of same version number
            should_update = (current_comp < latest_comp) or \
                            (current_comp == latest_comp and current_beta and not beta)

        if should_update:
            logging.info(
                f"An update to Invoice Buddy is available! Latest Version: {globals.latest_version}")
            
            # Create a messagebox
            msg = QMessageBox()
            msg.setWindowTitle("Update Available")
            msg.setText(f"Would you like to download the latest version of Invoice Buddy?")
            msg.setInformativeText(f"Current Version: {globals.current_version} | Latest Version: {globals.latest_version}")
            msg.setDetailedText(f"{changelog}")
            try:
                msg.setIconPixmap(QIcon(load_data_path("config", "assets/icon.png")).pixmap(64, 64))
            except Exception as e:
                msg.setIcon(QMessageBox.Icon.Information)
                logging.warning(f"Could not load Invoice Buddy icon for updater, defaulting to information icon.")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg.setDefaultButton(QMessageBox.StandardButton.Yes)

            # Call the messagebox and prompt for download
            reply = msg.exec()
            
            # Open correct download path if user chooses yes
            if reply == QMessageBox.StandardButton.Yes:
                if globals.os_name.startswith("Linux"):
                    webbrowser.open(url=linux_download_url)
                elif globals.os_name.startswith("Windows"):
                    webbrowser.open(url=windows_download_url)
                else:
                    webbrowser.open(url=latest_version_url)
                # Exit entire app after opening link
                sys.exit(0)

    except Exception as e:
        logging.error(f"An error occurred while checking for updates: {e}")
