from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(50)

        layout = QHBoxLayout(self)
        title = QLabel("Sistema GDA")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        layout.addWidget(title)
        layout.addStretch()
