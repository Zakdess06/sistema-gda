from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from app.core.store import store


class StatCard(QFrame):
    def __init__(self, titulo, valor):
        super().__init__()

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
        lbl_titulo.setStyleSheet("color:#cfcfcf; font-size:15px;")

        self.lbl_valor = QLabel(str(valor))
        self.lbl_valor.setAlignment(Qt.AlignCenter)
        self.lbl_valor.setStyleSheet("color:white; font-size:32px; font-weight:bold;")

        layout.addWidget(lbl_titulo)
        layout.addStretch()
        layout.addWidget(self.lbl_valor)

    def set_value(self, value):
        self.lbl_valor.setText(str(value))


class DashboardView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout(self)

        self.card_productos = StatCard("Productos", 0)
        self.card_stock = StatCard("Stock total", 0)
        self.card_entradas = StatCard("Entradas", 0)
        self.card_salidas = StatCard("Salidas", 0)
        self.card_herramientas = StatCard("Herramientas", 0)
        self.card_prestadas = StatCard("Prestadas", 0)

        layout.addWidget(self.card_productos, 0, 0)
        layout.addWidget(self.card_stock, 0, 1)
        layout.addWidget(self.card_entradas, 1, 0)
        layout.addWidget(self.card_salidas, 1, 1)
        layout.addWidget(self.card_herramientas, 2, 0)
        layout.addWidget(self.card_prestadas, 2, 1)

        
        store.subscribe(self.update_data)
        self.update_data()

    def update_data(self):
        self.card_productos.set_value(len(store.almacen))
        self.card_stock.set_value(sum(i.cantidad for i in store.almacen.values()))
        self.card_entradas.set_value(len(store.entradas))
        self.card_salidas.set_value(len(store.salidas))
        self.card_herramientas.set_value(len(store.herramientas))
        self.card_prestadas.set_value(
            sum(1 for h in store.herramientas.values() if h.estado == "Prestada")
        )
