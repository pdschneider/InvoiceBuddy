from types import SimpleNamespace

dark = SimpleNamespace(
    tabs = """
        QTabWidget::pane {
            border: 1px solid #444;
            border-radius: 5px;
            background-color: #2b2b2b;
        }
        QTabBar::tab {
            background-color: #333;
            color: #aaa;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }
        QTabBar::tab:selected {
            background-color: #2b2b2b;
            color: #2ecc71;
            font-weight: bold;
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
    """
)
