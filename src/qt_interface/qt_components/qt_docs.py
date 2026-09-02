# src/qt_interface/qt_components/qt_docs.py
import os
import webbrowser
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QTabWidget, QTextBrowser)
from PySide6.QtCore import QUrl
from src.qt_interface.qt_styles import dark
import logging


# Docs live at <project root>/docs/wiki/ — three levels up from this file
PROJECT_DOCS = os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs")
DOCS_DIR = os.path.join(PROJECT_DOCS, "wiki")
EXTRA_DOCS = ["companies.md"]


def create_docs_panel(globs):
    """Creates the docs overlay panel with a tab per markdown file."""

    # Main container
    docs_panel = QWidget(globs.window)
    docs_panel.setMinimumSize(650, 550)
    docs_panel.setStyleSheet("""
        background-color: rgb(43, 43, 43);
        border-radius: 10px;
    """)
    docs_panel.hide()

    layout = QVBoxLayout(docs_panel)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)

    # === HEADER ===
    title = QLabel("Documentation")
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
    layout.addWidget(title)

    # === TABS ===
    tabs = QTabWidget()
    tabs.setStyleSheet(dark.tabs)

    def on_anchor_clicked(url):
        """Handles links inside docs: web links open the browser,
        internal .md links switch to the matching tab."""
        url_str = url.toString()

        if url_str.startswith("http"):
            webbrowser.open(url_str)
            return

        # Internal doc link — find a tab whose filename matches
        fname = os.path.basename(url_str)
        wanted = fname[:-3] if fname.endswith(".md") else fname
        for i in range(tabs.count()):
            if tabs.tabText(i).lower() == wanted.lower().replace("-", " "):
                tabs.setCurrentIndex(i)
                return

        logging.warning(f"Docs link target not found: {url_str}")

    for fname in sorted(os.listdir(DOCS_DIR)):
        if not fname.endswith(".md"):
            continue

        tab_name = fname[:-3].replace("-", " ").title()

        viewer = QTextBrowser()
        viewer.setOpenLinks(False)          # we handle internal links ourselves
        viewer.setOpenExternalLinks(True)   # http links open in web browser
        viewer.setStyleSheet(
            "background-color: #333339; color: #ddd; border: none; padding: 10px;")

        md_path = os.path.join(DOCS_DIR, fname)
        with open(md_path, "r", encoding="utf-8") as f:
            viewer.setMarkdown(f.read())

        # Resolve relative image refs (../screenshots/foo.png) against docs/wiki/
        viewer.document().setBaseUrl(QUrl.fromLocalFile(DOCS_DIR + os.sep))

        viewer.anchorClicked.connect(on_anchor_clicked)
        tabs.addTab(viewer, tab_name)

    # Extra top-level docs (whitelisted only — not scanned automatically)
    for fname in EXTRA_DOCS:
        md_path = os.path.join(PROJECT_DOCS, fname)
        if not os.path.exists(md_path):
            logging.warning(f"Extra doc not found: {md_path}")
            continue

        tab_name = fname[:-3].replace("-", " ").title()

        viewer = QTextBrowser()
        viewer.setOpenLinks(False)
        viewer.setOpenExternalLinks(True)
        viewer.setStyleSheet(
            "background-color: #333339; color: #ddd; border: none; padding: 10px;")
        with open(md_path, "r", encoding="utf-8") as f:
            viewer.setMarkdown(f.read())
        viewer.document().setBaseUrl(PROJECT_DOCS + "/")
        viewer.anchorClicked.connect(on_anchor_clicked)
        tabs.addTab(viewer, tab_name)

    layout.addWidget(tabs)

    # Close Button
    close_btn = QPushButton("Close")
    close_btn.setStyleSheet(dark.close_button)
    close_btn.clicked.connect(lambda: toggle_docs_panel(globs))
    layout.addWidget(close_btn)

    globs.docs_panel = docs_panel
    return docs_panel


def toggle_docs_panel(globs):
    """Shows or hides the docs panel."""
    if globs.docs_panel.isVisible():
        globs.docs_panel.hide()
        globs.dim_overlay.hide()
    else:
        # Hide any other open panels
        for attr in ['settings_panel', 'changelog_panel',
                     'about_panel', 'report_panel']:
            panel = getattr(globs, attr, None)
            if panel and panel.isVisible():
                panel.hide()

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
        globs.docs_panel.resize(panel_w, panel_h)

        x = (parent_w - panel_w) // 2
        y = (parent_h - panel_h) // 2

        globs.docs_panel.move(x, y)
        globs.docs_panel.show()
        globs.docs_panel.raise_()
