from app.core.database import get_connection, return_connection

# ===================== TRABAJADOR DB =====================
def fetch_all_trabajadores():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, identificacion FROM trabajadores")
    rows = cursor.fetchall()
    return_connection(conn)
    return [
        {'id': row[0], 'nombre': row[1], 'identificacion': row[2]} for row in rows
    ]

def insert_trabajador(nombre, identificacion):
    conn = get_connection()
    cursor = conn.cursor()
    # Generar nuevo ID tipo T-XXX encontrando el siguiente disponible
    cursor.execute("SELECT id FROM trabajadores ORDER BY id DESC LIMIT 1")
    last_row = cursor.fetchone()
    
    if last_row:
        # Extraer el número del último ID (ej: "T-003" -> 3)
        try:
            last_id = last_row[0]
            last_num = int(last_id.split('-')[1])
            next_num = last_num + 1
        except (IndexError, ValueError):
            # Si hay error al parsear, usar COUNT como fallback
            cursor.execute("SELECT COUNT(*) FROM trabajadores")
            next_num = cursor.fetchone()[0] + 1
    else:
        # Primera inserción
        next_num = 1
    
    new_id = f"T-{next_num:03d}"
    
    # Validar que el ID no exista
    cursor.execute("SELECT id FROM trabajadores WHERE id = ?", (new_id,))
    if cursor.fetchone():
        # Si por algún motivo existe, buscar el siguiente disponible
        counter = next_num + 1
        while True:
            new_id = f"T-{counter:03d}"
            cursor.execute("SELECT id FROM trabajadores WHERE id = ?", (new_id,))
            if not cursor.fetchone():
                break
            counter += 1
    
    cursor.execute(
        "INSERT INTO trabajadores (id, nombre, identificacion) VALUES (?, ?, ?)",
        (new_id, nombre, identificacion)
    )
    conn.commit()
    return_connection(conn)
    return new_id

def update_trabajador(id, nombre, identificacion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE trabajadores SET nombre=?, identificacion=? WHERE id=?",
        (nombre, identificacion, id)
    )
    conn.commit()
    return_connection(conn)

def delete_trabajador(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trabajadores WHERE id=?", (id,))
    conn.commit()
    return_connection(conn)
