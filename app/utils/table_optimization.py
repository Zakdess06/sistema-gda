"""Utilidades para recarga eficiente de tablas sin parpadeo"""
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from typing import List, Dict, Any
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class TableUpdater:
    """Actualiza tablas de forma eficiente sin limpiar/recargar todo"""
    
    @staticmethod
    def update_specific_row(table: QTableWidget, row_index: int, data: List[Any]):
        """Actualiza una fila específica sin afectar las demás"""
        if row_index >= table.rowCount():
            return
        
        for col_index, value in enumerate(data):
            if col_index < table.columnCount():
                item = QTableWidgetItem(str(value))
                table.setItem(row_index, col_index, item)
    
    @staticmethod
    def add_rows(table: QTableWidget, rows_data: List[List[Any]]):
        """Agrega filas nuevas sin borrar las existentes"""
        for row_data in rows_data:
            row = table.rowCount()
            table.insertRow(row)
            for col_index, value in enumerate(row_data):
                if col_index < table.columnCount():
                    item = QTableWidgetItem(str(value))
                    table.setItem(row, col_index, item)
    
    @staticmethod
    def remove_rows_by_filter(table: QTableWidget, column: int, value: str):
        """Elimina filas que coincidan con un valor en una columna específica"""
        rows_to_delete = []
        for row in range(table.rowCount()):
            item = table.item(row, column)
            if item and item.text() == value:
                rows_to_delete.append(row)
        
        # Eliminar de atrás para adelante para no perder índices
        for row in reversed(rows_to_delete):
            table.removeRow(row)
    
    @staticmethod
    def highlight_row(table: QTableWidget, row: int, color: QColor = None):
        """Resalta una fila con un color (para mostrar cambios)"""
        if color is None:
            color = QColor(100, 200, 100)  # Verde claro
        
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                item.setBackground(color)
    
    @staticmethod
    def clear_highlight(table: QTableWidget, row: int):
        """Quita el resaltado de una fila"""
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                item.setBackground(Qt.transparent)
    
    @staticmethod
    def get_row_data(table: QTableWidget, row: int) -> List[str]:
        """Obtiene los datos de una fila completa"""
        row_data = []
        for col in range(table.columnCount()):
            item = table.item(row, col)
            row_data.append(item.text() if item else "")
        return row_data
    
    @staticmethod
    def find_row_by_column(table: QTableWidget, column: int, value: str) -> int:
        """Encuentra la primera fila donde una columna tiene un valor específico"""
        for row in range(table.rowCount()):
            item = table.item(row, column)
            if item and item.text() == value:
                return row
        return -1


class PaginatedTable:
    """Maneja tabla con paginación para optimizar UI con muchos datos"""
    
    def __init__(self, table: QTableWidget, rows_per_page: int = 50):
        self.table = table
        self.rows_per_page = rows_per_page
        self.all_data: List[List[Any]] = []
        self.current_page = 0
        self.total_pages = 0
    
    def set_data(self, all_rows: List[List[Any]]):
        """Establece todos los datos y calcula páginas"""
        self.all_data = all_rows
        self.current_page = 0
        self.total_pages = (len(all_rows) + self.rows_per_page - 1) // self.rows_per_page
        self._render_page()
    
    def _render_page(self):
        """Renderiza la página actual en la tabla"""
        self.table.setRowCount(0)
        
        start_row = self.current_page * self.rows_per_page
        end_row = min(start_row + self.rows_per_page, len(self.all_data))
        
        for page_row_idx, data_row_idx in enumerate(range(start_row, end_row)):
            row_data = self.all_data[data_row_idx]
            self.table.insertRow(page_row_idx)
            
            for col_idx, value in enumerate(row_data):
                if col_idx < self.table.columnCount():
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(page_row_idx, col_idx, item)
    
    def next_page(self) -> bool:
        """Va a la siguiente página"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._render_page()
            return True
        return False
    
    def prev_page(self) -> bool:
        """Va a la página anterior"""
        if self.current_page > 0:
            self.current_page -= 1
            self._render_page()
            return True
        return False
    
    def goto_page(self, page: int) -> bool:
        """Va a una página específica"""
        if 0 <= page < self.total_pages:
            self.current_page = page
            self._render_page()
            return True
        return False
    
    def get_page_info(self) -> Dict[str, int]:
        """Retorna info sobre la página actual"""
        return {
            'current_page': self.current_page + 1,
            'total_pages': self.total_pages,
            'total_rows': len(self.all_data),
            'rows_per_page': self.rows_per_page
        }
