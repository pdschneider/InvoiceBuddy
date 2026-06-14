# src/qt_interface/qt_settings/qt_advanced.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                               QCheckBox, QComboBox, QHBoxLayout,
                               QPushButton, QLineEdit)
from PySide6.QtCore import Qt
from src.utils.load_settings import load_data_path
from src.managers.file_management import browse_directory
import logging
import os


def create_paths_settings_tab(globals):
    """
    Create the General Settings tab for Qt interface.
    Returns a QWidget that can be added directly to the tab widget.
    """

    # Create the main widget that will BE the tab
    tab_widget = QWidget()
    layout = QVBoxLayout(tab_widget)
    layout.setContentsMargins(20, 20, 20, 20)  # More padding
    layout.setSpacing(20)  # More space between elements
    layout.setAlignment(Qt.AlignTop)  # Align everything to top

    # Title
    title = QLabel("Paths")
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
    layout.addWidget(title)

    # Default Paths
    default_inbox = os.path.normpath(load_data_path("local", "Inbox"))
    default_archive = os.path.normpath(load_data_path("local", "Archive"))

    # Inbox Entry Box
    inbox_entry_layout = QHBoxLayout()

    inbox_label = QLabel()
    inbox_label.setText("Inbox: ")
    inbox_entry_layout.addWidget(inbox_label)

    globals.inbox_entry_box = QLineEdit()
    if globals.inbox:
        globals.inbox_entry_box.setPlaceholderText(globals.inbox)
    else:
        globals.inbox_entry_box.setPlaceholderText(default_inbox)
    inbox_entry_layout.addWidget(globals.inbox_entry_box)

    inbox_browse = QPushButton()
    inbox_browse.setText("Browse")
    inbox_browse.clicked.connect(lambda: browse_directory(globals.inbox_entry_box))
    inbox_entry_layout.addWidget(inbox_browse)
    inbox_browse.setFixedWidth(150)

    layout.addLayout(inbox_entry_layout)

    # Archive Entry Box
    archive_entry_layout = QHBoxLayout()

    archive_label = QLabel()
    archive_label.setText("Archive: ")
    archive_entry_layout.addWidget(archive_label)

    globals.archive_entry_box = QLineEdit()
    if globals.archive:
        globals.archive_entry_box.setPlaceholderText(globals.archive)
    else:
        globals.archive_entry_box.setPlaceholderText(default_archive)
    archive_entry_layout.addWidget(globals.archive_entry_box)

    archive_browse = QPushButton()
    archive_browse.setText("Browse")
    archive_browse.clicked.connect(lambda: browse_directory(globals.archive_entry_box))
    archive_entry_layout.addWidget(archive_browse)
    archive_browse.setFixedWidth(150)

    layout.addLayout(archive_entry_layout)

    # Buddies Title
    title = QLabel("Buddies")
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
    layout.addWidget(title)

    # Add some spacer at the bottom so it doesn't hug the edge
    layout.addStretch()

    return tab_widget
