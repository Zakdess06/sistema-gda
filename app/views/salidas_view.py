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

        # ===== FORMULARIO SIMPLIFICADO =====
        form = QFormLayout()

        # Trabajador
        self.cmb_id_trabajador = QComboBox()
        form.addRow("Trabajador:", self.cmb_id_trabajador)

        # Producto (solo productos existentes con stock)
        self.cmb_partida = QComboBox()
        self.cmb_partida.setEditable(False)
        form.addRow("Producto:", self.cmb_partida)

        # Ubicación (se llena automáticamente)
        self.txt_ubicacion = QLineEdit()
        self.txt_ubicacion.setReadOnly(True)
        form.addRow("Ubicación:", self.txt_ubicacion)

        # Cantidad
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 100000)
        form.addRow("Cantidad:", self.spin_cantidad)

        # Proyecto
        self.txt_proyecto = QLineEdit()
        form.addRow("Proyecto:", self.txt_proyecto)

        # Destino
        self.txt_destino = QLineEdit()
        form.addRow("Destino:", self.txt_destino)

        # Observaciones (opcional)
        self.txt_obs = QLineEdit()
        form.addRow("Observaciones:", self.txt_obs)

        layout.addLayout(form)

        # ===== BOTÓN =====
        btn_layout = QHBoxLayout()
        self.btn_salida = QPushButton("Registrar salida")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_salida)
        layout.addLayout(btn_layout)

        # ===== TABLA =====
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Trabajador", "Producto",
            "Cantidad", "Proyecto", "Destino"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.cmb_id_trabajador.currentTextChanged.connect(self.load_partidas)
        self.cmb_partida.currentTextChanged.connect(self.update_cantidad_maxima)
        self.btn_salida.clicked.connect(self.registrar_salida)

        self.load_trabajadores()
        self.load_partidas()
        self.load_salidas()

    # ---------- CARGAS ----------
    def load_trabajadores(self):
        self.cmb_id_trabajador.clear()
        for id_trab, trabajador in store.trabajadores.items():
            self.cmb_id_trabajador.addItem(f"{id_trab} - {trabajador.nombre}", id_trab)

    def load_partidas(self):
        """Carga solo productos con stock disponible"""
        self.cmb_partida.clear()
        almacen = store.get_almacen()
        
        # Solo mostrar productos con stock
        for partida, item in almacen.items():
            if item.cantidad > 0:
                self.cmb_partida.addItem(f"{partida} - {item.descripcion}", partida)

        if self.cmb_partida.count() > 0:
            self.update_cantidad_maxima()
        else:
            self.btn_salida.setEnabled(False)

    def update_cantidad_maxima(self):
        """Actualiza el máximo permitido según el stock disponible y llena la ubicación"""
        codigo = self.cmb_partida.currentData()
        if not codigo:
            self.btn_salida.setEnabled(False)
            self.txt_ubicacion.clear()
            return

        almacen = store.get_almacen()
        item = almacen.get(codigo)
        if item and item.cantidad > 0:
            self.spin_cantidad.setMaximum(item.cantidad)
            self.spin_cantidad.setValue(1)
            self.txt_ubicacion.setText(item.ubicacion)
            self.btn_salida.setEnabled(True)
        else:
            self.btn_salida.setEnabled(False)
            self.txt_ubicacion.clear()


    def load_salidas(self):
        """Carga las salidas desde la BD"""
        self.table.setRowCount(0)
        
        # Recargar desde BD para obtener los datos más recientes
        from app.core.salidas_db import fetch_all_salidas
        salidas = fetch_all_salidas()
        
        for s in salidas:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(s.fecha))
            self.table.setItem(row, 1, QTableWidgetItem(f"{s.trabajador_id} - {s.trabajador_nombre}"))
            self.table.setItem(row, 2, QTableWidgetItem(s.partida))
            self.table.setItem(row, 3, QTableWidgetItem(str(s.cantidad)))
            self.table.setItem(row, 4, QTableWidgetItem(s.proyecto))
            self.table.setItem(row, 5, QTableWidgetItem(s.destino))

    # ---------- ACCIÓN ----------
    def registrar_salida(self):
        # Validar trabajador
        id_trabajador = self.cmb_id_trabajador.currentData()
        if not id_trabajador:
            QMessageBox.warning(self, "Error", "Seleccione un trabajador")
            return

        # Obtener nombre del trabajador
        trabajador = store.trabajadores.get(id_trabajador)
        if not trabajador:
            QMessageBox.warning(self, "Error", "Trabajador no encontrado")
            return

        # Validar producto
        codigo_partida = self.cmb_partida.currentData()
        if not codigo_partida:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        # Validar cantidad
        cantidad = self.spin_cantidad.value()
        if cantidad <= 0:
            QMessageBox.warning(self, "Error", "La cantidad debe ser mayor a 0")
            return

        # Validar proyecto
        proyecto = self.txt_proyecto.text().strip()
        if not proyecto:
            QMessageBox.warning(self, "Error", "El proyecto es obligatorio")
            return

        # Validar destino
        destino = self.txt_destino.text().strip()
        if not destino:
            QMessageBox.warning(self, "Error", "El destino es obligatorio")
            return

        try:
            almacen = store.get_almacen()
            item = almacen.get(codigo_partida)
            if not item:
                QMessageBox.warning(self, "Error", "Producto no encontrado")
                return

            # Validar disponibilidad
            if cantidad > item.cantidad:
                QMessageBox.critical(
                    self,
                    "Stock insuficiente",
                    f"Disponible: {item.cantidad} unidades"
                )
                return

            salida = Salida(
                fecha=datetime.now().strftime("%Y-%m-%d %H:%M"),
                partida=codigo_partida,
                descripcion=item.descripcion,
                cantidad=cantidad,
                unidad=item.unidad,
                trabajador_id=id_trabajador,
                trabajador_nombre=trabajador.nombre,
                proyecto=proyecto,
                destino=destino,
                entrego="",
                observaciones=self.txt_obs.text().strip(),
            )

            store.add_salida(salida)
            self.load_salidas()

            QMessageBox.information(self, "Éxito", "Salida registrada correctamente")

            # Limpiar formulario
            self.spin_cantidad.setValue(1)
            self.txt_destino.clear()
            self.txt_proyecto.clear()
            self.txt_obs.clear()
            self.txt_ubicacion.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
