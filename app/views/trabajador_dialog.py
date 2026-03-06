from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

from app.core.store import store, Trabajador
from app.core.bitacora import bitacora
from app.core.trabajador_db import insert_trabajador


class TrabajadorDialog(QDialog):
    def __init__(self, parent=None, trabajador=None):
        super().__init__(parent)

        # Herencia de QSS
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.trabajador = trabajador
        if trabajador:
            self.setWindowTitle("Editar Trabajador")
        else:
            self.setWindowTitle("Agregar Trabajador")

        self.setMinimumWidth(450)

        layout = QFormLayout(self)
        layout.setSpacing(16)

        # ----- CAMPOS PRINCIPALES -----
        self.txt_nombre = QLineEdit()
        self.txt_identificacion = QLineEdit()

        # Placeholders
        self.txt_nombre.setPlaceholderText("Nombre completo")
        self.txt_identificacion.setPlaceholderText("Cédula o ID")

        # Cargar datos si es edición
        if trabajador:
            self.txt_nombre.setText(trabajador.nombre)
            self.txt_identificacion.setText(trabajador.numero_identificacion)
            self.txt_identificacion.setReadOnly(True)  # No permitir cambiar identificación

        layout.addRow("Nombre:", self.txt_nombre)
        layout.addRow("Identificación:", self.txt_identificacion)

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
        nombre = self.txt_nombre.text().strip()
        identificacion = self.txt_identificacion.text().strip()

        if not nombre or not identificacion:
            QMessageBox.warning(self, "Error", "Nombre e identificación son obligatorios")
            return

        if self.trabajador:
            # Edición: actualizar trabajador existente
            self.trabajador.nombre = nombre
            # No se actualiza identificación en edición
            bitacora.log("Trabajador", f"Trabajador actualizado: {nombre}")
            QMessageBox.information(self, "OK", "Trabajador actualizado")
        else:
            # Creación: nuevo trabajador
            # Verificar que no exista la identificación
            for trab in store.trabajadores.values():
                if trab.numero_identificacion == identificacion:
                    QMessageBox.warning(self, "Error", f"La identificación {identificacion} ya existe")
                    return

            try:
                # Generar un ID único
                max_id = 0
                for trab_id in store.trabajadores.keys():
                    if trab_id.startswith('T'):
                        try:
                            num = int(trab_id[1:])
                            max_id = max(max_id, num)
                        except (ValueError, IndexError):
                            pass
                nuevo_id = f"T{max_id + 1:03d}"
                t = Trabajador(
                    id=nuevo_id,
                    nombre=nombre,
                    numero_identificacion=identificacion
                )
                store.trabajadores[nuevo_id] = t
                # Guardar en la base de datos
                insert_trabajador(nombre, identificacion)
                bitacora.log("Trabajador", f"Trabajador registrado: {nombre}")
                QMessageBox.information(self, "OK", "Trabajador registrado")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return

        self.accept()

