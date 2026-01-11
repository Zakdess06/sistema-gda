from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Qt


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(450)  

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        buttons = [
            "Dashboard",
            "Almacén",
            "Entradas",
            "Salidas",
            "Herramientas",
            "Reportes",
            "Configuración"
        ]

        self.buttons = []

        for text in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(64)  
            btn.setCursor(Qt.PointingHandCursor)
            btn.setObjectName("SidebarButton")

            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            layout.addWidget(btn)
            self.buttons.append(btn)
