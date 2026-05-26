# src/qt_interface/qt_inbox.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLabel, QFrame)
from PySide6.QtCore import Qt

def create_inbox_list(globals):
    """Creates the central file list pane."""
    
    pane = QWidget()
    layout = QVBoxLayout(pane)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)

    # Table
    table = QTableWidget()
    table.setColumnCount(1)
    table.setHorizontalHeaderLabels(["Inbox"])
    
    # Styling
    table.setStyleSheet("""
        QTableWidget {
            background-color: #2b2b2b;
            color: white;
            gridline-color: #444;
            selection-background-color: #3a3a3a;
            selection-color: #2ecc71;
        }
        QHeaderView::section {
            background-color: #333;
            color: #aaa;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
    """)

    # Configure headers
    header_view = table.horizontalHeader()
    header_view.setSectionResizeMode(QHeaderView.Stretch)

    layout.addWidget(table, stretch=1)

    # Store reference
    globals.file_table = table

    return pane
