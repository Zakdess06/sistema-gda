from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal


class Sidebar(QWidget):
    view_changed = Signal(str)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        buttons = {
            "Dashboard": "dashboard",
            "Almacén": "almacen",
            "Entradas": "entradas",
            "Salidas": "salidas",
            "Herramientas": "herramientas",
            "Reportes": "reportes",
            "Configuración": "configuracion",
        }

        for text, view_name in buttons.items():
            btn = QPushButton(text)
            btn.clicked.connect(lambda _, v=view_name: self.view_changed.emit(v))
            layout.addWidget(btn)

        layout.addStretch()
