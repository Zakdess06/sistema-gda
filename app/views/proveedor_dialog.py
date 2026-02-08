from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

from app.core.store import store, Proveedor
from app.core.bitacora import bitacora


class ProveedorDialog(QDialog):
    def __init__(self, parent=None, proveedor=None):
        super().__init__(parent)

        # Herencia de QSS
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.proveedor = proveedor
        if proveedor:
            self.setWindowTitle("Editar Proveedor")
        else:
            self.setWindowTitle("Agregar Proveedor")

        self.setMinimumWidth(500)

        layout = QFormLayout(self)
        layout.setSpacing(16)

        # ----- CAMPOS PRINCIPALES -----
        self.txt_nombre_comercial = QLineEdit()
        self.txt_nombre_fiscal = QLineEdit()
        self.txt_ubicacion = QLineEdit()
        self.txt_telefono = QLineEdit()

        # Placeholders
        self.txt_nombre_comercial.setPlaceholderText("Nombre comercial")
        self.txt_nombre_fiscal.setPlaceholderText("Nombre fiscal / RUC")
        self.txt_ubicacion.setPlaceholderText("Dirección")
        self.txt_telefono.setPlaceholderText("Teléfono de contacto")

        # Cargar datos si es edición
        if proveedor:
            self.txt_nombre_comercial.setText(proveedor.nombre_comercial)
            self.txt_nombre_fiscal.setText(proveedor.nombre_fiscal)
            self.txt_ubicacion.setText(proveedor.ubicacion)
            self.txt_telefono.setText(proveedor.telefono)

        layout.addRow("Nombre Comercial:", self.txt_nombre_comercial)
        layout.addRow("Nombre Fiscal:", self.txt_nombre_fiscal)
        layout.addRow("Ubicación:", self.txt_ubicacion)
        layout.addRow("Teléfono:", self.txt_telefono)

        # ----- BOTONES -----
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)

        layout.addRow(btn_layout)

        # ----- CONEXIONES -----
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.reject)

    def guardar(self):
        nombre_comercial = self.txt_nombre_comercial.text().strip()
        nombre_fiscal = self.txt_nombre_fiscal.text().strip()
        ubicacion = self.txt_ubicacion.text().strip()
        telefono = self.txt_telefono.text().strip()

        if not nombre_comercial or not nombre_fiscal:
            QMessageBox.warning(self, "Error", "Nombre comercial y nombre fiscal son obligatorios")
            return

        if self.proveedor:
            # Edición: actualizar proveedor existente
            self.proveedor.nombre_comercial = nombre_comercial
            self.proveedor.nombre_fiscal = nombre_fiscal
            self.proveedor.ubicacion = ubicacion
            self.proveedor.telefono = telefono
            bitacora.log("Proveedor", f"Proveedor actualizado: {nombre_comercial}")
            QMessageBox.information(self, "OK", "Proveedor actualizado")
        else:
            # Creación: nuevo proveedor
            try:
                # Generar un ID único
                max_id = 0
                for prov_id in store.proveedores.keys():
                    if prov_id.startswith('PR'):
                        try:
                            num = int(prov_id[2:])
                            max_id = max(max_id, num)
                        except (ValueError, IndexError):
                            pass
                
                nuevo_id = f"PR{max_id + 1:03d}"
                
                p = Proveedor(
                    id=nuevo_id,
                    nombre_comercial=nombre_comercial,
                    nombre_fiscal=nombre_fiscal,
                    ubicacion=ubicacion,
                    telefono=telefono
                )
                store.proveedores[nuevo_id] = p
                bitacora.log("Proveedor", f"Nuevo proveedor registrado: {nombre_comercial}")
                store.notify()
                QMessageBox.information(self, "OK", "Proveedor registrado")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return

        self.accept()
