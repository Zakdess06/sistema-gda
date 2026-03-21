from typing import Optional, List, Dict
from app.core.database import get_connection, return_connection


def fetch_proveedor_by_id(pid: str) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_comercial, nombre_fiscal, ubicacion, telefono FROM proveedores WHERE id = ?", (pid,))
    row = cursor.fetchone()
    return_connection(conn)
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
    return_connection(conn)
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
        return_connection(conn)
        return pid

    cursor.execute(
        "INSERT INTO proveedores (nombre_comercial, nombre_fiscal, ubicacion, telefono) VALUES (?, ?, ?, ?)",
        (nombre_comercial, '', ubicacion, telefono)
    )
    conn.commit()
    pid = cursor.lastrowid
    return_connection(conn)
    return pid

def insert_proveedor(nombre_comercial: str, nombre_fiscal: str, ubicacion: str = '', telefono: str = '') -> str:
    """Inserta un nuevo proveedor en la base de datos con un ID tipo PR-XXX y lo retorna"""
    conn = get_connection()
    cursor = conn.cursor()
    # Generar nuevo ID tipo PR-XXX encontrando el siguiente disponible
    cursor.execute("SELECT id FROM proveedores ORDER BY id DESC LIMIT 1")
    last_row = cursor.fetchone()
    
    if last_row:
        # Extraer el número del último ID (ej: "PR-003" -> 3)
        try:
            last_id = last_row[0]
            last_num = int(str(last_id).split('-')[1])
            next_num = last_num + 1
        except (IndexError, ValueError):
            # Si hay error al parsear, usar COUNT como fallback
            cursor.execute("SELECT COUNT(*) FROM proveedores")
            next_num = cursor.fetchone()[0] + 1
    else:
        # Primera inserción
        next_num = 1
    
    new_id = f"PR-{next_num:03d}"
    
    # Validar que el ID no exista
    cursor.execute("SELECT id FROM proveedores WHERE id = ?", (new_id,))
    if cursor.fetchone():
        # Si por algún motivo existe, buscar el siguiente disponible
        counter = next_num + 1
        while True:
            new_id = f"PR-{counter:03d}"
            cursor.execute("SELECT id FROM proveedores WHERE id = ?", (new_id,))
            if not cursor.fetchone():
                break
            counter += 1
    
    cursor.execute(
        "INSERT INTO proveedores (id, nombre_comercial, nombre_fiscal, ubicacion, telefono) VALUES (?, ?, ?, ?, ?)",
        (new_id, nombre_comercial, nombre_fiscal, ubicacion, telefono)
    )
    conn.commit()
    return_connection(conn)
    return new_id


def update_proveedor(pid: str, nombre_comercial: str, nombre_fiscal: str, ubicacion: str = '', telefono: str = ''):
    """Actualiza un proveedor existente"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE proveedores SET nombre_comercial=?, nombre_fiscal=?, ubicacion=?, telefono=? WHERE id=?",
        (nombre_comercial, nombre_fiscal, ubicacion, telefono, pid)
    )
    conn.commit()
    return_connection(conn)


def delete_proveedor(pid: int):
    """Elimina un proveedor de la base de datos"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proveedores WHERE id=?", (pid,))
    conn.commit()
    return_connection(conn)