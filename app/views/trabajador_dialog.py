from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

from app.core.store import store, Trabajador
from app.core.bitacora import bitacora
from app.core.event_manager import event_manager
from app.core.trabajador_db import insert_trabajador, update_trabajador


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

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        form_layout = QFormLayout()
        form_layout.setSpacing(14)

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

        form_layout.addRow("Nombre:", self.txt_nombre)
        form_layout.addRow("Identificación:", self.txt_identificacion)

        main_layout.addLayout(form_layout)

        # ----- BOTONES -----
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_guardar.setObjectName("PrimaryButton")
        self.btn_cancelar.setObjectName("DangerButton")
        self.btn_guardar.setMinimumHeight(38)
        self.btn_cancelar.setMinimumHeight(38)
        self.btn_guardar.setFixedWidth(110)
        self.btn_cancelar.setFixedWidth(110)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)

        main_layout.addLayout(btn_layout)

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
            # Verificar que la identificación no esté duplicada (a menos que sea la misma)
            for trab in store.trabajadores.values():
                if (trab.numero_identificacion == identificacion and 
                    trab.id != self.trabajador.id):
                    QMessageBox.warning(self, "Error", f"La identificación {identificacion} ya existe")
                    return
            
            self.trabajador.nombre = nombre
            self.trabajador.numero_identificacion = identificacion
            # Guardar en la base de datos
            update_trabajador(self.trabajador.id, nombre, identificacion)
            bitacora.log("Trabajador", f"Trabajador actualizado: {nombre}")
            QMessageBox.information(self, "OK", "Trabajador actualizado")
            # Notificar cambios en tiempo real
            event_manager.trabajador_changed.emit()
            store.notify()
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
                # Notificar cambios en tiempo real
                event_manager.trabajador_changed.emit()
                store.notify()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return

        self.accept()

