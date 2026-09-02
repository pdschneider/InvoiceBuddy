# src/qt_interface/qt_settings/qt_settings.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget
from PySide6.QtCore import Qt
from src.qt_interface.qt_settings.general_qt import create_general_settings_tab
from src.qt_interface.qt_settings.qt_advanced import create_advanced_settings_tab
from src.qt_interface.qt_settings.qt_paths import create_paths_settings_tab
from src.qt_interface.qt_settings.qt_spreadsheet import create_spreadsheet_settings_tab
from src.utils.save_qt import save_qt_settings
from src.qt_interface.qt_styles import dark


def create_settings_panel(globs):
    """Creates the settings overlay panel with tabs."""

    # Main container
    settings_panel = QWidget(globs.window)
    settings_panel.setMinimumSize(650, 550)
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
    tabs.setStyleSheet(dark.tabs)

    # General tab
    general_tab = create_general_settings_tab(globs)
    tabs.addTab(general_tab, "General")

    # Paths tab
    paths_tab = create_paths_settings_tab(globs)
    tabs.addTab(paths_tab, "Paths")

    # Spreadsheet tab
    spreadsheet_tab = create_spreadsheet_settings_tab(globs)
    tabs.addTab(spreadsheet_tab, "Spreadsheet")

    # Advanced tab
    advanced_tab = create_advanced_settings_tab(globs)
    tabs.addTab(advanced_tab, "Advanced")

    layout.addWidget(tabs)

    # Save Button
    save_btn = QPushButton("Save")
    save_btn.setStyleSheet(dark.save_button)
    save_btn.setCursor(Qt.PointingHandCursor)
    def on_close_click():
        """Save settings before closing the panel."""
        save_qt_settings(globs)  # Save first
        toggle_settings_panel(globs)  # Then close

    save_btn.clicked.connect(on_close_click)
    layout.addWidget(save_btn)

    # Store references
    globs.settings_panel = settings_panel
    globs.settings_tabs = tabs

    return settings_panel

def toggle_settings_panel(globs):
    """Shows or hides the settings panel."""
    if globs.settings_panel.isVisible():
        globs.settings_panel.hide()
        globs.dim_overlay.hide()
    else:
        # Hide any changelog panels currently open
        if hasattr(globs, 'changelog_panel') and globs.changelog_panel.isVisible():
            globs.changelog_panel.hide()

        tb_h = globs.title_bar.height()
        globs.dim_overlay.resize(globs.window.width(), globs.window.height() - tb_h)
        globs.dim_overlay.move(0, tb_h)
        globs.dim_overlay.show()
        globs.dim_overlay.raise_()

        # Dynamic size: 85% of window, but never below minimum (650x550)
        parent_w = globs.window.width()
        parent_h = globs.window.height()
        panel_w = max(650, int(parent_w * 0.85))
        panel_h = max(550, int(parent_h * 0.85))
        globs.settings_panel.resize(panel_w, panel_h)

        x = (parent_w - panel_w) // 2
        y = (parent_h - panel_h) // 2

        globs.settings_panel.move(x, y)
        globs.settings_panel.show()
        globs.settings_panel.raise_()
