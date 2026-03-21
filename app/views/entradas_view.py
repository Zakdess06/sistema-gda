from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QDialog
)

from app.core.store import store, Entrada
from app.core.bitacora import bitacora
from app.core.event_manager import event_manager
from app.views.entrada_dialog import EntradaDialog
from app.utils.table_utils import ajustar_ancho_tabla
class EntradasView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ========= BOTONES =========
        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("+ Agregar Producto")
        self.btn_agregar.setMinimumHeight(40)
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                min-height: 40px;
                min-width: 100px;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                background-color: #2563eb;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #3b82f6;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        
        self.btn_editar = QPushButton("✎ Editar Seleccionado")
        self.btn_editar.setMinimumHeight(40)
        self.btn_editar.setStyleSheet("""
            QPushButton {
                min-height: 40px;
                min-width: 100px;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                background-color: #161d26;
                color: #f0f4f8;
                border: 1px solid #1f2937;
            }
            QPushButton:hover {
                background-color: #1f2937;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #0f1419;
            }
        """)
        
        self.btn_eliminar = QPushButton("✕ Eliminar Seleccionado")
        self.btn_eliminar.setMinimumHeight(40)
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                min-height: 40px;
                min-width: 100px;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                background-color: #dc2626;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #ef4444;
            }
            QPushButton:pressed {
                background-color: #991b1b;
            }
        """)
        
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
        ajustar_ancho_tabla(self.table, anchos={
            0: 160,     # Partida
            1: 280,     # Descripción
            2: 80,      # Cantidad
            3: 70,      # Unidad
            4: 150,     # Proveedor
            5: 200      # Ubicación (se estira)
        })
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
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

    def show_warning(self, title, text):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowModality(Qt.ApplicationModal)
        msg.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        msg.exec()

    def selected_partida(self):
        """Obtiene la partida de la entrada seleccionada"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
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
            self.show_warning("Error", "Seleccione una entrada")
            return
        
        from app.core.entradas_db import fetch_all_entradas
        entradas = fetch_all_entradas()
        entrada = None
        for e in entradas:
            if e.partida == partida:
                entrada = e
                break
        
        if not entrada:
            self.show_warning("Error", "Entrada no encontrada")
            return
        
        dialog = EntradaDialog(self, entrada)
        if dialog.exec() == QDialog.Accepted:
            self.load_entradas()

    def eliminar(self):
        partida = self.selected_partida()
        if not partida:
            self.show_warning("Error", "Seleccione una entrada")
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

