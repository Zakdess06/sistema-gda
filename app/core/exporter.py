from openpyxl import Workbook
from openpyxl.styles import Font
from datetime import datetime
import json
import os


def export_to_excel(headers, rows, filename):
    wb = Workbook()
    ws = wb.active
    ws.title = "Datos"

    # HEADER
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)

    # DATA
    for row_i, row in enumerate(rows, start=2):
        for col_i, value in enumerate(row, start=1):
            ws.cell(row=row_i, column=col_i, value=value)

    wb.save(filename)


def export_almacen_to_json(filename):
    """Exporta todos los datos del almacén a un archivo JSON"""
    from app.core.store import store
    from app.core.entradas_db import fetch_all_entradas
    from app.core.salidas_db import fetch_all_salidas
    from app.core.prestamo_db import fetch_all_prestamos
    from app.core.trabajador_db import fetch_all_trabajadores
    from app.core.proveedor_db import fetch_all_proveedores
    from app.core.herramienta_db import fetch_all_herramientas

    data = {
        "export_date": datetime.now().isoformat(),
        "almacen": [
            {
                "id": item.id,
                "partida": item.partida,
                "descripcion": item.descripcion,
                "cantidad": item.cantidad,
                "unidad": item.unidad,
                "proveedor": item.proveedor,
                "ubicacion": item.ubicacion
            }
            for item in store.get_almacen().values()
        ],
        "entradas": [
            {
                "id": e.id,
                "fecha": e.fecha,
                "partida": e.partida,
                "descripcion": e.descripcion,
                "cantidad": e.cantidad,
                "unidad": e.unidad,
                "proveedor": e.proveedor,
                "recibio": e.recibio,
                "ubicacion": e.ubicacion,
                "observaciones": e.observaciones
            }
            for e in fetch_all_entradas()
        ],
        "salidas": [
            {
                "id": s.id,
                "fecha": s.fecha,
                "partida": s.partida,
                "descripcion": s.descripcion,
                "cantidad": s.cantidad,
                "unidad": s.unidad,
                "trabajador_id": s.trabajador_id,
                "trabajador_nombre": s.trabajador_nombre,
                "proyecto": s.proyecto,
                "destino": s.destino,
                "entrego": s.entrego,
                "observaciones": s.observaciones
            }
            for s in fetch_all_salidas()
        ],
        "prestamos": [
            {
                "id": p.id,
                "herramienta_codigo": p.herramienta_codigo,
                "herramienta_descripcion": p.herramienta_descripcion,
                "trabajador_id": p.trabajador_id,
                "trabajador_nombre": p.trabajador_nombre,
                "fecha_prestamo": p.fecha_prestamo,
                "fecha_regreso_estimada": p.fecha_regreso_estimada,
                "fecha_devolucion": p.fecha_devolucion,
                "estado_herramienta_prestamo": p.estado_herramienta_prestamo,
                "estado_devolucion": p.estado_devolucion,
                "comentarios": p.comentarios
            }
            for p in fetch_all_prestamos()
        ],
        "trabajadores": fetch_all_trabajadores(),
        "proveedores": fetch_all_proveedores(),
        "herramientas": [
            {
                "id": h.id,
                "partida": h.partida,
                "descripcion": h.descripcion,
                "estado": h.estado,
                "ubicacion": h.ubicacion
            }
            for h in fetch_all_herramientas()
        ]
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
