from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from app.core.store import store


class ConfiguracionView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== INFO SISTEMA =====
        info = QFrame()
        info.setFrameShape(QFrame.Box)
        info.setStyleSheet("""
            QFrame {
                border-radius: 10px;
                border: 1px solid #444;
                background-color: #1e1e1e;
                padding: 16px;
            }
        """)

        info_layout = QVBoxLayout(info)
        # asegurar márgenes y espaciado para que los elementos estén agrupados
        info_layout.setContentsMargins(16, 12, 16, 12)
        info_layout.setSpacing(6)

        lbl_titulo = QLabel("Sistema GDA")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")

        lbl_version = QLabel("Versión: Demo 1.0")
        lbl_version.setAlignment(Qt.AlignCenter)
        lbl_version.setStyleSheet("color: #ccc;")

        lbl_desc = QLabel(
            "Sistema de Gestión de Almacén\n"
            "Demo funcional sin base de datos\n"
            "Desarrollado para presentación"
        )
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setStyleSheet("color: #aaa;")

        info_layout.addWidget(lbl_titulo)
        info_layout.addWidget(lbl_version)
        info_layout.addWidget(lbl_desc)

        # ===== DERECHOS RESERVADOS =====
        footer_frame = QFrame()
        footer_frame.setFrameShape(QFrame.NoFrame)
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(4)

        lbl_footer = QLabel("Derechos reservados a TechCenter")
        lbl_footer.setAlignment(Qt.AlignCenter)
        lbl_footer.setStyleSheet("color: #777; font-size: 11px;")
        footer_layout.addWidget(lbl_footer)

        # Imagen dentro del mismo contenedor de derechos reservados
        footer_logo = QLabel()
        fpix = QPixmap("resources/techcenter-logo.png")
        if fpix.isNull():
            fpix = QPixmap("resources/techcenter.png")
        if not fpix.isNull():
            fpix = fpix.scaledToWidth(120, Qt.SmoothTransformation)
            footer_logo.setPixmap(fpix)
            footer_logo.setAlignment(Qt.AlignCenter)
            footer_layout.addWidget(footer_logo)

        info_layout.addWidget(footer_frame)



        layout.addWidget(info)

        # ===== BOTONES =====
        btn_reset = QPushButton("Reiniciar datos de demo")
        btn_reset.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
            }
        """)

        btn_reset.clicked.connect(self.reset_demo)

        layout.addWidget(btn_reset)
        layout.addStretch()

    def reset_demo(self):
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Reiniciar todos los datos de la demo?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            store.almacen.clear()
            store.entradas.clear()
            store.salidas.clear()
            store.herramientas.clear()

            # volver a cargar demo
            store.seed_demo()

            QMessageBox.information(
                self,
                "Listo",
                "Datos de la demo reiniciados"
            )
