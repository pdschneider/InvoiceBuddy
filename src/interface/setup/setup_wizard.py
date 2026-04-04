# Interface/Setup/setup_wizard.py
from PySide6.QtWidgets import (QWizard, QWizardPage,
                               QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout,
                               QLineEdit)
from PySide6.QtGui import QPixmap
import customtkinter as ctk
from src.utils.load_settings import load_data_path
from src.utils.save_settings import save_paths, save_all_settings
from src.utils.observers import setup_observer
from src.managers.file_management import browse_file, browse_directory
import logging
import shutil
import os


def create_wizard(globals):
    """Opens the wizard window."""
    # Create Wizard Window
    wizard = QWizard()
    wizard.setWindowTitle("Invoice Buddy Setup")
    wizard.resize(650, 600)

    # Welcome Page
    welcome_page = QWizardPage()
    wizard.addPage(welcome_page)
    welcome_page.setTitle("Welcome to Invoice Buddy")
    welcome_page.setSubTitle("A financial management app that makes data entry easier")
    welcome_page.setPixmap(QWizard.LogoPixmap, QPixmap("defaults/assets/icon.ico"))
    welcome_layout = QVBoxLayout()
    welcome_page.setLayout(welcome_layout)

    welcome_note = QLabel()
    welcome_note.setText(
        """
        Thank you for installing Invoice Buddy!
        
        Invoice Buddy is designed to make the invoice entry process easier. Instead of manually writing
        each filename and then entering the necessary data into your spreadsheet, the application takes
        care of it for you.
        """)
    welcome_layout.addWidget(welcome_note)

    # Paths Page
    paths_page = QWizardPage()
    wizard.addPage(paths_page)
    paths_page.setTitle("Choose Paths")
    paths_page.setSubTitle("Choose your workbook, inbox, and archive paths (Required)")
    paths_page.setPixmap(QWizard.LogoPixmap, QPixmap("defaults/assets/icon.ico"))

    # Paths Layout
    paths_layout = QVBoxLayout()
    paths_page.setLayout(paths_layout)

    # Instructions
    paths_instructions = QLabel()
    paths_instructions.setText(
        """
        To use Invoice Buddy, you must first choose an inbox and a workbook path.
        Your inbox is where you will add files to process.
        The workbook is the spreadsheet file in which you will be entering data.
        You will also need to choose an archive path for storing files after processing.
        Only choose the 'top-level' archive path. The application will create subfolders for you.
        """)
    paths_layout.addWidget(paths_instructions)

    # Default Paths
    default_inbox = os.path.normpath(load_data_path("local", "Inbox"))
    default_archive = os.path.normpath(load_data_path("local", "Archive"))

    # Inbox Entry Box
    inbox_entry_layout = QHBoxLayout()

    inbox_label = QLabel()
    inbox_label.setText("Inbox: ")
    inbox_entry_layout.addWidget(inbox_label)

    inbox_entry = QLineEdit()
    if globals.inbox:
        inbox_entry.setPlaceholderText(globals.inbox)
    else:
        inbox_entry.setPlaceholderText(default_inbox)
    inbox_entry_layout.addWidget(inbox_entry)

    inbox_browse = QPushButton()
    inbox_browse.setText("Browse")
    inbox_browse.clicked.connect(lambda: browse_directory(inbox_entry))
    inbox_entry_layout.addWidget(inbox_browse)
    inbox_browse.setFixedWidth(150)

    paths_page.registerField(
        "inbox",
        inbox_entry)
    paths_layout.addLayout(inbox_entry_layout)

    # Workbook Entry Box
    workbook_entry_layout = QHBoxLayout()

    workbook_label = QLabel()
    workbook_label.setText("Workbook: ")
    workbook_entry_layout.addWidget(workbook_label)

    workbook_entry = QLineEdit()
    if globals.workbook:
        workbook_entry.setPlaceholderText(globals.workbook)
    else:
        workbook_entry.setPlaceholderText("Workbook Path (Example: /home/family-pc/workbook.xlsx)")
    workbook_entry_layout.addWidget(workbook_entry)

    workbook_browse = QPushButton()
    workbook_browse.setText("Browse")
    workbook_browse.clicked.connect(lambda: browse_file(workbook_entry, _type="workbook"))
    workbook_entry_layout.addWidget(workbook_browse)
    workbook_browse.setFixedWidth(150)

    paths_page.registerField(
        "workbook",
        workbook_entry)
    paths_layout.addLayout(workbook_entry_layout)

    # Archive Entry Box
    archive_entry_layout = QHBoxLayout()

    archive_label = QLabel()
    archive_label.setText("Archive: ")
    archive_entry_layout.addWidget(archive_label)

    archive_entry = QLineEdit()
    if globals.archive:
        archive_entry.setPlaceholderText(globals.archive)
    else:
        archive_entry.setPlaceholderText(default_archive)
    archive_entry_layout.addWidget(archive_entry)

    archive_browse = QPushButton()
    archive_browse.setText("Browse")
    archive_browse.clicked.connect(lambda: browse_directory(archive_entry))
    archive_entry_layout.addWidget(archive_browse)
    archive_browse.setFixedWidth(150)

    paths_page.registerField(
        "archive",
        archive_entry)
    paths_layout.addLayout(archive_entry_layout)

    # Execute Wizard
    result = wizard.exec()

    if result == QWizard.Accepted:
        logging.info("Wizard finished")
        
        # Save inbox path, make directory if needed
        if str(wizard.field("inbox")):
            inbox_path = str(wizard.field("inbox"))
        elif globals.inbox:
            inbox_path = globals.inbox
        else:
            inbox_path = default_inbox
        if not os.path.isdir(inbox_path):
            os.makedirs(inbox_path)

        # Save workbook path
        if str(wizard.field("workbook")):
            workbook_path = str(wizard.field("workbook"))
        elif globals.workbook:
            workbook_path = globals.workbook
        else:
            workbook_path = ""

        # Save archive path, make directory if needed
        if str(wizard.field("archive")):
            archive_path = str(wizard.field("archive"))
        elif globals.archive:
            archive_path = globals.archive
        else:
            archive_path = default_archive
        if not os.path.isdir(archive_path):
            os.makedirs(archive_path)

        new_sources = {
        "inbox": inbox_path,
        "workbook": workbook_path,
        "archive": archive_path}

        print(f"Inbox: {inbox_path}")
        print(f"Workbook: {workbook_path}")
        print(f"Archive: {archive_path}")

        globals.inbox = inbox_path
        globals.workbook = workbook_path
        globals.archive = archive_path

        globals.inbox_dir_var = ctk.StringVar(value=inbox_path)
        globals.workbook_var = ctk.StringVar(value=workbook_path)
        globals.archive_path_var = ctk.StringVar(value=archive_path)
        
        # Save paths
        _apply_paths(globals, sources=new_sources)

        # Mimic Continue Button from Onboarding
        save_all_settings(globals, reject_toast=True, reject_metadata=True)
        try:
            setup_observer(globals, globals.inbox, key='inbox')
        except Exception as e:
            logging.error(f"Unable to set up observers due to: {e}")

        try:
            src_dir = os.path.normpath(
                load_data_path("local", "Welcome to Invoice Buddy.pdf"))
            shutil.copy2(src_dir, globals.inbox)
            logging.debug(f"Copied welcome document to inbox successfully!")
        except Exception as e:
            logging.error(f"Cannot load welcome file due to: {e}")

    else:
        logging.info("Wizard cancelled")

def _apply_paths(globals, sources):
    """Apply paths from the Wizard before exiting."""
    if sources:
        save_paths(globals, sources=sources)
