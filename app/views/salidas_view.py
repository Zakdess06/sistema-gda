from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout,
    QComboBox, QSpinBox, QLineEdit,
    QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QLabel
)
from PySide6.QtCore import Qt
from datetime import datetime

from app.core.store import store, Salida
from app.core.bitacora import bitacora
from app.core.trabajador_db import fetch_all_trabajadores
from app.models.trabajador import Trabajador
from app.utils.table_utils import ajustar_ancho_tabla
class SalidasView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(15)  # Reducir espaciado entre elementos
        layout.setContentsMargins(10, 10, 10, 10)  # Márgenes del contenedor

        # ===== FORMULARIO SIMPLIFICADO =====
        form = QFormLayout()
        form.setSpacing(12)  # Espaciado entre filas del formulario
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Trabajador
        self.cmb_id_trabajador = QComboBox()
        self.cmb_id_trabajador.setMinimumHeight(35)
        form.addRow("Trabajador:", self.cmb_id_trabajador)

        # Producto (solo productos existentes con stock)
        self.cmb_partida = QComboBox()
        self.cmb_partida.setEditable(False)
        self.cmb_partida.setMinimumHeight(35)
        form.addRow("Producto:", self.cmb_partida)

        # Ubicación (se llena automáticamente)
        self.txt_ubicacion = QLineEdit()
        self.txt_ubicacion.setReadOnly(True)
        self.txt_ubicacion.setMinimumHeight(35)
        form.addRow("Ubicación:", self.txt_ubicacion)

        # Cantidad
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 100000)
        self.spin_cantidad.setMinimumHeight(35)
        form.addRow("Cantidad:", self.spin_cantidad)

        # Proyecto
        self.txt_proyecto = QLineEdit()
        self.txt_proyecto.setMinimumHeight(35)
        form.addRow("Proyecto:", self.txt_proyecto)

        # Destino
        self.txt_destino = QLineEdit()
        self.txt_destino.setMinimumHeight(35)
        form.addRow("Destino:", self.txt_destino)

        # Observaciones (opcional)
        self.txt_obs = QLineEdit()
        self.txt_obs.setMinimumHeight(35)
        form.addRow("Observaciones:", self.txt_obs)

        layout.addLayout(form)

        # ===== BOTONES DE ACCIÓN =====
        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar producto")
        self.btn_agregar.setMinimumHeight(40)
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                min-height: 40px;
                min-width: 140px;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                background-color: #10b981;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #34d399;
            }
            QPushButton:pressed {
                background-color: #059669;
            }
        """)
        
        self.btn_registrar_todas = QPushButton("Registrar todas")
        self.btn_registrar_todas.setMinimumHeight(40)
        self.btn_registrar_todas.setStyleSheet("""
            QPushButton {
                min-height: 40px;
                min-width: 120px;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                background-color: #2563eb;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #3b82f6;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.btn_registrar_todas.setEnabled(False)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_agregar)
        btn_layout.addWidget(self.btn_registrar_todas)
        layout.addLayout(btn_layout)

        # ===== TABLA DE PRODUCTOS A REGISTRAR =====
        lbl_productos = QLabel("Productos a registrar:")
        layout.addWidget(lbl_productos)
        
        self.table_productos = QTableWidget(0, 6)
        self.table_productos.setHorizontalHeaderLabels([
            "Producto", "Descripción", "Cantidad", 
            "Unidad", "Ubicación", "Eliminar"
        ])
        ajustar_ancho_tabla(self.table_productos, anchos={
            0: 110,     # Producto
            1: 150,     # Descripción
            2: 80,      # Cantidad
            3: 60,      # Unidad
            4: 100,     # Ubicación
            5: 70       # Eliminar
        })
        self.table_productos.verticalHeader().setDefaultSectionSize(40)
        self.table_productos.setMaximumHeight(180)  # Reducir más la altura
        self.table_productos.setMinimumHeight(100)
        self.table_productos.setAlternatingRowColors(True)
        self.table_productos.setStyleSheet("""
            QTableWidget {
                gridline-color: #333;
                alternate-background-color: #1a1a1a;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QScrollBar:vertical {
                width: 12px;
                background-color: #0a0a0a;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777;
            }
        """)
        self.table_productos.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table_productos, 1)  # Proporción 1
        
        # Lista para guardar datos de productos temporalmente
        self.productos_temp = []

        # ===== TABLA DE HISTORIAL =====
        lbl_historial = QLabel("Historial de salidas:")
        layout.addWidget(lbl_historial)
        
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Trabajador", "Producto",
            "Cantidad", "Proyecto", "Destino"
        ])
        ajustar_ancho_tabla(self.table, anchos={
            0: 120,     # Fecha
            1: 140,     # Trabajador
            2: 160,     # Producto
            3: 80,      # Cantidad
            4: 180,     # Proyecto
            5: 150      # Destino
        })
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #333;
                alternate-background-color: #1a1a1a;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QScrollBar:vertical {
                width: 12px;
                background-color: #0a0a0a;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777;
            }
        """)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table, 3)  # Proporción 3 (más espacio)

        # ===== CONEXIONES =====
        self.cmb_id_trabajador.currentTextChanged.connect(self.load_partidas)
        self.cmb_partida.currentTextChanged.connect(self.update_cantidad_maxima)
        self.btn_agregar.clicked.connect(self.agregar_producto)
        self.btn_registrar_todas.clicked.connect(self.registrar_todas_salidas)

        self.load_trabajadores()
        self.load_partidas()
        self.load_salidas()
        # Actualizar automáticamente cuando cambie el almacén
        from app.core.event_manager import event_manager
        event_manager.almacen_changed.connect(self.load_partidas)
        event_manager.trabajador_changed.connect(self.load_trabajadores)
        event_manager.salida_added.connect(self.load_salidas)

    # ---------- CARGAS ----------
    def load_trabajadores(self):
        """Carga trabajadores desde la BD y actualiza el store"""
        # Actualizar store con datos de BD
        store.trabajadores.clear()
        for t in fetch_all_trabajadores():
            store.trabajadores[t['id']] = Trabajador(
                id=t['id'], 
                nombre=t['nombre'], 
                numero_identificacion=t['identificacion']
            )
        
        # Actualizar combo
        self.cmb_id_trabajador.clear()
        for id_trab, trabajador in store.trabajadores.items():
            self.cmb_id_trabajador.addItem(f"{id_trab} - {trabajador.nombre}", id_trab)

    def load_partidas(self):
        """Carga solo productos con stock disponible"""
        self.cmb_partida.clear()
        almacen = store.get_almacen()
        
        # Solo mostrar productos con stock
        for partida, item in almacen.items():
            if item.cantidad > 0:
                self.cmb_partida.addItem(f"{partida} - {item.descripcion}", partida)

        if self.cmb_partida.count() > 0:
            self.update_cantidad_maxima()
        else:
            self.btn_agregar.setEnabled(False)

    def update_cantidad_maxima(self):
        """Actualiza el máximo permitido según el stock disponible y llena la ubicación"""
        codigo = self.cmb_partida.currentData()
        if not codigo:
            self.btn_agregar.setEnabled(False)
            self.txt_ubicacion.clear()
            return

        almacen = store.get_almacen()
        item = almacen.get(codigo)
        if item and item.cantidad > 0:
            self.spin_cantidad.setMaximum(item.cantidad)
            self.spin_cantidad.setValue(1)
            self.txt_ubicacion.setText(item.ubicacion)
            self.btn_agregar.setEnabled(True)
        else:
            self.btn_agregar.setEnabled(False)
            self.txt_ubicacion.clear()


    def load_salidas(self):
        """Carga las salidas desde la BD"""
        self.table.setRowCount(0)
        
        # Recargar desde BD para obtener los datos más recientes
        from app.core.salidas_db import fetch_all_salidas
        salidas = fetch_all_salidas()
        
        for s in salidas:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(s.fecha))
            self.table.setItem(row, 1, QTableWidgetItem(f"{s.trabajador_id} - {s.trabajador_nombre}"))
            self.table.setItem(row, 2, QTableWidgetItem(s.partida))
            self.table.setItem(row, 3, QTableWidgetItem(str(s.cantidad)))
            self.table.setItem(row, 4, QTableWidgetItem(s.proyecto))
            self.table.setItem(row, 5, QTableWidgetItem(s.destino))

    # ---------- ACCIÓN ----------
    def agregar_producto(self):
        """Valida y agrega un producto a la lista de productos temporales"""
        # Validar trabajador
        id_trabajador = self.cmb_id_trabajador.currentData()
        if not id_trabajador:
            QMessageBox.warning(self, "Error", "Seleccione un trabajador")
            return

        # Obtener nombre del trabajador
        trabajador = store.trabajadores.get(id_trabajador)
        if not trabajador:
            QMessageBox.warning(self, "Error", "Trabajador no encontrado")
            return

        # Validar producto
        codigo_partida = self.cmb_partida.currentData()
        if not codigo_partida:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        # Validar cantidad
        cantidad = self.spin_cantidad.value()
        if cantidad <= 0:
            QMessageBox.warning(self, "Error", "La cantidad debe ser mayor a 0")
            return

        # Validar proyecto
        proyecto = self.txt_proyecto.text().strip()
        if not proyecto:
            QMessageBox.warning(self, "Error", "El proyecto es obligatorio")
            return

        # Validar destino
        destino = self.txt_destino.text().strip()
        if not destino:
            QMessageBox.warning(self, "Error", "El destino es obligatorio")
            return

        try:
            almacen = store.get_almacen()
            item = almacen.get(codigo_partida)
            if not item:
                QMessageBox.warning(self, "Error", "Producto no encontrado")
                return

            # Validar disponibilidad considerando productos ya agregados
            cantidad_en_lista = sum(
                p['cantidad'] for p in self.productos_temp 
                if p['partida'] == codigo_partida
            )
            cantidad_total = cantidad_en_lista + cantidad
            
            if cantidad_total > item.cantidad:
                disponible = item.cantidad - cantidad_en_lista
                QMessageBox.critical(
                    self,
                    "Stock insuficiente",
                    f"Disponible: {disponible} unidades (considerando lo ya agregado)"
                )
                return

            # Agregar a lista temporal
            producto_temp = {
                'partida': codigo_partida,
                'descripcion': item.descripcion,
                'cantidad': cantidad,
                'unidad': item.unidad,
                'ubicacion': item.ubicacion,
                'id_trabajador': id_trabajador,
                'trabajador_nombre': trabajador.nombre,
                'proyecto': proyecto,
                'destino': destino,
                'observaciones': self.txt_obs.text().strip()
            }
            self.productos_temp.append(producto_temp)

            # Actualizar tabla de productos
            self.actualizar_tabla_productos()

            # Habilitar botón de registrar
            self.btn_registrar_todas.setEnabled(True)

            # Limpiar solo cantidad y observaciones, mantener proyecto y destino
            self.spin_cantidad.setValue(1)
            self.txt_obs.clear()
            self.cmb_partida.setCurrentIndex(0)

            QMessageBox.information(self, "Éxito", "Producto agregado a la lista")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def actualizar_tabla_productos(self):
        """Actualiza la tabla visual de productos a registrar"""
        self.table_productos.setRowCount(0)
        
        for idx, prod in enumerate(self.productos_temp):
            row = self.table_productos.rowCount()
            self.table_productos.insertRow(row)
            self.table_productos.setRowHeight(row, 40)

            self.table_productos.setItem(row, 0, QTableWidgetItem(prod['partida']))
            self.table_productos.setItem(row, 1, QTableWidgetItem(prod['descripcion']))
            self.table_productos.setItem(row, 2, QTableWidgetItem(str(prod['cantidad'])))
            self.table_productos.setItem(row, 3, QTableWidgetItem(prod['unidad']))
            self.table_productos.setItem(row, 4, QTableWidgetItem(prod['ubicacion']))

            # Botón eliminar centrado
            btn_eliminar = QPushButton("×")
            btn_eliminar.setMaximumWidth(50)
            btn_eliminar.setMaximumHeight(50)
            btn_eliminar.setStyleSheet("""
                QPushButton {
                    padding: 0px;
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
                QPushButton:pressed {
                    background-color: #b91c1c;
                }
            """)
            btn_eliminar.clicked.connect(lambda checked, i=idx: self.eliminar_producto(i))
            
            # Crear contenedor centrado
            container = QWidget()
            layout_btn = QHBoxLayout(container)
            layout_btn.setContentsMargins(0, 0, 0, 0)
            layout_btn.addStretch()
            layout_btn.addWidget(btn_eliminar)
            layout_btn.addStretch()
            
            self.table_productos.setCellWidget(row, 5, container)

    def eliminar_producto(self, idx):
        """Elimina un producto de la lista temporal"""
        if 0 <= idx < len(self.productos_temp):
            self.productos_temp.pop(idx)
            self.actualizar_tabla_productos()
            
            if not self.productos_temp:
                self.btn_registrar_todas.setEnabled(False)

    def registrar_todas_salidas(self):
        """Registra todas las salidas acumuladas"""
        if not self.productos_temp:
            QMessageBox.warning(self, "Error", "No hay productos para registrar")
            return

        try:
            # Validar stock disponible antes de registrar
            almacen = store.get_almacen()
            for prod in self.productos_temp:
                item = almacen.get(prod['partida'])
                if not item or item.cantidad < prod['cantidad']:
                    disponible = item.cantidad if item else 0
                    QMessageBox.critical(
                        self,
                        "Stock insuficiente",
                        f"Producto {prod['partida']}: Solo hay {disponible} unidades disponibles"
                    )
                    return

            cantidad_registros = len(self.productos_temp)
            
            for prod in self.productos_temp:
                # Crear objeto Salida para cada producto
                salida = Salida(
                    fecha=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    partida=prod['partida'],
                    descripcion=prod['descripcion'],
                    cantidad=prod['cantidad'],
                    unidad=prod['unidad'],
                    trabajador_id=prod['id_trabajador'],
                    trabajador_nombre=prod['trabajador_nombre'],
                    proyecto=prod['proyecto'],
                    destino=prod['destino'],
                    entrego="",
                    observaciones=prod['observaciones']
                )
                store.add_salida(salida)
                
                # Decrementar stock del almacén
                item = almacen[prod['partida']]
                item.cantidad -= prod['cantidad']

            # Limpiar lista temporal
            self.productos_temp.clear()
            self.actualizar_tabla_productos()
            self.btn_registrar_todas.setEnabled(False)
            
            # Actualizar combo de partidas (quitar productos sin stock)
            self.load_partidas()
            
            # Actualizar tabla de historial
            self.load_salidas()

            QMessageBox.information(
                self, 
                "Éxito", 
                f"Se registraron {cantidad_registros} salidas correctamente"
            )

            # Limpiar formulario
            self.spin_cantidad.setValue(1)
            self.txt_destino.clear()
            self.txt_proyecto.clear()
            self.txt_obs.clear()
            self.txt_ubicacion.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error al registrar", str(e))
