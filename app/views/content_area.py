from PySide6.QtWidgets import QWidget, QStackedLayout, QLabel


class ContentArea(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QStackedLayout(self)

        self.dashboard = QLabel("Dashboard")
        self.almacen = QLabel("Almacén")
        self.entradas = QLabel("Entradas")
        self.salidas = QLabel("Salidas")

        for w in [
            self.dashboard,
            self.almacen,
            self.entradas,
            self.salidas
        ]:
            w.setStyleSheet("font-size: 24px;")
            self.layout.addWidget(w)

    def show_dashboard(self):
        self.layout.setCurrentWidget(self.dashboard)

    def show_almacen(self):
        self.layout.setCurrentWidget(self.almacen)

    def show_entradas(self):
        self.layout.setCurrentWidget(self.entradas)

    def show_salidas(self):
        self.layout.setCurrentWidget(self.salidas)
