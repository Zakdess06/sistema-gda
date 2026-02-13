from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QDialog
)

from app.core.store import store, Entrada
from app.core.bitacora import bitacora
from app.core.event_manager import event_manager
from app.views.entrada_dialog import EntradaDialog
class EntradasView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ========= BOTONES =========
        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("+ Agregar Producto")
        self.btn_editar = QPushButton("✎ Editar Seleccionado")
        self.btn_eliminar = QPushButton("✕ Eliminar Seleccionado")
        
        btn_layout.addWidget(self.btn_agregar)
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # ========= TABLA =========
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Partida", "Descripción", "Cantidad", "Unidad",
            "Proveedor", "Ubicación"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # ========= CONEXIONES =========
        self.btn_agregar.clicked.connect(self.agregar)
        self.btn_editar.clicked.connect(self.editar)
        self.btn_eliminar.clicked.connect(self.eliminar)

        store.subscribe(self.load_entradas)
        event_manager.entrada_added.connect(self.load_entradas)
        event_manager.almacen_changed.connect(self.load_entradas)
        event_manager.data_changed.connect(self.load_entradas)
        self.load_entradas()

    def selected_partida(self):
        """Obtiene la partida de la entrada seleccionada"""
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).text()

    # ---------- CARGAS ----------
    def load_entradas(self):
        """Carga las entradas (productos) desde la BD"""
        self.table.setRowCount(0)
        
        # Recargar desde BD para obtener los datos más recientes
        from app.core.entradas_db import fetch_all_entradas
        entradas = fetch_all_entradas()
        
        for e in entradas:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(e.partida))
            self.table.setItem(row, 1, QTableWidgetItem(e.descripcion))
            self.table.setItem(row, 2, QTableWidgetItem(str(e.cantidad)))
            self.table.setItem(row, 3, QTableWidgetItem(e.unidad))
            self.table.setItem(row, 4, QTableWidgetItem(e.proveedor))
            self.table.setItem(row, 5, QTableWidgetItem(e.ubicacion))

    # ---------- ACCIONES ----------
    def agregar(self):
        dialog = EntradaDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_entradas()

    def editar(self):
        partida = self.selected_partida()
        if not partida:
            QMessageBox.warning(self, "Error", "Seleccione una entrada")
            return
        
        from app.core.entradas_db import fetch_all_entradas
        entradas = fetch_all_entradas()
        entrada = None
        for e in entradas:
            if e.partida == partida:
                entrada = e
                break
        
        if not entrada:
            QMessageBox.warning(self, "Error", "Entrada no encontrada")
            return
        
        dialog = EntradaDialog(self, entrada)
        if dialog.exec() == QDialog.Accepted:
            self.load_entradas()

    def eliminar(self):
        partida = self.selected_partida()
        if not partida:
            QMessageBox.warning(self, "Error", "Seleccione una entrada")
            return
        
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar el producto {partida}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            from app.core.entradas_db import delete_entrada
            delete_entrada(partida)
            bitacora.log("Almacén", f"Producto eliminado: {partida}")
            self.load_entradas()

