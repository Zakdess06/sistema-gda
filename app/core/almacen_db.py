# app/core/almacen_db.py
from app.core.database import get_connection
from app.core.store import AlmacenItem


def fetch_all_almacen():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT partida, descripcion, unidad, cantidad, ubicacion, stock_minimo, proveedor_id FROM productos")
    rows = cursor.fetchall()
    conn.close()
    items = []
    for row in rows:
        partida, descripcion, unidad, cantidad, ubicacion, stock_minimo, proveedor_id = row
        # Para proveedor, puedes hacer join o buscar luego
        items.append(AlmacenItem(
            partida=partida,
            descripcion=descripcion,
            unidad=unidad,
            cantidad=cantidad,
            ubicacion=ubicacion,
            proveedor=str(proveedor_id) if proveedor_id else "",
            stock_minimo=stock_minimo or 0
        ))
    return items

def insert_almacen_item(item: AlmacenItem):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (partida, descripcion, unidad, cantidad, ubicacion, stock_minimo, proveedor_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (item.partida, item.descripcion, item.unidad, item.cantidad, item.ubicacion, item.stock_minimo, item.proveedor)
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
    cursor.execute(
        "UPDATE productos SET descripcion=?, unidad=?, cantidad=?, ubicacion=?, stock_minimo=?, proveedor_id=? WHERE partida=?",
        (item.descripcion, item.unidad, item.cantidad, item.ubicacion, item.stock_minimo, item.proveedor, item.partida)
    )
    conn.commit()
    conn.close()

def delete_almacen_item(partida: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE partida = ?", (partida,))
    conn.commit()
    conn.close()
