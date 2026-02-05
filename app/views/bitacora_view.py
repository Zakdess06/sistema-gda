from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

from app.core.bitacora import bitacora
from openpyxl import Workbook


class BitacoraView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== TÍTULO =====
        title = QLabel("Bitácora de Sistema")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # ===== BOTONES (ARRIBA) =====
        btn_layout = QHBoxLayout()

        self.btn_export = QPushButton("Exportar a Excel")
        self.btn_clear = QPushButton("Limpiar Bitácora")

        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # ===== TABLA =====
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Mensaje"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Ajustar ancho de columnas
        self.table.setColumnWidth(0, 180)  # Fecha
        self.table.setColumnWidth(1, 120)  # Tipo

        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.btn_export.clicked.connect(self.export_excel)
        self.btn_clear.clicked.connect(self.clear_bitacora)

        # Escuchar cambios en la bitácora
        bitacora.subscribe(self.load_data)

        # cargar datos iniciales
        self.load_data()

    # ---------- DATA ----------
    def load_data(self):
        self.table.setRowCount(0)

        # Mostrar en orden inverso (más reciente arriba)
        for log in reversed(bitacora.logs):
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Fecha
            fecha_item = QTableWidgetItem(log["fecha"])
            fecha_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, fecha_item)

            # Tipo
            tipo_item = QTableWidgetItem(log["tipo"])
            tipo_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, tipo_item)

            # Mensaje (completo, sin truncar)
            mensaje_item = QTableWidgetItem(log["mensaje"])
            self.table.setItem(row, 2, mensaje_item)

        # Auto-scroll al final (nuevos logs arriba)
        if self.table.rowCount() > 0:
            self.table.scrollToTop()

    # ---------- LIMPIAR ==========
    def clear_bitacora(self):
        confirm = QMessageBox.question(
            self,
            "Confirmar",
            "¿Estás seguro de que deseas limpiar toda la bitácora?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            bitacora.clear()
            QMessageBox.information(self, "Listo", "Bitácora limpiada")

    # ---------- EXPORTAR ----------
    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar bitácora",
            "bitacora.xlsx",
            "Excel (*.xlsx)"
        )

        if not path:
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Bitácora"

            # encabezados
            ws.append(["Fecha", "Tipo", "Mensaje"])

            for log in bitacora.logs:
                ws.append([
                    log["fecha"],
                    log["tipo"],
                    log["mensaje"]
                ])

            wb.save(path)

            QMessageBox.information(
                self,
                "Éxito",
                "Bitácora exportada correctamente"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )
