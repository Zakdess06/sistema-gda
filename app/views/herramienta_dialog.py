from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox
)
from PySide6.QtCore import Qt


class HerramientaDialog(QDialog):
    def __init__(self, parent=None, title="Nueva herramienta"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(420, 260)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Descripción
        layout.addWidget(QLabel("Descripción"))
        self.descripcion = QLineEdit()
        layout.addWidget(self.descripcion)

        # Ubicación
        layout.addWidget(QLabel("Ubicación"))
        self.ubicacion = QLineEdit()
        layout.addWidget(self.ubicacion)

        # Cantidad
        layout.addWidget(QLabel("Cantidad"))
        self.cantidad = QSpinBox()
        self.cantidad.setRange(1, 100000)
        layout.addWidget(self.cantidad)

        # Botones
        btns = QHBoxLayout()
        btns.addStretch()

        self.btn_ok = QPushButton("Guardar")
        self.btn_cancel = QPushButton("Cancelar")

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        btns.addWidget(self.btn_ok)
        btns.addWidget(self.btn_cancel)

        layout.addLayout(btns)

    def get_data(self):
        return (
            self.descripcion.text().strip(),
            self.ubicacion.text().strip(),
            self.cantidad.value()
        )

    def set_data(self, descripcion, ubicacion, cantidad):
        self.descripcion.setText(descripcion)
        self.ubicacion.setText(ubicacion)
        self.cantidad.setValue(cantidad)
