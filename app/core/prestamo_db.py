"""Módulo para gestionar préstamos en la base de datos"""
from app.core.database import get_connection
from app.models.prestamo_herramienta import Prestamo


def save_prestamo(prestamo: Prestamo):
    """Guarda un préstamo en la base de datos"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO prestamos 
            (prestamo_id, herramienta_codigo, cantidad, trabajador_solicita_id, 
             trabajador_despacha_id, trabajador_recibe_id, fecha_prestamo, 
             fecha_regreso_estimada, fecha_devolucion, estado_herramienta_prestamo, 
             estado_devolucion, comentarios)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prestamo.id,
            prestamo.herramienta_codigo,
            prestamo.cantidad,
            prestamo.trabajador_solicita_id,
            prestamo.trabajador_despacha_id,
            prestamo.trabajador_recibe_id,
            prestamo.fecha_prestamo,
            prestamo.fecha_regreso_estimada,
            prestamo.fecha_devolucion,
            prestamo.estado_herramienta_prestamo,
            prestamo.estado_devolucion,
            prestamo.comentarios
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error guardando préstamo: {e}")
        return False


def update_prestamo(prestamo: Prestamo):
    """Actualiza un préstamo en la base de datos"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE prestamos
            SET trabajador_recibe_id = ?, fecha_devolucion = ?, 
                estado_devolucion = ?, comentarios = ?
            WHERE prestamo_id = ?
        """, (
            prestamo.trabajador_recibe_id,
            prestamo.fecha_devolucion,
            prestamo.estado_devolucion,
            prestamo.comentarios,
            prestamo.id
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error actualizando préstamo: {e}")
        return False


def fetch_all_prestamos():
    """Obtiene todos los préstamos de la base de datos"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT prestamo_id, herramienta_codigo, cantidad, trabajador_solicita_id,
                   trabajador_despacha_id, trabajador_recibe_id, fecha_prestamo,
                   fecha_regreso_estimada, fecha_devolucion, estado_herramienta_prestamo,
                   estado_devolucion, comentarios
            FROM prestamos
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        prestamos = []
        for row in rows:
            prestamo = Prestamo(
                id=row[0],
                herramienta_codigo=row[1],
                cantidad=row[2],
                trabajador_solicita_id=row[3],
                trabajador_despacha_id=row[4],
                trabajador_recibe_id=row[5],
                fecha_prestamo=row[6],
                fecha_regreso_estimada=row[7],
                fecha_devolucion=row[8],
                estado_herramienta_prestamo=row[9],
                estado_devolucion=row[10],
                comentarios=row[11]
            )
            prestamos.append(prestamo)
        
        return prestamos
    except Exception as e:
        print(f"Error recuperando préstamos: {e}")
        return []
