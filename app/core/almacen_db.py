# app/core/almacen_db.py
from app.core.database import get_connection, return_connection
from app.core.store import AlmacenItem
from app.core.proveedor_db import fetch_proveedor_by_id, get_or_create_proveedor
from app.core.cache import cache


def fetch_all_almacen():
    """Obtiene todos los productos CON caché y un solo JOIN, NO N+1 queries  ⚡"""
    # Intentar obtener del caché primero
    cached_result = cache.get("almacen_all")
    if cached_result is not None:
        return cached_result
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # ✅ UN SOLO QUERY con JOIN en lugar de uno por cada fila
    cursor.execute("""
        SELECT 
            p.id,
            p.partida, 
            p.descripcion, 
            p.unidad, 
            p.cantidad, 
            p.ubicacion, 
            p.stock_minimo,
            COALESCE(prov.nombre_comercial, '') as proveedor_name
        FROM productos p
        LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
    """)
    
    rows = cursor.fetchall()
    return_connection(conn)
    
    items = []
    for row in rows:
        id_, partida, descripcion, unidad, cantidad, ubicacion, stock_minimo, proveedor_name = row
        items.append(AlmacenItem(
            id=id_,
            partida=partida,
            descripcion=descripcion,
            unidad=unidad,
            cantidad=cantidad,
            ubicacion=ubicacion,
            proveedor=str(proveedor_name) if proveedor_name else "",
            stock_minimo=stock_minimo or 0
        ))
    
    # Guardar en caché por 5 minutos
    cache.set("almacen_all", items, ttl_seconds=300)
    return items

def insert_almacen_item(item: AlmacenItem):
    conn = get_connection()
    cursor = conn.cursor()
    prov_id = None
    if getattr(item, 'proveedor', None):
        prov_id = get_or_create_proveedor(item.proveedor, ubicacion=item.ubicacion or "")

    # Generar nuevo ID tipo P-XXX evitando duplicados
    cursor.execute("SELECT id FROM productos WHERE id LIKE 'P-%'")
    existing_ids = cursor.fetchall()
    max_num = 0
    for (pid,) in existing_ids:
        try:
            num = int(pid.split('-')[1])
            if num > max_num:
                max_num = num
        except Exception:
            continue
    new_id = f"P-{max_num + 1:03d}"
    cursor.execute(
        "INSERT INTO productos (id, partida, descripcion, unidad, cantidad, ubicacion, stock_minimo, proveedor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (new_id, item.partida, item.descripcion, item.unidad, item.cantidad, item.ubicacion, item.stock_minimo, prov_id)
    )
    conn.commit()
    return_connection(conn)
    # Invalidar caché
    cache.delete("almacen_all")
    return new_id

def update_almacen_cantidad(partida: str, cantidad: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET cantidad = ? WHERE partida = ?", (cantidad, partida))
    conn.commit()
    return_connection(conn)
    cache.delete("almacen_all")

def update_almacen_item(item: AlmacenItem):
    conn = get_connection()
    cursor = conn.cursor()
    prov_id = None
    if getattr(item, 'proveedor', None):
        prov_id = get_or_create_proveedor(item.proveedor, ubicacion=item.ubicacion or "")

    cursor.execute(
        "UPDATE productos SET descripcion=?, unidad=?, cantidad=?, ubicacion=?, stock_minimo=?, proveedor_id=? WHERE id=?",
        (item.descripcion, item.unidad, item.cantidad, item.ubicacion, item.stock_minimo, prov_id, item.id)
    )
    conn.commit()
    return_connection(conn)
    cache.delete("almacen_all")

def delete_almacen_item_by_id(producto_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
    conn.commit()
    return_connection(conn)
    cache.delete("almacen_all")
