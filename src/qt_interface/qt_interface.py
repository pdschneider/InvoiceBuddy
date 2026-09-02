# src/qt_interface/qt_interface.py
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter)
from PySide6.QtCore import Qt, QEvent, QTimer, QObject
from src.qt_interface.qt_components.qt_title_bar import TitleBar
from src.qt_interface.qt_components.qt_top_bar import create_top_bar
from src.qt_interface.qt_preview import create_preview_pane
from src.qt_interface.qt_components.qt_sidebar import create_sidebar
from src.qt_interface.qt_settings.qt_settings import create_settings_panel
from src.qt_interface.qt_components.qt_mailbox import MailboxWidget
from src.managers.file_management import (open_workbook, open_directory,
                                          open_logs, open_config)
from src.utils.observers import setup_observer
from src.interface.setup.setup_wizard import create_wizard
from src.qt_interface.qt_components.qt_changelog import create_changelog_panel, toggle_changelog_panel
from src.qt_interface.qt_components.qt_about import create_about_panel, toggle_about_panel
from src.qt_interface.qt_components.qt_bug_report import create_report_panel, toggle_report_panel
from src.qt_interface.qt_components.qt_docs import create_docs_panel, toggle_docs_panel
from src.utils.icons import load_qt_icons
import logging
import os


class WindowResizeEventFilter(QObject):
    """
    Global event filter to handle cursor shape changes for frameless window resizing.
    This ensures mouse moves over child widgets also trigger edge detection.
    """
    
    def __init__(self, window, resize_margin=10):
        super().__init__()
        self.window = window
        self.resize_margin = resize_margin
        self.last_cursor_shape = Qt.ArrowCursor
        self.resize_state = {
            "active": False,
            "edge": None,
            "last_pos": None,
            "start_geom": None
        }
        
    def get_resize_edge_from_global(self, global_pos):
        geom = self.window.frameGeometry()
        x, y = global_pos.x(), global_pos.y()
        
        left = x <= geom.left() + self.resize_margin
        right = x >= geom.right() - self.resize_margin
        top = y <= geom.top() + self.resize_margin
        bottom = y >= geom.bottom() - self.resize_margin
        
        if top and left: return "TL"
        if top and right: return "TR"
        if bottom and left: return "BL"
        if bottom and right: return "BR"
        if left: return "L"
        if right: return "R"
        if top: return "T"
        if bottom: return "B"
        return None
    
    def get_cursor_shape(self, edge):
        shapes = {
            "L": Qt.SizeHorCursor, "R": Qt.SizeHorCursor,
            "T": Qt.SizeVerCursor, "B": Qt.SizeVerCursor,
            "TL": Qt.SizeFDiagCursor, "BR": Qt.SizeFDiagCursor,
            "TR": Qt.SizeBDiagCursor, "BL": Qt.SizeBDiagCursor,
            None: Qt.ArrowCursor
        }
        return shapes.get(edge, Qt.ArrowCursor)
    
    def eventFilter(self, obj, event):
        # Skip resize logic if a popup/menu is open
        if QApplication.activePopupWidget():
            return False
        if event.type() == QEvent.MouseMove:
            global_pos = event.globalPosition().toPoint()
            
            # --- Active resize drag ---
            if self.resize_state["active"]:
                start_geom = self.resize_state["start_geom"]
                start_pos = self.resize_state["last_pos"]
                
                total_delta = global_pos - start_pos
                edge = self.resize_state["edge"]
                
                min_w = self.window.minimumWidth()
                min_h = self.window.minimumHeight()
                
                # Start from original geometry each frame
                new_left = start_geom.left()
                new_right = start_geom.right()
                new_top = start_geom.top()
                new_bottom = start_geom.bottom()
                
                if edge in ["L", "TL", "BL"]:
                    new_left = start_geom.left() + total_delta.x()
                    if new_left > start_geom.right() - min_w:
                        new_left = start_geom.right() - min_w
                if edge in ["R", "TR", "BR"]:
                    new_right = start_geom.right() + total_delta.x()
                    if new_right < start_geom.left() + min_w:
                        new_right = start_geom.left() + min_w
                if edge in ["T", "TL", "TR"]:
                    new_top = start_geom.top() + total_delta.y()
                    if new_top > start_geom.bottom() - min_h:
                        new_top = start_geom.bottom() - min_h
                if edge in ["B", "BL", "BR"]:
                    new_bottom = start_geom.bottom() + total_delta.y()
                    if new_bottom < start_geom.top() + min_h:
                        new_bottom = start_geom.top() + min_h
                
                self.window.setGeometry(new_left, new_top, new_right - new_left, new_bottom - new_top)
                
                return True
            
            # --- Cursor shape only ---
            edge = self.get_resize_edge_from_global(global_pos)
            target_shape = self.get_cursor_shape(edge)
            
            if self.last_cursor_shape != target_shape:
                self.window.setCursor(target_shape)
                self.last_cursor_shape = target_shape
                
        elif event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                global_pos = event.globalPosition().toPoint()
                edge = self.get_resize_edge_from_global(global_pos)
                
                if edge:
                    self.resize_state["active"] = True
                    self.resize_state["edge"] = edge
                    self.resize_state["last_pos"] = global_pos
                    self.resize_state["start_geom"] = self.window.frameGeometry()
                    return True
        
        elif event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                if self.resize_state["active"]:
                    self.resize_state["active"] = False
                    self.resize_state["edge"] = None
                    self.resize_state["last_pos"] = None
                    self.resize_state["start_geom"] = None
                    self.window.setCursor(Qt.ArrowCursor)
                    return True
        
        return False


def create_qt_interface(globs):
    """Creates the main interface in PySide."""
    
    # Set Up Window
    globs.window.setWindowTitle("Invoice Buddy")
    if globs.saved_width and globs.saved_height and globs.saved_x and globs.saved_y:
        globs.window.setGeometry(globs.saved_x, globs.saved_y, globs.saved_width, globs.saved_height)
    else:
        globs.window.resize(900, 850)

    # Make Window Borderless
    globs.window.setWindowFlags(Qt.FramelessWindowHint)

    # Create Central Widget
    central_widget = QWidget()
    globs.window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    central_widget.setStyleSheet("background-color: #333339;")

    # Load Icons
    load_qt_icons(globs)

    # Add Title Bar
    title_bar = TitleBar(globs.window)
    main_layout.addWidget(title_bar)
    globs.title_bar = title_bar

    # Populate File Title Menu
    file_menu = title_bar.menu_bar.addMenu("File")
    open_inbox_Q = file_menu.addAction("Inbox")

    workbook_paths = []
    seen_paths = set()
    for sheet in globs.sheet_data.get("sheets", []):
        wb_path = sheet.get("workbook", "")
        if wb_path and wb_path not in seen_paths:
            seen_paths.add(wb_path)
            workbook_paths.append((wb_path, os.path.splitext(os.path.basename(wb_path))[0]))

    if len(workbook_paths) <= 1:
        open_workbook_Q = file_menu.addAction("Workbook")
        if workbook_paths:
            open_workbook_Q.triggered.connect(lambda: open_workbook(globs, workbook_paths[0][0]))
        else:
            open_workbook_Q.setEnabled(False)
    else:
        workbook_menu = file_menu.addMenu("Workbook")
        for wb_path, wb_name in workbook_paths:
            action = workbook_menu.addAction(wb_name)
            action.triggered.connect(lambda checked, p=wb_path: open_workbook(globs, p))

    open_archive_Q = file_menu.addAction("Archive")
    open_logs_Q = file_menu.addAction("Logs")
    open_config_Q = file_menu.addAction("Config")

    # Attach Actions to File Buttons
    open_inbox_Q.triggered.connect(lambda: open_directory(globs, globs.inbox))
    open_archive_Q.triggered.connect(lambda: open_directory(globs, globs.archive))
    open_logs_Q.triggered.connect(lambda: open_logs(globs))
    open_config_Q.triggered.connect(lambda: open_config(globs))
    
    # Populate Data Title Menu
    data_menu = title_bar.menu_bar.addMenu("Data")
    data_menu.addAction("Export / Import History (Coming Soon...)")
    data_menu.addAction("Export / Import Settings (Coming Soon...)")
    
    # Populate Help Title Menu
    help_menu = title_bar.menu_bar.addMenu("Help")
    view_changelog_Q = help_menu.addAction("Changelog")
    open_wizard_Q = help_menu.addAction("Wizard")
    open_report_Q = help_menu.addAction("Bug Report")
    view_about_Q = help_menu.addAction("About")

    # Attach Functions to Help Buttons
    view_about_Q.triggered.connect(lambda: toggle_about_panel(globs))
    view_changelog_Q.triggered.connect(lambda: toggle_changelog_panel(globs))
    open_wizard_Q.triggered.connect(lambda: create_wizard(globs))
    open_report_Q.triggered.connect(lambda: toggle_report_panel(globs))

    # Style Menus with Distinct Hover States
    menu_stylesheet = """
        QMenuBar::item { color: #aaaaaa; }
        QMenuBar::item:selected { color: #ffffff; }
        QMenu::item { color: #aaaaaa; }
        QMenu::item:selected { color: #ffffff; }
    """
    globs.window.setStyleSheet(menu_stylesheet)

    # Add the Top Bar
    top_bar = create_top_bar(globs)
    main_layout.addWidget(top_bar)
    globs.top_bar = top_bar

    # Panels for Main Workspace
    workspace_widget = QWidget()
    workspace_layout = QHBoxLayout(workspace_widget)
    workspace_layout.setContentsMargins(5, 0, 0, 0)
    workspace_layout.setSpacing(5)
    workspace_widget.setStyleSheet("background-color: #333339;")

    sidebar = create_sidebar(globs)
    workspace_layout.addWidget(sidebar)

    splitter = QSplitter(Qt.Horizontal)
    mailbox = MailboxWidget(globs)
    splitter.addWidget(mailbox)
    mailbox.setMinimumWidth(300)
    preview_pane = create_preview_pane(globs)
    splitter.addWidget(preview_pane)
    splitter.setSizes([400, 550])
    splitter.setChildrenCollapsible(False)
    workspace_layout.addWidget(splitter)

    main_layout.addWidget(workspace_widget)

    # Settings Panel
    create_settings_panel(globs)

    # Changelog Panel
    create_changelog_panel(globs)

    # About Panel
    create_about_panel(globs)

    # Report Panel
    create_report_panel(globs)

    # Docs Panel
    try:
        create_docs_panel(globs)
    except Exception as e:
        logging.error(f"Unable to create docs panel due to: {e}")

    # Dim Overlay for Panels
    dim_overlay = QWidget(globs.window)
    dim_overlay.setAttribute(Qt.WA_StyledBackground, True)
    dim_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
    dim_overlay.hide()

    def close_all_panels(event):
        """Closes all panels and the overlay when overlay is clicked."""
        if hasattr(globs, 'settings_panel') and globs.settings_panel.isVisible():
            globs.settings_panel.hide()
        if hasattr(globs, 'changelog_panel') and globs.changelog_panel.isVisible():
            globs.changelog_panel.hide()
        if hasattr(globs, 'about_panel') and globs.about_panel.isVisible():
            globs.about_panel.hide()
        if hasattr(globs, 'report_panel') and globs.report_panel.isVisible():
                    globs.report_panel.hide()
        if hasattr(globs, 'docs_panel') and globs.docs_panel.isVisible():
                    globs.docs_panel.hide()
        globs.dim_overlay.hide()

    dim_overlay.mousePressEvent = close_all_panels

    # Store references
    globs.splitter = splitter
    globs.mailbox = mailbox
    globs.preview_pane = preview_pane
    globs.sidebar = sidebar
    globs.dim_overlay = dim_overlay

    # Set up Watchdog Observers
    def update_mailbox_view():
        if hasattr(globs, 'current_folder') and globs.current_folder:
            mailbox.refresh_files(globs.current_folder)
        else:
            logging.warning("Cannot refresh mailbox: globs.current_folder is not set.")

    globs.observers = {}
    if hasattr(globs, 'current_folder') and globs.current_folder:
        observer = setup_observer(globs, globs.current_folder, key='current_folder', callback=update_mailbox_view)
        if observer:
            globs.observers['current_folder'] = observer
            update_mailbox_view()

    # Enable Cursor Feedback / Resize
    RESIZE_MARGIN = 10

    # State tracking
    globs.resize_state = {
        "active": False,
        "edge": None,
        "last_pos": None,
        "start_geom": None
    }

    # Enable mouse tracking so we get MouseMove even without pressing
    globs.window.setMouseTracking(True)
    for child in globs.window.findChildren(QWidget):
        child.setMouseTracking(True)

    # Install Global Event Filter for Cursor Changes
    resize_filter = WindowResizeEventFilter(globs.window)
    globs.app.installEventFilter(resize_filter)
    globs.resize_filter = resize_filter  # Keep it alive!
    print(f"Event filter installed: {globs.resize_filter is not None}")

    # Show the Window
    globs.window.setMinimumSize(800, 750)
    globs.window.show()
    if hasattr(globs, 'current_folder'):
        mailbox.refresh_files(globs.current_folder)

    # Update position on resize
    original_resize = globs.window.resizeEvent

    def custom_resize(event):
        original_resize(event)
        QTimer.singleShot(0, update_overlay_geometry)

    def update_overlay_geometry():
        """Updates overlay when resizing the window."""
        tb_h = globs.title_bar.height()
        globs.dim_overlay.resize(globs.window.width(), globs.window.height() - tb_h)
        globs.dim_overlay.move(0, tb_h)

        for panel_attr in ['settings_panel', 'changelog_panel',
                           'about_panel', 'report_panel', 'docs_panel']:
            panel = getattr(globs, panel_attr, None)
            if panel and panel.isVisible():

                # Dynamic resize for settings panel only
                if panel_attr == 'settings_panel' or panel_attr == 'docs_panel':
                    overlay_w = max(650, int(globs.window.width() * 0.85))
                    overlay_h = max(550, int(globs.window.height() * 0.85))
                    panel.resize(overlay_w, overlay_h)
                else:
                    overlay_w = max(globs.window.width(), 200)
                    overlay_h = max(globs.window.height() - tb_h, 150)

                globs.dim_overlay.resize(globs.window.width(), globs.window.height() - tb_h)
                globs.dim_overlay.move(0, tb_h)

                parent_w = globs.window.width()
                parent_h = globs.window.height()
                panel_w = panel.width()
                panel_h = panel.height()
                x = (parent_w - panel_w) // 2
                y = max(45, (parent_h - panel_h) // 2)
                panel.move(x, y)

    tb_h = globs.title_bar.height()
    globs.dim_overlay.resize(globs.window.width(), globs.window.height() - tb_h)
    globs.dim_overlay.move(0, tb_h)
    globs.window.resizeEvent = custom_resize
