# src/qt_interface/qt_settings/qt_settings.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget
from PySide6.QtCore import Qt
from src.qt_interface.qt_settings.general_qt import create_general_settings_tab
from src.utils.save_qt import save_qt_settings

def create_settings_panel(globals):
    """Creates the settings overlay panel with tabs."""

    # Main container
    settings_panel = QWidget(globals.window)
    settings_panel.setFixedSize(650, 550)
    settings_panel.setStyleSheet("""
        background-color: rgb(43, 43, 43);
        border-radius: 10px;
    """)
    settings_panel.hide()

    layout = QVBoxLayout(settings_panel)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)

    # === HEADER ===
    header_layout = QVBoxLayout()
    title = QLabel("Settings")
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
    header_layout.addWidget(title)
    layout.addLayout(header_layout)

    # === TABS ===
    tabs = QTabWidget()
    tabs.setStyleSheet("""
        QTabWidget::pane {
            border: 1px solid #444;
            border-radius: 5px;
            background-color: #2b2b2b;
        }
        QTabBar::tab {
            background-color: #333;
            color: #aaa;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }
        QTabBar::tab:selected {
            background-color: #2b2b2b;
            color: #2ecc71;
            font-weight: bold;
        }
    """)

    # Create General tab
    general_tab = create_general_settings_tab(globals)
    tabs.addTab(general_tab, "General")

    # Empty tabs for now
    connections_tab = QWidget()
    connections_tab.setStyleSheet("background-color: transparent;")
    tabs.addTab(connections_tab, "Connections")

    advanced_tab = QWidget()
    advanced_tab.setStyleSheet("background-color: transparent;")
    tabs.addTab(advanced_tab, "Advanced")

    layout.addWidget(tabs)

    # === CLOSE BUTTON ===
    close_btn = QPushButton("Save")
    close_btn.setStyleSheet("""
        QPushButton {
            background-color: #3a3a3a;
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
    """)
    close_btn.setCursor(Qt.PointingHandCursor)
    def on_close_click():
        """Save settings before closing the panel."""
        save_qt_settings(globals)  # Save first
        toggle_settings_panel(globals)  # Then close

    close_btn.clicked.connect(on_close_click)
    layout.addWidget(close_btn)

    # Store references
    globals.settings_panel = settings_panel
    globals.settings_tabs = tabs

    return settings_panel

def toggle_settings_panel(globals):
    """Shows or hides the settings panel."""
    if globals.settings_panel.isVisible():
        globals.settings_panel.hide()
    else:
        parent_w = globals.window.width()
        parent_h = globals.window.height()
        panel_w = globals.settings_panel.width()
        panel_h = globals.settings_panel.height()

        x = (parent_w - panel_w) // 2
        y = (parent_h - panel_h) // 2

        globals.settings_panel.move(x, y)
        globals.settings_panel.show()
