from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem
)

from app.core.store import store, Herramienta


class HerramientasView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== FORM =====
        form = QFormLayout()

        self.txt_codigo = QLineEdit()
        self.txt_nombre = QLineEdit()
        self.txt_responsable = QLineEdit()
        self.txt_obs = QLineEdit()

        form.addRow("Código:", self.txt_codigo)
        form.addRow("Nombre herramienta:", self.txt_nombre)
        form.addRow("Responsable:", self.txt_responsable)
        form.addRow("Observaciones:", self.txt_obs)

        layout.addLayout(form)

        # ===== BOTONES =====
        btns = QHBoxLayout()

        self.btn_add = QPushButton("Agregar")
        self.btn_prestar = QPushButton("Prestar")
        self.btn_devolver = QPushButton("Devolver")

        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_prestar)
        btns.addWidget(self.btn_devolver)

        layout.addLayout(btns)

        # ===== TABLA =====
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            "Código", "Nombre", "Estado", "Responsable"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.btn_add.clicked.connect(self.agregar)
        self.btn_prestar.clicked.connect(self.prestar)
        self.btn_devolver.clicked.connect(self.devolver)

        self.load_data()

    # ---------- DATA ----------
    def load_data(self):
        self.table.setRowCount(0)
        for h in store.herramientas.values():
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(h.codigo))
            self.table.setItem(row, 1, QTableWidgetItem(h.nombre))
            self.table.setItem(row, 2, QTableWidgetItem(h.estado))
            self.table.setItem(row, 3, QTableWidgetItem(h.responsable))

    def selected_codigo(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).text()

    # ---------- ACCIONES ----------
    def agregar(self):
        try:
            h = Herramienta(
                codigo=self.txt_codigo.text(),
                nombre=self.txt_nombre.text(),
                observaciones=self.txt_obs.text()
            )
            store.add_herramienta(h)
            self.load_data()
            QMessageBox.information(self, "OK", "Herramienta registrada")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def prestar(self):
        codigo = self.selected_codigo()
        responsable = self.txt_responsable.text()

        if not codigo or not responsable:
            return

        try:
            store.prestar_herramienta(codigo, responsable)
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def devolver(self):
        codigo = self.selected_codigo()
        if not codigo:
            return

        try:
            store.devolver_herramienta(codigo)
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
