from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QSpinBox, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt

from app.core.store import store, AlmacenItem


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

        # Cargar datos si es edición
        if producto:
            self.txt_partida.setText(producto.partida)
            self.txt_partida.setReadOnly(True)  # No permitir cambiar partida
            self.txt_descripcion.setText(producto.descripcion)
            self.cmb_unidad.setCurrentText(producto.unidad)
            self.spin_cantidad.setValue(producto.cantidad)
            self.txt_ubicacion.setText(producto.ubicacion)
            # intentar seleccionar proveedor en combo
            if producto.proveedor:
                index = self.cmb_proveedor.findText(producto.proveedor)
                if index >= 0:
                    self.cmb_proveedor.setCurrentIndex(index)
        else:
            # Auto-generar código para nuevo producto
            codigo_auto = store.generar_codigo_partida()
            self.txt_partida.setText(codigo_auto)
            self.txt_partida.setReadOnly(True)

        layout.addRow("Partida:", self.txt_partida)
        layout.addRow("Descripción:", self.txt_descripcion)
        layout.addRow("Unidad:", self.cmb_unidad)
        layout.addRow("Cantidad Actual:", self.spin_cantidad)
        layout.addRow("Stock Mínimo:", self.spin_stock_minimo)
        layout.addRow("Ubicación:", self.txt_ubicacion)
        layout.addRow("Proveedor:", self.cmb_proveedor)

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

        if not partida:
            QMessageBox.warning(self, "Error", "La partida es obligatoria")
            return

        if not descripcion:
            QMessageBox.warning(self, "Error", "La descripción es obligatoria")
            return

        if stock_minimo == 0:
            QMessageBox.warning(self, "Error", "El stock mínimo es obligatorio")
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
            self.producto = nuevo  # Asignar al atributo para poder acceder después
            store.add_producto(nuevo)

        self.accept()

    def get_data(self):
        return (
            self.txt_descripcion.text().strip(),
            self.spin_cantidad.value(),
            self.txt_ubicacion.text().strip(),
            self.cmb_proveedor.currentText().strip()
        )

    def set_data(self, d, c, u, p):
        self.txt_descripcion.setText(d)
        self.spin_cantidad.setValue(int(c))
        self.txt_ubicacion.setText(u)
        try:
            self.cmb_proveedor.setCurrentText(p)
        except Exception:
            self.cmb_proveedor.setEditText(p or "")
