# src/qt_interface/qt_components/qt_sidebar.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QListWidget,
                               QListWidgetItem)
from PySide6.QtCore import Qt
from src.managers.file_management import add_files

def create_sidebar(globs):
    """Creates the Invoice Buddy sidebar with folder navigation."""

    sidebar = QWidget()
    sidebar.setFixedWidth(160)
    sidebar.setAutoFillBackground(True)
    sidebar.setStyleSheet("background-color: rgb(43, 43, 43); border-right: 1px solid #333;") 

    layout = QVBoxLayout(sidebar)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)

    # === TOP ACTIONS ===
    top_layout = QHBoxLayout()

    # Add Files Button (Prominent)
    add_btn = QPushButton("+ Add Files")
    add_btn.setFixedHeight(35)
    add_btn.setFixedWidth(120)
    add_btn.setStyleSheet("background-color: #2ecc70; color: white; font-weight: bold;")
    add_btn.setCursor(Qt.PointingHandCursor)
    add_btn.clicked.connect(lambda: add_files(globs))
    top_layout.addWidget(add_btn)

    top_layout.addStretch()

    layout.addLayout(top_layout)

    # === NAVIGATION LIST ===
    nav_label = QLabel("Folders")
    nav_label.setStyleSheet("font-weight: bold; font-size: 14px; padding-top: 10px; color: #aaa;")
    layout.addWidget(nav_label)

    # Use QListWidget for easy selection handling
    nav_list = QListWidget()
    nav_list.setStyleSheet("""
        QListWidget {
            background-color: transparent;
            border: none;
            color: white;
            font-size: 14px;
        }
        QListWidget::item {
            padding: 10px;
            border-radius: 5px;
        }
        QListWidget::item:selected {
            background-color: #3a3a3a;
            color: #2ecc71;
        }
        QListWidget::item:hover {
            background-color: #333;
        }
    """)

    # Define Folders
    folders = ["Inbox", "Archive", "Budget", "Trash"]
    for folder in folders:
        item = QListWidgetItem(folder)
        item.setData(Qt.UserRole, folder.lower()) # Store key
        nav_list.addItem(item)

    nav_list.itemClicked.connect(lambda item: on_folder_click(item, globs))

    layout.addWidget(nav_list, stretch=1)

    # Store references
    globs.sidebar = sidebar
    globs.sidebar_nav_list = nav_list
    globs.sidebar_is_open = True # Default open for this layout

    return sidebar


def toggle_sidebar(globs, sidebar):
    """Toggles sidebar visibility (optional for this layout, but good to have)."""
    if globs.sidebar_is_open:
        sidebar.hide()
        globs.sidebar_is_open = False
    else:
        sidebar.show()
        globs.sidebar_is_open = True


def on_folder_click(item, globs):
    """Handles clicking a folder in the sidebar navigation."""
    folder_key = item.data(Qt.UserRole)

    if folder_key == 'inbox':
        globs.current_folder = globs.inbox
    elif folder_key == 'archive':
        globs.current_folder = globs.archive
    elif folder_key == 'budget':
        return  # Not implemented yet
    elif folder_key == 'trash':
        return  # Not implemented yet
    else:
        return

    # Clear the preview pane
    if hasattr(globs, 'preview_meta') and globs.preview_meta:
        globs.preview_meta.setText("Select a file to view details")
    if hasattr(globs, 'pdf_viewer') and globs.pdf_viewer:
        globs.pdf_viewer.doc.close()
        globs.pdf_viewer.view.setDocument(globs.pdf_viewer.doc)

    # Refresh the mailbox
    if hasattr(globs, 'mailbox') and globs.mailbox:
        globs.mailbox.refresh_files(globs.current_folder)
