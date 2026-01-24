from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt


class AlmacenView(QWidget):
    def __init__(self):
        super().__init__()

        # 🔹 Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 🔹 Título
        title = QLabel("Almacén")
        title.setObjectName("TitleLabel")
        main_layout.addWidget(title)

        # 🔹 Barra superior (botones a la derecha)
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        btn_new = QPushButton("+ Nuevo")
        btn_edit = QPushButton("Editar")
        btn_delete = QPushButton("Eliminar")
        btn_search = QPushButton("Buscar")

        for btn in [btn_new, btn_edit, btn_delete, btn_search]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setObjectName("ActionButton")
            btn.setMinimumHeight(44)
            top_bar.addWidget(btn)

        main_layout.addLayout(top_bar)

        # 🔹 Tabla
        table = QTableWidget(4, 5)
        table.setHorizontalHeaderLabels([
            "Partida", "Descripción", "Cantidad", "Ubicación", "Proveedor"
        ])

        # 🔥 CLAVES DE VISUAL
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setFixedHeight(48)
        table.verticalHeader().setDefaultSectionSize(44)

        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 🔹 Datos demo
        data = [
            ("P-001", "Tornillo 3/8", "500", "Almacén A", "FerreMax"),
            ("P-002", "Martillo", "12", "Estantería 2", "ToolsPro"),
            ("P-003", "Taladro", "4", "Bodega", "Bosch"),
            ("P-004", "Llave inglesa", "20", "Almacén B", "Truper"),
        ]

        for row, values in enumerate(data):
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)

                # Centrar cantidad
                if col == 2:
                    item.setTextAlignment(Qt.AlignCenter)

                table.setItem(row, col, item)

        main_layout.addWidget(table)
