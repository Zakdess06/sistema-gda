from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt

from app.core.store import store


class AlmacenView(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Almacén")
        title.setObjectName("TitleLabel")
        main_layout.addWidget(title)

        top_bar = QHBoxLayout()
        top_bar.addStretch()

        btn_new = QPushButton("+ Nueva pieza")
        btn_edit = QPushButton("Editar")
        btn_delete = QPushButton("Eliminar")
        btn_search = QPushButton("Buscar")

        for btn in [btn_new, btn_edit, btn_delete, btn_search]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setObjectName("ActionButton")
            btn.setMinimumHeight(44)
            top_bar.addWidget(btn)

        main_layout.addLayout(top_bar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Partida", "Descripción", "Cantidad", "Ubicación", "Proveedor"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setFixedHeight(48)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        main_layout.addWidget(self.table)

        self.refresh()

    def refresh(self):
        items = list(store.almacen.values())
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            vals = [item.partida, item.descripcion, str(item.cantidad), item.ubicacion, item.proveedor]
            for col, value in enumerate(vals):
                cell = QTableWidgetItem(value)
                if col == 2:
                    cell.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, cell)
