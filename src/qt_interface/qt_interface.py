from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QFrame, QLabel, QPushButton, QSizeGrip)
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QCursor
from src.qt_interface.qt_components.qt_title_bar import TitleBar
from src.qt_interface.qt_components.qt_top_bar import create_top_bar
from src.qt_interface.qt_inbox import create_inbox_list
from src.qt_interface.qt_preview import create_preview_pane
from src.qt_interface.qt_components.qt_sidebar import create_sidebar, toggle_sidebar
from src.qt_interface.qt_settings.qt_settings import create_settings_panel, toggle_settings_panel
from src.qt_interface.qt_components.qt_mailbox import MailboxWidget
from src.managers.file_management import open_workbook, open_directory, open_logs, open_config
from src.utils.observers import setup_observer
from src.interface.setup.setup_wizard import create_wizard
from src.qt_interface.qt_components.qt_changelog import create_changelog_panel, toggle_changelog_panel
from src.qt_interface.qt_components.qt_about import create_about_panel, toggle_about_panel
import logging
import webbrowser
import os


def create_qt_interface(globals):
    """Creates the main interface in PySide."""
    
    # 1. SETUP WINDOW
    globals.window.setWindowTitle("Invoice Buddy")
    if globals.saved_width and globals.saved_height and globals.saved_x and globals.saved_y:
        globals.window.setGeometry(globals.saved_x, globals.saved_y, globals.saved_width, globals.saved_height)
    else:
        globals.window.resize(900, 850)

    # 2. MAKE IT BORDERLESS
    globals.window.setWindowFlags(Qt.FramelessWindowHint)

    # 3. CENTRAL WIDGET
    central_widget = QWidget()
    globals.window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    central_widget.setStyleSheet("background-color: #333339;")

    # 4. ADD NEW TITLE BAR (Draggable + Menus + Buttons)
    title_bar = TitleBar(globals.window)
    main_layout.addWidget(title_bar)
    globals.title_bar = title_bar

    # Populate File Title Menu
    file_menu = title_bar.menu_bar.addMenu("File")
    open_inbox_Q = file_menu.addAction("Open Inbox")

    workbook_paths = []
    seen_paths = set()
    for sheet in globals.sheet_data.get("sheets", []):
        wb_path = sheet.get("workbook", "")
        if wb_path and wb_path not in seen_paths:
            seen_paths.add(wb_path)
            workbook_paths.append((wb_path, os.path.splitext(os.path.basename(wb_path))[0]))

    if len(workbook_paths) <= 1:
        open_workbook_Q = file_menu.addAction("Open Workbook")
        if workbook_paths:
            open_workbook_Q.triggered.connect(lambda: open_workbook(globals, workbook_paths[0][0]))
        else:
            open_workbook_Q.setEnabled(False)
    else:
        workbook_menu = file_menu.addMenu("Open Workbook")
        for wb_path, wb_name in workbook_paths:
            action = workbook_menu.addAction(wb_name)
            action.triggered.connect(lambda checked, p=wb_path: open_workbook(globals, p))

    open_logs_Q = file_menu.addAction("Open Logs")
    open_config_Q = file_menu.addAction("Open Config")

    # Attach Actions to File Buttons
    open_inbox_Q.triggered.connect(lambda: open_directory(globals.inbox))
    open_logs_Q.triggered.connect(lambda: open_logs(globals))
    open_config_Q.triggered.connect(lambda: open_config(globals))
    
    # Populate Data Title Menu
    data_menu = title_bar.menu_bar.addMenu("Data")
    data_menu.addAction("Export / Import History (Coming Soon...)")
    data_menu.addAction("Export / Import Settings (Coming Soon...)")
    
    # Populate Help Title Menu
    help_menu = title_bar.menu_bar.addMenu("Help")
    view_changelog_Q = help_menu.addAction("View Changelog")
    open_wizard_Q = help_menu.addAction("Open Wizard")
    view_github_Q = help_menu.addAction("Open Github")
    view_about_Q = help_menu.addAction("About")

    # Attach Functions to Help Buttons
    view_about_Q.triggered.connect(lambda: toggle_about_panel(globals))
    view_changelog_Q.triggered.connect(lambda: toggle_changelog_panel(globals))
    open_wizard_Q.triggered.connect(lambda: create_wizard(globals))
    view_github_Q.triggered.connect(lambda: webbrowser.open(
        url="https://github.com/pdschneider/InvoiceBuddy"))

    # Add the Top Bar
    top_bar = create_top_bar(globals)
    main_layout.addWidget(top_bar)
    globals.top_bar = top_bar

    # Panels for Main Workspace
    workspace_widget = QWidget()
    workspace_layout = QHBoxLayout(workspace_widget)
    workspace_layout.setContentsMargins(5, 0, 0, 0)
    workspace_layout.setSpacing(5)
    workspace_widget.setStyleSheet("background-color: #333339;")

    sidebar = create_sidebar(globals)
    workspace_layout.addWidget(sidebar)

    splitter = QSplitter(Qt.Horizontal)
    mailbox = MailboxWidget(globals)
    splitter.addWidget(mailbox)
    mailbox.setMinimumWidth(300)
    preview_pane = create_preview_pane(globals)
    splitter.addWidget(preview_pane)
    splitter.setSizes([400, 550])
    splitter.setChildrenCollapsible(False)
    workspace_layout.addWidget(splitter)

    main_layout.addWidget(workspace_widget)

    # Settings Panel
    create_settings_panel(globals)

    # Changelog Panel
    create_changelog_panel(globals)

    # About Panel
    create_about_panel(globals)

    # Dim Overlay for Panels
    dim_overlay = QWidget(globals.window)
    dim_overlay.setAttribute(Qt.WA_StyledBackground, True)
    dim_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
    dim_overlay.hide()

    def close_all_panels(event):
        """Closes all panels and the overlay when overlay is clicked."""
        if hasattr(globals, 'settings_panel') and globals.settings_panel.isVisible():
            globals.settings_panel.hide()
        if hasattr(globals, 'changelog_panel') and globals.changelog_panel.isVisible():
            globals.changelog_panel.hide()
        if hasattr(globals, 'about_panel') and globals.about_panel.isVisible():
            globals.about_panel.hide()
        globals.dim_overlay.hide()

    dim_overlay.mousePressEvent = close_all_panels

    # Store references
    globals.splitter = splitter
    globals.mailbox = mailbox
    globals.preview_pane = preview_pane
    globals.sidebar = sidebar
    globals.dim_overlay = dim_overlay

    # Set up Watchdog Observers
    def update_mailbox_view():
        if hasattr(globals, 'current_folder') and globals.current_folder:
            mailbox.refresh_files(globals.current_folder)
        else:
            logging.warning("Cannot refresh mailbox: globals.current_folder is not set.")

    globals.observers = {}
    if hasattr(globals, 'current_folder') and globals.current_folder:
        observer = setup_observer(globals, globals.current_folder, key='current_folder', callback=update_mailbox_view)
        if observer:
            globals.observers['current_folder'] = observer
            update_mailbox_view()

    # Enable Cursor Feedback / Resize
    RESIZE_MARGIN = 10

    # State tracking
    globals.resize_state = {
        "active": False,
        "edge": None,
        "last_pos": None,
        "start_geom": None
    }

    def get_resize_edge_from_global(window, global_pos):
        """
        Detects edge based on GLOBAL coordinates.
        This is the most reliable way for frameless windows.
        """
        geom = window.frameGeometry()
        x, y = global_pos.x(), global_pos.y()
        
        left = x <= geom.left() + RESIZE_MARGIN
        right = x >= geom.right() - RESIZE_MARGIN
        top = y <= geom.top() + RESIZE_MARGIN
        bottom = y >= geom.bottom() - RESIZE_MARGIN
        
        if top and left: return "TL"
        if top and right: return "TR"
        if bottom and left: return "BL"
        if bottom and right: return "BR"
        if left: return "L"
        if right: return "R"
        if top: return "T"
        if bottom: return "B"
        return None

    def get_cursor_shape(edge):
        """Returns the Qt.CursorShape enum."""
        shapes = {
            "L": Qt.SizeHorCursor, "R": Qt.SizeHorCursor,
            "T": Qt.SizeVerCursor, "B": Qt.SizeVerCursor,
            "TL": Qt.SizeFDiagCursor, "BR": Qt.SizeFDiagCursor,
            "TR": Qt.SizeBDiagCursor, "BL": Qt.SizeBDiagCursor,
            None: Qt.ArrowCursor
        }
        return shapes.get(edge, Qt.ArrowCursor)

    def handle_window_mouse_event(obj, event):
        if event.type() == QEvent.MouseMove:
            global_pos = event.globalPosition().toPoint()
            
            if globals.resize_state["active"]:
                # --- RESIZE LOGIC ---
                if globals.resize_state["last_pos"]:
                    delta = global_pos - globals.resize_state["last_pos"]
                    geom = globals.resize_state["start_geom"]
                    edge = globals.resize_state["edge"]
                    
                    if edge in ["L", "TL", "BL"]:
                        new_left = geom.left() + delta.x()
                        if new_left < geom.right() - 200: geom.setLeft(new_left)
                    if edge in ["R", "TR", "BR"]:
                        new_right = geom.right() + delta.x()
                        if new_right > geom.left() + 200: geom.setRight(new_right)
                    if edge in ["T", "TL", "TR"]:
                        new_top = geom.top() + delta.y()
                        if new_top < geom.bottom() - 150: geom.setTop(new_top)
                    if edge in ["B", "BL", "BR"]:
                        new_bottom = geom.bottom() + delta.y()
                        if new_bottom > geom.top() + 150: geom.setBottom(new_bottom)
                    
                    globals.window.setGeometry(geom)
                    globals.dim_overlay.resize(globals.window.width(), globals.window.height() - 35)
                    globals.dim_overlay.move(0, 35)
                
                globals.resize_state["last_pos"] = global_pos
                return True
            
            else:
                # --- CURSOR LOGIC ONLY ---
                # Detect edge using GLOBAL coordinates
                edge = get_resize_edge_from_global(globals.window, global_pos)
                target_shape = get_cursor_shape(edge)
                
                # Only set cursor if it changed (prevents flicker/performance hit)
                current_shape = globals.window.cursor().shape()
                if current_shape != target_shape:
                    globals.window.setCursor(target_shape)
                
                return False

        elif event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                global_pos = event.globalPosition().toPoint()
                edge = get_resize_edge_from_global(globals.window, global_pos)
                
                if edge:
                    globals.resize_state["active"] = True
                    globals.resize_state["edge"] = edge
                    globals.resize_state["last_pos"] = global_pos
                    globals.resize_state["start_geom"] = globals.window.frameGeometry()
                    return True
        
        elif event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                if globals.resize_state["active"]:
                    globals.resize_state["active"] = False
                    globals.resize_state["edge"] = None
                    globals.resize_state["last_pos"] = None
                    globals.resize_state["start_geom"] = None
                    globals.window.setCursor(Qt.ArrowCursor)
                    return True
        
        return False

    # Enable mouse tracking so we get MouseMove even without pressing
    globals.window.setMouseTracking(True)

    # Install Event Filter
    original_event = globals.window.event
    def custom_event(event):
        if handle_window_mouse_event(globals.window, event):
            return True
        return original_event(event)

    globals.window.event = custom_event

    # Show the Window
    globals.window.setMinimumSize(800, 750)
    globals.window.show()
    if hasattr(globals, 'current_folder'):
        mailbox.refresh_files(globals.current_folder)

    # Update position on resize
    original_resize = globals.window.resizeEvent

    def custom_resize(event):
        original_resize(event)
        QTimer.singleShot(0, update_overlay_geometry)
    
    def update_overlay_geometry():
        """Updates overlay (settings + changelog) when resizing the window."""
        globals.dim_overlay.resize(globals.window.width(), globals.window.height() - 35)
        globals.dim_overlay.move(0, 35)

        for panel_attr in ['settings_panel', 'changelog_panel', 'about_panel']:
            panel = getattr(globals, panel_attr, None)
            if panel and panel.isVisible():

                # Dynamic resize for settings panel only
                if panel_attr == 'settings_panel':
                    overlay_w = max(650, int(globals.window.width() * 0.85))
                    overlay_h = max(550, int(globals.window.height() * 0.85))
                    panel.resize(overlay_w, overlay_h)
                else:
                    overlay_w = max(globals.window.width(), 200)
                    overlay_h = max(globals.window.height() - 35, 150)

                globals.dim_overlay.resize(globals.window.width(), globals.window.height() - 35)
                globals.dim_overlay.move(0, 35)

                parent_w = globals.window.width()
                parent_h = globals.window.height()
                panel_w = panel.width()
                panel_h = panel.height()
                x = (parent_w - panel_w) // 2
                y = max(45, (parent_h - panel_h) // 2)
                panel.move(x, y)

    globals.dim_overlay.resize(globals.window.width(), globals.window.height() - 35)
    globals.dim_overlay.move(0, 35)
    globals.window.resizeEvent = custom_resize
