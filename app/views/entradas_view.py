from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QSpinBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate


class EntradaDialog(QDialog):
    """Dialog para NUEVA / EDITAR entrada."""
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setModal(True)
        self.setMinimumWidth(520)

        self.setWindowTitle("Nueva entrada" if data is None else "Editar entrada")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDate(QDate.currentDate())

        self.partida = QLineEdit()
        self.descripcion = QLineEdit()

        self.cantidad = QSpinBox()
        self.cantidad.setRange(1, 1_000_000)

        self.unidad = QLineEdit()
        self.proveedor = QLineEdit()
        self.recibio = QLineEdit()
        self.ubicacion = QLineEdit()
        self.observaciones = QLineEdit()

        form.addRow("Fecha:", self.fecha)
        form.addRow("Partida:", self.partida)
        form.addRow("Descripción:", self.descripcion)
        form.addRow("Cantidad:", self.cantidad)
        form.addRow("Unidad:", self.unidad)
        form.addRow("Proveedor:", self.proveedor)
        form.addRow("Recibió:", self.recibio)
        form.addRow("Ubicación:", self.ubicacion)
        form.addRow("Observaciones:", self.observaciones)

        layout.addLayout(form)

        # Botones
        btns = QHBoxLayout()
        btns.addStretch()

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_save = QPushButton("Guardar")
        self.btn_cancel.setObjectName("ActionButton")
        self.btn_save.setObjectName("ActionButton")

        btns.addWidget(self.btn_cancel)
        btns.addWidget(self.btn_save)
        layout.addLayout(btns)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self.accept)

        # Si viene data, prellenar (editar)
        if data is not None:
            y, m, d = map(int, data["fecha"].split("-"))
            self.fecha.setDate(QDate(y, m, d))

            self.partida.setText(data["partida"])
            self.descripcion.setText(data["descripcion"])
            self.cantidad.setValue(int(data["cantidad"]))
            self.unidad.setText(data["unidad"])
            self.proveedor.setText(data["proveedor"])
            self.recibio.setText(data["recibio"])
            self.ubicacion.setText(data["ubicacion"])
            self.observaciones.setText(data.get("observaciones", ""))

    def get_data(self):
        return {
            "fecha": self.fecha.date().toString("yyyy-MM-dd"),
            "partida": self.partida.text().strip(),
            "descripcion": self.descripcion.text().strip(),
            "cantidad": int(self.cantidad.value()),
            "unidad": self.unidad.text().strip(),
            "proveedor": self.proveedor.text().strip(),
            "recibio": self.recibio.text().strip(),
            "ubicacion": self.ubicacion.text().strip(),
            "observaciones": self.observaciones.text().strip(),
        }


class EntradasView(QWidget):
    def __init__(self):
        super().__init__()

        self.entradas = []            # lista completa (fuente)
        self.filtered_indexes = []    # mapea filas visibles -> índice real en self.entradas

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Entradas")
        title.setObjectName("TitleLabel")
        main_layout.addWidget(title)

        # Barra superior (derecha)
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar (partida, descripción, proveedor...)")
        self.search_input.setMinimumWidth(320)
        self.search_input.textChanged.connect(self.apply_filter)
        top_bar.addWidget(self.search_input)

        self.btn_new = QPushButton("+ Nueva entrada")
        self.btn_edit = QPushButton("Editar")
        self.btn_delete = QPushButton("Eliminar")

        for btn in [self.btn_new, self.btn_edit, self.btn_delete]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setObjectName("ActionButton")
            btn.setMinimumHeight(44)
            top_bar.addWidget(btn)

        main_layout.addLayout(top_bar)

        # Tabla
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Partida", "Descripción", "Cantidad",
            "Unidad", "Proveedor", "Recibió", "Ubicación"
        ])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setFixedHeight(48)
        self.table.verticalHeader().setDefaultSectionSize(44)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        main_layout.addWidget(self.table)

        # Conexiones
        self.btn_new.clicked.connect(self.nueva_entrada)
        self.btn_edit.clicked.connect(self.editar_entrada)
        self.btn_delete.clicked.connect(self.eliminar_entrada)

        # Datos demo (taller eléctrico)
        self.seed_demo()
        self.apply_filter()

    def focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()

    def seed_demo(self):
        self.entradas = [
            {
                "fecha": "2026-01-24",
                "partida": "E-004",
                "descripcion": "Fusible 30A",
                "cantidad": 50,
                "unidad": "Pza",
                "proveedor": "Truper",
                "recibio": "Juan Pérez",
                "ubicacion": "Caja Fusibles",
                "observaciones": ""
            },
            {
                "fecha": "2026-01-24",
                "partida": "E-003",
                "descripcion": "Relay 12V",
                "cantidad": 10,
                "unidad": "Pza",
                "proveedor": "Hella",
                "recibio": "Luis Gómez",
                "ubicacion": "Gaveta 3",
                "observaciones": "Entrega parcial"
            },
        ]

    def apply_filter(self):
        """Filtra por texto y refresca tabla."""
        q = self.search_input.text().strip().lower()

        self.filtered_indexes = []
        for i, e in enumerate(self.entradas):
            haystack = " ".join([
                e["fecha"],
                e["partida"],
                e["descripcion"],
                str(e["cantidad"]),
                e["unidad"],
                e["proveedor"],
                e["recibio"],
                e["ubicacion"],
                e.get("observaciones", "")
            ]).lower()

            if q == "" or q in haystack:
                self.filtered_indexes.append(i)

        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.filtered_indexes))

        for row, real_idx in enumerate(self.filtered_indexes):
            e = self.entradas[real_idx]
            vals = [
                e["fecha"], e["partida"], e["descripcion"], str(e["cantidad"]),
                e["unidad"], e["proveedor"], e["recibio"], e["ubicacion"]
            ]

            for col, value in enumerate(vals):
                item = QTableWidgetItem(value)
                if col == 3:  # cantidad
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def get_selected_real_index(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.filtered_indexes[row] if row < len(self.filtered_indexes) else None

    def validate_entry(self, e):
        if not e["partida"]:
            return "Partida es obligatoria."
        if not e["descripcion"]:
            return "Descripción es obligatoria."
        if not e["unidad"]:
            return "Unidad es obligatoria."
        if not e["proveedor"]:
            return "Proveedor es obligatorio."
        if not e["recibio"]:
            return "Recibió es obligatorio."
        if not e["ubicacion"]:
            return "Ubicación es obligatoria."
        if int(e["cantidad"]) <= 0:
            return "Cantidad debe ser mayor a 0."
        return None

    def nueva_entrada(self):
        dlg = EntradaDialog(self)
        if dlg.exec() == QDialog.Accepted:
            e = dlg.get_data()
            err = self.validate_entry(e)
            if err:
                QMessageBox.warning(self, "Faltan datos", err)
                return

            self.entradas.append(e)
            self.apply_filter()

    def editar_entrada(self):
        real_idx = self.get_selected_real_index()
        if real_idx is None:
            QMessageBox.information(self, "Editar", "Selecciona una fila para editar.")
            return

        dlg = EntradaDialog(self, data=self.entradas[real_idx])
        if dlg.exec() == QDialog.Accepted:
            e = dlg.get_data()
            err = self.validate_entry(e)
            if err:
                QMessageBox.warning(self, "Faltan datos", err)
                return

            self.entradas[real_idx] = e
            self.apply_filter()

    def eliminar_entrada(self):
        real_idx = self.get_selected_real_index()
        if real_idx is None:
            QMessageBox.information(self, "Eliminar", "Selecciona una fila para eliminar.")
            return

        e = self.entradas[real_idx]
        resp = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar la entrada de {e['partida']} ({e['descripcion']})?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self.entradas.pop(real_idx)
            self.apply_filter()
