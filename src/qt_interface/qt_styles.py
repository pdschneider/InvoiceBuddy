from types import SimpleNamespace

dark = SimpleNamespace(
    tabs = """
        QTabWidget::pane {
            border: none;
            border-top: 1px solid #3a3a40;
            background-color: transparent;
        }
        QTabBar::tab {
            background-color: transparent;
            color: #888;
            padding: 8px 18px;
            margin-right: 4px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-size: 13px;
        }
        QTabBar::tab:hover {
            color: #dddddd;
        }
        QTabBar::tab:selected {
            color: #2ecc71;
            border-bottom: 2px solid #2ecc71;
        }
    """,
    save_button = """
        QPushButton {
            background-color: #3a3a3a;
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
    """,
    scroll_area = """
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        QScrollBar:vertical {
            background-color: #333;
            width: 8px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background-color: #4a4a4a;
            min-height: 50px;
            border-radius: 4px;
        }
    """,
    close_button = """
        QPushButton {
            background-color: #3a3a3a;
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
    """,
    menu = """
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
        """,
    combobox = """
        QComboBox {
            color: white;
            background-color: #333;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 5px;
            font-size: 14px;
            min-width: 200px;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid white;
            margin-right: 10px;
        }
        QComboBox QAbstractItemView {
            background-color: #333;
            color: white;
            selection-background-color: #2ecc71;
            border: none;
        }
    """,
    browse_button = """
        QPushButton {
            background-color: #3a3a3a;
            color: white;
            padding: 10px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
        QToolTip {
            background-color: #2b2b2b; color: white; border: 1px solid #555;
        }
    """,
    line_edit = """
        background-color: #3a3a3a;
        color: white;
        padding: 10px;
        border-radius: 4px;
    """,
    minus_button = """
        QPushButton {
            background-color: #3a3a3a;
            color: white;
            padding: 10px;
            border-radius: 15px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
            font-weight: bold;
        }
        QToolTip {
            background-color: #2b2b2b; color: white; border: 1px solid #555;
        }
    """,
    hamburger_button = """
        QPushButton {
            background-color: transparent;
            border: 1px solid #555;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 22px;
            color: #e0e0e0;
        }

        QPushButton:hover {
            background-color: #3a3a3d;
            border-color: #777;
        }

        QPushButton:pressed {
            background-color: #2a2a2d;
            border-color: #777;
        }
    """,
    social_button = """
        QPushButton {
            background-color: transparent;
            border: none;
            padding: 8px 12px;
            font-size: 22px;
            color: #e0e0e0;
        }

        QPushButton:hover {
            background-color: #3a3a3d;
            border-radius: 6px;
        }

        QPushButton:pressed {
            background-color: #2a2a2d;
            border-radius: 6px;
        }
        QToolTip {
            background-color: #2b2b2b; color: white; border: 1px solid #555;
        }
    """,
    mailbox_button = """
        QPushButton {
            background-color: #3a3a3a; color: white; border: none;
            border-radius: 4px; font-size: 16px;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
        QToolTip {
            background-color: #2b2b2b; color: white; border: 1px solid #555;
        }
        """,
    delete_button = """
        QPushButton {
            background-color: #8B0000; color: white; border: none;
            border-radius: 4px; font-size: 16px;
        }
        QPushButton:hover {
            background-color: #a00000;
        }
        QToolTip {
            background-color: #2b2b2b; color: white; border: 1px solid #555;
        }
    """,
    mail_checkbox = """
        QCheckBox {
            background-color: transparent;
            border: none;
            spacing: 0;
        }
        QCheckBox::indicator {
            width: 14px;
            height: 14px;
            border: 2px solid #555;
            border-radius: 4px;
            background-color: #2b2b2b;
            margin: 1px;
        }
        QCheckBox::indicator:hover {
            border-color: #999;
        }
        QCheckBox::indicator:pressed {
            background-color: #444;
        }
        QCheckBox::indicator:checked {
            background-color: #888;
            border-color: #777;
        }
        QCheckBox::indicator:checked:hover {
            border-color: #ccc;
        }
    """,
    mailbox = """
        QScrollArea {
            background-color: transparent; border: none;
    """,
    mailbox_list = """
        QListWidget {
            background-color: #2b2b2b;
            border: none;
            color: white;
            font-size: 14px;
            outline: none;
        }
        QListWidget::item {
            padding: 10px;
            border-bottom: 1px solid #333;
        }
        QListWidget::item:selected {
            background-color: #3a3a3a;
            color: #2ecc71;
        }
        QListWidget::item:hover {
            background-color: #333;
        }
        QScrollBar:vertical {
            background: transparent;
            width: 10px;
            margin: 2px;
        }
        QScrollBar::handle:vertical {
            background: #555;
            border-radius: 3px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: #777;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
            width: 0;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        QScrollBar::corner {
            background: transparent;
        }
    """,
    master_checkbox = """
        QCheckBox {
            background-color: transparent;
            border: none;
            spacing: 0;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #666;
            border-radius: 5px;
            background-color: #222;
            margin: 1px;
        }
        QCheckBox::indicator:hover {
            border-color: #2ecc71;
        }
        QCheckBox::indicator:checked {
            background-color: #2ecc71;
            border-color: #2ecc71;
        }
        QCheckBox::indicator:checked:hover {
            background-color: #35d97e;
        }
        QCheckBox::indeterminate {
            background-color: #1a1a1a;
            border-color: #2ecc71;
        }
    """,
    settings_button = """
        QPushButton {
            background-color: transparent;
            color: white;
            font-size: 18px;
            border: 1px solid #555;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #3a3a3d;
            border-color: #777;
        }
    """,
    scrollbar = """
        QScrollBar:vertical {
            background-color: #2b2b2b;
            width: 10px;
            border-radius: 5px;
            margin: 0;
        }
        QScrollBar::handle {
            background-color: #505055;
            border-radius: 5px;
            min-height: 40px;
        }
        QScrollBar::handle:hover {
            background-color: #606066;
        }
        QScrollBar::add-page, QScrollBar::sub-page {
            background: none;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            height: 0;
            subcontrol-position: none;
        }
        QScrollBar::up-arrow, QScrollBar::down-arrow {
            width: 0;
            height: 0;
            image: none;
        }
    """,
    settings_checkbox = """
        QCheckBox {
            color: #d0d0d0; font-size: 13px; spacing: 10px;
            padding: 6px 10px;
            background-color: transparent; border-radius: 4px;
        }
        QCheckBox:hover { color: white; }
        QCheckBox::indicator {
            width: 18px; height: 18px;
            border: 1px solid #555; border-radius: 4px;
            background-color: #2b2b2b;
        }
        QCheckBox::indicator:hover { border: 1px solid #2ecc71; }
        QCheckBox::indicator:checked {
            background-color: #2ecc71; border: 1px solid #27ae60;
            image: url(none);
        }
        QCheckBox::indicator:checked:disabled { background-color: #555; border: 1px solid #555; }
    """
)
