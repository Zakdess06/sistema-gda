# app/views/prestamo_herramienta_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
    QComboBox, QLabel, QTextEdit, QSpinBox, QDateTimeEdit
)
from PySide6.QtCore import Qt, QDateTime, QTimer
from datetime import datetime

from app.core.store import store
from app.core.event_manager import event_manager
from app.controllers.prestamo_herramienta_controller import PrestamoHerramientaController
from app.core.bitacora import bitacora


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
        layout = QVBoxLayout(widget)

        # Seleccionar herramienta
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(QLabel("Herramienta:"))
        self.combo_herramienta = QComboBox()
        h_layout1.addWidget(self.combo_herramienta)
        h_layout1.addStretch()
        layout.addLayout(h_layout1)

        # Detalles de la herramienta
        h_layout_detalles = QHBoxLayout()
        h_layout_detalles.addWidget(QLabel("Ubicación:"))
        self.lbl_ubicacion = QLabel("-")
        h_layout_detalles.addWidget(self.lbl_ubicacion)
        h_layout_detalles.addWidget(QLabel("Cantidad disponible:"))
        self.lbl_cantidad = QLabel("0")
        h_layout_detalles.addWidget(self.lbl_cantidad)
        h_layout_detalles.addStretch()
        layout.addLayout(h_layout_detalles)

        # Trabajador que solicita
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(QLabel("Trabajador que solicita:"))
        self.combo_trabajador_solicita = QComboBox()
        h_layout2.addWidget(self.combo_trabajador_solicita)
        h_layout2.addStretch()
        layout.addLayout(h_layout2)

        # Trabajador que despacha
        h_layout3 = QHBoxLayout()
        h_layout3.addWidget(QLabel("Trabajador que despacha:"))
        self.combo_trabajador_despacha = QComboBox()
        h_layout3.addWidget(self.combo_trabajador_despacha)
        h_layout3.addStretch()
        layout.addLayout(h_layout3)

        # Estado de la herramienta
        h_layout4 = QHBoxLayout()
        h_layout4.addWidget(QLabel("Estado de la herramienta:"))
        self.combo_estado_prestamo = QComboBox()
        self.combo_estado_prestamo.addItems(["Bueno", "Regular", "Dañado"])
        h_layout4.addWidget(self.combo_estado_prestamo)
        h_layout4.addStretch()
        layout.addLayout(h_layout4)

        # Fecha de regreso estimada
        h_layout5 = QHBoxLayout()
        h_layout5.addWidget(QLabel("Fecha de regreso estimada:"))
        self.date_regreso_estimada = QDateTimeEdit()
        self.date_regreso_estimada.setDateTime(QDateTime.currentDateTime())
        self.date_regreso_estimada.setDisplayFormat("yyyy-MM-dd HH:mm")
        h_layout5.addWidget(self.date_regreso_estimada)
        h_layout5.addStretch()
        layout.addLayout(h_layout5)

        # Cantidad a prestar
        h_layout6 = QHBoxLayout()
        h_layout6.addWidget(QLabel("Cantidad a prestar:"))
        self.spin_cantidad_prestamo = QSpinBox()
        self.spin_cantidad_prestamo.setRange(1, 999999)
        self.spin_cantidad_prestamo.setValue(1)
        h_layout6.addWidget(self.spin_cantidad_prestamo)
        h_layout6.addStretch()
        layout.addLayout(h_layout6)

        # Botones
        h_layout_btn = QHBoxLayout()
        self.btn_solicitar = QPushButton("Crear Préstamo")
        self.btn_solicitar.clicked.connect(self.solicitar_prestamo)
        h_layout_btn.addWidget(self.btn_solicitar)
        h_layout_btn.addStretch()
        layout.addLayout(h_layout_btn)

        # Tabla de préstamos activos
        layout.addWidget(QLabel("Préstamos activos:"))
        self.table_activos = QTableWidget(0, 6)
        self.table_activos.setHorizontalHeaderLabels([
            "ID", "Herramienta", "Solicita", "Despacha", "Fecha", "Estado"
        ])
        self.table_activos.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table_activos)

        # Conectar cambios en combobox
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
        h_layout1.addWidget(self.combo_prestamo_devolver)
        h_layout1.addStretch()
        layout.addLayout(h_layout1)

        # Detalles del préstamo
        detalles_layout = QVBoxLayout()
        
        h_det1 = QHBoxLayout()
        h_det1.addWidget(QLabel("Herramienta:"))
        self.lbl_herr_devolver = QLabel("-")
        h_det1.addWidget(self.lbl_herr_devolver)
        h_det1.addWidget(QLabel("Estado al prestar:"))
        self.lbl_estado_prestamo = QLabel("-")
        h_det1.addWidget(self.lbl_estado_prestamo)
        h_det1.addStretch()
        detalles_layout.addLayout(h_det1)

        h_det2 = QHBoxLayout()
        h_det2.addWidget(QLabel("Solicitó:"))
        self.lbl_solicita_devolver = QLabel("-")
        h_det2.addWidget(self.lbl_solicita_devolver)
        h_det2.addWidget(QLabel("Despachó:"))
        self.lbl_despacha_devolver = QLabel("-")
        h_det2.addWidget(self.lbl_despacha_devolver)
        h_det2.addStretch()
        detalles_layout.addLayout(h_det2)

        h_det3 = QHBoxLayout()
        h_det3.addWidget(QLabel("Fecha de préstamo:"))
        self.lbl_fecha_prestamo = QLabel("-")
        h_det3.addWidget(self.lbl_fecha_prestamo)
        h_det3.addWidget(QLabel("Fecha de regreso estimada:"))
        self.lbl_fecha_regreso_estimada = QLabel("-")
        h_det3.addWidget(self.lbl_fecha_regreso_estimada)
        h_det3.addStretch()
        detalles_layout.addLayout(h_det3)

        layout.addLayout(detalles_layout)
        layout.addWidget(QLabel("_" * 80))

        # Trabajador que recibe
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(QLabel("Trabajador que recibe:"))
        self.combo_trabajador_recibe = QComboBox()
        h_layout2.addWidget(self.combo_trabajador_recibe)
        h_layout2.addStretch()
        layout.addLayout(h_layout2)

        # Estado de devolución
        h_layout3 = QHBoxLayout()
        h_layout3.addWidget(QLabel("Estado de devolución:"))
        self.combo_estado_devolucion = QComboBox()
        self.combo_estado_devolucion.addItems(["Bueno", "Regular", "Dañado"])
        h_layout3.addWidget(self.combo_estado_devolucion)
        h_layout3.addStretch()
        layout.addLayout(h_layout3)

        # Comentarios
        layout.addWidget(QLabel("Comentarios:"))
        self.txt_comentarios = QTextEdit()
        self.txt_comentarios.setMaximumHeight(100)
        layout.addWidget(self.txt_comentarios)

        # Botones
        h_layout_btn = QHBoxLayout()
        self.btn_devolver = QPushButton("Registrar Devolución")
        self.btn_devolver.clicked.connect(self.registrar_devolucion)
        h_layout_btn.addWidget(self.btn_devolver)
        h_layout_btn.addStretch()
        layout.addLayout(h_layout_btn)

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
        self.table_historial = QTableWidget(0, 10)
        self.table_historial.setHorizontalHeaderLabels([
            "ID", "Herramienta", "Solicita", "Despacha", "Recibe",
            "Fecha Préstamo", "Fecha Regreso Est.", "Fecha Devolución", "Estado Préstamo", "Estado Devolución"
        ])
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
            self.table_historial.setItem(row, 8, QTableWidgetItem(prestamo.estado_herramienta_devolucion or "-"))

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
