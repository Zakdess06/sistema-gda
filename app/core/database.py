import sqlite3
from pathlib import Path
from queue import Queue
from threading import Lock

# Ruta de la base de datos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "database.db"

# ===== CONNECTION POOL =====
class ConnectionPool:
    """Pool de conexiones reutilizables para optimizar acceso a BD"""
    def __init__(self, pool_size=5):
        self.pool = Queue(maxsize=pool_size)
        self.lock = Lock()
        self.pool_size = pool_size
        
        # Inicializar conexiones
        for _ in range(pool_size):
            try:
                conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
                conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
                conn.execute("PRAGMA cache_size=10000")  # Aumentar cache
                self.pool.put(conn)
            except Exception:
                pass
    
    def get_connection(self):
        """Obtiene una conexión del pool"""
        try:
            return self.pool.get(timeout=1)
        except:
            # Si el pool está vacío, crear una nueva
            conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA cache_size=10000")
            return conn
    
    def return_connection(self, conn):
        """Devuelve una conexión al pool"""
        try:
            self.pool.put(conn, timeout=1)
        except:
            conn.close()

# Instancia global
_pool = ConnectionPool()

def get_connection():
    """Devuelve una conexión optimizada del pool"""
    return _pool.get_connection()

def return_connection(conn):
    """Devuelve la conexión al pool para reutilización"""
    _pool.return_connection(conn)


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
            cantidad INTEGER DEFAULT 0,
            observaciones TEXT
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
            prestamo_id TEXT UNIQUE NOT NULL,
            herramienta_codigo TEXT NOT NULL,
            cantidad INTEGER,
            trabajador_solicita_id TEXT,
            trabajador_despacha_id TEXT,
            trabajador_recibe_id TEXT,
            fecha_prestamo TEXT,
            fecha_regreso_estimada TEXT,
            fecha_devolucion TEXT,
            estado_herramienta_prestamo TEXT,
            estado_devolucion TEXT,
            comentarios TEXT
        )
    """)

    # Tabla bitacora
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bitacora (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            tipo TEXT NOT NULL,
            mensaje TEXT NOT NULL
        )
    """)

    # Tabla entradas (auditoría con fechas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entradas_auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            partida TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER,
            unidad TEXT,
            proveedor TEXT,
            recibio TEXT,
            ubicacion TEXT,
            observaciones TEXT
        )
    """)

    # Tabla salidas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            partida TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER,
            unidad TEXT,
            trabajador_id TEXT,
            trabajador_nombre TEXT,
            proyecto TEXT,
            destino TEXT,
            entrego TEXT,
            observaciones TEXT
        )
    """)

    # ===== CREAR ÍNDICES PARA OPTIMIZAR BÚSQUEDAS =====
    # Índices en productos
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_productos_partida ON productos(partida)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_productos_proveedor ON productos(proveedor_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_productos_cantidad ON productos(cantidad)")
    
    # Índices en herramientas
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_herramientas_partida ON herramientas(partida)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_herramientas_codigo ON herramientas(id)")
    
    # Índices en entradas_auditoria
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_entradas_fecha ON entradas_auditoria(fecha)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_entradas_partida ON entradas_auditoria(partida)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_entradas_proveedor ON entradas_auditoria(proveedor)")
    
    # Índices en salidas
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_salidas_fecha ON salidas(fecha)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_salidas_partida ON salidas(partida)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_salidas_trabajador ON salidas(trabajador_id)")
    
    # Índices en prestamos
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prestamos_herramienta ON prestamos(herramienta_codigo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prestamos_prestamo_id ON prestamos(prestamo_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prestamos_fecha ON prestamos(fecha_prestamo)")
    
    # Índices en bitacora
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bitacora_fecha ON bitacora(fecha)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bitacora_tipo ON bitacora(tipo)")
    
    # Índices en trabajadores
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trabajadores_identificacion ON trabajadores(identificacion)")
    
    # Índices en proveedores
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_proveedores_nombre ON proveedores(nombre_comercial)")

    conn.commit()
    return_connection(conn)
