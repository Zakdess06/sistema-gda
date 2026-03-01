# app/core/salidas_db.py
from app.core.database import get_connection, return_connection
from app.core.store import Salida


def fetch_all_salidas():
    """Obtiene todas las salidas de la BD"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha, partida, descripcion, cantidad, unidad, trabajador_id, trabajador_nombre, proyecto, destino, entrego, observaciones
            FROM salidas
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        return_connection(conn)
        
        items = []
        for row in rows:
            fecha, partida, descripcion, cantidad, unidad, trabajador_id, trabajador_nombre, proyecto, destino, entrego, observaciones = row
            items.append(Salida(
                fecha=fecha,
                partida=partida,
                descripcion=descripcion,
                cantidad=cantidad,
                unidad=unidad,
                trabajador_id=trabajador_id,
                trabajador_nombre=trabajador_nombre,
                proyecto=proyecto,
                destino=destino,
                entrego=entrego,
                observaciones=observaciones
            ))
        return items
    except Exception:
        # Si la tabla no existe aún, devolver lista vacía
        return []


def insert_salida(salida: Salida):
    """Inserta una nueva salida en la BD"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO salidas (fecha, partida, descripcion, cantidad, unidad, trabajador_id, trabajador_nombre, proyecto, destino, entrego, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        salida.fecha,
        salida.partida,
        salida.descripcion,
        salida.cantidad,
        salida.unidad,
        salida.trabajador_id,
        salida.trabajador_nombre,
        salida.proyecto,
        salida.destino,
        salida.entrego,
        salida.observaciones
    ))
    conn.commit()
    return_connection(conn)


def delete_salida(id_salida: int):
    """Elimina una salida de la BD"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM salidas WHERE id = ?", (id_salida,))
    conn.commit()
    return_connection(conn)
