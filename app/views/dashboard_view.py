from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from app.core.store import store


class StatCard(QFrame):
    def __init__(self, titulo, valor):
        super().__init__()

        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                border-radius: 10px;
                border: 1px solid #444;
                background-color: #1e1e1e;
                padding: 14px;
            }
        """)

        layout = QVBoxLayout(self)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #cfcfcf;
            }
        """)

        self.lbl_valor = QLabel(str(valor))
        self.lbl_valor.setAlignment(Qt.AlignCenter)
        self.lbl_valor.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #ffffff;
            }
        """)

        layout.addWidget(lbl_titulo)
        layout.addStretch()
        layout.addWidget(self.lbl_valor)

    def set_value(self, value):
        self.lbl_valor.setText(str(value))



class DashboardView(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QGridLayout(self)

        self.card_productos = StatCard("Productos en almacén", 0)
        self.card_stock = StatCard("Stock total", 0)
        self.card_entradas = StatCard("Entradas registradas", 0)
        self.card_salidas = StatCard("Salidas registradas", 0)
        self.card_herramientas = StatCard("Herramientas totales", 0)
        self.card_prestadas = StatCard("Herramientas prestadas", 0)

        self.layout.addWidget(self.card_productos, 0, 0)
        self.layout.addWidget(self.card_stock, 0, 1)
        self.layout.addWidget(self.card_entradas, 1, 0)
        self.layout.addWidget(self.card_salidas, 1, 1)
        self.layout.addWidget(self.card_herramientas, 2, 0)
        self.layout.addWidget(self.card_prestadas, 2, 1)

        self.update_data()

    def update_data(self):
        total_productos = len(store.almacen)
        total_stock = sum(i.cantidad for i in store.almacen.values())
        total_entradas = len(store.entradas)
        total_salidas = len(store.salidas)
        total_herramientas = len(store.herramientas)
        prestadas = sum(
            1 for h in store.herramientas.values()
            if h.estado == "Prestada"
        )

        self.card_productos.set_value(total_productos)
        self.card_stock.set_value(total_stock)
        self.card_entradas.set_value(total_entradas)
        self.card_salidas.set_value(total_salidas)
        self.card_herramientas.set_value(total_herramientas)
        self.card_prestadas.set_value(prestadas)

    def showEvent(self, event):
        self.update_data()
        super().showEvent(event)
