from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QSpinBox, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt

from app.core.store import store, AlmacenItem
from app.core.entradas_db import insert_entrada
from app.core.store import Entrada
from datetime import datetime
from app.core.event_manager import event_manager
from app.core.trabajador_db import fetch_all_trabajadores


class ProductoDialog(QDialog):
    def __init__(self, parent=None, producto=None):
        super().__init__(parent)

        # Herencia de QSS
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.producto = producto
        if producto:
            self.setWindowTitle("Editar Producto")
        else:
            self.setWindowTitle("Agregar Producto")

        self.setMinimumWidth(450)

        layout = QFormLayout(self)
        layout.setSpacing(16)

        # ----- CAMPOS PRINCIPALES -----
        self.txt_partida = QLineEdit()
        self.txt_descripcion = QLineEdit()
        self.cmb_unidad = QComboBox()
        self.spin_cantidad = QSpinBox()
        self.spin_stock_minimo = QSpinBox()
        self.txt_ubicacion = QLineEdit()
        self.cmb_proveedor = QComboBox()
        self.cmb_proveedor.setEditable(False)

        # cargar proveedores existentes
        try:
            from app.core.proveedor_db import fetch_all_proveedores
            provs = fetch_all_proveedores()
            for p in provs:
                name = p.get('nombre_comercial') or ''
                if name:
                    self.cmb_proveedor.addItem(name)
        except Exception:
            pass

        # Unidades comunes
        unidades = ["Pza", "Kg", "Mt", "Lt", "Caja", "Rollo", "Tubo", "Otro"]
        self.cmb_unidad.addItems(unidades)

        # Configurar spinboxes
        self.spin_cantidad.setRange(0, 999999)
        self.spin_stock_minimo.setRange(0, 999999)

        # Placeholders
        self.txt_partida.setPlaceholderText("Se genera automáticamente")
        self.txt_descripcion.setPlaceholderText("Descripción del producto")
        self.txt_ubicacion.setPlaceholderText("Ej: Estante A, Gaveta 3")

        # Campo trabajador que recibe
        self.cmb_recibio = QComboBox()
        self.cmb_recibio.addItem("")
        try:
            for trab in fetch_all_trabajadores():
                self.cmb_recibio.addItem(trab['nombre'])
        except Exception:
            pass
        layout.insertRow(7, "Recibió:", self.cmb_recibio)

        # Cargar datos si es edición
        if producto:
            self.txt_partida.setText(producto.partida)
            self.txt_partida.setReadOnly(True)  # No permitir cambiar partida
            self.txt_descripcion.setText(producto.descripcion)
            self.cmb_unidad.setCurrentText(producto.unidad)
            self.spin_cantidad.setValue(producto.cantidad)
            self.spin_stock_minimo.setValue(producto.stock_minimo)
            self.txt_ubicacion.setText(producto.ubicacion)
            # intentar seleccionar proveedor en combo
            if producto.proveedor:
                index = self.cmb_proveedor.findText(producto.proveedor)
                if index >= 0:
                    self.cmb_proveedor.setCurrentIndex(index)
        else:
            # Auto-generar código para nuevo producto
            self.cmb_proveedor.currentTextChanged.connect(self.actualizar_codigo_partida)
            proveedor_nombre = self.cmb_proveedor.currentText().strip()
            codigo_auto = store.generar_codigo_partida(proveedor_nombre)
            self.txt_partida.setText(codigo_auto)
            self.txt_partida.setReadOnly(True)

        layout.addRow("Partida:", self.txt_partida)
        layout.addRow("Descripción:", self.txt_descripcion)
        layout.addRow("Unidad:", self.cmb_unidad)
        layout.addRow("Cantidad Actual:", self.spin_cantidad)
        layout.addRow("Stock Mínimo:", self.spin_stock_minimo)
        layout.addRow("Ubicación:", self.txt_ubicacion)
        layout.addRow("Proveedor:", self.cmb_proveedor)
        layout.addRow("Recibió:", self.cmb_recibio)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Guardar")
        self.btn_cancel = QPushButton("Cancelar")

        self.btn_ok.setObjectName("ActionButton")
        self.btn_cancel.setObjectName("ActionButton")

        self.btn_ok.clicked.connect(self.guardar)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)

        layout.addRow(btn_layout)

    def guardar(self):
        # Validaciones
        partida = self.txt_partida.text().strip()
        descripcion = self.txt_descripcion.text().strip()
        unidad = self.cmb_unidad.currentText()
        cantidad = self.spin_cantidad.value()
        stock_minimo = self.spin_stock_minimo.value()
        ubicacion = self.txt_ubicacion.text().strip()
        proveedor = self.cmb_proveedor.currentText().strip()
        recibio = self.cmb_recibio.currentText().strip()

        if not partida:
            QMessageBox.warning(self, "Error", "La partida es obligatoria")
            return

        if not descripcion:
            QMessageBox.warning(self, "Error", "La descripción es obligatoria")
            return


        if not ubicacion:
            QMessageBox.warning(self, "Error", "La ubicación es obligatoria")
            return

        # Verificar si partida ya existe (solo en agregar nuevo)
        almacen = store.get_almacen()
        if not self.producto and partida in almacen:
            QMessageBox.warning(self, "Error", f"La partida {partida} ya existe")
            return

        # Crear o actualizar producto
        if self.producto:
            # Edición: actualizar campos y persistir
            self.producto.descripcion = descripcion
            self.producto.unidad = unidad
            self.producto.cantidad = cantidad
            self.producto.ubicacion = ubicacion
            self.producto.proveedor = proveedor
            self.producto.stock_minimo = stock_minimo
            store.update_producto(self.producto)
        else:
            # Creación: crear item y persistir
            nuevo = AlmacenItem(
                partida=partida,
                descripcion=descripcion,
                unidad=unidad,
                cantidad=cantidad,
                ubicacion=ubicacion,
                proveedor=proveedor,
                stock_minimo=stock_minimo
            )
            store.add_producto(nuevo)
            # --- REGISTRAR ENTRADA EN AUDITORÍA ---
            from app.core.entradas_db import insert_entrada
            from app.core.store import Entrada
            from datetime import datetime
            recibio = self.cmb_recibio.currentText().strip()
            entrada_auditoria = Entrada(
                codigo="",
                fecha=datetime.now().strftime("%d/%m/%Y"),
                partida=partida,
                descripcion=descripcion,
                cantidad=cantidad,
                unidad=unidad,
                proveedor=proveedor,
                recibio=recibio,
                ubicacion=ubicacion,
                observaciones=""
            )
            insert_entrada(entrada_auditoria)
        self.accept()

    def get_data(self):
        return (
            self.txt_descripcion.text().strip(),
            self.spin_cantidad.value(),
            self.txt_ubicacion.text().strip(),
            self.cmb_proveedor.currentText().strip(),
            self.cmb_recibio.currentText().strip()
        )

    def set_data(self, d, c, u, p):
        self.txt_descripcion.setText(d)
        self.spin_cantidad.setValue(int(c))
        self.txt_ubicacion.setText(u)
        try:
            self.cmb_proveedor.setCurrentText(p)
        except Exception:
            self.cmb_proveedor.setEditText(p or "")

    def actualizar_codigo_partida(self):
        # Solo actualizar si es un producto nuevo (no edición)
        if not self.producto:
            proveedor_nombre = self.cmb_proveedor.currentText().strip()
            codigo_auto = store.generar_codigo_partida(proveedor_nombre)
            self.txt_partida.setText(codigo_auto)
