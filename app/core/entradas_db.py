# app/core/entradas_db.py
from app.core.database import get_connection
from app.core.store import Entrada


def fetch_all_entradas():
    """Obtiene todas las entradas de la BD"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT codigo, fecha, partida, descripcion, cantidad, unidad, proveedor, recibio, ubicacion, observaciones 
            FROM entradas 
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        items = []
        for row in rows:
            codigo, fecha, partida, descripcion, cantidad, unidad, proveedor, recibio, ubicacion, observaciones = row
            items.append(Entrada(
                codigo=codigo,
                fecha=fecha,
                partida=partida,
                descripcion=descripcion,
                cantidad=cantidad,
                unidad=unidad,
                proveedor=proveedor,
                recibio=recibio,
                ubicacion=ubicacion,
                observaciones=observaciones
            ))
        return items
    except Exception:
        # Si la tabla no existe aún, devolver lista vacía
        return []


def insert_entrada(entrada: Entrada):
    """Inserta una nueva entrada en la BD"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO entradas (codigo, fecha, partida, descripcion, cantidad, unidad, proveedor, recibio, ubicacion, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entrada.codigo,
        entrada.fecha,
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
    conn.close()


def delete_entrada(id_entrada: int):
    """Elimina una entrada de la BD"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entradas WHERE id = ?", (id_entrada,))
    conn.commit()
    conn.close()


def update_entrada(entrada: Entrada):
    """Actualiza una entrada en la BD"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE entradas 
        SET fecha=?, partida=?, descripcion=?, cantidad=?, unidad=?, proveedor=?, recibio=?, ubicacion=?, observaciones=?
        WHERE codigo=?
    """, (
        entrada.fecha,
        entrada.partida,
        entrada.descripcion,
        entrada.cantidad,
        entrada.unidad,
        entrada.proveedor,
        entrada.recibio,
        entrada.ubicacion,
        entrada.observaciones,
        entrada.codigo
    ))
    conn.commit()
    conn.close()

