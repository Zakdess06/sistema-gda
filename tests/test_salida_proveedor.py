import sys
from pathlib import Path
# asegurar que el proyecto esté en sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.database import init_database, get_connection
from app.core.store import store, AlmacenItem, Salida
from datetime import datetime

# inicializar BD
init_database()
conn = get_connection()
cur = conn.cursor()

# limpiar tablas relevantes para prueba
cur.execute("DELETE FROM productos")
cur.execute("DELETE FROM proveedores")
conn.commit()

# 1) crear producto con proveedor usando store
nuevo = AlmacenItem(
    partida='TEST-001',
    descripcion='Material de prueba',
    unidad='Pza',
    cantidad=10,
    ubicacion='Estante T1',
    proveedor='Proveedor Demo',
    stock_minimo=2
)
store.add_producto(nuevo)

# leer producto desde BD
cur.execute("SELECT partida, descripcion, unidad, cantidad, ubicacion, stock_minimo, proveedor_id FROM productos WHERE partida = ?", ('TEST-001',))
row = cur.fetchone()
print('Producto en BD:', row)

# obtener proveedor creado
prov_id = row[6]
cur.execute("SELECT id, nombre_comercial, ubicacion, telefono FROM proveedores WHERE id = ?", (prov_id,))
prov = cur.fetchone()
print('Proveedor en BD:', prov)

# 2) crear una salida y aplicar
sal = Salida(
    fecha=datetime.now().strftime('%Y-%m-%d %H:%M'),
    partida='TEST-001',
    descripcion='Material de prueba',
    cantidad=3,
    unidad='Pza',
    trabajador_id='T001',
    trabajador_nombre='Juan Pérez',
    proyecto='Prueba',
    destino='Obra X',
    entrego='Encargado'
)
store.add_salida(sal)

# verificar cantidad actualizada
cur.execute("SELECT cantidad FROM productos WHERE partida = ?", ('TEST-001',))
new_q = cur.fetchone()
print('Cantidad tras salida:', new_q[0])

conn.close()
print('Prueba completada')
