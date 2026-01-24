import sqlite3
from pathlib import Path

# Ruta de la base de datos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "database.db"


def get_connection():
    """Devuelve una conexión a la base de datos"""
    return sqlite3.connect(DB_PATH)


def init_database():
    """Crea las tablas principales si no existen"""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida TEXT NOT NULL,
            descripcion TEXT,
            unidad TEXT,
            ubicacion TEXT,
            cantidad INTEGER DEFAULT 0,
            stock_minimo INTEGER DEFAULT 0,
            proveedor_id INTEGER
        )
    """)

    # Tabla herramientas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS herramientas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida TEXT NOT NULL,
            descripcion TEXT,
            ubicacion TEXT,
            cantidad INTEGER DEFAULT 0
        )
    """)

    # Tabla trabajadores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trabajadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            identificacion TEXT UNIQUE
        )
    """)

    # Tabla proveedores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_comercial TEXT,
            nombre_fiscal TEXT,
            ubicacion TEXT,
            telefono TEXT
        )
    """)

    # Tabla prestamos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            herramienta_id INTEGER,
            trabajador_id INTEGER,
            fecha_prestamo TEXT,
            fecha_devolucion TEXT,
            estado TEXT,
            comentarios TEXT
        )
    """)

    conn.commit()
    conn.close()
