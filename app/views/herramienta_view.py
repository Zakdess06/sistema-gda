from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QMessageBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QDialog
)

from app.core.store import store, Herramienta
from app.core.bitacora import bitacora
from app.core.event_manager import event_manager
from app.views.herramienta_dialog import HerramientaDialog
from app.utils.table_utils import ajustar_ancho_tabla


class HerramientasView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== BOTONES =====
        btns = QHBoxLayout()

        self.btn_add = QPushButton("+ Agregar Herramienta")
        self.btn_edit = QPushButton("✎ Editar Seleccionado")
        self.btn_delete = QPushButton("✕ Eliminar Seleccionado")

        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_delete)
        btns.addStretch()

        layout.addLayout(btns)

        # ===== TABLA =====
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Código", "Descripción", "Ubicación", "Cantidad", "Observaciones"
        ])
        ajustar_ancho_tabla(self.table, anchos={
            0: 100,   # Código
            1: 280,   # Descripción
            2: 150,   # Ubicación
            3: 80,    # Cantidad
            4: 200    # Observaciones (se estira)
        })
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.btn_add.clicked.connect(self.agregar)
        self.btn_edit.clicked.connect(self.editar)
        self.btn_delete.clicked.connect(self.eliminar)

        store.subscribe(self.load_data)
        event_manager.herramienta_changed.connect(self.load_data)
        self.load_data()


    # ---------- DATA ----------
    def load_data(self):
        self.table.setRowCount(0)
        herramientas = store.get_herramientas()
        for h in herramientas.values():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(h.codigo))
            self.table.setItem(row, 1, QTableWidgetItem(h.descripcion))
            self.table.setItem(row, 2, QTableWidgetItem(h.ubicacion))
            self.table.setItem(row, 3, QTableWidgetItem(str(h.cantidad)))
            self.table.setItem(row, 4, QTableWidgetItem(getattr(h, 'observaciones', '')))

    def selected_codigo(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).text()

    # ---------- ACCIONES ----------
    def agregar(self):
        dialog = HerramientaDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()

    def editar(self):
        codigo = self.selected_codigo()
        if not codigo:
            QMessageBox.warning(self, "Error", "Seleccione una herramienta")
            return
        herramientas = store.get_herramientas()
        herramienta = herramientas.get(codigo)
        if not herramienta:
            QMessageBox.warning(self, "Error", "Herramienta no encontrada")
            return
        
        dialog = HerramientaDialog(self, herramienta)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()

    def eliminar(self):
        codigo = self.selected_codigo()
        if not codigo:
            QMessageBox.warning(self, "Error", "Seleccione una herramienta")
            return
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar la herramienta {codigo}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            store.delete_herramienta(codigo)
            bitacora.log("Herramienta", f"Herramienta eliminada: {codigo}")
            self.load_data()


