from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout,
    QComboBox, QSpinBox, QLineEdit,
    QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem
)
from datetime import date

from app.core.store import store, Salida


class SalidasView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== FORMULARIO =====
        form = QFormLayout()

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
        self.btn_salida = QPushButton(" Registrar salida")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_salida)
        layout.addLayout(btn_layout)

        # ===== TABLA =====
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Partida", "Descripción",
            "Cantidad", "Destino", "Entregó"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.cmb_partida.currentTextChanged.connect(self.update_descripcion)
        self.btn_salida.clicked.connect(self.registrar_salida)

        self.load_partidas()
        self.load_salidas()

    # ---------- CARGAS ----------
    def load_partidas(self):
        self.cmb_partida.clear()
        for partida in store.almacen.keys():
            self.cmb_partida.addItem(partida)

        if self.cmb_partida.count() > 0:
            self.update_descripcion(self.cmb_partida.currentText())

    def update_descripcion(self, partida):
        item = store.almacen.get(partida)
        if item:
            self.txt_descripcion.setText(item.descripcion)

    def load_salidas(self):
        self.table.setRowCount(0)
        for s in store.salidas:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(s.fecha))
            self.table.setItem(row, 1, QTableWidgetItem(s.partida))
            self.table.setItem(row, 2, QTableWidgetItem(s.descripcion))
            self.table.setItem(row, 3, QTableWidgetItem(str(s.cantidad)))
            self.table.setItem(row, 4, QTableWidgetItem(s.destino))
            self.table.setItem(row, 5, QTableWidgetItem(s.entrego))

    # ---------- ACCIÓN ----------
    def registrar_salida(self):
        partida = self.cmb_partida.currentText()
        if not partida:
            QMessageBox.warning(self, "Error", "Seleccione una partida")
            return

        try:
            salida = Salida(
                fecha=str(date.today()),
                partida=partida,
                descripcion=self.txt_descripcion.text(),
                cantidad=self.spin_cantidad.value(),
                unidad=store.almacen[partida].unidad,
                destino=self.txt_destino.text(),
                entrego=self.txt_entrego.text(),
                observaciones=self.txt_obs.text(),
            )

            store.add_salida(salida)
            self.load_salidas()

            QMessageBox.information(self, "Éxito", "Salida registrada correctamente")

            self.spin_cantidad.setValue(1)
            self.txt_obs.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
