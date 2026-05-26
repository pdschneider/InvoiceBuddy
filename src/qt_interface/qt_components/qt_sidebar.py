# src/qt_interface/qt_components/qt_sidebar.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QScrollArea, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QColor, QFont
from src.managers.file_management import add_files

def create_sidebar(globals):
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
    add_btn.clicked.connect(lambda: add_files(globals))
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

    layout.addWidget(nav_list, stretch=1)

    # Store references
    globals.sidebar = sidebar
    globals.sidebar_nav_list = nav_list
    globals.sidebar_is_open = True # Default open for this layout

    return sidebar

def toggle_sidebar(globals, sidebar):
    """Toggles sidebar visibility (optional for this layout, but good to have)."""
    # Implementation similar to your Pearl code, but maybe just hide/show
    if globals.sidebar_is_open:
        sidebar.hide()
        globals.sidebar_is_open = False
    else:
        sidebar.show()
        globals.sidebar_is_open = True
