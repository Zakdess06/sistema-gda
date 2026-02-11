from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont
import json
from pathlib import Path


class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("TopBar")
        self.setFixedHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        # ===== INFORMACIÓN DE LA EMPRESA =====
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                empresa_nombre = config.get("empresa", "Sistema GDA")
                responsable = config.get("responsable", "Usuario")
        except:
            empresa_nombre = "Sistema GDA"
            responsable = "Usuario"

        # Nombre de empresa
        empresa_label = QLabel(empresa_nombre)
        empresa_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 0.3px;
            }
        """)
        layout.addWidget(empresa_label)

        layout.addStretch()

        # ===== INFORMACIÓN DEL USUARIO Y HORA =====
        # Hora actual
        tiempo = QDateTime.currentDateTime().toString("dd/MM/yyyy · HH:mm")
        hora_label = QLabel(tiempo)
        hora_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                opacity: 0.9;
            }
        """)
        hora_label.setAlignment(Qt.AlignRight)

        # Usuario
        usuario_label = QLabel(responsable)
        usuario_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 500;
            }
        """)
        usuario_label.setAlignment(Qt.AlignRight)

        layout.addWidget(hora_label)
        layout.addWidget(usuario_label)
