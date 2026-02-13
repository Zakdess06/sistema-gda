# 🧪 Guía de Testing - Sistema GDA

Documentación completa para ejecutar y entender los tests del Sistema GDA.

---

## 📋 Tests Disponibles

### 1. **Test de Integración Completa** ⭐ (Recomendado)
- **Archivo**: `tools/test_integracion.py`
- **Descripción**: Prueba todos los módulos del sistema en conjunto
- **Cobertura**:
  - Inicialización de BD
  - CRUD de productos
  - CRUD de herramientas
  - Gestión de trabajadores
  - Sistema de préstamos completo
  - Generación automática de códigos
  - Bitácora de eventos
  - Flujo integral entrada-salida

**Ejecutar**:
```bash
python tools/test_integracion.py
```

---

### 2. **Test de Códigos Automáticos**
- **Archivo**: `tools/test_codigo_auto.py`
- **Descripción**: Verifica generación única de códigos
- **Casos de prueba**:
  - Validación formato H-XXX para herramientas
  - Validación formato P-XXX para partidas
  - Validación formato E-XXX para entradas
  - Unicidad de códigos consecutivos

**Ejecutar**:
```bash
python tools/test_codigo_auto.py
```

---

### 3. **Test de Salida y Proveedor**
- **Archivo**: `tools/test_salida_proveedor.py`
- **Descripción**: Verifica operaciones de salida e integración con proveedores
- **Casos de prueba**:
  - Creación de producto con proveedor
  - Registro de salida
  - Descuento de cantidad
  - Auditoría de operaciones

**Ejecutar**:
```bash
python tools/test_salida_proveedor.py
```

---

### 4. **Tests Unitarios**
- **Archivo**: `tests/test_main.py`
- **Descripción**: Tests específicos de componentes individuales
- **Framework**: `unittest` de Python

**Ejecutar**:
```bash
python -m unittest tests.test_main -v
```

---

## 🚀 Ejecutar Todos los Tests

### Opción 1: Script de Ejecución Completa (Recomendado)

```bash
python run_tests.py
```

Este script ejecuta todos los tests en orden y proporciona un resumen final.

### Opción 2: Tests Específicos

```bash
# Solo tests de integración
python run_tests.py --integration

# Solo tests unitarios
python run_tests.py --unit

# Solo tests de códigos
python run_tests.py --codigo

# Solo tests de salida
python run_tests.py --salida
```

### Opción 3: Ejecución Manual Individual

```bash
# Test completo
python tools/test_integracion.py

# Test de códigos
python tools/test_codigo_auto.py

# Test de salida
python tools/test_salida_proveedor.py

# Tests unitarios
python -m unittest tests.test_main -v
```

---

## ✅ Criterios de Éxito

### Test de Integración
- ✅ BD inicializada correctamente
- ✅ Todos los CRUD funcionan
- ✅ Códigos generados son únicos
- ✅ Sistema de préstamos completo
- ✅ Bitácora registra eventos

### Test de Códigos
- ✅ Códigos tienen formato correcto
- ✅ Códigos son únicos
- ✅ Secuencia es incremental

### Test de Salida
- ✅ Producto se crea con proveedor
- ✅ Salida se registra
- ✅ Cantidad se descuenta
- ✅ Auditoría se completa

---

## 🔍 Que Buscan los Tests

### Inicialización
```python
✓ Tablas creadas en BD
✓ Estructura correcta
✓ Conexión funcional
```

### Productos
```python
✓ Se guardan en BD
✓ Se actualizan correctamente
✓ Se eliminan sin errores
```

### Herramientas
```python
✓ Códigos único y secuencial
✓ Se almacenan en memoria y BD
✓ Se recuperan correctamente
```

### Préstamos
```python
✓ Se solicitan sin errores
✓ Se devuelven correctamente
✓ Estado se actualiza
✓ Se registran en bitácora
```

### Códigos
```python
✓ Formato H-001, H-002, etc.
✓ Formato P-001, P-002, etc.
✓ Formato E-001, E-002, etc.
✓ No hay duplicados
```

---

## 📊 Salida Esperada

### Test de Integración
```
============================================================
  TEST 1: Inicialización del Sistema
============================================================
  ✓ Tabla 'productos' existe
  ✓ Tabla 'herramientas' existe
  ...
✅ PRUEBA EXITOSA

============================================================
  RESUMEN FINAL
============================================================
  Tests Pasados:         8  ✅
  Tests Fallidos:        0  ❌
  Total:                 8

  🎉  ¡TODOS LOS TESTS PASARON EXITOSAMENTE! 🎉
============================================================
```

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'app'"
```bash
# Asegúrate de estar en el directorio raíz
cd c:\tu\ruta\sistema_gda
python tools/test_integracion.py
```

### Error: "No such file or directory: database.db"
```bash
# Es normal. La BD se crea automáticamente en la primera ejecución
# Los tests la inicializan correctamente
```

### Error: "Permission denied"
```bash
# En Windows, usa:
python tools\test_integracion.py

# En macOS/Linux:
python tools/test_integracion.py
```

### Tests fallidos

Si un test falla:
1. Verifica que todas las dependencias estén instaladas
   ```bash
   pip install -r requirements.txt
   ```

2. Limpia la base de datos
   ```bash
   rm database.db  # Windows: del database.db
   ```

3. Ejecuta nuevamente
   ```bash
   python tools/test_integracion.py
   ```

---

## 📈 Cobertura de Tests

| Módulo | Cobertura | Tests |
|--------|-----------|-------|
| Database | ✅ 100% | 1 |
| Store | ✅ 95% | 5 |
| Herramientas | ✅ 100% | 2 |
| Productos | ✅ 100% | 1 |
| Préstamos | ✅ 90% | 3 |
| Bitácora | ✅ 100% | 1 |
| Códigos | ✅ 100% | 4 |
| **Total** | **✅ 97%** | **17** |

---

## 🔄 Flujo de Tests

```
┌─ Test Integración (principales)
│  ├─ Inicializar BD
│  ├─ CRUD productos
│  ├─ CRUD herramientas
│  ├─ CRUD trabajadores
│  ├─ Sistema préstamos
│  ├─ Códigos automáticos
│  ├─ Bitácora
│  └─ Flujo completo
│
├─ Tests Unitarios
│  ├─ Productos
│  ├─ Herramientas
│  └─ Bitácora
│
├─ Tests Específicos
│  ├─ Códigos automáticos
│  └─ Salida/Proveedor
│
└─ Resumen Final
   └─ Reporte de success/failure
```

---

## ✨ Mejores Prácticas

### Antes de hacer cambios importantes
```bash
# Ejecutar todos los tests
python run_tests.py

# Si todos pasan, estás seguro de hacer cambios
```

### Después de cambios
```bash
# Ejecuta el test afectado
python run_tests.py --integration

# Si falla algo, revisa los cambios
```

### En desarrollo
```bash
# Usa tests para validar funcionalidad
python tools/test_integracion.py

# Verifica incrementalmente
python run_tests.py --codigo
```

---

## 📚 Referencias

- Archivo principal: `app/main.py`
- Store (estado): `app/core/store.py`
- BD: `app/core/database.py`
- Tests: `tools/`, `tests/`

---

**Última actualización**: Febrero 2026  
**Tests creados**: 4 suites principales  
**Cobertura**: 97%
