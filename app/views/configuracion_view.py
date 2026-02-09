from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QMessageBox, QFrame, QComboBox, QApplication, QDialog, QTableWidget, QTableWidgetItem, QHBoxLayout
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

        layout = QVBoxLayout(self)

        # ===== INFO SISTEMA =====
        info = QFrame()
        info.setFrameShape(QFrame.Box)
        info.setStyleSheet("""
            QFrame {
                border-radius: 10px;
                border: 1px solid #444;
                background-color: #1e1e1e;
                padding: 16px;
            }
        """)

        info_layout = QVBoxLayout(info)
        # asegurar márgenes y espaciado para que los elementos estén agrupados
        info_layout.setContentsMargins(16, 12, 16, 12)
        info_layout.setSpacing(6)

        lbl_titulo = QLabel("Sistema GDA")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")

        lbl_version = QLabel("Versión: Demo 2.1")
        lbl_version.setAlignment(Qt.AlignCenter)
        lbl_version.setStyleSheet("color: #ccc;")

        lbl_desc = QLabel(
            "Sistema de Gestión de Almacén\n"
            "Demo funcional sin base de datos\n"
            "Desarrollado para presentación"
        )
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setStyleSheet("color: #aaa;")

        info_layout.addWidget(lbl_titulo)
        info_layout.addWidget(lbl_version)
        info_layout.addWidget(lbl_desc)

        # ===== DERECHOS RESERVADOS =====
        footer_frame = QFrame()
        footer_frame.setFrameShape(QFrame.NoFrame)
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(4)

        lbl_footer = QLabel("Derechos reservados a TechCenter")
        lbl_footer.setAlignment(Qt.AlignCenter)
        lbl_footer.setStyleSheet("color: #777; font-size: 11px;")
        footer_layout.addWidget(lbl_footer)

        # Imagen dentro del mismo contenedor de derechos reservados
        footer_logo = QLabel()
        fpix = QPixmap("resources/techcenter-logo.png")
        if fpix.isNull():
            fpix = QPixmap("resources/techcenter.png")
        if not fpix.isNull():
            fpix = fpix.scaledToWidth(120, Qt.SmoothTransformation)
            footer_logo.setPixmap(fpix)
            footer_logo.setAlignment(Qt.AlignCenter)
            footer_layout.addWidget(footer_logo)

        info_layout.addWidget(footer_frame)



        layout.addWidget(info)

        # ===== TEMA (selector simple) =====
        lbl_selec = QLabel("Seleccionar tema:")
        lbl_selec.setStyleSheet("color: #ccc; margin-top:8px;")
        layout.addWidget(lbl_selec)

        self.cmb_tema = QComboBox()
        self.cmb_tema.addItems(["Oscuro", "Claro"])
        # establecer valor actual desde config
        cur = "Oscuro" if getattr(config, "theme", "dark") == "dark" else "Claro"
        self.cmb_tema.setCurrentText(cur)
        self.cmb_tema.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.cmb_tema)

        # ===== BOTONES =====
        btn_reset = QPushButton("Reiniciar datos de demo")
        btn_reset.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
            }
        """)

        btn_reset.clicked.connect(self.reset_demo)

        btn_trabajadores = QPushButton("Gestionar Trabajadores")
        btn_trabajadores.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
            }
        """)
        btn_trabajadores.clicked.connect(self.abrir_gestor_trabajadores)

        btn_proveedores = QPushButton("Gestionar Proveedores")
        btn_proveedores.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
            }
        """)
        btn_proveedores.clicked.connect(self.abrir_gestor_proveedores)

        layout.addWidget(btn_trabajadores)
        layout.addWidget(btn_proveedores)
        layout.addWidget(btn_reset)
        layout.addStretch()

    def reset_demo(self):
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Reiniciar todos los datos de la demo?",
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
                "Datos de la demo reiniciados"
            )

    def on_theme_changed(self, text):
        # mapa visible -> valor guardado
        theme = "dark" if text == "Oscuro" else "light"
        config.theme = theme
        try:
            config.save()
        except Exception:
            pass

        # aplicar estilo si la app está activa
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
        dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout(dialog)

        # Tabla de trabajadores
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Nombre", "Identificación"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Botones
        btn_layout = QHBoxLayout()
        btn_agregar = QPushButton("+ Agregar")
        btn_editar = QPushButton("✎ Editar")
        btn_eliminar = QPushButton("✕ Eliminar")
        btn_cerrar = QPushButton("Cerrar")

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
        dialog.setMinimumSize(700, 400)

        layout = QVBoxLayout(dialog)

        # Tabla de proveedores
        self.table_prov = QTableWidget(0, 4)
        self.table_prov.setHorizontalHeaderLabels(["Nombre Comercial", "Nombre Fiscal", "Ubicación", "Teléfono"])
        self.table_prov.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table_prov)

        # Botones
        btn_layout = QHBoxLayout()
        btn_agregar = QPushButton("+ Agregar")
        btn_editar = QPushButton("✎ Editar")
        btn_eliminar = QPushButton("✕ Eliminar")
        btn_cerrar = QPushButton("Cerrar")

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


