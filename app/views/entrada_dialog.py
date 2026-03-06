from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QSpinBox, 
    QComboBox, QMessageBox, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt
from datetime import date

from app.core.store import store, Entrada, AlmacenItem
from app.core.bitacora import bitacora
from app.core.event_manager import event_manager


class EntradaDialog(QDialog):
    def __init__(self, parent=None, entrada=None):
        super().__init__(parent)

        # Herencia de QSS
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.entrada = entrada
        if entrada:
            self.setWindowTitle("Editar Entrada")
        else:
            self.setWindowTitle("Nueva Entrada")

        self.setMinimumWidth(550)
        self.setMinimumHeight(550)

        # ===== LAYOUT PRINCIPAL =====
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ===== TÍTULO DESCRIPTIVO =====
        title_label = QLabel(
            "Editar información del producto"
            if entrada else "Registrar nuevo producto"
        )
        title_label.setStyleSheet("font-size: 13px; font-weight: 600; opacity: 0.9;")
        main_layout.addWidget(title_label)

        # ===== FORMULARIO =====
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # ----- CAMPOS PRINCIPALES -----
        self.txt_descripcion = QLineEdit()
        
        # Campos de unidad y stock mínimo
        self.cmb_unidad = QComboBox()
        unidades = ["Pza", "Kg", "Mt", "Lt", "Caja", "Rollo", "Tubo", "Otro"]
        self.cmb_unidad.addItems(unidades)
        
        self.spin_stock_minimo = QSpinBox()
        self.spin_stock_minimo.setRange(0, 999999)
        self.spin_stock_minimo.setValue(5)
        self.spin_stock_minimo.setMinimumHeight(36)
        
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 100000)
        self.spin_cantidad.setMinimumHeight(36)
        
        self.cmb_proveedor = QComboBox()
        self.cmb_proveedor.setEditable(False)
        self.cmb_proveedor.setMinimumHeight(36)
        
        self.txt_ubicacion = QLineEdit()
        
        self.cmb_recibio = QComboBox()
        self.cmb_recibio.setEditable(False)
        self.cmb_recibio.setMinimumHeight(36)
        
        self.txt_obs = QLineEdit()

        # Cargar proveedores
        self.load_proveedores()
        
        # Cargar trabajadores
        self.load_trabajadores()

        # Placeholders
        self.txt_descripcion.setPlaceholderText("Ej: Cemento Portland 50kg")
        self.txt_ubicacion.setPlaceholderText("Ej: Pasillo 2 - Estante A")
        self.txt_obs.setPlaceholderText("Observaciones (opcional)")

        # Cargar datos si es edición
        if entrada:
            self.txt_descripcion.setText(entrada.descripcion)
            self.spin_cantidad.setValue(entrada.cantidad)
            self.cmb_proveedor.setCurrentText(entrada.proveedor)
            self.txt_ubicacion.setText(entrada.ubicacion)
            self.cmb_recibio.setCurrentText(entrada.recibio)
            self.txt_obs.setText(entrada.observaciones)

        form_layout.addRow("Descripción:", self.txt_descripcion)
        form_layout.addRow("Unidad:", self.cmb_unidad)
        form_layout.addRow("Stock Mínimo:", self.spin_stock_minimo)
        form_layout.addRow("Cantidad:", self.spin_cantidad)
        form_layout.addRow("Proveedor:", self.cmb_proveedor)
        form_layout.addRow("Ubicación:", self.txt_ubicacion)
        form_layout.addRow("Recibió:", self.cmb_recibio)
        form_layout.addRow("Observaciones:", self.txt_obs)

        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        # ----- BOTONES -----
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_guardar.setObjectName("PrimaryButton")
        self.btn_cancelar.setObjectName("ActionButton")
        
        self.btn_guardar.setMinimumHeight(40)
        self.btn_cancelar.setMinimumHeight(40)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancelar, 1)
        btn_layout.addWidget(self.btn_guardar, 1)

        main_layout.addLayout(btn_layout)

        # ----- CONEXIONES -----
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.reject)

    def load_proveedores(self):
        """Carga los proveedores registrados en la BD"""
        self.cmb_proveedor.clear()
        self.cmb_proveedor.addItem("Sin proveedor")
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
        self.cmb_recibio.addItem("Sin asignar")
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
                # Edición: actualizar entrada en auditoría
                from datetime import datetime
                from app.core.entradas_db import insert_entrada
                
                # Crear nueva entrada en auditoría (registro de cambio)
                entrada_editada = Entrada(
                    codigo="",
                    fecha=datetime.now().strftime("%d/%m/%Y"),
                    partida=self.entrada.partida,
                    descripcion=descripcion,
                    cantidad=cantidad,
                    unidad=unidad,
                    proveedor=proveedor,
                    recibio=recibio,
                    ubicacion=ubicacion,
                    stock_minimo=stock_minimo,
                    observaciones=obs
                )
                
                # Guardar cambio en auditoría (actualiza cantidad)
                insert_entrada(entrada_editada)
                
                # Actualizar entrada en memoria
                self.entrada.descripcion = descripcion
                self.entrada.cantidad = cantidad
                self.entrada.unidad = unidad
                self.entrada.proveedor = proveedor
                self.entrada.ubicacion = ubicacion
                self.entrada.recibio = recibio
                self.entrada.observaciones = obs

                bitacora.log("Almacén", f"Producto actualizado: {self.entrada.partida} - {cantidad} {unidad}")
                store.notify()  # Notificar cambios y recargar desde BD
                event_manager.notify_entrada_add()  # Notificar cambios
                QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
            else:
                # Creación: generar partida automáticamente y crear entrada auditada
                from datetime import datetime
                from app.core.entradas_db import insert_entrada
                
                partida = store.generar_codigo_partida()
                
                # Crear objeto Entrada para auditoría
                entrada_auditada = Entrada(
                    codigo="",
                    fecha=datetime.now().strftime("%d/%m/%Y"),
                    partida=partida,
                    descripcion=descripcion,
                    cantidad=cantidad,
                    unidad=unidad,
                    proveedor=proveedor,
                    recibio=recibio,
                    ubicacion=ubicacion,
                    stock_minimo=stock_minimo,
                    observaciones=obs
                )
                
                # Guardar entrada (esto también guarda el producto en almacén)
                insert_entrada(entrada_auditada)
                
                bitacora.log("Almacén", f"Entrada registrada: {partida} ({descripcion}) - {cantidad} {unidad} | Proveedor: {proveedor} | Recibió: {recibio}")
                store.notify()  # Notificar cambios y recargar datos desde BD
                event_manager.notify_entrada_add()  # Notificar cambios para actualizar dashboard
                QMessageBox.information(self, "Éxito", f"Producto registrado: {partida}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.accept()
