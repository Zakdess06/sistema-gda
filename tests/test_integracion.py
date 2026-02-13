#!/usr/bin/env python
"""
Script de prueba de integración completa del Sistema GDA

Prueba los flujos principales:
1. Gestión de productos
2. Gestión de herramientas
3. Sistema de préstamos
4. Reportes y exportación
"""

import sys
from pathlib import Path

# Asegurar que el proyecto esté en sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.database import init_database, get_connection
from app.core.store import (
    store, AlmacenItem, Herramienta, Entrada, 
    Salida, Trabajador, Proveedor
)
from app.core.bitacora import bitacora
from app.models.prestamo_herramienta import PrestamoHerramienta
from datetime import datetime, timedelta


def test_section(title):
    """Decorador para imprimir secciones de prueba"""
    def decorator(func):
        def wrapper():
            print(f"\n{'='*60}")
            print(f"  {title}")
            print(f"{'='*60}")
            try:
                func()
                print("✅ PRUEBA EXITOSA\n")
            except Exception as e:
                print(f"❌ ERROR: {e}\n")
                raise
        return wrapper
    return decorator


# ============================================================================
# TEST 1: INICIALIZACIÓN DEL SISTEMA
# ============================================================================

@test_section("TEST 1: Inicialización del Sistema")
def test_init():
    """Verifica que la base de datos se inicialice correctamente"""
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar que las tablas existan
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = [
        'productos', 'herramientas', 'trabajadores', 'proveedores',
        'prestamos', 'entradas_auditoria', 'salidas', 'bitacora'
    ]
    
    for table in required_tables:
        assert table in tables, f"Tabla '{table}' no encontrada"
        print(f"  ✓ Tabla '{table}' existe")
    
    conn.close()


# ============================================================================
# TEST 2: GESTIÓN DE PRODUCTOS
# ============================================================================

@test_section("TEST 2: Gestión de Productos (Almacén)")
def test_productos():
    """Prueba CRUD de productos"""
    
    # 1. Crear producto
    producto = AlmacenItem(
        partida='TEST-P001',
        descripcion='Producto de Prueba',
        unidad='Pza',
        cantidad=100,
        ubicacion='Pasillo A, Estante 1',
        proveedor='Proveedor Demo',
        stock_minimo=10
    )
    store.add_producto(producto)
    print(f"  ✓ Producto creado: {producto.partida}")
    
    # 2. Verificar que se guardó en BD
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT partida, descripcion, cantidad FROM productos WHERE partida = ?",
        ('TEST-P001',)
    )
    result = cursor.fetchone()
    assert result is not None, "Producto no guardado en BD"
    assert result[2] == 100, "Cantidad incorrecta"
    print(f"  ✓ Producto verificado en BD: {result}")
    conn.close()
    
    # 3. Actualizar cantidad
    producto.cantidad = 85
    store.update_producto(producto)
    print(f"  ✓ Producto actualizado: nueva cantidad = 85")


# ============================================================================
# TEST 3: GESTIÓN DE HERRAMIENTAS
# ============================================================================

@test_section("TEST 3: Gestión de Herramientas")
def test_herramientas():
    """Prueba CRUD de herramientas"""
    
    # 1. Generar código automático
    codigo1 = store.generar_codigo_herramienta()
    codigo2 = store.generar_codigo_herramienta()
    
    print(f"  ✓ Código automático 1: {codigo1}")
    print(f"  ✓ Código automático 2: {codigo2}")
    
    assert codigo1.startswith('H-'), "Código no tiene formato H-"
    assert codigo1 != codigo2, "Códigos no son únicos"
    
    # 2. Crear herramienta
    herramienta = Herramienta(
        codigo=codigo1,
        descripcion='Taladro Inalámbrico',
        ubicacion='Almacén Central',
        cantidad=5,
        observaciones='Estado: Bueno, Batería incluida'
    )
    store.add_herramienta(herramienta)
    print(f"  ✓ Herramienta creada: {herramienta.codigo}")
    
    # 3. Verificar en BD
    herramientas = store.get_herramientas()
    assert codigo1 in herramientas, "Herramienta no encontrada en store"
    print(f"  ✓ Herramienta verificada: {herramientas[codigo1].descripcion}")


# ============================================================================
# TEST 4: GESTIÓN DE TRABAJADORES
# ============================================================================

@test_section("TEST 4: Gestión de Trabajadores")
def test_trabajadores():
    """Prueba registro de trabajadores"""
    
    # Crear trabajadores demo
    trabajadores = [
        ('T001', 'Juan Pérez'),
        ('T002', 'María López'),
        ('T003', 'Carlos García'),
    ]
    
    for id_trab, nombre in trabajadores:
        trab = Trabajador(id=id_trab, nombre=nombre)
        store.trabajadores[id_trab] = trab
        print(f"  ✓ Trabajador agregado: {nombre} ({id_trab})")


# ============================================================================
# TEST 5: SISTEMA DE PRÉSTAMOS
# ============================================================================

@test_section("TEST 5: Sistema de Préstamos de Herramientas")
def test_prestamos():
    """Prueba flujo completo de préstamo"""
    
    # Obtener herramienta creada en test anterior
    herramientas = store.get_herramientas()
    if not herramientas:
        print("  ⚠️ No hay herramientas creadas, saltando test")
        return
    
    herr_codigo = list(herramientas.keys())[0]
    herramienta = herramientas[herr_codigo]
    
    print(f"  ℹ️  Herramienta a prestar: {herr_codigo}")
    
    # 1. Solicitar préstamo
    try:
        prestamo = store.solicitar_prestamo(
            herramienta_codigo=herr_codigo,
            trabajador_solicita_id='T001',
            trabajador_despacha_id='T002',
            cantidad=2,
            estado_herramienta='Bueno',
            fecha_regreso_estimada=(
                (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M")
            )
        )
        print(f"  ✓ Préstamo creado: ID = {prestamo.id}")
        
        # 2. Verificar estado
        assert prestamo.es_activo(), "Préstamo no está activo"
        print(f"  ✓ Préstamo activo: {prestamo.trabajador_solicita_id}")
        
        # 3. Devolver préstamo
        store.devolver_prestamo(
            prestamo_id=prestamo.id,
            trabajador_recibe_id='T003',
            estado_devolucion='Bueno',
            comentarios='Sin daños'
        )
        
        prestamo_devuelto = store.prestamos[0]
        assert not prestamo_devuelto.es_activo(), "Préstamo no fue marcado como devuelto"
        print(f"  ✓ Préstamo devuelto correctamente")
        print(f"    - Recibido por: {prestamo_devuelto.trabajador_recibe_id}")
        print(f"    - Estado de devolución: {prestamo_devuelto.estado_herramienta_devolucion}")
        
    except ValueError as e:
        print(f"  ℹ️  {e}")


# ============================================================================
# TEST 6: GENERACIÓN AUTOMÁTICA DE CÓDIGOS
# ============================================================================

@test_section("TEST 6: Generación Automática de Códigos")
def test_codigos():
    """Prueba generador de códigos único"""
    
    # Códigos de herramientas
    codigos_h = set()
    for i in range(5):
        codigo = store.generar_codigo_herramienta()
        codigos_h.add(codigo)
        print(f"  ✓ Herramienta: {codigo}")
    
    assert len(codigos_h) == 5, "Códigos duplicados en herramientas"
    
    # Códigos de partidas
    codigos_p = set()
    for i in range(5):
        codigo = store.generar_codigo_partida()
        codigos_p.add(codigo)
        print(f"  ✓ Partida: {codigo}")
    
    assert len(codigos_p) == 5, "Códigos duplicados en partidas"


# ============================================================================
# TEST 7: BITÁCORA DE EVENTOS
# ============================================================================

@test_section("TEST 7: Bitácora del Sistema")
def test_bitacora():
    """Prueba registro de eventos en bitácora"""
    
    # Crear eventos
    bitacora.log('PRODUCTO', 'Producto test creado')
    bitacora.log('HERRAMIENTA', 'Herramienta test agregada')
    bitacora.log('PRESTAMO', 'Préstamo solicitado')
    
    print(f"  ✓ Eventos registrados")
    
    # Obtener logs
    logs = bitacora.obtener_logs(limite=10)
    print(f"  ✓ Total de logs en sistema: {len(logs)}")
    
    if logs:
        print(f"  ℹ️  Últimos 3 eventos:")
        for log in logs[-3:]:
            print(f"     - [{log['tipo']}] {log['mensaje']}")


# ============================================================================
# TEST 8: FLUJO COMPLETO (INTEGRATION TEST)
# ============================================================================

@test_section("TEST 8: Flujo Completo (Integration Test)")
def test_flujo_completo():
    """Prueba un flujo real de entrada-salida"""
    
    # 1. Crear producto
    entrada = Entrada(
        codigo=store.generar_codigo_entrada(),
        fecha=datetime.now().strftime("%d/%m/%Y"),
        partida='INT-TEST-001',
        descripcion='Producto de Integración',
        cantidad=50,
        unidad='Pza',
        proveedor='Proveedor Test',
        recibio='T001',
        ubicacion='Almacén Test',
        observaciones='Prueba de integración'
    )
    store.add_entrada(entrada)
    print(f"  ✓ Entrada creada: {entrada.codigo}")
    
    # 2. Crear salida
    salida = Salida(
        fecha=datetime.now().strftime("%d/%m/%Y"),
        partida='INT-TEST-001',
        descripcion='Producto de Integración',
        cantidad=10,
        unidad='Pza',
        trabajador_id='T001',
        trabajador_nombre='Juan Pérez',
        proyecto='Proyecto Test',
        destino='Taller A',
        entrego='T002',
        observaciones='Entrega de prueba'
    )
    store.add_salida(salida)
    print(f"  ✓ Salida creada")
    
    # 3. Verificar que salida se registró
    assert len(store.salidas) > 0, "Salida no fue registrada"
    print(f"  ✓ Salida verificada en store")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Ejecuta todos los tests"""
    
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                 TEST DE INTEGRACIÓN COMPLETA               ║")
    print("║                      SISTEMA GDA v3.4                      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    tests = [
        test_init,
        test_productos,
        test_herramientas,
        test_trabajadores,
        test_prestamos,
        test_codigos,
        test_bitacora,
        test_flujo_completo,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ {str(e)}\n")
    
    # Resumen
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                        RESUMEN FINAL                       ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print(f"║  Tests Pasados:     {passed:>5}  ✅                          ║")
    print(f"║  Tests Fallidos:    {failed:>5}  ❌                          ║")
    print(f"║  Total:             {passed + failed:>5}                          ║")
    print("║                                                            ║")
    
    if failed == 0:
        print("║  🎉  ¡TODOS LOS TESTS PASARON EXITOSAMENTE! 🎉           ║")
    else:
        print(f"║  ⚠️  {failed} TEST(S) FALLIDO(S) - REVISAR ERRORES          ║")
    
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
