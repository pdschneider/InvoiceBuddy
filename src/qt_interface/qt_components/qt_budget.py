# src/qt_interface/qt_components/qt_budget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class BudgetPage(QWidget):
    """Full-width budgeting page (categories/subcategories for now)."""

    def __init__(self, globs_obj, parent=None):
        super().__init__(parent)
        self.globs = globs_obj

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        placeholder = QLabel("Budget")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #888; font-size: 24px;")
        layout.addWidget(placeholder)
