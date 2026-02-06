# app/core/herramienta_db.py
from app.core.database import get_connection
from app.core.store import Herramienta

def fetch_all_herramientas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT partida, descripcion, ubicacion, cantidad FROM herramientas")
    rows = cursor.fetchall()
    conn.close()
    items = []
    for row in rows:
        partida, descripcion, ubicacion, cantidad = row
        items.append(Herramienta(
            codigo=partida,
            descripcion=descripcion,
            ubicacion=ubicacion,
            cantidad=cantidad
        ))
    return items

def insert_herramienta(item: Herramienta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO herramientas (partida, descripcion, ubicacion, cantidad) VALUES (?, ?, ?, ?)",
        (item.codigo, item.descripcion, item.ubicacion, item.cantidad)
    )
    conn.commit()
    conn.close()

def update_herramienta(item: Herramienta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE herramientas SET descripcion=?, ubicacion=?, cantidad=? WHERE partida=?",
        (item.descripcion, item.ubicacion, item.cantidad, item.codigo)
    )
    conn.commit()
    conn.close()

def delete_herramienta(codigo: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM herramientas WHERE partida = ?", (codigo,))
    conn.commit()
    conn.close()
