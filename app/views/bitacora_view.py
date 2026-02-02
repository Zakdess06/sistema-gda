from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox
)

from app.core.bitacora import bitacora
from openpyxl import Workbook


class BitacoraView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== BOTONES (ARRIBA) =====
        btn_layout = QHBoxLayout()

        self.btn_export = QPushButton("Exportar a Excel")
        btn_layout.addWidget(self.btn_export)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # ===== TABLA =====
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Mensaje"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.btn_export.clicked.connect(self.export_excel)

        # cargar datos iniciales
        self.load_data()

    # ---------- DATA ----------
    def load_data(self):
        self.table.setRowCount(0)

        for log in bitacora.logs:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(log["fecha"]))
            self.table.setItem(row, 1, QTableWidgetItem(log["tipo"]))
            self.table.setItem(row, 2, QTableWidgetItem(log["mensaje"]))

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
