from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
)

from app.views.topbar import TopBar
from app.views.sidebar import Sidebar
from app.views.dashboard_view import DashboardView
from app.views.almacen_view import AlmacenView
from app.views.salidas_view import SalidasView
from app.views.herramienta_view import HerramientasView
from app.views.prestamo_herramienta_view import PrestamoHerramientaView
from app.views.reportes_view import ReportesView
from app.views.configuracion_view import ConfiguracionView
from app.views.bitacora_view import BitacoraView



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema GDA - Gestión de Almacén")
        self.resize(1400, 900)

        # ===== WIDGET CENTRAL =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # ===== LAYOUT PRINCIPAL (VERTICAL) =====
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== TOPBAR =====
        self.topbar = TopBar()
        main_layout.addWidget(self.topbar)

        # ===== CONTENIDO (HORIZONTAL: SIDEBAR + STACK) =====
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        content_layout.addWidget(self.sidebar)

        # Stack de vistas
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, 1)

        # Vistas
        self.views = {
            "dashboard": DashboardView(),
            "almacen": AlmacenView(),
            "salidas": SalidasView(),
            "herramientas": HerramientasView(),
            "prestamos": PrestamoHerramientaView(),
            "reportes": ReportesView(),
            "bitacora": BitacoraView(),
            "configuracion": ConfiguracionView(),
        }

        for view in self.views.values():
            self.stack.addWidget(view)

        main_layout.addLayout(content_layout, 1)

        # ===== CONEXIÓN DE SEÑALES =====
        self.sidebar.view_changed.connect(self.change_view)

        self.change_view("dashboard")

    def change_view(self, view_name):
        if view_name in self.views:
            self.stack.setCurrentWidget(self.views[view_name])
