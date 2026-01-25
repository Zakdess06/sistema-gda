from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QMessageBox,
    QDialog, QFormLayout, QSpinBox
)
from PySide6.QtCore import Qt


# =========================
# Diálogo de producto
# =========================
class ProductoDialog(QDialog):
    def __init__(self, parent=None, titulo="Producto"):
        super().__init__(parent)

        # Forzar herencia de QSS
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setWindowTitle(titulo)
        self.setMinimumWidth(420)

        layout = QFormLayout(self)
        layout.setSpacing(16)

        self.descripcion = QLineEdit()
        self.cantidad = QSpinBox()
        self.ubicacion = QLineEdit()
        self.proveedor = QLineEdit()

        self.descripcion.setPlaceholderText("Descripción")
        self.ubicacion.setPlaceholderText("Ubicación")
        self.proveedor.setPlaceholderText("Proveedor")

        self.cantidad.setRange(0, 999999)

        layout.addRow("Descripción:", self.descripcion)
        layout.addRow("Cantidad:", self.cantidad)
        layout.addRow("Ubicación:", self.ubicacion)
        layout.addRow("Proveedor:", self.proveedor)

        # Botones personalizados (evita romper QSS)
        btn_layout = QHBoxLayout()

        self.btn_ok = QPushButton("Guardar")
        self.btn_cancel = QPushButton("Cancelar")

        self.btn_ok.setObjectName("ActionButton")
        self.btn_cancel.setObjectName("ActionButton")

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)

        layout.addRow(btn_layout)

    def get_data(self):
        return (
            self.descripcion.text().strip(),
            self.cantidad.value(),
            self.ubicacion.text().strip(),
            self.proveedor.text().strip()
        )

    def set_data(self, d, c, u, p):
        self.descripcion.setText(d)
        self.cantidad.setValue(int(c))
        self.ubicacion.setText(u)
        self.proveedor.setText(p)


# =========================
# Vista de Almacén
# =========================
class AlmacenView(QWidget):
    def __init__(self):
        super().__init__()

        main = QVBoxLayout(self)
        main.setSpacing(16)

        # Título
        title = QLabel("Almacén")
        title.setObjectName("TitleLabel")
        main.addWidget(title)

        # Barra superior
        top = QHBoxLayout()

        # Buscador con estilo
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar producto...")
        self.search.textChanged.connect(self.buscar)

        self.search.setStyleSheet("""
        QLineEdit {
            background-color: #2a2a2a;
            color: white;
            border: 2px solid #3a3a3a;
            border-radius: 10px;
            padding: 10px 14px;
            font-size: 24px;
        }

        QLineEdit:focus {
            border: 2px solid #0094C2;
        }

        QLineEdit::placeholder {
            color: #9a9a9a;
        }
        """)

        top.addWidget(self.search)
        top.addStretch()

        # Botones de acción (juntos)
        self.btn_new = QPushButton("+ Nuevo")
        self.btn_edit = QPushButton("Editar")
        self.btn_delete = QPushButton("Eliminar")

        for b in (self.btn_new, self.btn_edit, self.btn_delete):
            b.setObjectName("ActionButton")
            b.setCursor(Qt.PointingHandCursor)
            top.addWidget(b)

        main.addLayout(top)

        # Tabla
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Partida", "Descripción", "Cantidad", "Ubicación", "Proveedor"]
        )

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setDefaultSectionSize(48)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        main.addWidget(self.table)

        # Conexiones
        self.btn_new.clicked.connect(self.agregar)
        self.btn_edit.clicked.connect(self.editar)
        self.btn_delete.clicked.connect(self.eliminar)

    # =========================
    # Lógica
    # =========================
    def agregar(self):
        dlg = ProductoDialog(self, "Nuevo producto")
        if dlg.exec():
            d, c, u, p = dlg.get_data()
            if not d:
                QMessageBox.warning(self, "Error", "La descripción es obligatoria")
                return

            partida = f"P-{self.table.rowCount() + 1:03d}"
            self.insert_row((partida, d, str(c), u, p))

    def editar(self):
        r = self.table.currentRow()
        if r < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona un producto")
            return

        dlg = ProductoDialog(self, "Editar producto")
        dlg.set_data(
            self.table.item(r, 1).text(),
            self.table.item(r, 2).text(),
            self.table.item(r, 3).text(),
            self.table.item(r, 4).text()
        )

        if dlg.exec():
            d, c, u, p = dlg.get_data()
            self.table.item(r, 1).setText(d)
            self.table.item(r, 2).setText(str(c))
            self.table.item(r, 3).setText(u)
            self.table.item(r, 4).setText(p)

    def eliminar(self):
        r = self.table.currentRow()
        if r >= 0:
            self.table.removeRow(r)

    def buscar(self, texto):
        texto = texto.lower()
        for r in range(self.table.rowCount()):
            visible = False
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item and texto in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(r, not visible)

    def insert_row(self, data):
        r = self.table.rowCount()
        self.table.insertRow(r)
        for c, v in enumerate(data):
            self.table.setItem(r, c, QTableWidgetItem(v))
