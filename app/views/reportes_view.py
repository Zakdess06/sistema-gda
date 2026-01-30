from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem
)

from app.core.store import store


class ReportesView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        tabs.addTab(self.tab_almacen(), "Almacén")
        tabs.addTab(self.tab_entradas(), "Entradas")
        tabs.addTab(self.tab_salidas(), "Salidas")
        tabs.addTab(self.tab_herramientas(), "Herramientas")

        layout.addWidget(tabs)

    # -------- TABS --------
    def tab_almacen(self):
        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels([
            "Partida", "Descripción", "Unidad",
            "Cantidad", "Ubicación", "Proveedor"
        ])
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        for item in store.almacen.values():
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(row, 0, QTableWidgetItem(item.partida))
            table.setItem(row, 1, QTableWidgetItem(item.descripcion))
            table.setItem(row, 2, QTableWidgetItem(item.unidad))
            table.setItem(row, 3, QTableWidgetItem(str(item.cantidad)))
            table.setItem(row, 4, QTableWidgetItem(item.ubicacion))
            table.setItem(row, 5, QTableWidgetItem(item.proveedor))

        return table

    def tab_entradas(self):
        table = QTableWidget(0, 7)
        table.setHorizontalHeaderLabels([
            "Fecha", "Partida", "Descripción",
            "Cantidad", "Unidad", "Proveedor", "Recibió"
        ])
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        for e in store.entradas:
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(row, 0, QTableWidgetItem(e.fecha))
            table.setItem(row, 1, QTableWidgetItem(e.partida))
            table.setItem(row, 2, QTableWidgetItem(e.descripcion))
            table.setItem(row, 3, QTableWidgetItem(str(e.cantidad)))
            table.setItem(row, 4, QTableWidgetItem(e.unidad))
            table.setItem(row, 5, QTableWidgetItem(e.proveedor))
            table.setItem(row, 6, QTableWidgetItem(e.recibio))

        return table

    def tab_salidas(self):
        table = QTableWidget(0, 7)
        table.setHorizontalHeaderLabels([
            "Fecha", "Partida", "Descripción",
            "Cantidad", "Unidad", "Destino", "Entregó"
        ])
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        for s in store.salidas:
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(row, 0, QTableWidgetItem(s.fecha))
            table.setItem(row, 1, QTableWidgetItem(s.partida))
            table.setItem(row, 2, QTableWidgetItem(s.descripcion))
            table.setItem(row, 3, QTableWidgetItem(str(s.cantidad)))
            table.setItem(row, 4, QTableWidgetItem(s.unidad))
            table.setItem(row, 5, QTableWidgetItem(s.destino))
            table.setItem(row, 6, QTableWidgetItem(s.entrego))

        return table

    def tab_herramientas(self):
        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels([
            "Código", "Nombre", "Estado", "Responsable"
        ])
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        for h in store.herramientas.values():
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(row, 0, QTableWidgetItem(h.codigo))
            table.setItem(row, 1, QTableWidgetItem(h.nombre))
            table.setItem(row, 2, QTableWidgetItem(h.estado))
            table.setItem(row, 3, QTableWidgetItem(h.responsable))

        return table
