# app/views/prestamo_herramienta_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
    QComboBox, QLabel, QTextEdit, QSpinBox, QDateTimeEdit,
    QFrame, QGridLayout
)
from PySide6.QtCore import Qt, QDateTime, QTimer
from datetime import datetime

from app.core.store import store
from app.core.event_manager import event_manager
from app.controllers.prestamo_herramienta_controller import PrestamoHerramientaController
from app.core.bitacora import bitacora
from app.utils.table_utils import ajustar_ancho_tabla


class PrestamoHerramientaView(QWidget):
    """Vista para gestionar préstamos de herramientas"""

    def __init__(self):
        super().__init__()
        self.controller = PrestamoHerramientaController()
        self.prestamo_seleccionado = None

        layout = QVBoxLayout(self)

        # ===== TABS =====
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Solicitar Préstamo
        self.tab_solicitar = self.crear_tab_solicitar()
        self.tabs.addTab(self.tab_solicitar, "Solicitar Préstamo")

        # Tab 2: Devoluciones
        self.tab_devolver = self.crear_tab_devolver()
        self.tabs.addTab(self.tab_devolver, "Registrar Devolución")

        # Tab 3: Historial
        self.tab_historial = self.crear_tab_historial()
        self.tabs.addTab(self.tab_historial, "Historial Completo")

        # Subscribirse a cambios en store
        store.subscribe(self.cargar_datos)
        event_manager.prestamo_solicitado.connect(self.cargar_datos)
        event_manager.prestamo_devuelto.connect(self.cargar_datos)
        event_manager.herramienta_changed.connect(self.cargar_datos)
        event_manager.data_changed.connect(self.cargar_datos)
        self.cargar_datos()

        # Timer para revisar préstamos vencidos cada minuto
        self._vencidos_timer = QTimer(self)
        self._vencidos_timer.timeout.connect(self.check_overdue)
        self._vencidos_timer.start(60 * 1000)
        # comprobación inicial
        self.check_overdue()

    # ========== TAB 1: SOLICITAR PRÉSTAMO ==========
    def crear_tab_solicitar(self) -> QWidget:
        """Crea la pestaña para solicitar préstamos"""
        widget = QWidget()
        outer_layout = QVBoxLayout(widget)
        outer_layout.setSpacing(10)
        outer_layout.setContentsMargins(12, 12, 12, 12)

        # título con acento y caja con los campos de solicitud
        title_lbl = QLabel("Solicitud de préstamo")
        title_lbl.setStyleSheet("font-size:14px; font-weight:700; padding:6px 8px; border-left:4px solid #3a85ff; margin-bottom:6px;")
        outer_layout.addWidget(title_lbl)

        # formulario simple sin caja decorativa
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(12)

        def crear_linea():
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Plain)
            line.setLineWidth(0)
            # make separator fully transparent and zero-height
            line.setFixedHeight(0)
            line.setStyleSheet("QFrame{background-color:transparent; border:none; margin:0px; padding:0px;}")
            return line

        # fila 0 - herramienta
        lbl = QLabel("Herramienta:")
        lbl.setFixedWidth(160)
        lbl.setStyleSheet("font-weight:600;")
        self.combo_herramienta = QComboBox()
        self.combo_herramienta.setMinimumWidth(380)
        self.combo_herramienta.setMaximumWidth(500)
        grid.addWidget(lbl, 0, 0)
        grid.addWidget(self.combo_herramienta, 0, 1, 1, 3)
        grid.addWidget(crear_linea(), 1, 0, 1, 4)

        # fila 2 - ubicación y cantidad
        lbl_ubi = QLabel("Ubicación:")
        lbl_ubi.setFixedWidth(160)
        grid.addWidget(lbl_ubi, 2, 0)
        self.lbl_ubicacion = QLabel("-")
        self.lbl_ubicacion.setStyleSheet("color:#dcdcdc;")
        self.lbl_ubicacion.setObjectName("ValueLabel")
        grid.addWidget(self.lbl_ubicacion, 2, 1)
        lbl_cd = QLabel("Cantidad disponible:")
        lbl_cd.setFixedWidth(160)
        grid.addWidget(lbl_cd, 2, 2)
        self.lbl_cantidad = QLabel("0")
        self.lbl_cantidad.setObjectName("ValueLabel")
        grid.addWidget(self.lbl_cantidad, 2, 3)
        grid.addWidget(crear_linea(), 3, 0, 1, 4)

        # fila 4 - trabajador solicita
        lbl_sol = QLabel("Trabajador que solicita:")
        lbl_sol.setFixedWidth(160)
        grid.addWidget(lbl_sol, 4, 0)
        self.combo_trabajador_solicita = QComboBox()
        self.combo_trabajador_solicita.setMinimumWidth(260)
        self.combo_trabajador_solicita.setMaximumWidth(480)
        grid.addWidget(self.combo_trabajador_solicita, 4, 1, 1, 3)
        grid.addWidget(crear_linea(), 5, 0, 1, 4)

        # fila 6 - trabajador despacha
        lbl_dep = QLabel("Trabajador que despacha:")
        lbl_dep.setFixedWidth(160)
        grid.addWidget(lbl_dep, 6, 0)
        self.combo_trabajador_despacha = QComboBox()
        self.combo_trabajador_despacha.setMinimumWidth(260)
        self.combo_trabajador_despacha.setMaximumWidth(480)
        grid.addWidget(self.combo_trabajador_despacha, 6, 1, 1, 3)
        grid.addWidget(crear_linea(), 7, 0, 1, 4)

        # fila 8 - estado herramienta
        lbl_est = QLabel("Estado de la herramienta:")
        lbl_est.setFixedWidth(160)
        grid.addWidget(lbl_est, 8, 0)
        self.combo_estado_prestamo = QComboBox()
        self.combo_estado_prestamo.addItems(["Bueno", "Regular", "Dañado"])
        grid.addWidget(self.combo_estado_prestamo, 8, 1)
        grid.addWidget(crear_linea(), 9, 0, 1, 4)

        # fila 10 - fecha regreso estimada
        lbl_fecha = QLabel("Fecha de regreso estimada:")
        lbl_fecha.setFixedWidth(160)
        grid.addWidget(lbl_fecha, 10, 0)
        self.date_regreso_estimada = QDateTimeEdit()
        self.date_regreso_estimada.setDateTime(QDateTime.currentDateTime())
        self.date_regreso_estimada.setDisplayFormat("yyyy-MM-dd HH:mm")
        grid.addWidget(self.date_regreso_estimada, 10, 1, 1, 3)
        grid.addWidget(crear_linea(), 11, 0, 1, 4)

        # fila 12 - cantidad a prestar
        lbl_cant = QLabel("Cantidad a prestar:")
        lbl_cant.setFixedWidth(160)
        grid.addWidget(lbl_cant, 12, 0)
        self.spin_cantidad_prestamo = QSpinBox()
        self.spin_cantidad_prestamo.setRange(1, 999999)
        self.spin_cantidad_prestamo.setValue(1)
        self.spin_cantidad_prestamo.setMaximumWidth(100)
        grid.addWidget(self.spin_cantidad_prestamo, 12, 1)

        # botón dentro del formulario
        self.btn_solicitar = QPushButton("Crear Préstamo")
        self.btn_solicitar.setMinimumHeight(36)
        self.btn_solicitar.clicked.connect(self.solicitar_prestamo)
        grid.addWidget(self.btn_solicitar, 13, 0, 1, 2)

        outer_layout.addLayout(grid)
        outer_layout.addSpacing(20)

        # tabla de préstamos activos
        outer_layout.addWidget(QLabel("Préstamos activos:"))
        self.table_activos = QTableWidget(0, 6)
        self.table_activos.setHorizontalHeaderLabels([
            "ID", "Herramienta", "Solicita", "Despacha", "Fecha", "Estado"
        ])
        ajustar_ancho_tabla(self.table_activos, anchos={
            0: 120,  # ID
            1: 180,  # Herramienta
            2: 140,  # Solicita
            3: 140,  # Despacha
            4: 140,  # Fecha
            5: 100   # Estado (se estira)
        })
        self.table_activos.setEditTriggers(QTableWidget.NoEditTriggers)
        outer_layout.addWidget(self.table_activos)

        # conectar cambios
        self.combo_herramienta.currentIndexChanged.connect(self.actualizar_detalles_herramienta)
        self.combo_trabajador_solicita.currentIndexChanged.connect(self.on_trabajador_solicita_changed)
        self.combo_trabajador_despacha.currentIndexChanged.connect(self.on_trabajador_despacha_changed)

        return widget

    # ========== TAB 2: REGISTRAR DEVOLUCIÓN ==========
    def crear_tab_devolver(self) -> QWidget:
        """Crea la pestaña para registrar devoluciones"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Seleccionar préstamo
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(QLabel("Préstamo a devolver:"))
        self.combo_prestamo_devolver = QComboBox()
        self.combo_prestamo_devolver.setMinimumWidth(520)
        h_layout1.addWidget(self.combo_prestamo_devolver)
        h_layout1.addStretch()
        layout.addLayout(h_layout1)

        # Detalles del préstamo: usar grid y agrupar en una caja para mejor alineación
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(-1)

        # Función auxiliar para crear línea separadora horizontal (blanca brillante)
        def crear_linea_horizontal():
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Plain)
            line.setLineWidth(1)
            # make separator invisible to remove harsh lines from layout
            line.setFixedHeight(0)
            line.setStyleSheet("QFrame{background-color:transparent; border:none; margin:0px; padding:0px;}")
            return line

        # Fila 0
        lbl_herr = QLabel("Herramienta:")
        lbl_herr.setFixedWidth(140)
        lbl_herr.setStyleSheet("font-weight:600;")
        self.lbl_herr_devolver = QLabel("-")
        self.lbl_herr_devolver.setStyleSheet("color: #dcdcdc;")
        self.lbl_herr_devolver.setObjectName("ValueLabel")

        lbl_estado = QLabel("Estado al prestar:")
        lbl_estado.setFixedWidth(140)
        lbl_estado.setStyleSheet("font-weight:600;")
        self.lbl_estado_prestamo = QLabel("-")
        self.lbl_estado_prestamo.setStyleSheet("color: #dcdcdc;")
        self.lbl_estado_prestamo.setObjectName("ValueLabel")

        grid.addWidget(lbl_herr, 0, 0, Qt.AlignLeft)
        grid.addWidget(self.lbl_herr_devolver, 0, 1)
        grid.addWidget(lbl_estado, 0, 2, Qt.AlignLeft)
        grid.addWidget(self.lbl_estado_prestamo, 0, 3)

        # Línea horizontal separadora después de fila 0
        for col in range(4):
            grid.addWidget(crear_linea_horizontal(), 1, col)

        # Fila 1 (ajustada a índice 2 por la línea anterior)
        lbl_sol = QLabel("Solicitó:")
        lbl_sol.setFixedWidth(140)
        lbl_sol.setStyleSheet("font-weight:600;")
        self.lbl_solicita_devolver = QLabel("-")
        self.lbl_solicita_devolver.setStyleSheet("color: #dcdcdc;")
        self.lbl_solicita_devolver.setObjectName("ValueLabel")

        lbl_desp = QLabel("Despachó:")
        lbl_desp.setFixedWidth(140)
        lbl_desp.setStyleSheet("font-weight:600;")
        self.lbl_despacha_devolver = QLabel("-")
        self.lbl_despacha_devolver.setStyleSheet("color: #dcdcdc;")
        self.lbl_despacha_devolver.setObjectName("ValueLabel")

        grid.addWidget(lbl_sol, 2, 0, Qt.AlignLeft)
        grid.addWidget(self.lbl_solicita_devolver, 2, 1)
        grid.addWidget(lbl_desp, 2, 2, Qt.AlignLeft)
        grid.addWidget(self.lbl_despacha_devolver, 2, 3)

        # Línea horizontal separadora después de fila 1
        for col in range(4):
            grid.addWidget(crear_linea_horizontal(), 3, col)

        # Fila 2 (ajustada a índice 4 por la línea anterior)
        lbl_fecha = QLabel("Fecha de préstamo:")
        lbl_fecha.setFixedWidth(140)
        lbl_fecha.setStyleSheet("font-weight:600;")
        self.lbl_fecha_prestamo = QLabel("-")
        self.lbl_fecha_prestamo.setStyleSheet("color: #dcdcdc;")
        self.lbl_fecha_prestamo.setObjectName("ValueLabel")

        lbl_regreso = QLabel("Fecha de regreso estimada:")
        lbl_regreso.setFixedWidth(140)
        lbl_regreso.setStyleSheet("font-weight:600;")
        self.lbl_fecha_regreso_estimada = QLabel("-")
        self.lbl_fecha_regreso_estimada.setStyleSheet("color: #dcdcdc;")
        self.lbl_fecha_regreso_estimada.setObjectName("ValueLabel")

        grid.addWidget(lbl_fecha, 4, 0, Qt.AlignLeft)
        grid.addWidget(self.lbl_fecha_prestamo, 4, 1)
        grid.addWidget(lbl_regreso, 4, 2, Qt.AlignLeft)
        grid.addWidget(self.lbl_fecha_regreso_estimada, 4, 3)

        # Agrupar en caja con bordes suaves
        from PySide6.QtWidgets import QGroupBox
        box = QGroupBox()
        box.setObjectName("Card")
        box.setLayout(grid)
        box.setStyleSheet("QGroupBox{border:1px solid #2f2f2f; border-radius:6px; margin-top:6px; padding:10px;} QGroupBox::title{subcontrol-origin:margin; left:10px;}" )
        # Título con acento a la izquierda
        title_lbl = QLabel("Detalles del préstamo")
        title_lbl.setStyleSheet("font-size:14px; font-weight:700; padding:6px 8px; border-left:4px solid #3a85ff; margin-bottom:6px;")
        layout.addWidget(title_lbl)
        layout.addWidget(box)

        # línea divisoria pequeña
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setFixedHeight(6)
        layout.addWidget(line)

        # Agrupar campos de devolución en una caja separada
        gbox_dev = QGroupBox("Devolución")
        gbox_dev.setObjectName("Card")
        gbox_dev_layout = QVBoxLayout()

        # Trabajador que recibe
        h_layout2 = QHBoxLayout()
        lbl_recibe = QLabel("Trabajador que recibe:")
        lbl_recibe.setFixedWidth(160)
        self.combo_trabajador_recibe = QComboBox()
        self.combo_trabajador_recibe.setMaximumWidth(420)
        h_layout2.addWidget(lbl_recibe)
        h_layout2.addWidget(self.combo_trabajador_recibe)
        h_layout2.addStretch()
        gbox_dev_layout.addLayout(h_layout2)

        # Estado de devolución
        h_layout3 = QHBoxLayout()
        lbl_estado = QLabel("Estado de devolución:")
        lbl_estado.setFixedWidth(160)
        self.combo_estado_devolucion = QComboBox()
        self.combo_estado_devolucion.addItems(["Bueno", "Regular", "Dañado"])
        self.combo_estado_devolucion.setMaximumWidth(220)
        h_layout3.addWidget(lbl_estado)
        h_layout3.addWidget(self.combo_estado_devolucion)
        h_layout3.addStretch()
        gbox_dev_layout.addLayout(h_layout3)

        # Comentarios con marco
        lbl_com = QLabel("Comentarios:")
        gbox_dev_layout.addWidget(lbl_com)
        comment_frame = QFrame()
        comment_frame.setStyleSheet("QFrame{border:1px solid #2f2f2f; border-radius:6px; background: #111111;}")
        comment_layout = QVBoxLayout(comment_frame)
        self.txt_comentarios = QTextEdit()
        self.txt_comentarios.setMinimumHeight(100)
        self.txt_comentarios.setStyleSheet("QTextEdit{background:transparent;}")
        comment_layout.addWidget(self.txt_comentarios)
        gbox_dev_layout.addWidget(comment_frame)

        # Botón alineado a la derecha dentro de la caja
        h_layout_btn = QHBoxLayout()
        h_layout_btn.addStretch()
        self.btn_devolver = QPushButton("Registrar Devolución")
        self.btn_devolver.setObjectName("PrimaryButton")
        self.btn_devolver.clicked.connect(self.registrar_devolucion)
        self.btn_devolver.setMinimumWidth(160)
        h_layout_btn.addWidget(self.btn_devolver)
        gbox_dev_layout.addLayout(h_layout_btn)

        gbox_dev.setLayout(gbox_dev_layout)
        gbox_dev.setStyleSheet("QGroupBox{border:1px solid #2f2f2f; border-radius:6px; padding:10px; margin-top:8px;} QGroupBox:title{subcontrol-origin:margin; left:10px; font-weight:700;}" )
        layout.addWidget(gbox_dev)

        # Conectar cambios
        self.combo_prestamo_devolver.currentIndexChanged.connect(self.actualizar_detalles_prestamo)

        return widget

    # ========== TAB 3: HISTORIAL ==========
    def crear_tab_historial(self) -> QWidget:
        """Crea la pestaña de historial"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Filtros
        h_filtros = QHBoxLayout()
        h_filtros.addWidget(QLabel("Filtrar por:"))
        
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Todos", "Solo activos", "Solo devueltos"])
        self.combo_filtro.currentIndexChanged.connect(self.cargar_historial)
        h_filtros.addWidget(self.combo_filtro)
        h_filtros.addStretch()
        layout.addLayout(h_filtros)

        # Tabla de historial
        self.table_historial = QTableWidget(0, 9)
        self.table_historial.setHorizontalHeaderLabels([
            "ID", "Herramienta", "Solicita", "Despacha", "Recibe",
            "Fecha Préstamo", "Fecha Regreso Est.", "Fecha Devolución", "Estado Préstamo"
        ])
        ajustar_ancho_tabla(self.table_historial, anchos={
            0: 120,  # ID
            1: 180,  # Herramienta
            2: 140,  # Solicita
            3: 140,  # Despacha
            4: 140,  # Recibe
            5: 140,  # Fecha Préstamo
            6: 140,  # Fecha Regreso Est.
            7: 140,  # Fecha Devolución
            8: 100   # Estado Préstamo
        })
        self.table_historial.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table_historial)

        return widget

    # ========== MÉTODOS DE CARGA DE DATOS ==========
    def cargar_datos(self):
        """Recarga todos los datos en la vista"""
        self.actualizar_combos_herramientas()
        self.actualizar_combos_trabajadores()
        # Aplicar filtros de exclusión mutua después de cargar trabajadores
        self.actualizar_combo_solicita()
        self.cargar_prestamos_activos()
        self.actualizar_combos_prestamos()
        self.cargar_historial()

    def actualizar_combos_herramientas(self):
        """Actualiza el combo de herramientas disponibles"""
        self.combo_herramienta.blockSignals(True)
        self.combo_herramienta.clear()

        # Obtener solo herramientas registradas (no productos del almacén)
        herramientas = self.controller.obtener_herramientas_disponibles()
        for h in herramientas:
            self.combo_herramienta.addItem(f"{h.codigo} - {h.descripcion}", h.codigo)

        self.combo_herramienta.blockSignals(False)
        # Forzar actualización aunque no haya cambio de índice
        self.actualizar_detalles_herramienta()

    def actualizar_combos_trabajadores(self):
        """Actualiza los combos de trabajadores"""
        # Combo trabajador que solicita
        self.combo_trabajador_solicita.blockSignals(True)
        self.combo_trabajador_solicita.clear()
        for trab in store.trabajadores.values():
            self.combo_trabajador_solicita.addItem(trab.nombre, trab.id)
        self.combo_trabajador_solicita.blockSignals(False)

        # Combo trabajador que despacha
        self.combo_trabajador_despacha.blockSignals(True)
        self.combo_trabajador_despacha.clear()
        for trab in store.trabajadores.values():
            self.combo_trabajador_despacha.addItem(trab.nombre, trab.id)
        self.combo_trabajador_despacha.blockSignals(False)

        # Combo trabajador que recibe
        self.combo_trabajador_recibe.blockSignals(True)
        self.combo_trabajador_recibe.clear()
        for trab in store.trabajadores.values():
            self.combo_trabajador_recibe.addItem(trab.nombre, trab.id)
        self.combo_trabajador_recibe.blockSignals(False)

    def actualizar_combo_despacha(self):
        """Actualiza el combo de despacha excluyendo al trabajador que solicita"""
        id_solicita = self.combo_trabajador_solicita.currentData()
        id_despacha_actual = self.combo_trabajador_despacha.currentData()
        
        self.combo_trabajador_despacha.blockSignals(True)
        self.combo_trabajador_despacha.clear()
        
        for trab in store.trabajadores.values():
            # No mostrar el trabajador que solicita
            if trab.id != id_solicita:
                self.combo_trabajador_despacha.addItem(trab.nombre, trab.id)
        
        # Seleccionar el primero disponible o mantener si es válido
        if id_despacha_actual and id_despacha_actual != id_solicita:
            for i in range(self.combo_trabajador_despacha.count()):
                if self.combo_trabajador_despacha.itemData(i) == id_despacha_actual:
                    self.combo_trabajador_despacha.setCurrentIndex(i)
                    self.combo_trabajador_despacha.blockSignals(False)
                    return
        
        # Si no se pudo mantener la selección, usar el primero
        if self.combo_trabajador_despacha.count() > 0:
            self.combo_trabajador_despacha.setCurrentIndex(0)
        
        self.combo_trabajador_despacha.blockSignals(False)
        # Actualizar solicita en respuesta
        self.actualizar_combo_solicita()

    def actualizar_combo_solicita(self):
        """Actualiza el combo de solicita excluyendo al trabajador que despacha"""
        id_despacha = self.combo_trabajador_despacha.currentData()
        id_solicita_actual = self.combo_trabajador_solicita.currentData()
        
        self.combo_trabajador_solicita.blockSignals(True)
        self.combo_trabajador_solicita.clear()
        
        for trab in store.trabajadores.values():
            # No mostrar el trabajador que despacha
            if trab.id != id_despacha:
                self.combo_trabajador_solicita.addItem(trab.nombre, trab.id)
        
        # Seleccionar el primero disponible o mantener si es válido
        if id_solicita_actual and id_solicita_actual != id_despacha:
            for i in range(self.combo_trabajador_solicita.count()):
                if self.combo_trabajador_solicita.itemData(i) == id_solicita_actual:
                    self.combo_trabajador_solicita.setCurrentIndex(i)
                    self.combo_trabajador_solicita.blockSignals(False)
                    return
        
        # Si no se pudo mantener la selección, usar el primero
        if self.combo_trabajador_solicita.count() > 0:
            self.combo_trabajador_solicita.setCurrentIndex(0)
        
        self.combo_trabajador_solicita.blockSignals(False)

    def on_trabajador_solicita_changed(self):
        """Se llama cuando cambia el trabajador que solicita"""
        self.actualizar_combo_despacha()

    def on_trabajador_despacha_changed(self):
        """Se llama cuando cambia el trabajador que despacha"""
        self.actualizar_combo_solicita()

    def actualizar_combos_prestamos(self):
        """Actualiza el combo de préstamos activos"""
        self.combo_prestamo_devolver.blockSignals(True)
        self.combo_prestamo_devolver.clear()

        prestamos = self.controller.listar_prestamos_activos()
        for p in prestamos:
            herr = store.herramientas.get(p.herramienta_codigo)
            herr_desc = f"{p.herramienta_codigo}" if herr else p.herramienta_codigo
            texto = f"{p.id} - {herr_desc} ({p.trabajador_solicita_id})"
            self.combo_prestamo_devolver.addItem(texto, p.id)

        self.combo_prestamo_devolver.blockSignals(False)
        self.actualizar_detalles_prestamo()

    def actualizar_detalles_herramienta(self):
        """Actualiza los detalles de la herramienta seleccionada"""
        codigo = self.combo_herramienta.currentData()
        if not codigo:
            self.lbl_ubicacion.setText("-")
            self.lbl_cantidad.setText("0")
            self.btn_solicitar.setEnabled(False)
            return

        herramientas = store.get_herramientas()
        herramienta = herramientas.get(codigo)
        if herramienta:
            self.lbl_ubicacion.setText(herramienta.ubicacion)
            self.lbl_cantidad.setText(str(herramienta.cantidad))
            try:
                # actualizar maximo de cantidad a prestar
                self.spin_cantidad_prestamo.setMaximum(int(herramienta.cantidad))
                self.spin_cantidad_prestamo.setValue(min(self.spin_cantidad_prestamo.value(), herramienta.cantidad))
                self.btn_solicitar.setEnabled(herramienta.cantidad > 0)
            except Exception:
                pass
        else:
            self.lbl_ubicacion.setText("-")
            self.lbl_cantidad.setText("0")
            self.btn_solicitar.setEnabled(False)

    def actualizar_detalles_prestamo(self):
        """Actualiza los detalles del préstamo seleccionado"""
        prestamo_id = self.combo_prestamo_devolver.currentData()
        if not prestamo_id:
            self.limpiar_detalles_prestamo()
            return

        prestamo = self.controller.obtener_prestamo_por_id(prestamo_id)
        if not prestamo:
            self.limpiar_detalles_prestamo()
            return

        herr = store.herramientas.get(prestamo.herramienta_codigo)
        herr_desc = herr.descripcion if herr else prestamo.herramienta_codigo

        trab_solicita = store.trabajadores.get(prestamo.trabajador_solicita_id)
        trab_despacha = store.trabajadores.get(prestamo.trabajador_despacha_id)

        self.lbl_herr_devolver.setText(herr_desc)
        self.lbl_estado_prestamo.setText(prestamo.estado_herramienta_prestamo)
        self.lbl_solicita_devolver.setText(trab_solicita.nombre if trab_solicita else prestamo.trabajador_solicita_id)
        self.lbl_despacha_devolver.setText(trab_despacha.nombre if trab_despacha else prestamo.trabajador_despacha_id)
        self.lbl_fecha_prestamo.setText(prestamo.fecha_prestamo)
        # mostrar fecha de regreso estimada con hora si existe
        if getattr(prestamo, 'fecha_regreso_estimada', None):
            self.lbl_fecha_regreso_estimada.setText(prestamo.fecha_regreso_estimada)
        else:
            self.lbl_fecha_regreso_estimada.setText("-")

    def limpiar_detalles_prestamo(self):
        """Limpia los detalles del préstamo"""
        self.lbl_herr_devolver.setText("-")
        self.lbl_estado_prestamo.setText("-")
        self.lbl_solicita_devolver.setText("-")
        self.lbl_despacha_devolver.setText("-")
        self.lbl_fecha_prestamo.setText("-")

    # ========== CARGAR TABLAS ==========
    def cargar_prestamos_activos(self):
        """Carga la tabla de préstamos activos"""
        self.table_activos.setRowCount(0)
        prestamos = self.controller.listar_prestamos_activos()

        for prestamo in prestamos:
            row = self.table_activos.rowCount()
            self.table_activos.insertRow(row)

            herr = store.herramientas.get(prestamo.herramienta_codigo)
            herr_desc = f"{prestamo.herramienta_codigo} - {herr.descripcion}" if herr else prestamo.herramienta_codigo

            trab_solicita = store.trabajadores.get(prestamo.trabajador_solicita_id)
            trab_despacha = store.trabajadores.get(prestamo.trabajador_despacha_id)

            self.table_activos.setItem(row, 0, QTableWidgetItem(prestamo.id))
            self.table_activos.setItem(row, 1, QTableWidgetItem(herr_desc))
            self.table_activos.setItem(row, 2, QTableWidgetItem(trab_solicita.nombre if trab_solicita else prestamo.trabajador_solicita_id))
            self.table_activos.setItem(row, 3, QTableWidgetItem(trab_despacha.nombre if trab_despacha else prestamo.trabajador_despacha_id))
            self.table_activos.setItem(row, 4, QTableWidgetItem(prestamo.fecha_prestamo))
            self.table_activos.setItem(row, 5, QTableWidgetItem(prestamo.estado_herramienta_prestamo))

            # resaltar si está vencido
            try:
                from app.controllers.prestamo_herramienta_controller import PrestamoHerramientaController
                vencidos = [p.id for p in PrestamoHerramientaController.listar_prestamos_vencidos()]
                if prestamo.id in vencidos:
                    for col in range(self.table_activos.columnCount()):
                        it = self.table_activos.item(row, col)
                        if it:
                            it.setBackground(Qt.red)
            except Exception:
                pass

    def cargar_historial(self):
        """Carga la tabla de historial"""
        self.table_historial.setRowCount(0)

        filtro = self.combo_filtro.currentText()
        if filtro == "Solo activos":
            prestamos = self.controller.listar_prestamos_activos()
        elif filtro == "Solo devueltos":
            prestamos = [p for p in self.controller.listar_todos_prestamos() if not p.es_activo()]
        else:
            prestamos = self.controller.listar_todos_prestamos()

        for prestamo in prestamos:
            row = self.table_historial.rowCount()
            self.table_historial.insertRow(row)

            herr = store.herramientas.get(prestamo.herramienta_codigo)
            herr_desc = f"{prestamo.herramienta_codigo}" if herr else prestamo.herramienta_codigo

            trab_solicita = store.trabajadores.get(prestamo.trabajador_solicita_id)
            trab_despacha = store.trabajadores.get(prestamo.trabajador_despacha_id)
            trab_recibe = store.trabajadores.get(prestamo.trabajador_recibe_id)

            self.table_historial.setItem(row, 0, QTableWidgetItem(prestamo.id))
            self.table_historial.setItem(row, 1, QTableWidgetItem(herr_desc))
            self.table_historial.setItem(row, 2, QTableWidgetItem(trab_solicita.nombre if trab_solicita else "-"))
            self.table_historial.setItem(row, 3, QTableWidgetItem(trab_despacha.nombre if trab_despacha else "-"))
            self.table_historial.setItem(row, 4, QTableWidgetItem(trab_recibe.nombre if trab_recibe else "-"))
            self.table_historial.setItem(row, 5, QTableWidgetItem(prestamo.fecha_prestamo))
            self.table_historial.setItem(row, 6, QTableWidgetItem(prestamo.fecha_devolucion or "-"))
            self.table_historial.setItem(row, 7, QTableWidgetItem(prestamo.estado_herramienta_prestamo))

    # ========== ACCIONES ==========
    def solicitar_prestamo(self):
        """Maneja la solicitud de préstamo"""
        herramienta_codigo = self.combo_herramienta.currentData()
        trabajador_solicita_id = self.combo_trabajador_solicita.currentData()
        trabajador_despacha_id = self.combo_trabajador_despacha.currentData()
        estado = self.combo_estado_prestamo.currentText()
        fecha_regreso = self.date_regreso_estimada.dateTime().toString("yyyy-MM-dd HH:mm")
        cantidad = int(self.spin_cantidad_prestamo.value())

        success, message, prestamo_id = self.controller.solicitar_prestamo(
            herramienta_codigo=herramienta_codigo,
            trabajador_solicita_id=trabajador_solicita_id,
            trabajador_despacha_id=trabajador_despacha_id,
            cantidad=cantidad,
            estado_herramienta=estado,
            fecha_regreso_estimada=fecha_regreso
        )

        if success:
            QMessageBox.information(self, "Éxito", message)
            self.cargar_datos()
        else:
            QMessageBox.warning(self, "Error", message)

    def check_overdue(self):
        """Revisa préstamos vencidos y muestra alerta si hay alguno."""
        try:
            from app.controllers.prestamo_herramienta_controller import PrestamoHerramientaController
            vencidos = PrestamoHerramientaController.listar_prestamos_vencidos()
            if not vencidos:
                return

            lines = []
            for p in vencidos:
                lines.append(f"{p.id} - {p.herramienta_codigo} | Regreso estimado: {p.fecha_regreso_estimada} | Solicitó: {p.trabajador_solicita_id}")

            QMessageBox.warning(
                self,
                "Préstamos vencidos",
                "Se encontraron préstamos vencidos:\n\n" + "\n".join(lines)
            )

            # refrescar tablas para mostrar resaltado
            self.cargar_prestamos_activos()
        except Exception:
            pass

    def registrar_devolucion(self):
        """Maneja el registro de devolución"""
        prestamo_id = self.combo_prestamo_devolver.currentData()
        trabajador_recibe_id = self.combo_trabajador_recibe.currentData()
        estado_devolucion = self.combo_estado_devolucion.currentText()
        comentarios = self.txt_comentarios.toPlainText().strip()

        success, message = self.controller.devolver_prestamo(
            prestamo_id=prestamo_id,
            trabajador_recibe_id=trabajador_recibe_id,
            estado_devolucion=estado_devolucion,
            comentarios=comentarios
        )

        if success:
            QMessageBox.information(self, "Éxito", message)
            self.txt_comentarios.clear()
            self.cargar_datos()
        else:
            QMessageBox.warning(self, "Error", message)
