from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QIcon, QPixmap

app = QApplication([])

icon = QIcon(r"C:\Users\Phillip\Code\InvoiceBuddy\data\assets\github.svg")
print("isNull:", icon.isNull())

pm = icon.pixmap(64, 64)
label = QLabel()
label.setStyleSheet("background-color: #333339;")
label.setPixmap(pm)
label.show()

print("Window shown — close it to end the test")
app.exec()