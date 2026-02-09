# app/core/entradas_db.py
# Las entradas ahora se manejan directamente con la tabla productos
# Una entrada es simplemente agregar un producto al almacén

from app.core.database import get_connection
from app.core.store import Entrada
from app.core.proveedor_db import get_or_create_proveedor


def fetch_all_entradas():
    """Obtiene todas las entradas (productos) de la BD"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT partida, descripcion, cantidad, unidad, proveedor_id, ubicacion
            FROM productos
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        items = []
        for row in rows:
            partida, descripcion, cantidad, unidad, proveedor_id, ubicacion = row
            
            # Obtener nombre del proveedor
            proveedor_nombre = ""
            if proveedor_id:
                from app.core.proveedor_db import fetch_proveedor_by_id
                prov = fetch_proveedor_by_id(proveedor_id)
                if prov:
                    proveedor_nombre = prov.get('nombre_comercial', '')
            
            items.append(Entrada(
                codigo="",  # No usamos código en el novo sistema
                fecha="",   # Las entradas no tienen fecha en productos
                partida=partida,
                descripcion=descripcion,
                cantidad=cantidad,
                unidad=unidad,
                proveedor=proveedor_nombre,
                recibio="",
                ubicacion=ubicacion,
                observaciones=""
            ))
        return items
    except Exception:
        return []


def insert_entrada(entrada: Entrada):
    """Inserta una nueva entrada (crea un nuevo producto)"""
    from app.core.almacen_db import insert_almacen_item
    from app.core.store import AlmacenItem
    
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
        stock_minimo=0
    )
    
    insert_almacen_item(producto)


def delete_entrada(partida: str):
    """Elimina una entrada (elimina el producto)"""
    from app.core.almacen_db import delete_almacen_item
    delete_almacen_item(partida)


def update_entrada(entrada: Entrada):
    """Actualiza una entrada (actualiza el producto)"""
    from app.core.almacen_db import update_almacen_item
    from app.core.store import AlmacenItem
    
    # Obtener o crear proveedor
    prov_id = None
    if entrada.proveedor:
        prov_id = get_or_create_proveedor(entrada.proveedor, ubicacion=entrada.ubicacion or "")
    
    producto = AlmacenItem(
        partida=entrada.partida,
        descripcion=entrada.descripcion,
        unidad=entrada.unidad,
        cantidad=entrada.cantidad,
        ubicacion=entrada.ubicacion,
        proveedor=entrada.proveedor,
        stock_minimo=0
    )
    
    update_almacen_item(producto)

