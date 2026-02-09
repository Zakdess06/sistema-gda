from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QSpinBox, QComboBox, QMessageBox, QVBoxLayout
)
from PySide6.QtCore import Qt
from datetime import date

from app.core.store import store, Entrada, AlmacenItem
from app.core.bitacora import bitacora


class EntradaDialog(QDialog):
    def __init__(self, parent=None, entrada=None):
        super().__init__(parent)

        # Herencia de QSS
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.entrada = entrada
        if entrada:
            self.setWindowTitle("Editar Entrada")
        else:
            self.setWindowTitle("Registrar Entrada")

        self.setMinimumWidth(550)

        main_layout = QVBoxLayout(self)
        layout = QFormLayout()
        layout.setSpacing(16)
        main_layout.addLayout(layout)

        # ----- CAMPOS PRINCIPALES -----
        # Ya no necesitamos código y fecha - una entrada ahora es solo crear un producto
        
        self.txt_descripcion = QLineEdit()
        
        # Campos de unidad y stock mínimo (siempre visibles)
        self.cmb_unidad = QComboBox()
        unidades = ["Pza", "Kg", "Mt", "Lt", "Caja", "Rollo", "Tubo", "Otro"]
        self.cmb_unidad.addItems(unidades)
        
        self.spin_stock_minimo = QSpinBox()
        self.spin_stock_minimo.setRange(0, 999999)
        self.spin_stock_minimo.setValue(5)
        
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 100000)
        
        self.cmb_proveedor = QComboBox()
        self.cmb_proveedor.setEditable(False)
        
        self.txt_ubicacion = QLineEdit()
        
        self.cmb_recibio = QComboBox()
        self.cmb_recibio.setEditable(False)
        
        self.txt_obs = QLineEdit()

        # Cargar proveedores
        self.load_proveedores()
        
        # Cargar trabajadores
        self.load_trabajadores()

        # Placeholders
        self.txt_descripcion.setPlaceholderText("Descripción del producto")
        self.txt_ubicacion.setPlaceholderText("Ubicación del almacén")
        self.txt_obs.setPlaceholderText("Observaciones")

        # Cargar datos si es edición
        if entrada:
            self.txt_descripcion.setText(entrada.descripcion)
            self.spin_cantidad.setValue(entrada.cantidad)
            self.cmb_proveedor.setCurrentText(entrada.proveedor)
            self.txt_ubicacion.setText(entrada.ubicacion)
            self.cmb_recibio.setCurrentText(entrada.recibio)
            self.txt_obs.setText(entrada.observaciones)
        else:
            # Nueva entrada - valores por defecto
            pass

        layout.addRow("Descripción:", self.txt_descripcion)
        layout.addRow("Unidad:", self.cmb_unidad)
        layout.addRow("Stock Mínimo:", self.spin_stock_minimo)
        layout.addRow("Cantidad:", self.spin_cantidad)
        layout.addRow("Proveedor:", self.cmb_proveedor)
        layout.addRow("Ubicación:", self.txt_ubicacion)
        layout.addRow("Recibió:", self.cmb_recibio)
        layout.addRow("Observaciones:", self.txt_obs)

        # ----- BOTONES -----
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)

        main_layout.addLayout(btn_layout)

        # ----- CONEXIONES -----
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.reject)

    def load_proveedores(self):
        """Carga los proveedores registrados en la BD"""
        self.cmb_proveedor.clear()
        try:
            from app.core.proveedor_db import fetch_all_proveedores
            proveedores = fetch_all_proveedores()
            for prov in proveedores:
                nombre = prov.get('nombre_comercial') or prov.get('nombre_fiscal') or ''
                if nombre:
                    self.cmb_proveedor.addItem(nombre)
        except Exception:
            pass

    def load_trabajadores(self):
        """Carga los trabajadores registrados en el store"""
        self.cmb_recibio.clear()
        try:
            for trab in store.trabajadores.values():
                self.cmb_recibio.addItem(trab.nombre)
        except Exception:
            pass

    def guardar(self):
        descripcion = self.txt_descripcion.text().strip()
        unidad = self.cmb_unidad.currentText().strip()
        stock_minimo = self.spin_stock_minimo.value()
        cantidad = self.spin_cantidad.value()
        proveedor = self.cmb_proveedor.currentText().strip()
        ubicacion = self.txt_ubicacion.text().strip()
        recibio = self.cmb_recibio.currentText().strip()
        obs = self.txt_obs.text().strip()

        if not descripcion or not cantidad or not unidad or not ubicacion:
            QMessageBox.warning(self, "Error", "Complete los campos obligatorios")
            return

        if stock_minimo <= 0:
            QMessageBox.warning(self, "Error", "Stock Mínimo debe ser mayor a 0")
            return

        try:
            if self.entrada:
                # Edición: actualizar producto existente
                self.entrada.descripcion = descripcion
                self.entrada.cantidad = cantidad
                self.entrada.unidad = unidad
                self.entrada.proveedor = proveedor
                self.entrada.ubicacion = ubicacion
                self.entrada.recibio = recibio
                self.entrada.observaciones = obs

                store.update_entrada(self.entrada)
                bitacora.log("Almacén", f"Producto actualizado: {self.entrada.partida} - {cantidad} {unidad}")
                QMessageBox.information(self, "OK", "Producto actualizado")
            else:
                # Creación: generar partida automáticamente y crear producto
                partida = store.generar_codigo_partida()
                
                # Crear el nuevo producto
                nuevo_producto = AlmacenItem(
                    partida=partida,
                    descripcion=descripcion,
                    unidad=unidad,
                    cantidad=cantidad,
                    ubicacion=ubicacion,
                    proveedor=proveedor,
                    stock_minimo=stock_minimo
                )
                store.add_producto(nuevo_producto)
                bitacora.log("Almacén", f"Entrada registrada: {partida} ({descripcion}) - {cantidad} {unidad} | Proveedor: {proveedor} | Recibió: {recibio}")
                QMessageBox.information(self, "OK", f"Producto registrado: {partida}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.accept()
