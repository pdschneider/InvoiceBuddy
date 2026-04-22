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
    repo = "pdschneider/InvoiceBuddy"
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {"Accept": "application/vnd.github+json"}

    try:
        # Query github for the version
        response = requests.get(url, headers=headers, timeout=10)

        # Gracefully exit if status code is not 200
        if response.status_code != 200:
            logging.warning(
                f"Unable to fetch latest version | Status Code: {response.status_code}")
            return

        # Parse just the version number from data
        data = response.json()
        globals.latest_version = data["tag_name"].replace('v', '')
        latest_version_url = data["html_url"]
        assets = data["assets"]
        changelog = str(data["body"])

        # Remove markdown elements from changelog
        changelog = changelog.replace("###", "").replace("##", "")

        # print(f"\n\nChangelog: {changelog}\n\n") # <-- Prints Changelog

        # Log if assets is not available
        if not assets:
            logging.warning(f"Unable to locate download URLs.")

        # Declare download variables
        windows_download_url = None
        linux_download_url = None

        # Locate the correct file
        for asset in assets:
            download_url = asset["browser_download_url"]
            if download_url.endswith(".AppImage"):
                linux_download_url = download_url
            elif download_url.endswith(".exe"):
                windows_download_url = download_url

        # print(f"{data}")  # <-- Prints entire output

        # Gracefully exit if the latest version is still not found
        if not globals.latest_version:
            logging.warning(f"Latest version not found.")
            return

        # Check if this is the latest version
        if globals.current_version < globals.latest_version:
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
                logging.warning(f"Could not load invoice Buddy icon for updater, defaulting to information icon.")
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
