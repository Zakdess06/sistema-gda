from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt

from app.core.store import store, Herramienta
from app.core.bitacora import bitacora


class HerramientaDialog(QDialog):
    def __init__(self, parent=None, herramienta=None):
        super().__init__(parent)

        # Herencia de QSS
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.herramienta = herramienta
        if herramienta:
            self.setWindowTitle("Editar Herramienta")
        else:
            self.setWindowTitle("Agregar Herramienta")

        self.setMinimumWidth(450)

        layout = QFormLayout(self)
        layout.setSpacing(16)

        # ----- CAMPOS PRINCIPALES -----
        self.txt_codigo = QLineEdit()
        self.txt_codigo.setReadOnly(True)
        self.txt_descripcion = QLineEdit()
        self.txt_ubicacion = QLineEdit()
        self.spin_cantidad = QSpinBox()
        self.txt_obs = QLineEdit()

        # Configurar spinbox
        self.spin_cantidad.setRange(0, 999)

        # Placeholders
        self.txt_codigo.setPlaceholderText("Código automático")
        self.txt_descripcion.setPlaceholderText("Descripción de la herramienta")
        self.txt_ubicacion.setPlaceholderText("Ej: Gaveta Herramientas")
        self.txt_obs.setPlaceholderText("Observaciones")

        # Cargar datos si es edición
        if herramienta:
            self.txt_codigo.setText(herramienta.codigo)
            self.txt_descripcion.setText(herramienta.descripcion)
            self.txt_ubicacion.setText(herramienta.ubicacion)
            self.spin_cantidad.setValue(herramienta.cantidad)
            self.txt_obs.setText(getattr(herramienta, 'observaciones', ''))
        else:
            # Auto-generar código para nueva herramienta
            codigo_auto = store.generar_codigo_herramienta()
            self.txt_codigo.setText(codigo_auto)

        layout.addRow("Código:", self.txt_codigo)
        layout.addRow("Descripción:", self.txt_descripcion)
        layout.addRow("Ubicación:", self.txt_ubicacion)
        layout.addRow("Cantidad:", self.spin_cantidad)
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
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.reject)

    def guardar(self):
        codigo = self.txt_codigo.text().strip()
        descripcion = self.txt_descripcion.text().strip()
        ubicacion = self.txt_ubicacion.text().strip()
        cantidad = self.spin_cantidad.value()
        obs = self.txt_obs.text().strip()

        if not codigo or not descripcion or not ubicacion:
            QMessageBox.warning(self, "Error", "Código, descripción y ubicación son obligatorios")
            return

        if self.herramienta:
            # Edición: actualizar herramienta existente
            self.herramienta.descripcion = descripcion
            self.herramienta.ubicacion = ubicacion
            self.herramienta.cantidad = cantidad
            self.herramienta.observaciones = obs

            store.update_herramienta(self.herramienta)
            bitacora.log("Herramienta", f"Herramienta actualizada: {codigo}")
            QMessageBox.information(self, "OK", "Herramienta actualizada")
        else:
            # Creación: nueva herramienta
            herramientas = store.get_herramientas()
            if codigo in herramientas:
                QMessageBox.warning(self, "Error", f"El código {codigo} ya existe")
                return

            try:
                h = Herramienta(
                    codigo=codigo,
                    descripcion=descripcion,
                    ubicacion=ubicacion,
                    cantidad=cantidad,
                    observaciones=obs
                )
                store.add_herramienta(h)
                bitacora.log("Herramienta", f"Nueva herramienta registrada: {codigo} - {descripcion}")
                QMessageBox.information(self, "OK", "Herramienta registrada")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return

        self.accept()

