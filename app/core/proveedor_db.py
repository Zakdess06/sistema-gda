from typing import Optional, List, Dict
from app.core.database import get_connection


def fetch_proveedor_by_id(pid: int) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_comercial, nombre_fiscal, ubicacion, telefono FROM proveedores WHERE id = ?", (pid,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    id_, nombre_comercial, nombre_fiscal, ubicacion, telefono = row
    return {
        'id': id_,
        'nombre_comercial': nombre_comercial,
        'nombre_fiscal': nombre_fiscal,
        'ubicacion': ubicacion,
        'telefono': telefono,
    }


def fetch_all_proveedores() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_comercial, nombre_fiscal, ubicacion, telefono FROM proveedores")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        id_, nombre_comercial, nombre_fiscal, ubicacion, telefono = row
        result.append({
            'id': id_,
            'nombre_comercial': nombre_comercial,
            'nombre_fiscal': nombre_fiscal,
            'ubicacion': ubicacion,
            'telefono': telefono,
        })
    return result


def get_or_create_proveedor(nombre_comercial: str, ubicacion: str = '', telefono: str = '') -> int:
    """Busca un proveedor por nombre comercial (case-insensitive). Si no existe, lo crea y devuelve su id."""
    nombre_comercial = (nombre_comercial or '').strip()
    if not nombre_comercial:
        return 0

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM proveedores WHERE lower(nombre_comercial) = lower(?)", (nombre_comercial,))
    row = cursor.fetchone()
    if row:
        pid = row[0]
        conn.close()
        return pid

    cursor.execute(
        "INSERT INTO proveedores (nombre_comercial, nombre_fiscal, ubicacion, telefono) VALUES (?, ?, ?, ?)",
        (nombre_comercial, '', ubicacion, telefono)
    )
    conn.commit()
    pid = cursor.lastrowid
    conn.close()
    return pid
