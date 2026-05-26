# src/qt_interface/qt_components/qt_viewer.py
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import Qt
import logging

class NativePdfViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.doc = QPdfDocument(self)
        self.view = QPdfView(self)

        self.view.setDocument(self.doc)
        self.view.setMinimumSize(200, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.view)

    def load_pdf(self, file_path):
        """Loads a PDF file into the viewer."""
        if not file_path:
            return

        logging.debug(f"Loading PDF: {file_path}")

        # Start loading. DO NOT check status here. It is async.
        self.doc.load(file_path)

        # Set the mode immediately. Qt will apply it when the doc is ready.
        # Use MultiPage for scrolling through all pages.
        self.view.setPageMode(QPdfView.PageMode.MultiPage)
        self.view.setZoomMode(QPdfView.ZoomMode.FitInView)

        # Force a repaint to ensure the UI updates
        self.view.update()
        self.view.repaint()
