from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

from app.core.store import store
from app.views.herramienta_dialog import HerramientaDialog


class HerramientaView(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("Herramientas")
        title.setObjectName("TitleLabel")
        main_layout.addWidget(title)

        # Barra superior
        top_bar = QHBoxLayout()

        self.btn_new = QPushButton("+ Nuevo")
        self.btn_edit = QPushButton("Editar")
        self.btn_delete = QPushButton("Eliminar")

        for btn in (self.btn_new, self.btn_edit, self.btn_delete):
            btn.setObjectName("ActionButton")
            btn.setCursor(Qt.PointingHandCursor)
            top_bar.addWidget(btn)

        top_bar.addStretch()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar herramienta...")
        self.search.setObjectName("ActionSearch")
        self.search.textChanged.connect(self.buscar)
        top_bar.addWidget(self.search)

        main_layout.addLayout(top_bar)

        # Tabla
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Partida", "Descripción", "Ubicación", "Cantidad"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        main_layout.addWidget(self.table)

        # Conexiones
        self.btn_new.clicked.connect(self.agregar)
        self.btn_edit.clicked.connect(self.editar)
        self.btn_delete.clicked.connect(self.eliminar)

        self.refresh()

    # =========================
    # Refrescar tabla
    # =========================
    def refresh(self):
        items = list(store.herramientas.values())
        self.table.setRowCount(len(items))

        for row, h in enumerate(items):
            valores = [
                h.partida,
                h.descripcion,
                h.ubicacion,
                str(h.cantidad)
            ]

            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                if col == 3:
                    cell.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, cell)

    # =========================
    # Acciones
    # =========================
    def agregar(self):
        dlg = HerramientaDialog(self, "Nueva herramienta")
        if dlg.exec():
            d, u, c = dlg.get_data()

            if not d:
                QMessageBox.warning(self, "Error", "La descripción es obligatoria")
                return

            partida = f"H-{len(store.herramientas) + 1:03d}"

            store.herramientas[partida] = type("Herramienta", (), {
                "partida": partida,
                "descripcion": d,
                "ubicacion": u,
                "cantidad": c
            })()

            self.refresh()

    def editar(self):
        r = self.table.currentRow()
        if r < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona una herramienta")
            return

        partida = self.table.item(r, 0).text()
        h = store.herramientas.get(partida)

        dlg = HerramientaDialog(self, "Editar herramienta")
        dlg.set_data(h.descripcion, h.ubicacion, h.cantidad)

        if dlg.exec():
            d, u, c = dlg.get_data()
            h.descripcion = d
            h.ubicacion = u
            h.cantidad = c
            self.refresh()

    def eliminar(self):
        r = self.table.currentRow()
        if r < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona una herramienta")
            return

        partida = self.table.item(r, 0).text()
        if partida in store.herramientas:
            del store.herramientas[partida]
            self.refresh()

    # =========================
    # Búsqueda
    # =========================
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
