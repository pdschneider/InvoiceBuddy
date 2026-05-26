from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QFrame, QLabel, QPushButton, QSizeGrip)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QCursor
from src.qt_interface.qt_components.qt_title_bar import TitleBar
from src.qt_interface.qt_components.qt_top_bar import create_top_bar
from src.qt_interface.qt_inbox import create_inbox_list
from src.qt_interface.qt_preview import create_preview_pane
from src.qt_interface.qt_components.qt_sidebar import create_sidebar, toggle_sidebar
from src.qt_interface.qt_settings.qt_settings import create_settings_panel, toggle_settings_panel
from src.qt_interface.qt_components.qt_mailbox import MailboxWidget
from src.utils.observers import setup_observer
import logging


def create_interface(globals):
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

    # 4. ADD NEW TITLE BAR (Draggable + Menus + Buttons)
    title_bar = TitleBar(globals.window)
    main_layout.addWidget(title_bar)
    globals.title_bar = title_bar

    # 5. POPULATE MENUS IN TITLE BAR
    file_menu = title_bar.menu_bar.addMenu("File")
    file_menu.addAction("Open Logs")
    file_menu.addAction("Open Config")
    
    data_menu = title_bar.menu_bar.addMenu("Data")
    data_menu.addAction("Export / Import History")
    data_menu.addAction("Export / Import Settings")
    
    help_menu = title_bar.menu_bar.addMenu("Help")
    help_menu.addAction("View Changelog")
    help_menu.addAction("Open Wizard")
    help_menu.addAction("View Github")

    # 6. ADD YOUR EXISTING TOP BAR (Unchanged)
    top_bar = create_top_bar(globals)
    main_layout.addWidget(top_bar)
    globals.top_bar = top_bar

    # 7. MAIN WORKSPACE
    splitter = QSplitter(Qt.Horizontal)
    sidebar = create_sidebar(globals)
    splitter.addWidget(sidebar)
    mailbox = MailboxWidget(globals)
    splitter.addWidget(mailbox)
    preview_pane = create_preview_pane(globals)
    splitter.addWidget(preview_pane)
    splitter.setSizes([250, 400, 550])
    main_layout.addWidget(splitter)

    # 8. SETTINGS PANEL
    create_settings_panel(globals)

    # Store refs
    globals.splitter = splitter
    globals.mailbox = mailbox
    globals.preview_pane = preview_pane
    globals.sidebar = sidebar

    # 9. WATCHDOG
    def update_mailbox_view():
        if hasattr(globals, 'inbox') and globals.inbox:
            mailbox.refresh_files(globals.inbox)
        else:
            logging.warning("Cannot refresh mailbox: globals.inbox is not set.")

    globals.observers = {}
    if hasattr(globals, 'inbox') and globals.inbox:
        observer = setup_observer(globals, globals.inbox, key='inbox', callback=update_mailbox_view)
        if observer:
            globals.observers['inbox'] = observer
            update_mailbox_view()

    # 9.5 ENABLE CURSOR FEEDBACK & RESIZE (SIMPLIFIED)
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

    # 10. SHOW
    globals.window.show()
    if hasattr(globals, 'inbox'):
        mailbox.refresh_files(globals.inbox)

    # Update position on resize
    original_resize = globals.window.resizeEvent
    def custom_resize(event):
        original_resize(event)
    globals.window.resizeEvent = custom_resize
