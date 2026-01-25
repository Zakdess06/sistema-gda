from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QSpinBox
)
from PySide6.QtCore import Qt


class ProductoDialog(QDialog):
    def __init__(self, parent=None, titulo="Producto"):
        super().__init__(parent)

        # Herencia de QSS
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setWindowTitle(titulo)
        self.setMinimumWidth(420)

        layout = QFormLayout(self)
        layout.setSpacing(16)

        self.descripcion = QLineEdit()
        self.cantidad = QSpinBox()
        self.ubicacion = QLineEdit()
        self.proveedor = QLineEdit()

        self.descripcion.setPlaceholderText("Descripción")
        self.ubicacion.setPlaceholderText("Ubicación")
        self.proveedor.setPlaceholderText("Proveedor")

        self.cantidad.setRange(0, 999999)

        layout.addRow("Descripción:", self.descripcion)
        layout.addRow("Cantidad:", self.cantidad)
        layout.addRow("Ubicación:", self.ubicacion)
        layout.addRow("Proveedor:", self.proveedor)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Guardar")
        self.btn_cancel = QPushButton("Cancelar")

        self.btn_ok.setObjectName("ActionButton")
        self.btn_cancel.setObjectName("ActionButton")

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)

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
