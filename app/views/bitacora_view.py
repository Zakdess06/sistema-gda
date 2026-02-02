from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt

from app.core.bitacora import bitacora


class BitacoraView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        lbl = QLabel("Bitácora del sistema")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(lbl)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Acción", "Detalle"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        # 🔥 OBSERVER
        bitacora.subscribe(self.load_data)

        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)

        for log in bitacora.items:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(log.fecha))
            self.table.setItem(row, 1, QTableWidgetItem(log.accion))
            self.table.setItem(row, 2, QTableWidgetItem(log.detalle))
