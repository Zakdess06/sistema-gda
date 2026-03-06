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
    # Generar nuevo ID tipo T-XXX
    cursor.execute("SELECT COUNT(*) FROM trabajadores")
    count = cursor.fetchone()[0] + 1
    new_id = f"T-{count:03d}"
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
