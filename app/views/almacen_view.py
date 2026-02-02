from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt

from app.core.store import store, AlmacenItem
from app.core.config import config


class AlmacenView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== BOTONES =====
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Agregar producto demo")
        self.btn_delete = QPushButton("Eliminar seleccionado")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # ===== TABLA =====
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Partida", "Descripción", "Unidad",
            "Cantidad", "Ubicación", "Proveedor"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.btn_add.clicked.connect(self.add_demo_product)
        self.btn_delete.clicked.connect(self.delete_selected)

        # escuchar cambios del store
        store.subscribe(self.load_data)

        self.load_data()

    # ===================== DATA =====================

    def load_data(self):
        self.table.setRowCount(0)

        for item in store.almacen.values():
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(item.partida))
            self.table.setItem(row, 1, QTableWidgetItem(item.descripcion))
            self.table.setItem(row, 2, QTableWidgetItem(item.unidad))

            # ----- CANTIDAD CON ALERTA -----
            cantidad_item = QTableWidgetItem(str(item.cantidad))
            cantidad_item.setTextAlignment(Qt.AlignCenter)

            if item.cantidad <= config.stock_minimo:
                cantidad_item.setForeground(Qt.red)

            self.table.setItem(row, 3, cantidad_item)

            self.table.setItem(row, 4, QTableWidgetItem(item.ubicacion))
            self.table.setItem(row, 5, QTableWidgetItem(item.proveedor))

    # ===================== ACCIONES =====================

    def add_demo_product(self):
        partida = f"E-{len(store.almacen) + 1:03d}"

        if partida in store.almacen:
            QMessageBox.warning(self, "Error", "La partida ya existe")
            return

        nuevo = AlmacenItem(
            partida=partida,
            descripcion="Producto demo",
            unidad="Pza",
            cantidad=config.stock_minimo,  # intencional para mostrar alerta
            ubicacion="Demo",
            proveedor="Proveedor demo"
        )

        store.almacen[partida] = nuevo
        store.notify()  # actualiza dashboard y vistas

    def delete_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            return

        partida = self.table.item(selected, 0).text()

        confirm = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Eliminar la partida {partida}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            store.almacen.pop(partida, None)
            store.notify()

    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)
