from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QMessageBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QDialog
)

from app.core.store import store, Herramienta
from app.core.bitacora import bitacora
from app.core.event_manager import event_manager
from app.views.herramienta_dialog import HerramientaDialog
from app.utils.table_utils import ajustar_ancho_tabla


class HerramientasView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ===== BOTONES =====
        btns = QHBoxLayout()

        self.btn_add = QPushButton("+ Agregar Herramienta")
        self.btn_add.setMinimumHeight(40)
        self.btn_add.setStyleSheet("""
            QPushButton {
                min-height: 40px;
                min-width: 100px;
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
        
        self.btn_edit = QPushButton("✎ Editar Seleccionado")
        self.btn_edit.setMinimumHeight(40)
        self.btn_edit.setStyleSheet("""
            QPushButton {
                min-height: 40px;
                min-width: 100px;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                background-color: #161d26;
                color: #f0f4f8;
                border: 1px solid #1f2937;
            }
            QPushButton:hover {
                background-color: #1f2937;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #0f1419;
            }
        """)
        
        self.btn_delete = QPushButton("✕ Eliminar Seleccionado")
        self.btn_delete.setMinimumHeight(40)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                min-height: 40px;
                min-width: 100px;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                background-color: #dc2626;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #ef4444;
            }
            QPushButton:pressed {
                background-color: #991b1b;
            }
        """)

        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_delete)
        btns.addStretch()

        layout.addLayout(btns)

        # ===== TABLA =====
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Código", "Descripción", "Ubicación", "Cantidad", "Observaciones"
        ])
        ajustar_ancho_tabla(self.table, anchos={
            0: 100,   # ID (Código)
            1: 100,   # Código
            2: 280,   # Descripción
            3: 150,   # Ubicación
            4: 80,    # Cantidad
            5: 200    # Observaciones (se estira)
        })
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # ===== CONEXIONES =====
        self.btn_add.clicked.connect(self.agregar)
        self.btn_edit.clicked.connect(self.editar)
        self.btn_delete.clicked.connect(self.eliminar)

        store.subscribe(self.load_data)
        event_manager.herramienta_changed.connect(self.load_data)
        self.load_data()

    def show_warning(self, title, text):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowModality(Qt.ApplicationModal)
        msg.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        msg.exec()


    # ---------- DATA ----------
    def load_data(self):
        self.table.setRowCount(0)
        herramientas = store.get_herramientas()
        for h in herramientas.values():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(h.codigo))  # ID = código
            self.table.setItem(row, 1, QTableWidgetItem(h.codigo))
            self.table.setItem(row, 2, QTableWidgetItem(h.descripcion))
            self.table.setItem(row, 3, QTableWidgetItem(h.ubicacion))
            self.table.setItem(row, 4, QTableWidgetItem(str(h.cantidad)))
            self.table.setItem(row, 5, QTableWidgetItem(getattr(h, 'observaciones', '')))

    def selected_codigo(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        return self.table.item(row, 1).text()

    # ---------- ACCIONES ----------
    def agregar(self):
        dialog = HerramientaDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()

    def editar(self):
        codigo = self.selected_codigo()
        if not codigo:
            QMessageBox.warning(self, "Error", "Seleccione una herramienta")
            return
        herramientas = store.get_herramientas()
        herramienta = herramientas.get(codigo)
        if not herramienta:
            self.show_warning("Error", "Herramienta no encontrada")
            return
        
        dialog = HerramientaDialog(self, herramienta)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()

    def eliminar(self):
        codigo = self.selected_codigo()
        if not codigo:
            QMessageBox.warning(self, "Error", "Seleccione una herramienta")
            return
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar la herramienta {codigo}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            store.delete_herramienta(codigo)
            bitacora.log("Herramienta", f"Herramienta eliminada: {codigo}")
            self.load_data()


