from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon

from app.core.store import store, AlmacenItem
from app.core.config import config
from app.core.bitacora import bitacora
from app.core.event_manager import event_manager
from app.views.producto_dialog import ProductoDialog
from app.views.restock_dialog import RestockDialog
from app.utils.table_utils import ajustar_ancho_tabla
from app.core.entradas_db import insert_entrada
from app.core.store import Entrada
from datetime import datetime
from app.core.database import get_connection, return_connection


class AlmacenView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== BOTONES =====
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("+ Agregar Producto")
        self.btn_add.setMinimumHeight(40)
        self.btn_add.setStyleSheet("""
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
        
        self.btn_restock = QPushButton("Hacer Restock")
        self.btn_restock.setMinimumHeight(40)
        self.btn_restock.setStyleSheet("""
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
        
        self.btn_edit = QPushButton("Editar Seleccionado")
        self.btn_edit.setMinimumHeight(40)
        self.btn_edit.setStyleSheet("""
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
        
        self.btn_delete = QPushButton("Eliminar Seleccionado")
        self.btn_delete.setMinimumHeight(40)
        self.btn_delete.setStyleSheet("""
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

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_restock)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # ===== TABLA =====
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "ID", "\u26a0", "Partida", "Descripción", "Unidad",
            "Cantidad", "Stock Mín.", "Ubicación", "Proveedor"
        ])
        # Configurar anchos apropiados para cada columna
        ajustar_ancho_tabla(self.table, anchos={
            0: 120,    # ID (Partida)
            1: 40,     # Advertencia
            2: 160,    # Partida
            3: 250,    # Descripción
            4: 70,     # Unidad
            5: 80,     # Cantidad
            6: 80,     # Stock Mín
            7: 150,    # Ubicación
            8: 150     # Proveedor
        })
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.btn_add.clicked.connect(self.add_product)
        self.btn_restock.clicked.connect(self.restock_selected)
        self.btn_edit.clicked.connect(self.edit_selected)
        self.btn_delete.clicked.connect(self.delete_selected)

        # escuchar cambios del store
        event_manager.almacen_changed.connect(self.load_data)

        self.load_data()

    def show_warning(self, title, text):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowModality(Qt.ApplicationModal)
        msg.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        msg.exec()

    # ===================== DATA =====================

    def load_data(self):
        self.table.setRowCount(0)
        almacen = store.get_almacen()
        for item in almacen.values():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item.id)))  # ID real
            self.table.setItem(row, 1, QTableWidgetItem(""))  # Advertencia (relleno)
            self.table.setItem(row, 2, QTableWidgetItem(item.partida))
            self.table.setItem(row, 3, QTableWidgetItem(item.descripcion))
            self.table.setItem(row, 4, QTableWidgetItem(item.unidad))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.cantidad)))
            self.table.setItem(row, 6, QTableWidgetItem(str(item.stock_minimo)))
            self.table.setItem(row, 7, QTableWidgetItem(item.ubicacion))
            self.table.setItem(row, 8, QTableWidgetItem(item.proveedor))

    # ===================== ACCIONES =====================

    def add_product(self):
        dialog = ProductoDialog(self)
        if dialog.exec():
            # ProductoDialog ya guardó el producto en la BD
            # Solo refrescar la vista y log
            self.load_data()
            if dialog.producto:
                bitacora.log("Almacén", f"Nuevo producto agregado: {dialog.producto.partida}")

    def restock_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            self.show_warning("Error", "Seleccione un producto para hacer restock")
            return
        partida = self.table.item(selected, 2).text()  # Columna 2 es la partida
        almacen = store.get_almacen()
        producto = almacen.get(partida)
        if not producto:
            QMessageBox.warning(self, "Error", "Producto no encontrado")
            return
        dialog = RestockDialog(self, producto)
        if dialog.exec():
            store.update_producto(producto)
            bitacora.log("Almacén", f"Restock realizado: {partida} - +{dialog.spin_cantidad.value()} unidades")
            # Registrar restock como entrada en auditoría (sin modificar almacén)
            recibio = getattr(dialog, 'recibio', "")
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO entradas_auditoria 
                (fecha, partida, descripcion, cantidad, unidad, proveedor, recibio, ubicacion, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().strftime("%d/%m/%Y"),
                producto.partida,
                producto.descripcion,
                dialog.spin_cantidad.value(),
                producto.unidad,
                producto.proveedor,
                recibio,
                producto.ubicacion,
                "Restock"
            ))
            conn.commit()
            return_connection(conn)
            event_manager.notify_entrada_add()

    def edit_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            self.show_warning("Error", "Seleccione un producto para editar")
            return
        producto_id = self.table.item(selected, 0).text()
        almacen = store.get_almacen()
        producto = None
        for item in almacen.values():
            if str(item.id) == producto_id:
                producto = item
                break
        if not producto:
            QMessageBox.warning(self, "Error", "Producto no encontrado")
            return
        # Crear una copia del producto para edición, asegurando que el id se mantenga
        from copy import deepcopy
        producto_edit = deepcopy(producto)
        dialog = ProductoDialog(self, producto_edit)
        if dialog.exec():
            # El dialog modifica producto_edit, que tiene el id correcto
            store.update_producto(producto_edit)
            bitacora.log("Almacén", f"Producto editado: {producto_id}")
            self.load_data()  # Refrescar la tabla inmediatamente

    def delete_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_warning("Error", "Seleccione un producto para eliminar")
            return

        selected = selected_rows[0].row()
        producto_id = self.table.item(selected, 0).text()
        partida = self.table.item(selected, 2).text()
        descripcion = self.table.item(selected, 3).text()
        
        # Mostrar ventana de confirmación
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Confirmar eliminación")
        msg_box.setText(f"¿Está seguro de que desea eliminar el producto?\n\nPartida: {partida}\nDescripción: {descripcion}")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec() == QMessageBox.Yes:
            # Aquí eliminamos directamente sin validaciones extras
            store.delete_producto(producto_id)
            bitacora.log("Almacén", f"Producto eliminado: {producto_id}")
