# src/qt_interface/qt_settings/qt_paths.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel,
                               QPushButton, QLineEdit)
from PySide6.QtCore import Qt
from src.utils.load_settings import load_data_path
from src.managers.file_management import browse_directory
import os


def create_paths_settings_tab(globs):
    """
    Create the General Settings tab for Qt interface.
    Returns a QWidget that can be added directly to the tab widget.
    """

    # Create the main widget that will BE the tab
    tab_widget = QWidget()
    tab_widget.setStyleSheet("color: #d0d0d0;")
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

    globs.inbox_entry_box = QLineEdit()
    if globs.inbox:
        globs.inbox_entry_box.setPlaceholderText(globs.inbox)
    else:
        globs.inbox_entry_box.setPlaceholderText(default_inbox)
    inbox_entry_layout.addWidget(globs.inbox_entry_box)

    inbox_browse = QPushButton()
    inbox_browse.setText("Browse")
    inbox_browse.clicked.connect(lambda: browse_directory(globs, globs.inbox_entry_box))
    inbox_entry_layout.addWidget(inbox_browse)
    inbox_browse.setFixedWidth(150)

    layout.addLayout(inbox_entry_layout)

    # Archive Entry Box
    archive_entry_layout = QHBoxLayout()

    archive_label = QLabel()
    archive_label.setText("Archive: ")
    archive_entry_layout.addWidget(archive_label)

    globs.archive_entry_box = QLineEdit()
    if globs.archive:
        globs.archive_entry_box.setPlaceholderText(globs.archive)
    else:
        globs.archive_entry_box.setPlaceholderText(default_archive)
    archive_entry_layout.addWidget(globs.archive_entry_box)

    archive_browse = QPushButton()
    archive_browse.setText("Browse")
    archive_browse.clicked.connect(lambda: browse_directory(globs, globs.archive_entry_box))
    archive_entry_layout.addWidget(archive_browse)
    archive_browse.setFixedWidth(150)

    layout.addLayout(archive_entry_layout)

    # Buddies Title
    buddies_title = QLabel("Buddies")
    buddies_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
    layout.addWidget(buddies_title)

    # Buddies container — rows get inserted here
    globs.buddy_container = QWidget()
    globs.buddy_container_layout = QVBoxLayout(globs.buddy_container)
    globs.buddy_container_layout.setContentsMargins(0, 0, 0, 0)
    globs.buddy_container_layout.setSpacing(8)
    globs.buddy_container_layout.setAlignment(Qt.AlignTop)
    layout.addWidget(globs.buddy_container)

    # Initialize buddy tracking lists for Qt mode
    if not hasattr(globs, 'buddy_entries'):
        globs.buddy_entries = []
    if not hasattr(globs, 'max_buddies'):
        globs.max_buddies = 3

    # Add Buddy Button
    globs.buddy_add_btn = QPushButton("+ Add Buddy")
    globs.buddy_add_btn.setFixedWidth(120)
    globs.buddy_add_btn.setStyleSheet("background-color: #3a3a3a; color: white; border-radius: 4px; padding: 6px;")
    globs.buddy_add_btn.setCursor(Qt.PointingHandCursor)
    layout.addWidget(globs.buddy_add_btn)

    def add_buddy():
        """Create a new buddy row with name, path, browse, and remove button."""
        if len(globs.buddy_entries) >= globs.max_buddies:
            return

        row = QWidget()
        row.setStyleSheet("background-color: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        # Name field
        name_input = QLineEdit()
        name_input.setPlaceholderText("Buddy name")
        name_input.setFixedWidth(120)
        row_layout.addWidget(name_input)

        # Path field
        path_input = QLineEdit()
        path_input.setPlaceholderText("Folder path...")
        row_layout.addWidget(path_input)

        # Browse button
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(lambda: browse_directory(globs, path_input))
        row_layout.addWidget(browse_btn)

        # Remove button
        remove_btn = QPushButton("-")
        remove_btn.setFixedWidth(30)
        remove_btn.clicked.connect(lambda checked, r=row: remove_buddy(r))
        row_layout.addWidget(remove_btn)

        # Insert at the top of the container (before the stretch)
        globs.buddy_container_layout.addWidget(row)

        # Track it
        globs.buddy_entries.append({
            "frame": row,
            "name_input": name_input,
            "path_input": path_input
        })

        # Hide add button if at max
        if len(globs.buddy_entries) >= globs.max_buddies:
            globs.buddy_add_btn.hide()

    def remove_buddy(row):
        """Remove a buddy row and clean up."""
        for entry in globs.buddy_entries[:]:
            if entry["frame"] == row:
                row.deleteLater()
                globs.buddy_entries.remove(entry)
                break

        if len(globs.buddy_entries) < globs.max_buddies:
            globs.buddy_add_btn.show()

    # Connect the add button
    globs.buddy_add_btn.clicked.connect(add_buddy)

    # Populate existing buddies from saved config
    if hasattr(globs, 'buddies') and globs.buddies:
        candidates = [(k, v) for k, v in globs.buddies.items() if k != "inbox"][:globs.max_buddies]
        for name, path in candidates:
            add_buddy()
            latest = globs.buddy_entries[-1]
            latest["name_input"].setText(name)
            latest["path_input"].setText(path)

    # Add some spacer at the bottom so it doesn't hug the edge
    layout.addStretch()

    return tab_widget
