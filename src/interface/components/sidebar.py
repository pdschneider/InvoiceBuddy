# src.interface.components.sidebar
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget,
    QListWidgetItem, QGraphicsDropShadowEffect
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
    QTimer, QRect
)
from PySide6.QtGui import (
    QColor, QPixmap, QPainter, QFont, QTransform,
    QIcon
)
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

    # Top Actions
    top_layout = QHBoxLayout()

    # Add Files Button
    add_btn = QPushButton("+ Add Files")
    add_btn.setFixedHeight(34)
    add_btn.setFixedWidth(140)
    add_btn.setStyleSheet("""
        QPushButton {
            background-color: #2ecc71; color: white;
            font-weight: bold; font-size: 13px;
            border: 1px solid #1f8c4c; border-radius: 17px;
            padding: 4px 14px; text-align: center;
        }
        QPushButton:hover { background-color: #38d97d; border-color: #22995a; }
        QPushButton:pressed { background-color: #27ae60; }
    """)

    # Drop Shadow Effect
    glow = QGraphicsDropShadowEffect(add_btn)
    glow.setBlurRadius(0)  # invisible until hovered
    glow.setColor(QColor(46, 204, 113, 160))
    glow.setOffset(0, 0)
    add_btn.setGraphicsEffect(glow)

    glow_anim = QPropertyAnimation(glow, b"blurRadius", add_btn)
    glow_anim.setDuration(180)
    glow_anim.setEasingCurve(QEasingCurve.OutCubic)

    def glow_in(e=None):
        glow_anim.stop()
        glow_anim.setStartValue(glow.blurRadius())
        glow_anim.setEndValue(22)
        glow_anim.start()

    def glow_out(e=None):
        glow_anim.stop()
        glow_anim.setStartValue(glow.blurRadius())
        glow_anim.setEndValue(0)
        glow_anim.start()

    add_btn.enterEvent = glow_in
    add_btn.leaveEvent = glow_out

    add_btn.setCursor(Qt.PointingHandCursor)
    add_btn.clicked.connect(lambda: add_files(globs))
    top_layout.addWidget(add_btn)

    # Refresh Inbox button (inbox view only; observer reconnect)
    refresh_btn = QPushButton("↻")
    refresh_btn.setFixedSize(34, 34)
    refresh_btn.setCursor(Qt.PointingHandCursor)
    refresh_btn.setToolTip("Reconnect & Refresh Inbox")
    refresh_btn.setStyleSheet("""
        QPushButton {
            background-color: transparent; color: #2ecc71;
            font-size: 16px; border: none;
        }
        QPushButton:hover { color: #38d97d; }
        QPushButton:pressed { color: #2bd06e; }
        QPushButton:disabled { color: #666; }
    """)
    refresh_btn.clicked.connect(lambda: (
        globs.reconnect_observers() if hasattr(globs, 'reconnect_observers')
        else globs.mailbox.refresh_files(globs.current_folder)))

    def _glyph_at_angle(deg, gray=False):
        pm = QPixmap(24, 24)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setPen(QColor(102, 102, 102) if gray else QColor(46, 204, 113))
        f = QFont()
        f.setPixelSize(18)
        p.setFont(f)
        # Rotate around center before drawing the glyph
        p.translate(12, 12)
        p.rotate(deg)
        p.drawText(QRect(-12, -12, 24, 24), Qt.AlignCenter, "↻")
        p.end()
        return pm

    _spin_angle = {"deg": 0}

    def _spin_tick():
        _spin_angle["deg"] = (_spin_angle["deg"] + 30) % 360
        refresh_btn.setIcon(QIcon(_glyph_at_angle(_spin_angle["deg"], gray=True)))
        refresh_btn.setText("")

    spin_timer = QTimer(refresh_btn)
    spin_timer.timeout.connect(_spin_tick)

    def set_refresh_spinning(spinning):
        if spinning:
            refresh_btn.setEnabled(False)
            refresh_btn.setIcon(QIcon(_glyph_at_angle(0, gray=True)))
            refresh_btn.setText("")
            spin_timer.start(50)
        else:
            spin_timer.stop()
            refresh_btn.setText("↻")
            refresh_btn.setIcon(QIcon())
            refresh_btn.setEnabled(True)

    globs.set_refresh_spinning = set_refresh_spinning

    globs.refresh_inbox_btn = refresh_btn

    top_layout.addStretch()

    layout.addLayout(top_layout)

    # Use QListWidget for easy selection handling
    nav_list = QListWidget()
    nav_list.setFocusPolicy(Qt.NoFocus)
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
    folders = ["Inbox", "Transactions", "Budget", "Insights", "Trash"]  # Eventual stack
    folders = ["Inbox", "Accounts", "Budget"]
    for folder in folders:
        item = QListWidgetItem(folder)
        item.setData(Qt.UserRole, folder.lower()) # Store key
        nav_list.addItem(item)

    nav_list.itemClicked.connect(lambda item: on_folder_click(item, globs))

    # Dock the ↻ inside the nav list, beside the "Inbox" row
    refresh_btn.setParent(nav_list.viewport())
    refresh_btn.hide()

    def _dock_refresh_btn(event, orig=nav_list.showEvent):
        orig(event)
        r = nav_list.visualRect(nav_list.indexFromItem(nav_list.item(0)))
        if r.isValid():
            refresh_btn.move(r.right() - 38,
                             r.top() + (r.height() - 34) // 2)
            refresh_btn.raise_()

    nav_list.showEvent = _dock_refresh_btn

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

    # Pages that take over the whole workspace
    if folder_key == 'budget':
        globs.page_stack.setCurrentWidget(globs.budget_page)
        return
    elif folder_key == 'accounts':
        globs.page_stack.setCurrentWidget(globs.accounts_page)
        return
    elif folder_key == 'insights':
        return  # Not implemented yet
    elif folder_key == 'trash':
        return  # Not implemented yet

    # File views always go back to page 0 (mailbox + preview)
    if hasattr(globs, 'page_stack'):
        globs.page_stack.setCurrentIndex(0)

    if folder_key == 'inbox':
        globs.current_folder = globs.inbox
    elif folder_key == 'transactions':
        return  # Not implemented yet
    else:
        return

    # Deselect, then let the state machine update the preview
    globs.selected_file = None

    # Collapse the transaction editor if open
    editor = getattr(globs, 'transaction_editor', None)
    if editor and editor.left_stack.currentWidget() is editor:
        editor.left_stack.setCurrentWidget(globs.mailbox)

    # Refresh the mailbox
    if hasattr(globs, 'mailbox') and globs.mailbox:
        globs.mailbox.refresh_files(globs.current_folder)
