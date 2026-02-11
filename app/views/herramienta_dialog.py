from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, 
    QHBoxLayout, QSpinBox, QMessageBox, QLabel
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
            self.setWindowTitle("Nueva Herramienta")

        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        # ===== LAYOUT PRINCIPAL =====
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ===== TÍTULO DESCRIPTIVO =====
        title_label = QLabel(
            "Editar información de la herramienta" 
            if herramienta else "Registrar nueva herramienta"
        )
        title_label.setStyleSheet("font-size: 13px; font-weight: 600; opacity: 0.9;")
        main_layout.addWidget(title_label)

        # ===== FORMULARIO =====
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # ----- CAMPOS PRINCIPALES -----
        self.txt_codigo = QLineEdit()
        self.txt_codigo.setReadOnly(True)
        self.txt_codigo.setStyleSheet("background-color: rgba(128, 128, 128, 0.1);")
        self.txt_descripcion = QLineEdit()
        self.txt_ubicacion = QLineEdit()
        self.spin_cantidad = QSpinBox()
        self.txt_obs = QLineEdit()

        # Configurar spinbox
        self.spin_cantidad.setRange(0, 999)
        self.spin_cantidad.setMinimumHeight(36)

        # Placeholders
        self.txt_codigo.setPlaceholderText("Código automático")
        self.txt_descripcion.setPlaceholderText("Ej: Destornillador de cabeza plana")
        self.txt_ubicacion.setPlaceholderText("Ej: Gaveta A - Estante 2")
        self.txt_obs.setPlaceholderText("Observaciones (opcional)")

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

        form_layout.addRow("Código:", self.txt_codigo)
        form_layout.addRow("Descripción:", self.txt_descripcion)
        form_layout.addRow("Ubicación:", self.txt_ubicacion)
        form_layout.addRow("Cantidad:", self.spin_cantidad)
        form_layout.addRow("Observaciones:", self.txt_obs)

        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        # ----- BOTONES =====
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
            QMessageBox.information(self, "Éxito", "Herramienta actualizada correctamente")
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
                QMessageBox.information(self, "Éxito", "Herramienta registrada correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return

        self.accept()

