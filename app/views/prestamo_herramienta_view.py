# app/views/prestamo_herramienta_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
    QComboBox, QLabel, QTextEdit, QSpinBox, QDateTimeEdit,
    QFrame, QGridLayout, QFormLayout, QScrollArea
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
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #1f2937;
            }
            QTabBar::tab {
                min-height: 36px;
                padding: 8px 20px;
                background-color: #0f1419;
                color: #9ca3af;
                border: 1px solid #1f2937;
                margin-right: 2px;
                font-size: 12px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #2563eb;
                color: white;
                border: 1px solid #2563eb;
            }
            QTabBar::tab:hover {
                background-color: #161d26;
                color: #f0f4f8;
            }
        """)
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
        # Widget principal con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Widget interno para el scroll
        widget_interno = QWidget()
        main_layout = QVBoxLayout(widget_interno)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Título
        title_lbl = QLabel("Solicitud de préstamo")
        title_lbl.setStyleSheet("font-size:15px; font-weight:700; color:#ffffff; margin-bottom:10px;")
        main_layout.addWidget(title_lbl)

        # ===== SECCIÓN 1: HERRAMIENTA =====
        lbl_sec1 = QLabel("Herramienta")
        lbl_sec1.setStyleSheet("font-size:12px; font-weight:600; color:#aaaaaa; margin-bottom:8px;")
        main_layout.addWidget(lbl_sec1)
        
        h_layout1 = QHBoxLayout()
        h_layout1.setSpacing(12)
        h_layout1.addWidget(QLabel("Herramienta:"))
        self.combo_herramienta = QComboBox()
        self.combo_herramienta.setMinimumHeight(36)
        h_layout1.addWidget(self.combo_herramienta, 1)
        main_layout.addLayout(h_layout1)
        main_layout.addSpacing(12)

        # Ubicación y disponible
        h_layout2 = QHBoxLayout()
        h_layout2.setSpacing(12)
        h_layout2.addWidget(QLabel("Ubicación:"))
        self.lbl_ubicacion = QLabel("-")
        self.lbl_ubicacion.setMinimumHeight(32)
        self.lbl_ubicacion.setStyleSheet("padding:6px; background-color:#1a1a1a; border-radius:4px;")
        h_layout2.addWidget(self.lbl_ubicacion, 1)
        h_layout2.addSpacing(15)
        h_layout2.addWidget(QLabel("Disponible:"))
        self.lbl_cantidad = QLabel("0")
        self.lbl_cantidad.setMinimumHeight(32)
        self.lbl_cantidad.setMinimumWidth(80)
        self.lbl_cantidad.setStyleSheet("padding:6px; background-color:#1a1a1a; border-radius:4px; text-align:center;")
        h_layout2.addWidget(self.lbl_cantidad)
        main_layout.addLayout(h_layout2)
        main_layout.addSpacing(15)

        # ===== SECCIÓN 2: TRABAJADORES =====
        lbl_sec2 = QLabel("Trabajadores")
        lbl_sec2.setStyleSheet("font-size:12px; font-weight:600; color:#aaaaaa; margin-bottom:8px;")
        main_layout.addWidget(lbl_sec2)

        h_layout3 = QHBoxLayout()
        h_layout3.setSpacing(12)
        h_layout3.addWidget(QLabel("Solicita:"))
        self.combo_trabajador_solicita = QComboBox()
        self.combo_trabajador_solicita.setMinimumHeight(36)
        h_layout3.addWidget(self.combo_trabajador_solicita, 1)
        main_layout.addLayout(h_layout3)
        main_layout.addSpacing(10)

        h_layout4 = QHBoxLayout()
        h_layout4.setSpacing(12)
        h_layout4.addWidget(QLabel("Despacha:"))
        self.combo_trabajador_despacha = QComboBox()
        self.combo_trabajador_despacha.setMinimumHeight(36)
        h_layout4.addWidget(self.combo_trabajador_despacha, 1)
        main_layout.addLayout(h_layout4)
        main_layout.addSpacing(15)

        # ===== SECCIÓN 3: DETALLES DEL PRÉSTAMO =====
        lbl_sec3 = QLabel("Detalles del Préstamo")
        lbl_sec3.setStyleSheet("font-size:12px; font-weight:600; color:#aaaaaa; margin-bottom:8px;")
        main_layout.addWidget(lbl_sec3)

        h_layout5 = QHBoxLayout()
        h_layout5.setSpacing(12)
        h_layout5.addWidget(QLabel("Estado:"))
        self.combo_estado_prestamo = QComboBox()
        self.combo_estado_prestamo.addItems(["Bueno", "Regular", "Dañado"])
        self.combo_estado_prestamo.setMinimumHeight(36)
        h_layout5.addWidget(self.combo_estado_prestamo, 1)
        main_layout.addLayout(h_layout5)
        main_layout.addSpacing(10)

        h_layout6 = QHBoxLayout()
        h_layout6.setSpacing(12)
        h_layout6.addWidget(QLabel("Fecha regreso:"))
        self.date_regreso_estimada = QDateTimeEdit()
        self.date_regreso_estimada.setDateTime(QDateTime.currentDateTime())
        self.date_regreso_estimada.setDisplayFormat("yyyy-MM-dd")
        self.date_regreso_estimada.setCalendarPopup(True)
        self.date_regreso_estimada.setMinimumHeight(36)
        self.date_regreso_estimada.setMinimumWidth(150)
        self.date_regreso_estimada.setStyleSheet("""
            QDateTimeEdit {
                padding: 6px;
                border: 1px solid #3f3f3f;
                border-radius: 4px;
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QDateTimeEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #3f3f3f;
            }
        """)
        h_layout6.addWidget(self.date_regreso_estimada, 1)
        main_layout.addLayout(h_layout6)
        main_layout.addSpacing(10)

        h_layout7 = QHBoxLayout()
        h_layout7.setSpacing(12)
        h_layout7.addWidget(QLabel("Cantidad:"))
        self.spin_cantidad_prestamo = QSpinBox()
        self.spin_cantidad_prestamo.setRange(1, 999999)
        self.spin_cantidad_prestamo.setValue(1)
        self.spin_cantidad_prestamo.setMinimumHeight(36)
        self.spin_cantidad_prestamo.setMaximumWidth(120)
        h_layout7.addWidget(self.spin_cantidad_prestamo)
        h_layout7.addStretch()
        main_layout.addLayout(h_layout7)
        main_layout.addSpacing(12)

        # Botón
        self.btn_solicitar = QPushButton("Crear Préstamo")
        self.btn_solicitar.setMinimumHeight(40)
        self.btn_solicitar.setMaximumWidth(200)
        self.btn_solicitar.setStyleSheet("""
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
        self.btn_solicitar.clicked.connect(self.solicitar_prestamo)
        main_layout.addWidget(self.btn_solicitar)
        main_layout.addSpacing(10)

        # Tabla de préstamos activos
        table_title = QLabel("Préstamos activos:")
        table_title.setStyleSheet("font-weight:600; font-size:12px; color:#aaaaaa; margin-bottom:12px;")
        main_layout.addWidget(table_title)
        
        self.table_activos = QTableWidget(0, 6)
        self.table_activos.setHorizontalHeaderLabels([
            "ID", "Herramienta", "Solicita", "Despacha", "Fecha", "Estado"
        ])
        self.table_activos.setMinimumHeight(200)
        ajustar_ancho_tabla(self.table_activos, anchos={
            0: 120,  # ID
            1: 180,  # Herramienta
            2: 140,  # Solicita
            3: 140,  # Despacha
            4: 140,  # Fecha
            5: 100   # Estado (se estira)
        })
        self.table_activos.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.table_activos)

        # Conexiones
        self.combo_herramienta.currentIndexChanged.connect(self.actualizar_detalles_herramienta)
        self.combo_trabajador_solicita.currentIndexChanged.connect(self.on_trabajador_solicita_changed)
        self.combo_trabajador_despacha.currentIndexChanged.connect(self.on_trabajador_despacha_changed)

        # Agregar widget interno al scroll
        main_layout.addStretch()
        scroll.setWidget(widget_interno)
        return scroll

    # ========== TAB 2: REGISTRAR DEVOLUCIÓN ==========
    def crear_tab_devolver(self) -> QWidget:
        """Crea la pestaña para registrar devoluciones"""
        # Widget principal con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Widget interno para el scroll
        widget_interno = QWidget()
        main_layout = QVBoxLayout(widget_interno)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Título
        title_lbl = QLabel("Registrar Devolución")
        title_lbl.setStyleSheet("font-size:15px; font-weight:700; color:#ffffff; margin-bottom:10px;")
        main_layout.addWidget(title_lbl)

        # ===== SECCIÓN 1: SELECCIONAR PRÉSTAMO =====
        lbl_sec1 = QLabel("Seleccionar Préstamo")
        lbl_sec1.setStyleSheet("font-size:12px; font-weight:600; color:#aaaaaa; margin-bottom:8px;")
        main_layout.addWidget(lbl_sec1)

        h_layout1 = QHBoxLayout()
        h_layout1.setSpacing(12)
        h_layout1.addWidget(QLabel("Préstamo:"))
        self.combo_prestamo_devolver = QComboBox()
        self.combo_prestamo_devolver.setMinimumHeight(36)
        h_layout1.addWidget(self.combo_prestamo_devolver, 1)
        main_layout.addLayout(h_layout1)
        main_layout.addSpacing(15)

        # ===== SECCIÓN 2: DETALLES DEL PRÉSTAMO =====
        lbl_sec2 = QLabel("Detalles del Préstamo")
        lbl_sec2.setStyleSheet("font-size:12px; font-weight:600; color:#aaaaaa; margin-bottom:8px;")
        main_layout.addWidget(lbl_sec2)

        # Herramienta y Estado
        h_layout2 = QHBoxLayout()
        h_layout2.setSpacing(12)
        h_layout2.addWidget(QLabel("Herramienta:"))
        self.lbl_herr_devolver = QLabel("-")
        self.lbl_herr_devolver.setMinimumHeight(32)
        self.lbl_herr_devolver.setStyleSheet("padding:6px; background-color:#1a1a1a; border-radius:4px;")
        h_layout2.addWidget(self.lbl_herr_devolver, 1)
        h_layout2.addSpacing(15)
        h_layout2.addWidget(QLabel("Estado al prestar:"))
        self.lbl_estado_prestamo = QLabel("-")
        self.lbl_estado_prestamo.setMinimumHeight(32)
        self.lbl_estado_prestamo.setMinimumWidth(100)
        self.lbl_estado_prestamo.setStyleSheet("padding:6px; background-color:#1a1a1a; border-radius:4px; text-align:center;")
        h_layout2.addWidget(self.lbl_estado_prestamo)
        main_layout.addLayout(h_layout2)
        main_layout.addSpacing(10)

        # Solicitó y Despachó
        h_layout3 = QHBoxLayout()
        h_layout3.setSpacing(12)
        h_layout3.addWidget(QLabel("Solicitó:"))
        self.lbl_solicita_devolver = QLabel("-")
        self.lbl_solicita_devolver.setMinimumHeight(32)
        self.lbl_solicita_devolver.setStyleSheet("padding:6px; background-color:#1a1a1a; border-radius:4px;")
        h_layout3.addWidget(self.lbl_solicita_devolver, 1)
        h_layout3.addSpacing(15)
        h_layout3.addWidget(QLabel("Despachó:"))
        self.lbl_despacha_devolver = QLabel("-")
        self.lbl_despacha_devolver.setMinimumHeight(32)
        self.lbl_despacha_devolver.setMinimumWidth(100)
        self.lbl_despacha_devolver.setStyleSheet("padding:6px; background-color:#1a1a1a; border-radius:4px;")
        h_layout3.addWidget(self.lbl_despacha_devolver)
        main_layout.addLayout(h_layout3)
        main_layout.addSpacing(10)

        # Fechas
        h_layout4 = QHBoxLayout()
        h_layout4.setSpacing(12)
        h_layout4.addWidget(QLabel("Fecha de préstamo:"))
        self.lbl_fecha_prestamo = QLabel("-")
        self.lbl_fecha_prestamo.setMinimumHeight(32)
        self.lbl_fecha_prestamo.setStyleSheet("padding:6px; background-color:#1a1a1a; border-radius:4px;")
        h_layout4.addWidget(self.lbl_fecha_prestamo, 1)
        h_layout4.addSpacing(15)
        h_layout4.addWidget(QLabel("Regreso estimado:"))
        self.lbl_fecha_regreso_estimada = QLabel("-")
        self.lbl_fecha_regreso_estimada.setMinimumHeight(32)
        self.lbl_fecha_regreso_estimada.setMinimumWidth(130)
        self.lbl_fecha_regreso_estimada.setStyleSheet("padding:6px; background-color:#1a1a1a; border-radius:4px;")
        h_layout4.addWidget(self.lbl_fecha_regreso_estimada)
        main_layout.addLayout(h_layout4)
        main_layout.addSpacing(15)

        # ===== SECCIÓN 3: DEVOLUCIÓN =====
        lbl_sec3 = QLabel("Información de Devolución")
        lbl_sec3.setStyleSheet("font-size:12px; font-weight:600; color:#aaaaaa; margin-bottom:8px;")
        main_layout.addWidget(lbl_sec3)

        # Trabajador que recibe
        h_layout5 = QHBoxLayout()
        h_layout5.setSpacing(12)
        h_layout5.addWidget(QLabel("Trabajador que recibe:"))
        self.combo_trabajador_recibe = QComboBox()
        self.combo_trabajador_recibe.setMinimumHeight(36)
        h_layout5.addWidget(self.combo_trabajador_recibe, 1)
        main_layout.addLayout(h_layout5)
        main_layout.addSpacing(10)

        # Estado de devolución
        h_layout6 = QHBoxLayout()
        h_layout6.setSpacing(12)
        h_layout6.addWidget(QLabel("Estado de devolución:"))
        self.combo_estado_devolucion = QComboBox()
        self.combo_estado_devolucion.addItems(["Bueno", "Regular", "Dañado"])
        self.combo_estado_devolucion.setMinimumHeight(36)
        h_layout6.addWidget(self.combo_estado_devolucion, 1)
        main_layout.addLayout(h_layout6)
        main_layout.addSpacing(10)

        # Comentarios
        lbl_com = QLabel("Comentarios:")
        lbl_com.setStyleSheet("font-size:11px; color:#cccccc;")
        main_layout.addWidget(lbl_com)
        
        self.txt_comentarios = QTextEdit()
        self.txt_comentarios.setMinimumHeight(100)
        self.txt_comentarios.setStyleSheet("QTextEdit{padding:6px; background-color:#1a1a1a; border-radius:4px;}")
        main_layout.addWidget(self.txt_comentarios)
        main_layout.addSpacing(12)

        # Botón
        self.btn_devolver = QPushButton("Registrar Devolución")
        self.btn_devolver.setMinimumHeight(40)
        self.btn_devolver.setMaximumWidth(200)
        self.btn_devolver.setStyleSheet("""
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
        self.btn_devolver.clicked.connect(self.registrar_devolucion)
        main_layout.addWidget(self.btn_devolver)

        main_layout.addStretch()

        # Conexión
        self.combo_prestamo_devolver.currentIndexChanged.connect(self.actualizar_detalles_prestamo)

        scroll.setWidget(widget_interno)
        return scroll

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
        self.actualizar_combo_despacha()
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
        for i, p in enumerate(prestamos):
            # Obtener datos relacionados
            herramientas = store.get_herramientas()
            herramienta = herramientas.get(p.herramienta_codigo, None)
            nombre_herramienta = herramienta.descripcion if herramienta else p.herramienta_codigo
            
            trabajador = store.trabajadores.get(p.trabajador_solicita_id, None)
            nombre_trabajador = trabajador.nombre if trabajador else p.trabajador_solicita_id
            
            # Crear texto descriptivo para el combo
            display_text = f"{p.id} - {nombre_herramienta} ({nombre_trabajador})"
            
            # Agregar item al combo con el ID como userData
            self.combo_prestamo_devolver.addItem(display_text, p.id)

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

        herramientas = store.get_herramientas()
        herr = herramientas.get(prestamo.herramienta_codigo)
        herr_desc = herr.descripcion if herr else prestamo.herramienta_codigo

        trab_solicita = store.trabajadores.get(prestamo.trabajador_solicita_id)
        trab_despacha = store.trabajadores.get(prestamo.trabajador_despacha_id)
        trab_recibe = store.trabajadores.get(prestamo.trabajador_recibe_id)

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

        for i, p in enumerate(prestamos):
            row = self.table_activos.rowCount()
            self.table_activos.insertRow(row)
            
            # Obtener datos relacionados
            herramientas = store.get_herramientas()
            herramienta = herramientas.get(p.herramienta_codigo, None)
            nombre_herramienta = herramienta.descripcion if herramienta else p.herramienta_codigo
            
            trabajador_solicita = store.trabajadores.get(p.trabajador_solicita_id, None)
            nombre_solicita = trabajador_solicita.nombre if trabajador_solicita else p.trabajador_solicita_id
            
            trabajador_despacha = store.trabajadores.get(p.trabajador_despacha_id, None)
            nombre_despacha = trabajador_despacha.nombre if trabajador_despacha else p.trabajador_despacha_id
            
            # Insertar datos en el orden correcto de columnas
            self.table_activos.setItem(row, 0, QTableWidgetItem(str(p.id)))  # ID
            self.table_activos.setItem(row, 1, QTableWidgetItem(nombre_herramienta))  # Herramienta
            self.table_activos.setItem(row, 2, QTableWidgetItem(nombre_solicita))  # Solicita
            self.table_activos.setItem(row, 3, QTableWidgetItem(nombre_despacha))  # Despacha
            self.table_activos.setItem(row, 4, QTableWidgetItem(p.fecha_prestamo))  # Fecha
            self.table_activos.setItem(row, 5, QTableWidgetItem("Activo"))  # Estado

            # resaltar si está vencido
            try:
                from app.controllers.prestamo_herramienta_controller import PrestamoHerramientaController
                vencidos = [v.id for v in PrestamoHerramientaController.listar_prestamos_vencidos()]
                if p.id in vencidos:
                    # Cambiar el estado a "Vencido"
                    self.table_activos.item(row, 5).setText("Vencido")
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
            self.table_historial.setItem(row, 6, QTableWidgetItem(prestamo.fecha_regreso_estimada or "-"))
            self.table_historial.setItem(row, 7, QTableWidgetItem(prestamo.fecha_devolucion or "-"))
            self.table_historial.setItem(row, 8, QTableWidgetItem(prestamo.estado_herramienta_prestamo))

    # ========== ACCIONES ==========
    def solicitar_prestamo(self):
        """Maneja la solicitud de préstamo"""
        herramienta_codigo = self.combo_herramienta.currentData()
        trabajador_solicita_id = self.combo_trabajador_solicita.currentData()
        trabajador_despacha_id = self.combo_trabajador_despacha.currentData()
        estado = self.combo_estado_prestamo.currentText()
        fecha_regreso = self.date_regreso_estimada.dateTime().toString("yyyy-MM-dd")
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
