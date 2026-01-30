from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox
)

from app.core.store import store, AlmacenItem


class AlmacenView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ----- BOTONES -----
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Agregar producto demo")
        self.btn_delete = QPushButton("Eliminar seleccionado")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # ----- TABLA -----
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Partida", "Descripción", "Unidad",
            "Cantidad", "Ubicación", "Proveedor"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # ----- CONEXIONES -----
        self.btn_add.clicked.connect(self.add_demo_product)
        self.btn_delete.clicked.connect(self.delete_selected)

        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)

        for item in store.almacen.values():
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(item.partida))
            self.table.setItem(row, 1, QTableWidgetItem(item.descripcion))
            self.table.setItem(row, 2, QTableWidgetItem(item.unidad))
            self.table.setItem(row, 3, QTableWidgetItem(str(item.cantidad)))
            self.table.setItem(row, 4, QTableWidgetItem(item.ubicacion))
            self.table.setItem(row, 5, QTableWidgetItem(item.proveedor))

    def add_demo_product(self):
        partida = f"E-{len(store.almacen) + 1:03d}"

        if partida in store.almacen:
            QMessageBox.warning(self, "Error", "La partida ya existe")
            return

        nuevo = AlmacenItem(
            partida=partida,
            descripcion="Producto demo",
            unidad="Pza",
            cantidad=10,
            ubicacion="Demo",
            proveedor="Proveedor demo"
        )

        store.almacen[partida] = nuevo
        self.load_data()

    def delete_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            return

        partida = self.table.item(selected, 0).text()

        confirm = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Eliminar la partida {partida}?",
        )

        if confirm == QMessageBox.Yes:
            store.almacen.pop(partida, None)
            self.load_data()
            
    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)
