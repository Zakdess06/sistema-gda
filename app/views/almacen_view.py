from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

from app.core.store import store
from app.views.producto_dialog import ProductoDialog


class AlmacenView(QWidget):
    def __init__(self):
        super().__init__()

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("Almacén")
        title.setObjectName("TitleLabel")
        main_layout.addWidget(title)

        # Barra superior: botones + buscador
        top_bar = QHBoxLayout()

        # Botones
        self.btn_new = QPushButton("+ Nuevo")
        self.btn_edit = QPushButton("Editar")
        self.btn_delete = QPushButton("Eliminar")

        for btn in [self.btn_new, self.btn_edit, self.btn_delete]:
            btn.setObjectName("ActionButton")
            btn.setCursor(Qt.PointingHandCursor)
            top_bar.addWidget(btn)

        top_bar.addStretch()

        # Buscador
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar producto...")
        self.search.setObjectName("ActionSearch")
        self.search.textChanged.connect(self.buscar)
        top_bar.addWidget(self.search)

        main_layout.addLayout(top_bar)

        # Tabla
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Partida", "Descripción", "Cantidad", "Ubicación", "Proveedor"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        main_layout.addWidget(self.table)

        # Conectar botones
        self.btn_new.clicked.connect(self.agregar)
        self.btn_edit.clicked.connect(self.editar)
        self.btn_delete.clicked.connect(self.eliminar)

        # Cargar datos iniciales desde store
        self.refresh()

    # =========================
    # Refrescar tabla desde store
    # =========================
    def refresh(self):
        items = list(store.almacen.values())
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            vals = [item.partida, item.descripcion, str(item.cantidad), item.ubicacion, item.proveedor]
            for col, value in enumerate(vals):
                cell = QTableWidgetItem(value)
                if col == 2:  # Centrar columna "Cantidad"
                    cell.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, cell)

    # =========================
    # Acciones
    # =========================
    def agregar(self):
        dlg = ProductoDialog(self, "Nuevo producto")
        if dlg.exec():
            d, c, u, p = dlg.get_data()
            if not d:
                QMessageBox.warning(self, "Error", "La descripción es obligatoria")
                return

            # Crear nueva partida automática
            partida = f"P-{len(store.almacen) + 1:03d}"

            # Guardar en store
            store.almacen[partida] = type('Item', (), {
                'partida': partida,
                'descripcion': d,
                'cantidad': c,
                'ubicacion': u,
                'proveedor': p
            })()

            self.refresh()

    def editar(self):
        r = self.table.currentRow()
        if r < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona un producto")
            return

        partida = self.table.item(r, 0).text()
        item = store.almacen.get(partida)

        dlg = ProductoDialog(self, "Editar producto")
        dlg.set_data(item.descripcion, item.cantidad, item.ubicacion, item.proveedor)

        if dlg.exec():
            d, c, u, p = dlg.get_data()
            item.descripcion = d
            item.cantidad = c
            item.ubicacion = u
            item.proveedor = p
            self.refresh()

    def eliminar(self):
        r = self.table.currentRow()
        if r >= 0:
            partida = self.table.item(r, 0).text()
            if partida in store.almacen:
                del store.almacen[partida]
            self.refresh()

    # =========================
    # Búsqueda en tabla
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
