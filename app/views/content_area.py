from PySide6.QtWidgets import QWidget, QStackedLayout, QLabel
from app.views.almacen_view import AlmacenView
from app.views.entradas_view import EntradasView  # <- nuevo


class ContentArea(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QStackedLayout(self)

        self.dashboard = QLabel("Dashboard")
        self.dashboard.setStyleSheet("font-size: 24px;")

        self.almacen = AlmacenView()
        self.entradas = EntradasView()   # <- ya no QLabel

        self.salidas = QLabel("Salidas")
        self.salidas.setStyleSheet("font-size: 24px;")

        self.layout.addWidget(self.dashboard)
        self.layout.addWidget(self.almacen)
        self.layout.addWidget(self.entradas)
        self.layout.addWidget(self.salidas)

    def show_dashboard(self):
        self.layout.setCurrentWidget(self.dashboard)

    def show_almacen(self):
        self.layout.setCurrentWidget(self.almacen)

    def show_entradas(self):
        self.layout.setCurrentWidget(self.entradas)

    def show_salidas(self):
        self.layout.setCurrentWidget(self.salidas)
