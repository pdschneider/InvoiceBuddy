# src/qt_interface/qt_components/qt_title_bar.py
from PySide6.QtWidgets import (QWidget, QHBoxLayout,
                               QMenuBar, QToolButton,
                               QMenu, QStyle)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QAction


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.parent_window = parent
        
        # Set Style
        self.setFixedHeight(35)
        self.setStyleSheet("""
            TitleBar {
                background-color: #1a1a1a;
                border-bottom: 0px solid transparent;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)
        layout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        # Menus
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setNativeMenuBar(False)
        self.menu_bar.setStyleSheet("""
            QMenuBar { background-color: transparent; border: none; color: white; margin-top: 4px;}
            QMenuBar::item { padding: 5px 10px; color: #ccc; }
            QMenuBar::item:selected { background-color: #444; color: white; }
        """)

        layout.addWidget(self.menu_bar, 0, Qt.AlignVCenter)
        layout.addStretch()

        # Window Controls
        self.min_btn = QToolButton(self)
        self.min_btn.setText("_")
        self.min_btn.setFixedSize(30, 30)
        self.min_btn.setStyleSheet("""
    QToolButton { color: white; border: none; background: transparent; border-radius: 15px; font-size: 17px; }
    QToolButton:hover { background-color: #333333; }
""")
        self.min_btn.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.min_btn, 0, Qt.AlignVCenter)
        
        self.max_btn = QToolButton(self)
        self.max_btn.setText("□")
        self.max_btn.setFixedSize(30, 30)
        self.max_btn.setStyleSheet("""
    QToolButton { color: white; border: none; background: transparent; border-radius: 15px; font-size: 15px; }
    QToolButton:hover { background-color: #333333; }
""")
        self.max_btn.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.max_btn, 0, Qt.AlignVCenter)
        
        self.close_btn = QToolButton(self)
        self.close_btn.setText("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
    QToolButton { color: white; border: none; background: transparent; border-radius: 15px; font-size: 23px; }
    QToolButton:hover { background-color: #333333; }
""")
        self.close_btn.clicked.connect(self.parent_window.close)
        layout.addWidget(self.close_btn, 0, Qt.AlignVCenter)

        self.dragging = False
        self.drag_position = QPoint()

    def contextMenuEvent(self, event):
        """Show context menu on right-click."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #444;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 30px 6px 8px;
                min-width: 120px;
                margin-left: 4px;
            }
            QMenu::item:selected {
                background-color: #444;
            }
        """)
        
        style = self.style()
        
        minimize_action = QAction("Minimize", menu)
        minimize_action.setIcon(style.standardIcon(QStyle.SP_TitleBarMinButton))
        minimize_action.triggered.connect(self.parent_window.showMinimized)
        menu.addAction(minimize_action)
        
        if self.parent_window.isMaximized():
            restore_action = QAction("Restore", menu)
            restore_action.setIcon(style.standardIcon(QStyle.SP_TitleBarNormalButton))
        else:
            restore_action = QAction("Maximize", menu)
            restore_action.setIcon(style.standardIcon(QStyle.SP_TitleBarMaxButton))
        restore_action.triggered.connect(self.toggle_maximize)
        menu.addAction(restore_action)
        
        menu.addSeparator()
        
        close_action = QAction("Close", menu)
        close_action.setIcon(style.standardIcon(QStyle.SP_TitleBarCloseButton))
        close_action.triggered.connect(self.parent_window.close)
        menu.addAction(close_action)
        
        menu.exec_(event.globalPos())

    def toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.max_btn.setText("□")
        else:
            self.parent_window.showMaximized()
            self.max_btn.setText("❐")

    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if isinstance(child, QToolButton):
            return
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        event.accept()
