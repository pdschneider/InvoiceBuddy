# src.interface.components.sidebar
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget,
    QListWidgetItem, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor
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
    folders = ["Inbox", "Budget"]
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

    # Pages that take over the whole workspace
    if folder_key == 'budget':
        globs.page_stack.setCurrentWidget(globs.budget_page)
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
