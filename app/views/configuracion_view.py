from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QMessageBox, QFrame, QComboBox, QApplication, QDialog, 
    QTableWidget, QTableWidgetItem, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from app.core.store import store
from app.core.config import config
from app.views.trabajador_dialog import TrabajadorDialog
from app.views.proveedor_dialog import ProveedorDialog


class ConfiguracionView(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # ===== INFORMACIÓN DEL SISTEMA =====
        info_frame = QFrame()
        info_frame.setObjectName("InfoFrame")
        info_frame.setStyleSheet("""
            QFrame#InfoFrame {
                border-radius: 8px;
                border: 1px solid #30363d;
                padding: 20px;
            }
        """)
        
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)
        info_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Sistema GDA")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: 700; letter-spacing: 0.3px;")

        version = QLabel("Versión: Demo 3.4")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("font-size: 12px; opacity: 0.9;")

        description = QLabel(
            "Sistema de Gestión de Almacén\n"
            "Gestión eficiente de inventario y herramientas\n"
            "Desarrollado para pequeños y medianos almacenes"
        )
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("font-size: 13px; line-height: 1.6; opacity: 0.8;")

        info_layout.addWidget(title)
        info_layout.addWidget(version)
        info_layout.addSpacing(8)
        info_layout.addWidget(description)

        main_layout.addWidget(info_frame)

        # ===== SELECTOR DE TEMA =====
        theme_section_layout = QVBoxLayout()
        theme_section_layout.setSpacing(12)
        
        theme_label = QLabel("Seleccionar tema:")
        theme_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        theme_section_layout.addWidget(theme_label)

        self.cmb_tema = QComboBox()
        self.cmb_tema.addItems(["Oscuro", "Claro"])
        current_theme = "Oscuro" if getattr(config, "theme", "dark") == "dark" else "Claro"
        self.cmb_tema.setCurrentText(current_theme)
        self.cmb_tema.setMinimumHeight(36)
        self.cmb_tema.currentTextChanged.connect(self.on_theme_changed)
        theme_section_layout.addWidget(self.cmb_tema)
        
        main_layout.addLayout(theme_section_layout)

        # ===== SECCIÓN DE GESTIÓN =====
        management_label = QLabel("Administración del sistema:")
        management_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        main_layout.addWidget(management_label)

        # Contenedor para botones
        btn_container_layout = QVBoxLayout()
        btn_container_layout.setSpacing(10)

        btn_trabajadores = QPushButton("Gestionar Trabajadores")
        btn_trabajadores.setObjectName("ActionButton")
        btn_trabajadores.setMinimumHeight(40)
        btn_trabajadores.setCursor(Qt.PointingHandCursor)
        btn_trabajadores.clicked.connect(self.abrir_gestor_trabajadores)

        btn_proveedores = QPushButton("Gestionar Proveedores")
        btn_proveedores.setObjectName("ActionButton")
        btn_proveedores.setMinimumHeight(40)
        btn_proveedores.setCursor(Qt.PointingHandCursor)
        btn_proveedores.clicked.connect(self.abrir_gestor_proveedores)

        btn_reset = QPushButton("Reiniciar datos de demo")
        btn_reset.setObjectName("DangerButton")
        btn_reset.setMinimumHeight(40)
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.clicked.connect(self.reset_demo)

        btn_container_layout.addWidget(btn_trabajadores)
        btn_container_layout.addWidget(btn_proveedores)
        btn_container_layout.addWidget(btn_reset)
        
        main_layout.addLayout(btn_container_layout)

        # ===== ESPACIO VACÍO =====
        main_layout.addStretch()

        # ===== PIE DE PÁGINA =====
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(8)
        footer_layout.setContentsMargins(0, 20, 0, 0)

        footer_label = QLabel("© 2026 TechCenter - Todos los derechos reservados")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("font-size: 11px; opacity: 0.6;")
        footer_layout.addWidget(footer_label)

        main_layout.addLayout(footer_layout)

    def reset_demo(self):
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Reiniciar todos los datos de la demo?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            store.almacen.clear()
            store.entradas.clear()
            store.salidas.clear()
            store.herramientas.clear()

            # volver a cargar demo
            store.seed_demo()
            store.notify()

            QMessageBox.information(
                self,
                "Listo",
                "Datos de la demo reiniciados correctamente"
            )

    def on_theme_changed(self, text):
        # Extraer tema del texto (incluyendo emojis)
        theme = "dark" if "Oscuro" in text else "light"
        config.theme = theme
        try:
            config.save()
        except Exception:
            pass

        # Aplicar estilo si la app está activa
        app = QApplication.instance()
        if app:
            qss_path = "app/styles/dark.qss" if theme == "dark" else "app/styles/light.qss"
            try:
                with open(qss_path, "r", encoding="utf-8") as f:
                    app.setStyleSheet(f.read())
            except Exception:
                pass

    def abrir_gestor_trabajadores(self):
        """Abre ventana para gestionar trabajadores"""
        dialog = QDialog(self)
        dialog.setAttribute(Qt.WA_StyledBackground, True)
        dialog.setWindowTitle("Gestionar Trabajadores")
        dialog.setMinimumSize(650, 450)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Tabla de trabajadores
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Nombre", "Identificación"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_agregar = QPushButton("Agregar")
        btn_editar = QPushButton("Editar")
        btn_eliminar = QPushButton("Eliminar")
        btn_cerrar = QPushButton("Cerrar")

        btn_agregar.setObjectName("PrimaryButton")
        btn_editar.setObjectName("ActionButton")
        btn_eliminar.setObjectName("DangerButton")
        btn_cerrar.setObjectName("ActionButton")
        
        btn_agregar.setMinimumHeight(36)
        btn_editar.setMinimumHeight(36)
        btn_eliminar.setMinimumHeight(36)
        btn_cerrar.setMinimumHeight(36)

        btn_agregar.clicked.connect(lambda: self.agregar_trabajador(dialog))
        btn_editar.clicked.connect(lambda: self.editar_trabajador(dialog))
        btn_eliminar.clicked.connect(lambda: self.eliminar_trabajador(dialog))
        btn_cerrar.clicked.connect(dialog.accept)

        btn_layout.addWidget(btn_agregar)
        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_eliminar)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)

        layout.addLayout(btn_layout)

        # Cargar trabajadores
        self.cargar_trabajadores_tabla()

        dialog.exec()

    def cargar_trabajadores_tabla(self):
        """Carga los trabajadores en la tabla"""
        self.table.setRowCount(0)
        for trab in store.trabajadores.values():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(trab.nombre))
            self.table.setItem(row, 1, QTableWidgetItem(trab.numero_identificacion))

    def agregar_trabajador(self, parent_dialog):
        """Abre dialog para agregar trabajador"""
        dialog = TrabajadorDialog(parent_dialog)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_trabajadores_tabla()

    def editar_trabajador(self, parent_dialog):
        """Abre dialog para editar trabajador seleccionado"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(parent_dialog, "Error", "Seleccione un trabajador")
            return

        nombre = self.table.item(row, 0).text()
        # Encontrar el trabajador en el store
        trabajador = None
        for trab in store.trabajadores.values():
            if trab.nombre == nombre:
                trabajador = trab
                break

        if not trabajador:
            QMessageBox.warning(parent_dialog, "Error", "Trabajador no encontrado")
            return

        dialog = TrabajadorDialog(parent_dialog, trabajador)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_trabajadores_tabla()

    def eliminar_trabajador(self, parent_dialog):
        """Elimina el trabajador seleccionado"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(parent_dialog, "Error", "Seleccione un trabajador")
            return

        nombre = self.table.item(row, 0).text()
        confirm = QMessageBox.question(
            parent_dialog,
            "Confirmar eliminación",
            f"¿Eliminar al trabajador {nombre}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Encontrar y eliminar del store
            for trab_id, trab in list(store.trabajadores.items()):
                if trab.nombre == nombre:
                    del store.trabajadores[trab_id]
                    store.notify()
                    self.cargar_trabajadores_tabla()
                    return

    def abrir_gestor_proveedores(self):
        """Abre ventana para gestionar proveedores"""
        dialog = QDialog(self)
        dialog.setAttribute(Qt.WA_StyledBackground, True)
        dialog.setWindowTitle("Gestionar Proveedores")
        dialog.setMinimumSize(750, 450)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Tabla de proveedores
        self.table_prov = QTableWidget(0, 4)
        self.table_prov.setHorizontalHeaderLabels(["Nombre Comercial", "Nombre Fiscal", "Ubicación", "Teléfono"])
        self.table_prov.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_prov.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_prov.setAlternatingRowColors(True)
        layout.addWidget(self.table_prov)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_agregar = QPushButton("Agregar")
        btn_editar = QPushButton("Editar")
        btn_eliminar = QPushButton("Eliminar")
        btn_cerrar = QPushButton("Cerrar")

        btn_agregar.setObjectName("PrimaryButton")
        btn_editar.setObjectName("ActionButton")
        btn_eliminar.setObjectName("DangerButton")
        btn_cerrar.setObjectName("ActionButton")
        
        btn_agregar.setMinimumHeight(36)
        btn_editar.setMinimumHeight(36)
        btn_eliminar.setMinimumHeight(36)
        btn_cerrar.setMinimumHeight(36)

        btn_agregar.clicked.connect(lambda: self.agregar_proveedor(dialog))
        btn_editar.clicked.connect(lambda: self.editar_proveedor(dialog))
        btn_eliminar.clicked.connect(lambda: self.eliminar_proveedor(dialog))
        btn_cerrar.clicked.connect(dialog.accept)

        btn_layout.addWidget(btn_agregar)
        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_eliminar)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)

        layout.addLayout(btn_layout)

        # Cargar proveedores
        self.cargar_proveedores_tabla()

        dialog.exec()

    def cargar_proveedores_tabla(self):
        """Carga los proveedores en la tabla"""
        self.table_prov.setRowCount(0)
        for prov in store.proveedores.values():
            row = self.table_prov.rowCount()
            self.table_prov.insertRow(row)
            self.table_prov.setItem(row, 0, QTableWidgetItem(prov.nombre_comercial))
            self.table_prov.setItem(row, 1, QTableWidgetItem(prov.nombre_fiscal))
            self.table_prov.setItem(row, 2, QTableWidgetItem(prov.ubicacion))
            self.table_prov.setItem(row, 3, QTableWidgetItem(prov.telefono))

    def agregar_proveedor(self, parent_dialog):
        """Abre dialog para agregar proveedor"""
        dialog = ProveedorDialog(parent_dialog)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_proveedores_tabla()

    def editar_proveedor(self, parent_dialog):
        """Abre dialog para editar proveedor seleccionado"""
        row = self.table_prov.currentRow()
        if row < 0:
            QMessageBox.warning(parent_dialog, "Error", "Seleccione un proveedor")
            return

        nombre_comercial = self.table_prov.item(row, 0).text()
        # Encontrar el proveedor en el store
        proveedor = None
        for prov in store.proveedores.values():
            if prov.nombre_comercial == nombre_comercial:
                proveedor = prov
                break

        if not proveedor:
            QMessageBox.warning(parent_dialog, "Error", "Proveedor no encontrado")
            return

        dialog = ProveedorDialog(parent_dialog, proveedor)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_proveedores_tabla()

    def eliminar_proveedor(self, parent_dialog):
        """Elimina el proveedor seleccionado"""
        row = self.table_prov.currentRow()
        if row < 0:
            QMessageBox.warning(parent_dialog, "Error", "Seleccione un proveedor")
            return

        nombre_comercial = self.table_prov.item(row, 0).text()
        confirm = QMessageBox.question(
            parent_dialog,
            "Confirmar eliminación",
            f"¿Eliminar al proveedor {nombre_comercial}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Encontrar y eliminar del store
            for prov_id, prov in list(store.proveedores.items()):
                if prov.nombre_comercial == nombre_comercial:
                    store.delete_proveedor(prov_id)
                    self.cargar_proveedores_tabla()
                    return


