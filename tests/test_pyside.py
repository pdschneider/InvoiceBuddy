import sys
from PySide6.QtWidgets import QApplication, QMainWindow

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("Bare Bones PySide6")
window.resize(800, 600)
window.show()

sys.exit(app.exec())