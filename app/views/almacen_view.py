from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt

from app.core.store import store, AlmacenItem
from app.core.config import config
from app.core.bitacora import bitacora
from app.views.producto_dialog import ProductoDialog


class AlmacenView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== BOTONES =====
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Agregar Producto")
        self.btn_edit = QPushButton("Editar Seleccionado")
        self.btn_delete = QPushButton("Eliminar Seleccionado")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # ===== TABLA =====
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Partida", "Descripción", "Unidad",
            "Cantidad", "Stock Mín.", "Ubicación", "Proveedor"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.btn_add.clicked.connect(self.add_product)
        self.btn_edit.clicked.connect(self.edit_selected)
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

            if item.cantidad <= item.stock_minimo:
                cantidad_item.setForeground(Qt.red)

            self.table.setItem(row, 3, cantidad_item)

            # ----- STOCK MÍNIMO -----
            stock_min_item = QTableWidgetItem(str(item.stock_minimo))
            stock_min_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, stock_min_item)

            self.table.setItem(row, 5, QTableWidgetItem(item.ubicacion))
            self.table.setItem(row, 6, QTableWidgetItem(item.proveedor))

    # ===================== ACCIONES =====================

    def add_product(self):
        dialog = ProductoDialog(self)
        if dialog.exec():
            bitacora.log("Almacén", f"Nuevo producto agregado: {dialog.txt_partida.text()}")

    def edit_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Error", "Seleccione un producto para editar")
            return

        partida = self.table.item(selected, 0).text()
        producto = store.almacen.get(partida)

        if not producto:
            QMessageBox.warning(self, "Error", "Producto no encontrado")
            return

        dialog = ProductoDialog(self, producto)
        if dialog.exec():
            bitacora.log("Almacén", f"Producto editado: {partida}")

    def delete_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Error", "Seleccione un producto para eliminar")
            return

        partida = self.table.item(selected, 0).text()

        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar la partida {partida}?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            store.almacen.pop(partida, None)
            store.notify()
            bitacora.log("Almacén", f"Producto eliminado: {partida}")

    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)
