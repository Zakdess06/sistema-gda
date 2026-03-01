# app/core/herramienta_db.py
from app.core.database import get_connection, return_connection
from app.core.store import Herramienta

def fetch_all_herramientas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT partida, descripcion, ubicacion, cantidad, observaciones FROM herramientas")
    rows = cursor.fetchall()
    return_connection(conn)
    items = []
    for row in rows:
        partida, descripcion, ubicacion, cantidad, observaciones = row
        items.append(Herramienta(
            codigo=partida,
            descripcion=descripcion,
            ubicacion=ubicacion,
            cantidad=cantidad,
            observaciones=observaciones
        ))
    return items

def insert_herramienta(item: Herramienta):
    conn = get_connection()
    cursor = conn.cursor()
    obs = getattr(item, 'observaciones', '')
    cursor.execute(
        "INSERT INTO herramientas (partida, descripcion, ubicacion, cantidad, observaciones) VALUES (?, ?, ?, ?, ?)",
        (item.codigo, item.descripcion, item.ubicacion, item.cantidad, obs)
    )
    conn.commit()
    return_connection(conn)

def update_herramienta(item: Herramienta):
    conn = get_connection()
    cursor = conn.cursor()
    obs = getattr(item, 'observaciones', '')
    cursor.execute(
        "UPDATE herramientas SET descripcion=?, ubicacion=?, cantidad=?, observaciones=? WHERE partida=?",
        (item.descripcion, item.ubicacion, item.cantidad, obs, item.codigo)
    )
    conn.commit()
    return_connection(conn)

def delete_herramienta(codigo: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM herramientas WHERE partida = ?", (codigo,))
    conn.commit()
    return_connection(conn)
