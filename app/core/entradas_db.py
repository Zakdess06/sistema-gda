# app/core/entradas_db.py
# Las entradas ahora se manejan directamente con la tabla productos
# Una entrada es simplemente agregar un producto al almacén

from app.core.database import get_connection, return_connection
from app.core.store import Entrada
from app.core.proveedor_db import get_or_create_proveedor


def fetch_all_entradas():
    """Obtiene todas las entradas auditadas (con fechas reales)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha, partida, descripcion, cantidad, unidad, proveedor, recibio, ubicacion, observaciones
            FROM entradas_auditoria
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        return_connection(conn)
        
        items = []
        for row in rows:
            try:
                fecha, partida, descripcion, cantidad, unidad, proveedor, recibio, ubicacion, observaciones = row
                # Validar y convertir valores a strings válidos, evitando None
                items.append(Entrada(
                    codigo="",
                    fecha=str(fecha) if fecha else "",
                    partida=str(partida) if partida else "",
                    descripcion=str(descripcion) if descripcion else "",
                    cantidad=int(cantidad) if cantidad else 0,
                    unidad=str(unidad) if unidad else "",
                    proveedor=str(proveedor) if proveedor else "",
                    recibio=str(recibio) if recibio else "",
                    ubicacion=str(ubicacion) if ubicacion else "",
                    observaciones=str(observaciones) if observaciones else ""
                ))
            except Exception:
                continue
        return items
    except Exception:
        return []


def insert_entrada(entrada: Entrada):
    """Inserta una nueva entrada en la auditoría y actualiza almacén"""
    from app.core.almacen_db import insert_almacen_item
    from app.core.store import AlmacenItem
    from datetime import datetime
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Grabar en tabla de auditoría con fecha actual
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    cursor.execute("""
        INSERT INTO entradas_auditoria 
        (fecha, partida, descripcion, cantidad, unidad, proveedor, recibio, ubicacion, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        fecha_actual,
        entrada.partida,
        entrada.descripcion,
        entrada.cantidad,
        entrada.unidad,
        entrada.proveedor,
        entrada.recibio,
        entrada.ubicacion,
        entrada.observaciones
    ))
    
    conn.commit()
    return_connection(conn)
    
    # También actualizar almacén (producto)
    # Obtener o crear proveedor
    prov_id = None
    if entrada.proveedor:
        prov_id = get_or_create_proveedor(entrada.proveedor, ubicacion=entrada.ubicacion or "")
    
    # Crear producto
    producto = AlmacenItem(
        partida=entrada.partida,
        descripcion=entrada.descripcion,
        unidad=entrada.unidad,
        cantidad=entrada.cantidad,
        ubicacion=entrada.ubicacion,
        proveedor=entrada.proveedor,
        stock_minimo=entrada.stock_minimo
    )
    
    insert_almacen_item(producto)


def delete_entrada(partida: str):
    """Elimina una entrada (elimina el producto)"""
    from app.core.almacen_db import delete_almacen_item_by_id
    # Obtener el ID del producto primero
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM productos WHERE partida = ?", (partida,))
    result = cursor.fetchone()
    return_connection(conn)
    if result:
        producto_id = result[0]
        delete_almacen_item_by_id(producto_id)


def update_entrada(entrada: Entrada):
    """Actualiza una entrada (registra en auditoría)"""
    from app.core.almacen_db import update_almacen_item
    from app.core.store import AlmacenItem
    from datetime import datetime
    
    # También registrar en auditoría
    insert_entrada(entrada)
    
    # Actualizar producto en almacén
    producto = AlmacenItem(
        partida=entrada.partida,
        descripcion=entrada.descripcion,
        unidad=entrada.unidad,
        cantidad=entrada.cantidad,
        ubicacion=entrada.ubicacion,
        proveedor=entrada.proveedor,
        stock_minimo=entrada.stock_minimo
    )
    
    update_almacen_item(producto)

