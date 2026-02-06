from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget
)

from app.views.sidebar import Sidebar
from app.views.dashboard_view import DashboardView
from app.views.almacen_view import AlmacenView
from app.views.entradas_view import EntradasView
from app.views.salidas_view import SalidasView
from app.views.herramienta_view import HerramientasView
from app.views.prestamo_herramienta_view import PrestamoHerramientaView
from app.views.reportes_view import ReportesView
from app.views.configuracion_view import ConfiguracionView
from app.views.bitacora_view import BitacoraView



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema GDA")
        self.resize(1200, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Stack de vistas
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Vistas
        self.views = {
            "dashboard": DashboardView(),
            "almacen": AlmacenView(),
            "entradas": EntradasView(),
            "salidas": SalidasView(),
            "herramientas": HerramientasView(),
            "prestamos": PrestamoHerramientaView(),
            "reportes": ReportesView(),
            "bitacora": BitacoraView(),
            "configuracion": ConfiguracionView(),
        }

        for view in self.views.values():
            self.stack.addWidget(view)

        self.sidebar.view_changed.connect(self.change_view)

        self.change_view("dashboard")

    def change_view(self, view_name):
        if view_name in self.views:
            self.stack.setCurrentWidget(self.views[view_name])
