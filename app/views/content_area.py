from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class ContentArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("ContentArea")

        layout = QVBoxLayout(self)
        label = QLabel("Área de trabajo")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
