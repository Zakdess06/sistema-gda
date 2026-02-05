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
        self.txt_proveedor = QLineEdit()

        # Unidades comunes
        unidades = ["Pza", "Kg", "Mt", "Lt", "Caja", "Rollo", "Tubo", "Otro"]
        self.cmb_unidad.addItems(unidades)

        # Configurar spinboxes
        self.spin_cantidad.setRange(0, 999999)
        self.spin_stock_minimo.setRange(0, 999999)

        # Placeholders
        self.txt_partida.setPlaceholderText("Ej: E-001")
        self.txt_descripcion.setPlaceholderText("Descripción del producto")
        self.txt_ubicacion.setPlaceholderText("Ej: Estante A, Gaveta 3")
        self.txt_proveedor.setPlaceholderText("Nombre del proveedor")

        # Cargar datos si es edición
        if producto:
            self.txt_partida.setText(producto.partida)
            self.txt_partida.setReadOnly(True)  # No permitir cambiar partida
            self.txt_descripcion.setText(producto.descripcion)
            self.cmb_unidad.setCurrentText(producto.unidad)
            self.spin_cantidad.setValue(producto.cantidad)
            self.txt_ubicacion.setText(producto.ubicacion)
            self.txt_proveedor.setText(producto.proveedor)

        layout.addRow("Partida:", self.txt_partida)
        layout.addRow("Descripción:", self.txt_descripcion)
        layout.addRow("Unidad:", self.cmb_unidad)
        layout.addRow("Cantidad Actual:", self.spin_cantidad)
        layout.addRow("Stock Mínimo:", self.spin_stock_minimo)
        layout.addRow("Ubicación:", self.txt_ubicacion)
        layout.addRow("Proveedor:", self.txt_proveedor)

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
        proveedor = self.txt_proveedor.text().strip()

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
        if not self.producto and partida in store.almacen:
            QMessageBox.warning(self, "Error", f"La partida {partida} ya existe")
            return

        # Crear o actualizar producto
        if self.producto:
            # Edición
            self.producto.descripcion = descripcion
            self.producto.unidad = unidad
            self.producto.cantidad = cantidad
            self.producto.ubicacion = ubicacion
            self.producto.proveedor = proveedor
        else:
            # Creación
            nuevo = AlmacenItem(
                partida=partida,
                descripcion=descripcion,
                unidad=unidad,
                cantidad=cantidad,
                ubicacion=ubicacion,
                proveedor=proveedor
            )
            store.almacen[partida] = nuevo

        store.notify()
        self.accept()

        layout.addRow(btn_layout)

    def get_data(self):
        return (
            self.descripcion.text().strip(),
            self.cantidad.value(),
            self.ubicacion.text().strip(),
            self.proveedor.text().strip()
        )

    def set_data(self, d, c, u, p):
        self.descripcion.setText(d)
        self.cantidad.setValue(int(c))
        self.ubicacion.setText(u)
        self.proveedor.setText(p)
