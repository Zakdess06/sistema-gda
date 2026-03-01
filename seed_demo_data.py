#!/usr/bin/env python
"""
Script para inyectar datos de prueba realistas en todo el sistema
Genera entradas, salidas, herramientas, préstamos para los últimos 7 días
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from app.core.database import init_database, get_connection
from app.core.store import store, AlmacenItem, Entrada, Salida, Herramienta, Trabajador, Proveedor
from app.core.entradas_db import insert_entrada
from app.core.salidas_db import insert_salida
from app.core.herramienta_db import insert_herramienta
from app.core.proveedor_db import insert_proveedor
from app.core.bitacora import bitacora
from app.models.prestamo_herramienta import PrestamoHerramienta
from app.core.prestamo_db import save_prestamo


def seed_demo():
    """Inyecta datos de prueba realistas"""
    
    print("🔄 Inicializando base de datos...")
    init_database()
    
    # =========== TRABAJADORES ===========
    print("\n✅ Creando trabajadores...")
    trabajadores = [
        Trabajador(id='T001', nombre='Juan Pérez', numero_identificacion='12345678'),
        Trabajador(id='T002', nombre='María López', numero_identificacion='87654321'),
        Trabajador(id='T003', nombre='Carlos Ruiz', numero_identificacion='11223344'),
        Trabajador(id='T004', nombre='Ana García', numero_identificacion='55667788'),
        Trabajador(id='T005', nombre='Roberto Díaz', numero_identificacion='99887766'),
        Trabajador(id='T006', nombre='Patricia Martínez', numero_identificacion='44332211'),
        Trabajador(id='T007', nombre='Diego Fernández', numero_identificacion='66554433'),
        Trabajador(id='T008', nombre='Sofía Ramírez', numero_identificacion='22113344'),
        Trabajador(id='T009', nombre='Miguel Rodríguez', numero_identificacion='77665544'),
        Trabajador(id='T010', nombre='Elena Sánchez', numero_identificacion='33221155'),
        Trabajador(id='T011', nombre='Fernando Gutiérrez', numero_identificacion='88776655'),
        Trabajador(id='T012', nombre='Valentina Castillo', numero_identificacion='55443322'),
    ]
    store.trabajadores = {t.id: t for t in trabajadores}
    
    # =========== PROVEEDORES ===========
    print("✅ Creando proveedores...")
    proveedores_data = [
        ('ConstruMundo', 'Construcciones Mundo S.A.', 'Calle Principal 123', '555-1234'),
        ('TecnoSupply', 'Tecnología y Suministros', 'Av. Central 456', '555-5678'),
        ('VerdeMas', 'Distribuidora Verde', 'Calle Verde 789', '555-9012'),
        ('MetalPro', 'Metalurgía Profesional', 'Parque Industrial 321', '555-3456'),
        ('CéramicaPlus', 'Cerámica y Materiales Plus', 'Zona Industrial 654', '555-7890'),
        ('ObraExpress', 'Obra Express Distribuidora', 'Carrera 5 432', '555-0123'),
        ('ElastiMateriales', 'Elásticos y Materiales', 'Calle 10 654', '555-4567'),
        ('VidrioPerfecto', 'Vidrio Perfecto S.A.', 'Av. Principal 987', '555-8901'),
        ('HerramientasMax', 'Herramientas Máxima Calidad', 'Zona 3 159', '555-2345'),
        ('PinturasPro', 'Pinturas Profesionales', 'Calle 8 753', '555-6789'),
        ('ClavosYTuercas', 'Clavos y Tuercas Industriales', 'Carrera 7 852', '555-0246'),
        ('MaterialesPremium', 'Materiales Premium Construcción', 'Av. 4 963', '555-1357'),
    ]
    
    for nombre_com, nombre_fiscal, ubicacion, telefono in proveedores_data:
        insert_proveedor(nombre_com, nombre_fiscal, ubicacion, telefono)
    
    # =========== HERRAMIENTAS ===========
    print("✅ Creando herramientas...")
    herramientas_data = [
        ('Taladro Bosch', 'Almacén A', 3, 'Disponible'),
        ('Martillo 2kg', 'Almacén B', 5, 'Disponible'),
        ('Compresor', 'Almacén A', 1, 'Disponible'),
        ('Esmeriladora', 'Almacén C', 2, 'Disponible'),
        ('Sierras manuales', 'Almacén B', 8, 'Disponible'),
        ('Nivel láser', 'Almacén A', 2, 'Disponible'),
        ('Destornillador eléctrico', 'Almacén C', 4, 'Disponible'),
        ('Cinta métrica 25m', 'Almacén B', 10, 'Disponible'),
        ('Escalera aluminio 3m', 'Almacén A', 2, 'Disponible'),
        ('Pala cuadrada', 'Almacén B', 6, 'Disponible'),
        ('Pico punta', 'Almacén C', 4, 'Disponible'),
        ('Carretilla', 'Almacén A', 2, 'Disponible'),
    ]
    
    for desc, ubicacion, cantidad, estado in herramientas_data:
        codigo = store.generar_codigo_herramienta()
        herramienta = Herramienta(
            codigo=codigo,
            descripcion=desc,
            ubicacion=ubicacion,
            cantidad=cantidad,
            estado=estado
        )
        insert_herramienta(herramienta)
    
    # =========== ENTRADAS (últimos 7 días) ===========
    print("✅ Creando entradas...")
    entradas_data = [
        ('Cemento Portland 50kg', 'Pza', 50, 'ConstruMundo', 'Juan Pérez', 'Estante A1', 10, 'Entrada de stock'),
        ('Varilla 1/2"', 'Mt', 100, 'MetalPro', 'María López', 'Estante B2', 5, 'Importado'),
        ('Tubo PVC', 'Mt', 200, 'TecnoSupply', 'Carlos Ruiz', 'Estante C1', 8, 'En buen estado'),
        ('Pintura latex', 'Lt', 150, 'VerdeMas', 'Ana García', 'Bodega 1', 20, 'Stock regular'),
        ('Arena 25kg', 'Pza', 80, 'ConstruMundo', 'Roberto Díaz', 'Patio exterior', 15, 'Seco y limpio'),
        ('Ladrillo rojo', 'Pza', 500, 'MetalPro', 'Patricia Martínez', 'Bodega 2', 25, 'Lote completo'),
        ('Mortero pre-mezclado', 'Kg', 200, 'TecnoSupply', 'Diego Fernández', 'Estante D1', 18, 'Listo para usar'),
        ('Cerámicas blancas', 'Caja', 100, 'CéramicaPlus', 'Sofía Ramírez', 'Estante E2', 12, ''),
        ('Tuberías galvanizadas', 'Mt', 150, 'ObraExpress', 'Miguel Rodríguez', 'Estante A3', 8, 'Protegidas'),
        ('Vidrio templado 4mm', 'Pza', 40, 'VidrioPerfecto', 'Elena Sánchez', 'Almacén A', 6, 'Frágil - manipular con cuidado'),
        ('Alambre recocido', 'Kg', 250, 'ClavosYTuercas', 'Fernando Gutiérrez', 'Estante B4', 10, ''),
        ('Cinta adhesiva industrial', 'Rollo', 30, 'MaterialesPremium', 'Valentina Castillo', 'Estante C2', 5, 'Varias medidas'),
    ]
    
    hoy = datetime.now()
    for i, (desc, unidad, cant, prov, recibio, ubicacion, stock_min, obs) in enumerate(entradas_data):
        # Distribuir en los últimos 7 días
        dias_atras = i % 7
        fecha = hoy - timedelta(days=dias_atras)
        fecha_str = fecha.strftime("%d/%m/%Y")
        
        entrada = Entrada(
            codigo="",
            fecha=fecha_str,
            partida=store.generar_codigo_partida(),
            descripcion=desc,
            cantidad=cant,
            unidad=unidad,
            proveedor=prov,
            recibio=recibio,
            ubicacion=ubicacion,
            observaciones=obs
        )
        insert_entrada(entrada)
        store.entradas.append(entrada)
    
    # =========== SALIDAS (últimos 7 días) ===========
    print("✅ Creando salidas...")
    salidas_data = [
        ('Cemento Portland 50kg', 'Pza', 10, 'Proyecto Hospital', 'Despacho',),
        ('Varilla 1/2"', 'Mt', 25, 'Obra Centro Comercial', 'Despacho'),
        ('Tubo PVC', 'Mt', 50, 'Proyecto Hospital', 'Despacho'),
        ('Pintura latex', 'Lt', 30, 'Mantenimiento', 'Uso interno'),
        ('Arena 25kg', 'Pza', 15, 'Obra Centro Comercial', 'Despacho'),
        ('Mortero pre-mezclado', 'Kg', 40, 'Proyecto Hospital', 'Despacho'),
        ('Cerámicas blancas', 'Caja', 20, 'Reforma Baños', 'Despacho'),
        ('Tuberías galvanizadas', 'Mt', 35, 'Instalación Agua', 'Despacho'),
        ('Vidrio templado 4mm', 'Pza', 8, 'Proyecto Oficinas', 'Despacho'),
        ('Alambre recocido', 'Kg', 50, 'Obra Centro Comercial', 'Despacho'),
        ('Cinta adhesiva industrial', 'Rollo', 5, 'Mantenimiento', 'Uso interno'),
        ('Ladrillo rojo', 'Pza', 80, 'Proyecto Hospital', 'Despacho'),
    ]
    
    for i, (desc, unidad, cant, proyecto, destino) in enumerate(salidas_data):
        dias_atras = (i // 2) % 7
        fecha = hoy - timedelta(days=dias_atras)
        fecha_str = fecha.strftime("%d/%m/%Y")
        
        salida = Salida(
            fecha=fecha_str,
            partida=f"INFO-{i:03d}",
            descripcion=desc,
            cantidad=cant,
            unidad=unidad,
            trabajador_id=trabajadores[i % len(trabajadores)].id,
            trabajador_nombre=trabajadores[i % len(trabajadores)].nombre,
            proyecto=proyecto,
            destino=destino,
            entrego=trabajadores[i % len(trabajadores)].nombre,
            observaciones="Salida normal"
        )
        insert_salida(salida)
        store.salidas.append(salida)
    
    # =========== PRÉSTAMOS ===========
    print("✅ Creando préstamos...")
    herramientas = store.get_herramientas()
    herr_list = list(herramientas.values())
    
    prestamos_data = [
        (0, 'T001', 'T002', 'T001', 'Bueno', (hoy + timedelta(days=5)).strftime("%Y-%m-%d %H:%M")),  # Taladro - activo
        (1, 'T002', 'T003', '', 'Bueno', (hoy + timedelta(days=3)).strftime("%Y-%m-%d %H:%M")),  # Martillo - devuelto
        (2, 'T003', 'T004', '', 'Regular', (hoy + timedelta(days=4)).strftime("%Y-%m-%d %H:%M")),  # Compresor - devuelto
        (3, 'T004', 'T005', 'T005', 'Excelente', (hoy + timedelta(days=6)).strftime("%Y-%m-%d %H:%M")),  # Esmeriladora - activo
        (4, 'T005', 'T006', '', 'Bueno', (hoy + timedelta(days=2)).strftime("%Y-%m-%d %H:%M")),  # Sierras - devuelto
        (5, 'T006', 'T007', 'T007', 'Bueno', (hoy + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")),  # Nivel - activo
        (6, 'T007', 'T008', '', 'Excelente', (hoy + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")),  # Destornillador - devuelto
        (7, 'T008', 'T009', 'T009', 'Regular', (hoy + timedelta(days=5)).strftime("%Y-%m-%d %H:%M")),  # Cinta métrica - activo
        (8, 'T009', 'T010', '', 'Bueno', (hoy - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")),  # Escalera - devuelto
        (9, 'T010', 'T011', 'T011', 'Bueno', (hoy + timedelta(days=4)).strftime("%Y-%m-%d %H:%M")),  # Pala - activo
        (10, 'T011', 'T012', '', 'Excelente', (hoy + timedelta(days=3)).strftime("%Y-%m-%d %H:%M")),  # Pico - devuelto
        (11, 'T001', 'T002', 'T002', 'Bueno', (hoy + timedelta(days=6)).strftime("%Y-%m-%d %H:%M")),  # Carretilla - activo
    ]
    
    for idx, (herr_idx, solicita, despacha, recibe, estado, fecha_reg) in enumerate(prestamos_data):
        if herr_idx < len(herr_list):
            herramienta = herr_list[herr_idx]
            
            fecha_prest = (hoy - timedelta(days=2 + (idx % 5))).strftime("%Y-%m-%d %H:%M")
            fecha_dev = "" if recibe else (hoy - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
            
            prestamo = PrestamoHerramienta(
                id=f"PREST-{2026:04d}-{idx:03d}",
                herramienta_codigo=herramienta.codigo,
                trabajador_solicita_id=solicita,
                trabajador_despacha_id=despacha,
                trabajador_recibe_id=recibe,
                fecha_prestamo=fecha_prest,
                fecha_regreso_estimada=fecha_reg,
                fecha_devolucion=fecha_dev,
                estado_herramienta_prestamo=estado,
                estado_herramienta_devolucion=estado if fecha_dev else "",
                cantidad=1
            )
            save_prestamo(prestamo)
            store.prestamos.append(prestamo)
    
    # =========== BITÁCORA ===========
    print("✅ Registrando en bitácora...")
    bitacora.log("Sistema", "Datos de demostración inyectados correctamente")
    
    print("\n" + "="*60)
    print("✅ DATOS DE PRUEBA INYECTADOS EXITOSAMENTE")
    print("="*60)
    print(f"✓ Trabajadores: {len(trabajadores)}")
    print(f"✓ Proveedores: {len(proveedores_data)}")
    print(f"✓ Herramientas: {len(herramientas_data)}")
    print(f"✓ Entradas: {len(entradas_data)}")
    print(f"✓ Salidas: {len(salidas_data)}")
    print(f"✓ Préstamos: {len(prestamos_data)}")
    print("="*60)
    print("\nLa aplicación ya tiene datos para probar:\n")
    print("📊 Dashboard: Verá gráficas con movimiento de últimos 7 días")
    print("📦 Almacén: Habrá productos con stock disponible")
    print("↔️  Salidas: Hay registros de despachos")
    print("🔧 Herramientas: Hay tools con préstamos activos y devueltos")
    print("📋 Bitácora: Se registrará todo")


if __name__ == "__main__":
    seed_demo()
