from PySide6.QtWidgets import QWidget, QHBoxLayout, QMenuBar, QToolButton
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor
from PySide6.QtGui import QColor

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
                border-bottom: 2px solid #2ecc71;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)

        # --- LEFT: Menus ---
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setNativeMenuBar(False)
        self.menu_bar.setStyleSheet("""
            QMenuBar { background-color: transparent; border: none; color: white; }
            QMenuBar::item { padding: 5px 10px; color: #ccc; }
            QMenuBar::item:selected { background-color: #444; color: white; }
        """)
        layout.addWidget(self.menu_bar)

        layout.addStretch()

        # --- RIGHT: Window Controls ---
        self.min_btn = QToolButton(self)
        self.min_btn.setText("_")
        self.min_btn.setFixedSize(30, 30)
        self.min_btn.setStyleSheet("color: white; border: none; background: transparent;")
        self.min_btn.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.min_btn)
        
        self.max_btn = QToolButton(self)
        self.max_btn.setText("□")
        self.max_btn.setFixedSize(30, 30)
        self.max_btn.setStyleSheet("color: white; border: none; background: transparent;")
        self.max_btn.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.max_btn)
        
        self.close_btn = QToolButton(self)
        self.close_btn.setText("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("color: white; border: none; background: transparent;")
        self.close_btn.clicked.connect(self.parent_window.close)
        layout.addWidget(self.close_btn)

        self.dragging = False
        self.drag_position = QPoint()

    def toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.max_btn.setText("□")
        else:
            self.parent_window.showMaximized()
            self.max_btn.setText("❐")

    def mousePressEvent(self, event):
        if self.childAt(event.pos()):
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
