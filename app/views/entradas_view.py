from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout,
    QComboBox, QSpinBox, QLineEdit,
    QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QDialog
)
from datetime import date

from app.core.store import store, Entrada
from app.core.bitacora import bitacora
from app.views.entrada_dialog import EntradaDialog
from app.views.producto_dialog import ProductoDialog
class EntradasView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ========= BOTONES =========
        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("+ Agregar Entrada")
        self.btn_editar = QPushButton("✎ Editar Seleccionado")
        self.btn_eliminar = QPushButton("✕ Eliminar Seleccionado")
        
        btn_layout.addWidget(self.btn_agregar)
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # ========= TABLA =========
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Código", "Fecha", "Partida", "Descripción",
            "Cantidad", "Proveedor", "Ubicación"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # ========= CONEXIONES =========
        self.btn_agregar.clicked.connect(self.agregar)
        self.btn_editar.clicked.connect(self.editar)
        self.btn_eliminar.clicked.connect(self.eliminar)

        store.subscribe(self.load_entradas)
        self.load_entradas()

    def selected_codigo(self):
        """Obtiene el código de la entrada seleccionada"""
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).text()
    # ---------- CARGAS ----------
    def load_entradas(self):
        """Carga las entradas desde la BD"""
        self.table.setRowCount(0)
        
        # Recargar desde BD para obtener los datos más recientes
        from app.core.entradas_db import fetch_all_entradas
        entradas = fetch_all_entradas()
        
        for e in entradas:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(e.codigo))
            self.table.setItem(row, 1, QTableWidgetItem(e.fecha))
            self.table.setItem(row, 2, QTableWidgetItem(e.partida))
            self.table.setItem(row, 3, QTableWidgetItem(e.descripcion))
            self.table.setItem(row, 4, QTableWidgetItem(str(e.cantidad)))
            self.table.setItem(row, 5, QTableWidgetItem(e.proveedor))
            self.table.setItem(row, 6, QTableWidgetItem(e.ubicacion))

    # ---------- ACCIONES ----------
    def agregar(self):
        dialog = EntradaDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_entradas()

    def editar(self):
        codigo = self.selected_codigo()
        if not codigo:
            QMessageBox.warning(self, "Error", "Seleccione una entrada")
            return
        
        from app.core.entradas_db import fetch_all_entradas
        entradas = fetch_all_entradas()
        entrada = None
        for e in entradas:
            if e.codigo == codigo:
                entrada = e
                break
        
        if not entrada:
            QMessageBox.warning(self, "Error", "Entrada no encontrada")
            return
        
        dialog = EntradaDialog(self, entrada)
        if dialog.exec() == QDialog.Accepted:
            self.load_entradas()

    def eliminar(self):
        codigo = self.selected_codigo()
        if not codigo:
            QMessageBox.warning(self, "Error", "Seleccione una entrada")
            return
        
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar la entrada {codigo}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            from app.core.entradas_db import fetch_all_entradas, delete_entrada
            entradas = fetch_all_entradas()
            for e in entradas:
                if e.codigo == codigo:
                    # Encontrar el ID basado en la posición
                    delete_entrada(entradas.index(e) + 1)
                    bitacora.log("Entrada", f"Entrada eliminada: {codigo}")
                    self.load_entradas()
                    return

