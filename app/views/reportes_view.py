from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QComboBox, QPushButton,
    QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt
from datetime import datetime

from app.core.store import store
from app.core.bitacora import bitacora
from app.core.exporter import export_to_excel
from app.utils.table_utils import ajustar_ancho_tabla


class ReportesView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        lbl = QLabel("Reportes")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(lbl)

        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems([
            "Almacén",
            "Entradas",
            "Salidas",
            "Stock Mínimo",
            "Productos Más Solicitados"
        ])
        self.cmb_tipo.currentTextChanged.connect(self.load_preview)
        layout.addWidget(self.cmb_tipo)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        btn_export = QPushButton("Exportar a Excel")
        btn_export.clicked.connect(self.exportar)
        layout.addWidget(btn_export)

        self.load_preview()

    # ---------- PREVIEW ----------

    def load_preview(self):
        tipo = self.cmb_tipo.currentText()

        if tipo == "Almacén":
            headers = ["Partida", "Descripción", "Unidad", "Cantidad", "Stock Mín.", "Ubicación", "Proveedor"]
            rows = [
                (
                    i.partida,
                    i.descripcion,
                    i.unidad,
                    i.cantidad,
                    i.stock_minimo,
                    i.ubicacion,
                    i.proveedor
                )
                for i in store.get_almacen().values()
            ]

        elif tipo == "Entradas":
            headers = [
                "Fecha", "Partida", "Descripción",
                "Cantidad", "Unidad", "Proveedor",
                "Recibió", "Ubicación"
            ]
            rows = [
                (
                    e.fecha,
                    e.partida,
                    e.descripcion,
                    e.cantidad,
                    e.unidad,
                    e.proveedor,
                    e.recibio,
                    e.ubicacion
                )
                for e in store.entradas
            ]

        elif tipo == "Salidas":
            headers = [
                "Fecha", "Trabajador", "Proyecto",
                "Partida", "Descripción", "Cantidad",
                "Destino", "Entregó"
            ]
            # Recargar desde BD para obtener los datos más recientes
            from app.core.salidas_db import fetch_all_salidas
            salidas = fetch_all_salidas()
            rows = [
                (
                    s.fecha,
                    f"{s.trabajador_id} - {s.trabajador_nombre}",
                    s.proyecto,
                    s.partida,
                    s.descripcion,
                    s.cantidad,
                    s.destino,
                    s.entrego
                )
                for s in salidas
            ]

        elif tipo == "Stock Mínimo":
            headers = ["Partida", "Descripción", "Cantidad", "Stock Mín.", "Diferencia", "Ubicación", "Proveedor"]
            rows = [
                (
                    i.partida,
                    i.descripcion,
                    i.cantidad,
                    i.stock_minimo,
                    i.stock_minimo - i.cantidad,  # Cuánto falta para llegar al mínimo
                    i.ubicacion,
                    i.proveedor
                )
                for i in store.get_almacen().values()
                if i.cantidad <= i.stock_minimo
            ]

        elif tipo == "Productos Más Solicitados":
            headers = ["Partida", "Descripción", "Unidad", "Total Salidas", "Ubicación", "Proveedor"]
            # Recargar desde BD para obtener los datos más recientes
            from app.core.salidas_db import fetch_all_salidas
            salidas = fetch_all_salidas()
            
            # Agrupar salidas por partida
            salidas_por_partida = {}
            for s in salidas:
                if s.partida not in salidas_por_partida:
                    salidas_por_partida[s.partida] = {
                        'cantidad_total': 0,
                        'veces_solicitado': 0
                    }
                salidas_por_partida[s.partida]['cantidad_total'] += s.cantidad
                salidas_por_partida[s.partida]['veces_solicitado'] += 1
            
            # Crear filas ordenadas por cantidad total (descendente)
            almacen = store.get_almacen()
            rows = []
            for partida, datos in sorted(salidas_por_partida.items(), key=lambda x: x[1]['cantidad_total'], reverse=True):
                item = almacen.get(partida)
                if item:
                    rows.append((
                        partida,
                        item.descripcion,
                        item.unidad,
                        datos['cantidad_total'],
                        item.ubicacion,
                        item.proveedor
                    ))

        self.populate_table(headers, rows)

    def populate_table(self, headers, rows):
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # Ajustar anchos según columnas actuales
        ajustar_ancho_tabla(self.table)

        for row_data in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)

            for col, value in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    # ---------- EXPORT ----------

    def exportar(self):
        tipo = self.cmb_tipo.currentText()

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte",
            f"{tipo.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            "Excel (*.xlsx)"
        )

        if not path:
            return

        try:
            if tipo == "Almacén":
                self.export_almacen(path)
            elif tipo == "Entradas":
                self.export_entradas(path)
            elif tipo == "Salidas":
                self.export_salidas(path)
            elif tipo == "Stock Mínimo":
                self.export_stock_minimo(path)
            elif tipo == "Productos Más Solicitados":
                self.export_productos_mas_solicitados(path)
            
            QMessageBox.information(self, "Listo", "Reporte exportado correctamente")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ---------- EXPORT METHODS ----------

    def export_almacen(self, path):
        headers = ["Partida", "Descripción", "Unidad", "Cantidad", "Stock Mín.", "Ubicación", "Proveedor"]
        almacen = store.get_almacen()
        rows = [
            (
                i.partida,
                i.descripcion,
                i.unidad,
                i.cantidad,
                i.stock_minimo,
                i.ubicacion,
                i.proveedor
            )
            for i in almacen.values()
        ]
        export_to_excel(headers, rows, path)

    def export_entradas(self, path):
        headers = [
            "Fecha", "Partida", "Descripción",
            "Cantidad", "Unidad", "Proveedor",
            "Recibió", "Ubicación", "Observaciones"
        ]
        rows = [
            (
                e.fecha,
                e.partida,
                e.descripcion,
                e.cantidad,
                e.unidad,
                e.proveedor,
                e.recibio,
                e.ubicacion,
                e.observaciones
            )
            for e in store.entradas
        ]
        export_to_excel(headers, rows, path)

    def export_salidas(self, path):
        headers = [
            "Fecha", "ID Trabajador", "Nombre Trabajador",
            "Proyecto", "Partida", "Descripción",
            "Cantidad", "Destino", "Entregó", "Observaciones"
        ]
        rows = [
            (
                s.fecha,
                s.trabajador_id,
                s.trabajador_nombre,
                s.proyecto,
                s.partida,
                s.descripcion,
                s.cantidad,
                s.destino,
                s.entrego,
                s.observaciones
            )
            for s in store.salidas
        ]
        export_to_excel(headers, rows, path)

    def export_stock_minimo(self, path):
        headers = ["Partida", "Descripción", "Cantidad", "Stock Mín.", "Diferencia", "Ubicación", "Proveedor"]
        rows = [
            (
                i.partida,
                i.descripcion,
                i.cantidad,
                i.stock_minimo,
                i.stock_minimo - i.cantidad,
                i.ubicacion,
                i.proveedor
            )
            for i in store.get_almacen().values()
            if i.cantidad <= i.stock_minimo
        ]
        export_to_excel(headers, rows, path)

    def export_productos_mas_solicitados(self, path):
        headers = ["Partida", "Descripción", "Unidad", "Total Salidas", "Ubicación", "Proveedor"]
        from app.core.salidas_db import fetch_all_salidas
        salidas = fetch_all_salidas()
        
        # Agrupar salidas por partida
        salidas_por_partida = {}
        for s in salidas:
            if s.partida not in salidas_por_partida:
                salidas_por_partida[s.partida] = {
                    'cantidad_total': 0,
                    'veces_solicitado': 0
                }
            salidas_por_partida[s.partida]['cantidad_total'] += s.cantidad
            salidas_por_partida[s.partida]['veces_solicitado'] += 1
        
        # Crear filas ordenadas por cantidad total (descendente)
        almacen = store.get_almacen()
        rows = []
        for partida, datos in sorted(salidas_por_partida.items(), key=lambda x: x[1]['cantidad_total'], reverse=True):
            item = almacen.get(partida)
            if item:
                rows.append((
                    partida,
                    item.descripcion,
                    item.unidad,
                    datos['cantidad_total'],
                    item.ubicacion,
                    item.proveedor
                ))
        
        export_to_excel(headers, rows, path)