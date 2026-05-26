# src/qt_interface/qt_components/qt_top_bar.py
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from src.qt_interface.qt_components.qt_sidebar import toggle_sidebar
from src.qt_interface.qt_settings.qt_settings import toggle_settings_panel

def create_top_bar(globals):
    """Creates the top navigation bar for Invoice Buddy."""
    top_bar_widget = QWidget()
    top_bar_widget.setFixedHeight(50)

    top_bar_layout = QHBoxLayout(top_bar_widget)
    top_bar_layout.setContentsMargins(10, 5, 10, 5)
    top_bar_layout.setSpacing(10)

    # == Left Side ==
    hamburger_button = QPushButton("☰")
    hamburger_button.setFixedSize(40, 40)
    hamburger_button.setCursor(QCursor(Qt.PointingHandCursor))
    hamburger_button.clicked.connect(lambda: toggle_sidebar(globals, globals.sidebar))
    top_bar_layout.addWidget(hamburger_button)

    # App Title
    title_label = QLabel("Invoice Buddy")
    title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
    top_bar_layout.addWidget(title_label)

    top_bar_layout.addSpacing(20)

    # == Center: Search Bar ==
    search_bar = QLineEdit()
    search_bar.setPlaceholderText("Search by Vendor, Invoice #, or Date...")
    search_bar.setFixedWidth(300)
    search_bar.setStyleSheet("""
        QLineEdit {
            background-color: #333;
            color: white;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 5px 10px;
        }
        QLineEdit:focus {
            border: 1px solid #2ecc71;
        }
    """)
    top_bar_layout.addWidget(search_bar)

    top_bar_layout.addStretch()

    # == Right Side ==
    # Settings
    settings_button = QPushButton("⚙")
    settings_button.setFixedSize(40, 40)
    settings_button.setCursor(QCursor(Qt.PointingHandCursor))
    settings_button.setStyleSheet("background-color: transparent; color: white; font-size: 18px;")
    settings_button.clicked.connect(lambda: toggle_settings_panel(globals))
    top_bar_layout.addWidget(settings_button)

    # Help/About
    help_button = QPushButton("?")
    help_button.setFixedSize(40, 40)
    help_button.setCursor(QCursor(Qt.PointingHandCursor))
    help_button.setStyleSheet("background-color: transparent; color: white; font-size: 18px;")
    top_bar_layout.addWidget(help_button)

    return top_bar_widget
