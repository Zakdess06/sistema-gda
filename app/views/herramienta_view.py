from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QMessageBox, QSpinBox,
    QTableWidget, QTableWidgetItem
)

from app.core.store import store, Herramienta
from app.core.bitacora import bitacora


class HerramientasView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== FORM =====
        form = QFormLayout()

        self.txt_codigo = QLineEdit()
        self.txt_descripcion = QLineEdit()
        self.txt_ubicacion = QLineEdit()
        self.spin_cantidad = QSpinBox()
        self.txt_obs = QLineEdit()

        self.txt_codigo.setPlaceholderText("Ej: H-001")
        self.txt_descripcion.setPlaceholderText("Descripción de la herramienta")
        self.txt_ubicacion.setPlaceholderText("Ej: Gaveta Herramientas")
        self.spin_cantidad.setRange(0, 999)
        self.txt_obs.setPlaceholderText("Observaciones")

        form.addRow("Código:", self.txt_codigo)
        form.addRow("Descripción:", self.txt_descripcion)
        form.addRow("Ubicación:", self.txt_ubicacion)
        form.addRow("Cantidad:", self.spin_cantidad)
        form.addRow("Observaciones:", self.txt_obs)

        layout.addLayout(form)

        # ===== BOTONES =====
        btns = QHBoxLayout()

        self.btn_add = QPushButton("Agregar Herramienta")
        self.btn_edit = QPushButton("Editar Seleccionado")
        self.btn_delete = QPushButton("Eliminar Seleccionado")

        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_delete)
        btns.addStretch()

        layout.addLayout(btns)

        # ===== TABLA =====
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Código", "Descripción", "Ubicación", "Cantidad", "Observaciones"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.btn_add.clicked.connect(self.agregar)
        self.btn_edit.clicked.connect(self.editar)
        self.btn_delete.clicked.connect(self.eliminar)

        store.subscribe(self.load_data)
        self.load_data()

    # ---------- DATA ----------
    def load_data(self):
        self.table.setRowCount(0)
        herramientas = store.get_herramientas()
        for h in herramientas.values():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(h.codigo))
            self.table.setItem(row, 1, QTableWidgetItem(h.descripcion))
            self.table.setItem(row, 2, QTableWidgetItem(h.ubicacion))
            self.table.setItem(row, 3, QTableWidgetItem(str(h.cantidad)))
            self.table.setItem(row, 4, QTableWidgetItem(getattr(h, 'observaciones', '')))

    def selected_codigo(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).text()

    # ---------- ACCIONES ----------
    def agregar(self):
        codigo = self.txt_codigo.text().strip()
        descripcion = self.txt_descripcion.text().strip()
        ubicacion = self.txt_ubicacion.text().strip()
        cantidad = self.spin_cantidad.value()

        if not codigo or not descripcion or not ubicacion:
            QMessageBox.warning(self, "Error", "Complete todos los campos obligatorios")
            return

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
                observaciones=self.txt_obs.text().strip()
            )
            store.add_herramienta(h)
            self.clear_form()
            bitacora.log("Herramienta", f"Nueva herramienta registrada: {codigo} - {descripcion}")
            QMessageBox.information(self, "OK", "Herramienta registrada")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def editar(self):
        codigo = self.selected_codigo()
        if not codigo:
            QMessageBox.warning(self, "Error", "Seleccione una herramienta")
            return
        herramientas = store.get_herramientas()
        herramienta = herramientas.get(codigo)
        if not herramienta:
            QMessageBox.warning(self, "Error", "Herramienta no encontrada")
            return
        # Cargar datos en formulario
        self.txt_codigo.setText(herramienta.codigo)
        self.txt_codigo.setReadOnly(True)
        self.txt_descripcion.setText(herramienta.descripcion)
        self.txt_ubicacion.setText(herramienta.ubicacion)
        self.spin_cantidad.setValue(herramienta.cantidad)
        self.txt_obs.setText(getattr(herramienta, 'observaciones', ''))

    def eliminar(self):
        codigo = self.selected_codigo()
        if not codigo:
            QMessageBox.warning(self, "Error", "Seleccione una herramienta")
            return
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar la herramienta {codigo}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            store.delete_herramienta(codigo)
            bitacora.log("Herramienta", f"Herramienta eliminada: {codigo}")
            self.clear_form()

    def clear_form(self):
        self.txt_codigo.setText("")
        self.txt_codigo.setReadOnly(False)
        self.txt_descripcion.setText("")
        self.txt_ubicacion.setText("")
        self.spin_cantidad.setValue(0)
        self.txt_obs.setText("")

