from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout,
    QComboBox, QSpinBox, QLineEdit,
    QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem
)
from datetime import datetime

from app.core.store import store, Salida
from app.core.bitacora import bitacora
class SalidasView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== FORMULARIO =====
        form = QFormLayout()

        # ----- DATOS DEL TRABAJADOR -----
        self.cmb_id_trabajador = QComboBox()
        self.txt_nombre_trabajador = QLineEdit()
        self.txt_nombre_trabajador.setReadOnly(True)
        self.txt_proyecto = QLineEdit()

        form.addRow("Trabajador:", self.cmb_id_trabajador)
        form.addRow("Nombre:", self.txt_nombre_trabajador)
        form.addRow("Proyecto:", self.txt_proyecto)

        # ----- DATOS DEL MATERIAL -----
        self.cmb_partida = QComboBox()
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setReadOnly(True)

        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 100000)

        self.txt_destino = QLineEdit()
        self.txt_entrego = QLineEdit()
        self.txt_obs = QLineEdit()

        form.addRow("Partida:", self.cmb_partida)
        form.addRow("Descripción:", self.txt_descripcion)
        form.addRow("Cantidad:", self.spin_cantidad)
        form.addRow("Destino:", self.txt_destino)
        form.addRow("Entregó:", self.txt_entrego)
        form.addRow("Observaciones:", self.txt_obs)

        layout.addLayout(form)

        # ===== BOTÓN =====
        btn_layout = QHBoxLayout()
        self.btn_salida = QPushButton("Registrar salida")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_salida)
        layout.addLayout(btn_layout)

        # ===== TABLA =====
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Trabajador", "Proyecto",
            "Partida", "Descripción", "Cantidad",
            "Destino", "Entregó"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.cmb_id_trabajador.currentTextChanged.connect(self.update_nombre_trabajador)
        self.cmb_partida.currentTextChanged.connect(self.update_descripcion)
        self.btn_salida.clicked.connect(self.registrar_salida)

        self.load_trabajadores()
        self.load_partidas()
        self.load_salidas()

    # ---------- CARGAS ----------
    def load_trabajadores(self):
        self.cmb_id_trabajador.clear()
        for id_trab, trabajador in store.trabajadores.items():
            self.cmb_id_trabajador.addItem(f"{id_trab} - {trabajador.nombre}", id_trab)

        if self.cmb_id_trabajador.count() > 0:
            self.update_nombre_trabajador(self.cmb_id_trabajador.currentText())

    def update_nombre_trabajador(self, texto):
        id_trabajador = self.cmb_id_trabajador.currentData()
        if id_trabajador and id_trabajador in store.trabajadores:
            trabajador = store.trabajadores[id_trabajador]
            self.txt_nombre_trabajador.setText(trabajador.nombre)
        else:
            self.txt_nombre_trabajador.clear()

    def load_partidas(self):
        self.cmb_partida.clear()
        almacen = store.get_almacen()
        for partida in almacen.keys():
            self.cmb_partida.addItem(partida)

        if self.cmb_partida.count() > 0:
            self.update_descripcion(self.cmb_partida.currentText())

    def update_descripcion(self, partida):
        almacen = store.get_almacen()
        item = almacen.get(partida)
        if not item:
            self.txt_descripcion.clear()
            self.btn_salida.setEnabled(False)
            return

        self.txt_descripcion.setText(item.descripcion)

        # bloquear si no hay stock
        self.btn_salida.setEnabled(item.cantidad > 0)

        # ajustar máximo permitido
        self.spin_cantidad.setMaximum(item.cantidad)

    def load_salidas(self):
        self.table.setRowCount(0)
        for s in store.salidas:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(s.fecha))
            self.table.setItem(row, 1, QTableWidgetItem(f"{s.trabajador_id} - {s.trabajador_nombre}"))
            self.table.setItem(row, 2, QTableWidgetItem(s.proyecto))
            self.table.setItem(row, 3, QTableWidgetItem(s.partida))
            self.table.setItem(row, 4, QTableWidgetItem(s.descripcion))
            self.table.setItem(row, 5, QTableWidgetItem(str(s.cantidad)))
            self.table.setItem(row, 6, QTableWidgetItem(s.destino))
            self.table.setItem(row, 7, QTableWidgetItem(s.entrego))

    # ---------- ACCIÓN ----------
    def registrar_salida(self):
        # ===== VALIDACIONES DE TRABAJADOR =====
        id_trabajador = self.cmb_id_trabajador.currentData()
        nombre_trabajador = self.txt_nombre_trabajador.text().strip()
        proyecto = self.txt_proyecto.text().strip()

        if not id_trabajador:
            QMessageBox.warning(self, "Error", "Seleccione un trabajador")
            return

        if not proyecto:
            QMessageBox.warning(self, "Error", "El nombre del proyecto es obligatorio")
            return

        # ===== VALIDACIONES DE MATERIAL =====
        partida = self.cmb_partida.currentText()
        if not partida:
            QMessageBox.warning(self, "Error", "Seleccione una partida")
            return

        if not self.txt_destino.text().strip():
            QMessageBox.warning(self, "Error", "El destino es obligatorio")
            return

        if not self.txt_entrego.text().strip():
            QMessageBox.warning(self, "Error", "El nombre de quien entrega es obligatorio")
            return

        almacen = store.get_almacen()
        disponible = almacen[partida].cantidad
        cantidad = self.spin_cantidad.value()

        if cantidad > disponible:
            QMessageBox.critical(
                self,
                "Stock insuficiente",
                f"Disponible: {disponible}"
            )
            return

        # ===== VALIDACIÓN: MÁXIMO 25 PRODUCTOS =====
        # Contar cuántos productos hay en salidas no completadas (de este pedido)
        # Por ahora se valida por salida individual
        if cantidad > 25:
            QMessageBox.critical(
                self,
                "Límite excedido",
                f"No se pueden sacar más de 25 unidades por producto en una salida"
            )
            return

        try:
            almacen = store.get_almacen()
            salida = Salida(
                fecha=datetime.now().strftime("%Y-%m-%d %H:%M"),
                partida=partida,
                descripcion=self.txt_descripcion.text(),
                cantidad=cantidad,
                unidad=almacen[partida].unidad,
                trabajador_id=id_trabajador,
                trabajador_nombre=nombre_trabajador,
                proyecto=proyecto,
                destino=self.txt_destino.text(),
                entrego=self.txt_entrego.text(),
                observaciones=self.txt_obs.text(),
            )

            store.add_salida(salida)
            self.load_salidas()
            self.update_descripcion(partida)

            QMessageBox.information(self, "Éxito", "Salida registrada correctamente")

            # Limpiar formulario
            self.spin_cantidad.setValue(1)
            self.txt_destino.clear()
            self.txt_entrego.clear()
            self.txt_obs.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
