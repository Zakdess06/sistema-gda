# app/views/restock_dialog.py

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QSpinBox, QLabel, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from app.core.trabajador_db import fetch_all_trabajadores


class RestockDialog(QDialog):
    """Diálogo para hacer restock de un producto existente (solo solicita cantidad)"""
    
    def __init__(self, parent=None, producto=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setWindowTitle("Hacer Restock")
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.raise_()
        self.activateWindow()
        self.setMinimumWidth(400)

        self.producto = producto

        layout = QFormLayout(self)
        layout.setSpacing(16)

        # Información del producto (solo lectura)
        lbl_partida = QLineEdit()
        lbl_partida.setText(producto.partida)
        lbl_partida.setReadOnly(True)
        layout.addRow("Partida:", lbl_partida)

        lbl_descripcion = QLineEdit()
        lbl_descripcion.setText(producto.descripcion)
        lbl_descripcion.setReadOnly(True)
        layout.addRow("Descripción:", lbl_descripcion)

        lbl_cantidad_actual = QLineEdit()
        lbl_cantidad_actual.setText(str(producto.cantidad))
        lbl_cantidad_actual.setReadOnly(True)
        layout.addRow("Cantidad Actual:", lbl_cantidad_actual)

        # Solo campo de cantidad a agregar
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 999999)
        self.spin_cantidad.setValue(1)
        self.spin_cantidad.setToolTip("Cantidad a agregar al stock actual")
        layout.addRow("Cantidad a Agregar:", self.spin_cantidad)

        # Cantidad resultante (informativa)
        self.lbl_nueva_cantidad = QLineEdit()
        self.lbl_nueva_cantidad.setReadOnly(True)
        self.actualizar_nueva_cantidad()
        self.spin_cantidad.valueChanged.connect(self.actualizar_nueva_cantidad)
        layout.addRow("Cantidad Total:", self.lbl_nueva_cantidad)

        # Campo trabajador que recibe
        self.cmb_recibio = QComboBox()
        self.cmb_recibio.addItem("")
        try:
            for trab in fetch_all_trabajadores():
                self.cmb_recibio.addItem(trab['nombre'])
        except Exception:
            pass
        layout.insertRow(4, "Recibió:", self.cmb_recibio)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Confirmar Restock")
        self.btn_cancel = QPushButton("Cancelar")

        self.btn_ok.setObjectName("ActionButton")
        self.btn_cancel.setObjectName("ActionButton")

        self.btn_ok.clicked.connect(self.guardar)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)

        layout.addRow(btn_layout)

    def actualizar_nueva_cantidad(self):
        """Actualiza la etiqueta de cantidad total"""
        cantidad_a_agregar = self.spin_cantidad.value()
        cantidad_total = self.producto.cantidad + cantidad_a_agregar
        self.lbl_nueva_cantidad.setText(str(cantidad_total))

    def guardar(self):
        """Guarda el restock"""
        cantidad_a_agregar = self.spin_cantidad.value()
        self.producto.cantidad += cantidad_a_agregar
        self.recibio = self.cmb_recibio.currentText().strip()
        self.accept()
