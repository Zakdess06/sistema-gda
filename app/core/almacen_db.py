# app/core/almacen_db.py
from app.core.database import get_connection
from app.core.store import AlmacenItem
from app.core.proveedor_db import fetch_proveedor_by_id, get_or_create_proveedor


def fetch_all_almacen():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT partida, descripcion, unidad, cantidad, ubicacion, stock_minimo, proveedor_id FROM productos")
    rows = cursor.fetchall()
    conn.close()
    items = []
    for row in rows:
        partida, descripcion, unidad, cantidad, ubicacion, stock_minimo, proveedor_id = row
        proveedor_name = ""
        if proveedor_id:
            prov = fetch_proveedor_by_id(proveedor_id)
            if prov:
                proveedor_name = prov.get('nombre_comercial', '')

        items.append(AlmacenItem(
            partida=partida,
            descripcion=descripcion,
            unidad=unidad,
            cantidad=cantidad,
            ubicacion=ubicacion,
            proveedor=str(proveedor_name) if proveedor_name else "",
            stock_minimo=stock_minimo or 0
        ))
    return items

def insert_almacen_item(item: AlmacenItem):
    conn = get_connection()
    cursor = conn.cursor()
    prov_id = None
    if getattr(item, 'proveedor', None):
        # crear o recuperar proveedor por nombre
        prov_id = get_or_create_proveedor(item.proveedor, ubicacion=item.ubicacion or "")

    cursor.execute(
        "INSERT INTO productos (partida, descripcion, unidad, cantidad, ubicacion, stock_minimo, proveedor_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (item.partida, item.descripcion, item.unidad, item.cantidad, item.ubicacion, item.stock_minimo, prov_id)
    )
    conn.commit()
    conn.close()

def update_almacen_cantidad(partida: str, cantidad: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET cantidad = ? WHERE partida = ?", (cantidad, partida))
    conn.commit()
    conn.close()

def update_almacen_item(item: AlmacenItem):
    conn = get_connection()
    cursor = conn.cursor()
    prov_id = None
    if getattr(item, 'proveedor', None):
        prov_id = get_or_create_proveedor(item.proveedor, ubicacion=item.ubicacion or "")

    cursor.execute(
        "UPDATE productos SET descripcion=?, unidad=?, cantidad=?, ubicacion=?, stock_minimo=?, proveedor_id=? WHERE partida=?",
        (item.descripcion, item.unidad, item.cantidad, item.ubicacion, item.stock_minimo, prov_id, item.partida)
    )
    conn.commit()
    conn.close()

def delete_almacen_item(partida: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE partida = ?", (partida,))
    conn.commit()
    conn.close()
