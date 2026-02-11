from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt


class Sidebar(QWidget):
    view_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setMinimumWidth(280)
        self.setMaximumWidth(340)
        
        self.current_button = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== TÍTULO =====
        title = QLabel("Sistema GDA")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                padding: 24px 20px;
                border-bottom: 1px solid #1f2937;
                letter-spacing: 0.5px;
                color: #f0f4f8;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # ===== BOTONES DE NAVEGACIÓN =====
        buttons = {
            "Dashboard": "dashboard",
            "Almacén": "almacen",
            "Salidas": "salidas",
            "Herramientas": "herramientas",
            "Préstamos": "prestamos",
            "Reportes": "reportes",
            "Bitácora": "bitacora",
            "Configuración": "configuracion",
        }

        self.buttons_map = {}
        
        for text, view_name in buttons.items():
            btn = QPushButton(text)
            btn.setObjectName("SidebarButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(50)
            btn.clicked.connect(
                lambda _, v=view_name, b=btn: self._on_button_clicked(v, b)
            )
            layout.addWidget(btn)
            self.buttons_map[view_name] = btn

        layout.addStretch()
        
        # ===== SELECCIONAR PRIMERO POR DEFECTO =====
        if "dashboard" in self.buttons_map:
            self.buttons_map["dashboard"].click()

    def _on_button_clicked(self, view_name, button):
        """Maneja el click en botones del sidebar"""
        # Restaurar estilo del botón anterior
        if self.current_button and self.current_button != button:
            self.current_button.setStyleSheet("")
        
        # Enfatizar botón actual con color distintivo
        self.current_button = button
        button.setStyleSheet("""
            QPushButton#SidebarButton {
                background-color: #1e3a8a;
                border-left: 4px solid #2563eb;
                color: #ffffff;
            }
        """)
        
        # Emitir señal
        self.view_changed.emit(view_name)
