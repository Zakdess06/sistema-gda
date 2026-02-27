"""Utilidades para configurar tablas con anchos apropiados"""
from PySide6.QtWidgets import QTableWidget, QHeaderView


def ajustar_ancho_tabla(table: QTableWidget, anchos: dict = None, stretch_last=True):
    """
    Ajusta los anchos de las columnas de una tabla
    
    Args:
        table: QTableWidget a ajustar
        anchos: Dict con {columna_index: ancho_px}
                Si no se proporciona, distribuye equitativamente
        stretch_last: Si True, estira la última columna (default True)
    """
    num_columnas = table.columnCount()
    
    if anchos:
        # Aplicar anchos específicos
        for col, ancho in anchos.items():
            if col < num_columnas:
                table.setColumnWidth(col, ancho)
    else:
        # Distribuir equitativamente
        ancho_por_columna = 800 // num_columnas if num_columnas > 0 else 100
        for col in range(num_columnas):
            table.setColumnWidth(col, ancho_por_columna)
    
    # Configurar header
    if stretch_last:
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(
            num_columnas - 1, 
            QHeaderView.Stretch
        )
    
    # Hacer filas con altura adecuada
    table.verticalHeader().setDefaultSectionSize(32)
    table.setMinimumHeight(300)
    
    return table
