from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QMessageBox, QFrame, QComboBox, QApplication, QDialog, 
    QTableWidget, QTableWidgetItem, QHBoxLayout, QSpacerItem, QSizePolicy,
    QListWidget, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from app.core.store import store
from app.core.config import config
from app.core.event_manager import event_manager
from app.core.cache import cache
from app.views.trabajador_dialog import TrabajadorDialog
from app.views.proveedor_dialog import ProveedorDialog
from app.utils.table_utils import ajustar_ancho_tabla
from app.core.trabajador_db import delete_trabajador, fetch_all_trabajadores
from app.models.trabajador import Trabajador


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

        version = QLabel("Release 1.0")
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

        btn_backup = QPushButton("Respaldos del sistema")
        btn_backup.setObjectName("ActionButton")
        btn_backup.setMinimumHeight(40)
        btn_backup.setCursor(Qt.PointingHandCursor)
        btn_backup.clicked.connect(self.abrir_administrar_respaldo)

        btn_clean_cache = QPushButton("Limpiar Caché")
        btn_clean_cache.setObjectName("ActionButton")
        btn_clean_cache.setMinimumHeight(40)
        btn_clean_cache.setCursor(Qt.PointingHandCursor)
        btn_clean_cache.clicked.connect(self.limpiar_cache)

        btn_container_layout.addWidget(btn_trabajadores)
        btn_container_layout.addWidget(btn_proveedores)
        btn_container_layout.addWidget(btn_backup)
        btn_container_layout.addWidget(btn_clean_cache)
        
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

    def crear_respaldo(self):
        """Crea un respaldo del archivo de base de datos"""
        import os
        import shutil
        from datetime import datetime
        from app.core.database import DB_PATH
        
        try:
            # Crear carpeta de respaldos si no existe
            backup_dir = os.path.join(str(DB_PATH).replace("database.db", ""), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generar nombre del respaldo con timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_filename = f"database_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Copiar el archivo
            if os.path.exists(DB_PATH):
                shutil.copy2(DB_PATH, backup_path)
                
                QMessageBox.information(
                    self,
                    "Respaldo completado",
                    f"Respaldo creado exitosamente\n\nArchivo: {backup_filename}\nUbicación: backups/"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Advertencia",
                    "La base de datos no existe aún"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al crear respaldo: {str(e)}"
            )

    def abrir_administrar_respaldo(self):
        """Muestra un diálogo con lista de respaldos y opciones"""
        import os
        import shutil
        from app.core.database import DB_PATH
        from datetime import datetime
        
        dialog = QDialog(self)
        dialog.setAttribute(Qt.WA_StyledBackground, True)
        dialog.setWindowTitle("Respaldos del sistema")
        dialog.setMinimumSize(550, 400)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # etiqueta que muestra información del respaldo/carga actual
        current_label = QLabel()
        current_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        layout.addWidget(current_label)

        list_widget = QListWidget()
        layout.addWidget(list_widget)

        def refresh_list():
            list_widget.clear()
            backup_dir = os.path.join(str(DB_PATH).replace("database.db", ""), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            # agregar archivos .db ordenados por nombre inverso (más recientes primero)
            for fname in sorted(os.listdir(backup_dir), reverse=True):
                if fname.endswith(".db"):
                    list_widget.addItem(fname)

        def update_current_label():
            if os.path.exists(DB_PATH):
                mtime = datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime("%Y-%m-%d %H:%M:%S")
                current_label.setText(f"Base de datos activa (últ mod): {mtime}")
            else:
                current_label.setText("Base de datos activa: no existe")

        refresh_list()
        update_current_label()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_crear = QPushButton("Crear respaldo")
        btn_restaurar = QPushButton("Restaurar")
        btn_descargar = QPushButton("Descargar")
        btn_eliminar = QPushButton("Eliminar")
        btn_cerrar = QPushButton("Cerrar")

        btn_crear.setObjectName("PrimaryButton")
        btn_restaurar.setObjectName("ActionButton")
        btn_descargar.setObjectName("ActionButton")
        btn_eliminar.setObjectName("DangerButton")
        btn_cerrar.setObjectName("ActionButton")

        for btn in (btn_crear, btn_restaurar, btn_descargar, btn_eliminar, btn_cerrar):
            btn.setMinimumHeight(36)

        btn_layout.addWidget(btn_crear)
        btn_layout.addWidget(btn_restaurar)
        btn_layout.addWidget(btn_descargar)
        btn_layout.addWidget(btn_eliminar)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)

        layout.addLayout(btn_layout)

        def hacer_crear():
            self.crear_respaldo()
            refresh_list()

        def hacer_restaurar():
            item = list_widget.currentItem()
            if not item:
                QMessageBox.warning(dialog, "Error", "Seleccione un respaldo")
                return
            reply = QMessageBox.question(
                dialog,
                "Confirmar restauración",
                "Se sobrescribirá la base de datos actual. ¿Desea continuar?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                backup_dir = os.path.join(str(DB_PATH).replace("database.db", ""), "backups")
                src = os.path.join(backup_dir, item.text())
                try:
                    shutil.copy2(src, DB_PATH)
                    QMessageBox.information(
                        dialog,
                        "Restaurado",
                        "Respaldo restaurado correctamente. Reinicie la aplicación si es necesario."
                    )
                    update_current_label()
                except Exception as e:
                    QMessageBox.critical(dialog, "Error", f"Error al restaurar: {str(e)}")

        def hacer_descargar():
            item = list_widget.currentItem()
            if not item:
                QMessageBox.warning(dialog, "Error", "Seleccione un respaldo")
                return
            backup_dir = os.path.join(str(DB_PATH).replace("database.db", ""), "backups")
            src = os.path.join(backup_dir, item.text())
            dest, _ = QFileDialog.getSaveFileName(
                dialog,
                "Guardar respaldo como",
                item.text(),
                "Base de datos (*.db)"
            )
            if dest:
                try:
                    shutil.copy2(src, dest)
                    QMessageBox.information(
                        dialog,
                        "Descargado",
                        f"Respaldo guardado en:\n{dest}"
                    )
                except Exception as e:
                    QMessageBox.critical(dialog, "Error", f"Error al descargar: {str(e)}")

        def hacer_eliminar():
            item = list_widget.currentItem()
            if not item:
                QMessageBox.warning(dialog, "Error", "Seleccione un respaldo para eliminar")
                return
            reply = QMessageBox.question(
                dialog,
                "Confirmar eliminacion",
                f"¿Desea eliminar el respaldo '{item.text()}'?\n\nEsta acción no se puede deshacer.",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                backup_dir = os.path.join(str(DB_PATH).replace("database.db", ""), "backups")
                backup_path = os.path.join(backup_dir, item.text())
                try:
                    os.remove(backup_path)
                    QMessageBox.information(
                        dialog,
                        "Eliminado",
                        "Respaldo eliminado correctamente."
                    )
                    refresh_list()
                except Exception as e:
                    QMessageBox.critical(dialog, "Error", f"Error al eliminar: {str(e)}")

        btn_crear.clicked.connect(hacer_crear)
        btn_restaurar.clicked.connect(hacer_restaurar)
        btn_descargar.clicked.connect(hacer_descargar)
        btn_eliminar.clicked.connect(hacer_eliminar)
        btn_cerrar.clicked.connect(dialog.accept)

        dialog.exec()

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
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Identificación"])
        ajustar_ancho_tabla(self.table, anchos={0: 120, 1: 320, 2: 200})
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
        
        # Conectar evento para recargar en tiempo real
        event_manager.trabajador_changed.connect(self.cargar_trabajadores_tabla)

        dialog.exec()

    def cargar_trabajadores_tabla(self):
        """Carga los trabajadores en la tabla"""
        self.table.setRowCount(0)
        for t in store.trabajadores.values():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(t.id)))  # ID
            self.table.setItem(row, 1, QTableWidgetItem(t.nombre))
            self.table.setItem(row, 2, QTableWidgetItem(t.numero_identificacion))

    def agregar_trabajador(self, parent_dialog):
        """Abre dialog para agregar trabajador"""
        from app.core.trabajador_db import fetch_all_trabajadores
        dialog = TrabajadorDialog(parent_dialog)
        if dialog.exec() == QDialog.Accepted:
            # Recargar trabajadores desde la base de datos
            store.trabajadores.clear()
            for t in fetch_all_trabajadores():
                store.trabajadores[t['id']] = Trabajador(id=t['id'], nombre=t['nombre'], numero_identificacion=t['identificacion'])
            self.cargar_trabajadores_tabla()

    def editar_trabajador(self, parent_dialog):
        """Abre dialog para editar trabajador seleccionado"""
        from app.core.trabajador_db import fetch_all_trabajadores
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(parent_dialog, "Error", "Seleccione un trabajador")
            return

        # Obtener el ID del trabajador desde la columna 0
        id_trabajador = self.table.item(row, 0).text()
        # Encontrar el trabajador en el store
        trabajador = store.trabajadores.get(id_trabajador)

        if not trabajador:
            QMessageBox.warning(parent_dialog, "Error", "Trabajador no encontrado")
            return

        dialog = TrabajadorDialog(parent_dialog, trabajador)
        if dialog.exec() == QDialog.Accepted:
            # Recargar trabajadores desde la base de datos
            store.trabajadores.clear()
            for t in fetch_all_trabajadores():
                store.trabajadores[t['id']] = Trabajador(id=t['id'], nombre=t['nombre'], numero_identificacion=t['identificacion'])
            self.cargar_trabajadores_tabla()

    def eliminar_trabajador(self, parent_dialog):
        """Elimina el trabajador seleccionado"""
        from app.core.trabajador_db import delete_trabajador, fetch_all_trabajadores
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(parent_dialog, "Error", "Seleccione un trabajador")
            return

        nombre = self.table.item(row, 0).text()
        identificacion = self.table.item(row, 1).text()
        confirm = QMessageBox.question(
            parent_dialog,
            "Confirmar eliminación",
            f"¿Eliminar al trabajador {nombre}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Buscar el trabajador por identificación
            trabajador_id = None
            for trab_id, trab in list(store.trabajadores.items()):
                if trab.numero_identificacion == identificacion:
                    trabajador_id = trab_id
                    break
            if trabajador_id:
                # Eliminar de la base de datos
                delete_trabajador(identificacion)
                # Eliminar del store
                del store.trabajadores[trabajador_id]
                # Recargar trabajadores desde la base de datos
                store.trabajadores.clear()
                for t in fetch_all_trabajadores():
                    store.trabajadores[t['id']] = Trabajador(id=t['id'], nombre=t['nombre'], numero_identificacion=t['identificacion'])
                store.notify()
                self.cargar_trabajadores_tabla()
            else:
                QMessageBox.warning(parent_dialog, "Error", "Trabajador no encontrado")

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
        self.table_prov = QTableWidget(0, 5)
        self.table_prov.setHorizontalHeaderLabels(["ID", "Nombre Comercial", "Nombre Fiscal", "Ubicación", "Teléfono"])
        ajustar_ancho_tabla(self.table_prov, anchos={0: 80, 1: 260, 2: 240, 3: 220, 4: 140})
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
        """Carga los proveedores en la tabla desde la base de datos"""
        from app.core.proveedor_db import fetch_all_proveedores
        self.table_prov.setRowCount(0)
        proveedores_lista = fetch_all_proveedores()
        for prov in proveedores_lista:
            row = self.table_prov.rowCount()
            self.table_prov.insertRow(row)
            self.table_prov.setItem(row, 0, QTableWidgetItem(str(prov['id'])))  # ID
            self.table_prov.setItem(row, 1, QTableWidgetItem(prov['nombre_comercial']))
            self.table_prov.setItem(row, 2, QTableWidgetItem(prov['nombre_fiscal']))
            self.table_prov.setItem(row, 3, QTableWidgetItem(prov['ubicacion']))
            self.table_prov.setItem(row, 4, QTableWidgetItem(prov['telefono']))

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

        prov_id = self.table_prov.item(row, 0).text()
        proveedor = store.proveedores.get(prov_id)
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

        prov_id = self.table_prov.item(row, 0).text()
        confirm = QMessageBox.question(
            parent_dialog,
            "Confirmar eliminación",
            f"¿Eliminar al proveedor con ID {prov_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            if prov_id in store.proveedores:
                store.delete_proveedor(prov_id)
                self.cargar_proveedores_tabla()

    def limpiar_cache(self):
        """Limpia las entradas expiradas del caché para mejorar el rendimiento"""
        stats = cache.get_stats()
        
        if stats['total_entries'] == 0:
            QMessageBox.information(
                self,
                "Caché Limpio",
                "El caché está vacío. No hay nada que limpiar."
            )
            return
        
        reply = QMessageBox.question(
            self,
            "Limpiar Caché",
            f"Esto eliminará las entradas expiradas del caché para mejorar el rendimiento.\n\n"
            f"Entradas expiradas: {stats['expired_entries']}\n"
            f"Total de entradas: {stats['total_entries']}\n\n"
            f"No se eliminarán datos del sistema.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            cleaned = cache.cleanup_expired()
            QMessageBox.information(
                self,
                "Caché Limpio",
                f"Se limpiaron {cleaned} entradas expiradas del caché.\n"
                f"El rendimiento del sistema ha mejorado."
            )


