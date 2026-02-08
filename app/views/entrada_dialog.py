from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QSpinBox, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from datetime import date

from app.core.store import store, Entrada
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

        self.setMinimumWidth(500)

        layout = QFormLayout(self)
        layout.setSpacing(16)

        # ----- CAMPOS PRINCIPALES -----
        self.txt_codigo = QLineEdit()
        self.txt_codigo.setReadOnly(True)
        
        self.txt_fecha = QLineEdit()
        self.txt_fecha.setReadOnly(True)
        
        self.cmb_partida = QComboBox()
        self.cmb_partida.setEditable(True)
        
        self.txt_descripcion = QLineEdit()
        
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
        
        # Cargar partidas
        self.load_partidas()
        
        # Cargar trabajadores
        self.load_trabajadores()

        # Placeholders
        self.txt_codigo.setPlaceholderText("Código automático")
        self.txt_descripcion.setPlaceholderText("Descripción del producto")
        self.txt_ubicacion.setPlaceholderText("Ubicación del almacén")
        self.txt_obs.setPlaceholderText("Observaciones")

        # Cargar datos si es edición
        if entrada:
            self.txt_codigo.setText(entrada.codigo)
            self.txt_fecha.setText(entrada.fecha)
            self.cmb_partida.setCurrentText(entrada.partida)
            self.txt_descripcion.setText(entrada.descripcion)
            self.spin_cantidad.setValue(entrada.cantidad)
            self.cmb_proveedor.setCurrentText(entrada.proveedor)
            self.txt_ubicacion.setText(entrada.ubicacion)
            self.cmb_recibio.setCurrentText(entrada.recibio)
            self.txt_obs.setText(entrada.observaciones)
        else:
            # Auto-generar código para nueva entrada
            codigo_auto = store.generar_codigo_entrada()
            self.txt_codigo.setText(codigo_auto)
            self.txt_fecha.setText(str(date.today()))

        layout.addRow("Código:", self.txt_codigo)
        layout.addRow("Fecha:", self.txt_fecha)
        layout.addRow("Partida:", self.cmb_partida)
        layout.addRow("Descripción:", self.txt_descripcion)
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

        layout.addRow(btn_layout)

        # ----- CONEXIONES -----
        self.cmb_partida.currentTextChanged.connect(self.update_descripcion)
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.reject)

    def load_partidas(self):
        """Carga las partidas del almacén"""
        self.cmb_partida.clear()
        almacen = store.get_almacen()
        for partida in almacen.keys():
            self.cmb_partida.addItem(partida)

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

    def update_descripcion(self, partida):
        """Auto-completa descripción y ubicación basado en partida (solo en edición)"""
        # Solo auto-completar si estamos editando
        if self.entrada:
            almacen = store.get_almacen()
            item = almacen.get(partida)
            if item:
                self.txt_descripcion.setText(item.descripcion)
                self.txt_ubicacion.setText(item.ubicacion)
            else:
                self.txt_descripcion.clear()
                self.txt_ubicacion.clear()

    def guardar(self):
        codigo = self.txt_codigo.text().strip()
        fecha = self.txt_fecha.text().strip()
        partida = self.cmb_partida.currentText().strip()
        descripcion = self.txt_descripcion.text().strip()
        cantidad = self.spin_cantidad.value()
        proveedor = self.cmb_proveedor.currentText().strip()
        ubicacion = self.txt_ubicacion.text().strip()
        recibio = self.cmb_recibio.currentText().strip()
        obs = self.txt_obs.text().strip()

        if not codigo or not fecha or not partida or not cantidad:
            QMessageBox.warning(self, "Error", "Complete los campos obligatorios")
            return

        try:
            almacen = store.get_almacen()
            unidad = almacen.get(partida, {}).unidad if partida in almacen else ''

            if self.entrada:
                # Edición: actualizar entrada existente
                self.entrada.fecha = fecha
                self.entrada.partida = partida
                self.entrada.descripcion = descripcion
                self.entrada.cantidad = cantidad
                self.entrada.unidad = unidad
                self.entrada.proveedor = proveedor
                self.entrada.ubicacion = ubicacion
                self.entrada.recibio = recibio
                self.entrada.observaciones = obs

                store.update_entrada(self.entrada)
                bitacora.log("Entrada", f"Entrada {codigo} actualizada: {partida} +{cantidad}")
                QMessageBox.information(self, "OK", "Entrada actualizada")
            else:
                # Creación: nueva entrada
                entrada = Entrada(
                    codigo=codigo,
                    fecha=fecha,
                    partida=partida,
                    descripcion=descripcion,
                    cantidad=cantidad,
                    unidad=unidad,
                    proveedor=proveedor,
                    recibio=recibio,
                    ubicacion=ubicacion,
                    observaciones=obs
                )
                store.add_entrada(entrada)
                bitacora.log("Entrada", f"Entrada {codigo} registrada: {partida} +{cantidad} | Recibió: {recibio}")
                QMessageBox.information(self, "OK", "Entrada registrada")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.accept()
