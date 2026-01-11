from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Qt


class Sidebar(QWidget):
    def __init__(self, content):
        super().__init__()

        self.content = content
        self.setObjectName("Sidebar")
        self.setFixedWidth(450)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)

        
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_almacen = QPushButton("Almacén")
        self.btn_entradas = QPushButton("Entradas")
        self.btn_salidas = QPushButton("Salidas")
        self.btn_herramientas = QPushButton("Herramientas")
        self.btn_reportes = QPushButton("Reportes")
        self.btn_config = QPushButton("Configuración")

        self.buttons = [
            self.btn_dashboard,
            self.btn_almacen,
            self.btn_entradas,
            self.btn_salidas,
            self.btn_herramientas,
            self.btn_reportes,
            self.btn_config
        ]

        for btn in self.buttons:
            btn.setMinimumHeight(64)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setObjectName("SidebarButton")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(btn)

        
        self.btn_dashboard.clicked.connect(self.content.show_dashboard)
        self.btn_almacen.clicked.connect(self.content.show_almacen)
        self.btn_entradas.clicked.connect(self.content.show_entradas)
        self.btn_salidas.clicked.connect(self.content.show_salidas)
