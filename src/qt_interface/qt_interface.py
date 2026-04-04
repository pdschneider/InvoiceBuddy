# src/qt_interface/qt_interface.py
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt


def create_interface(globals):
    """Creates the main interface in PySide."""
    # Set up main window attributes
    globals.window.setWindowTitle("Invoice Buddy")
    if globals.saved_width and globals.saved_height and globals.saved_x and globals.saved_y:
        w = globals.saved_width
        h = globals.saved_height
        x = globals.saved_x
        y = globals.saved_y
        globals.window.setGeometry(x, y, w, h)
    else:
        globals.window.resize(900, 850)

    # Central Widget
    central_widget = QWidget()
    globals.window.setCentralWidget(central_widget)

    # Configure layout
    main_layout = QVBoxLayout(central_widget)
    globals.window.setLayout(main_layout)

    title = QLabel()
    title.setText("Invoice Buddy")
    title.setAlignment(Qt.AlignCenter)
    main_layout.addWidget(title)

    # Show window
    globals.window.show()
