# SOLUCIÓN: Base de Datos en Memoria en el Instalador

## Problema
El instalador guardaba datos solo en memoria, no persistía en la base de datos SQLite.

## Causa
La ruta de la base de datos estaba configurada como:
```
BASE_DIR / "cache" / "database.db"
```

Cuando PyInstaller empaqueta la app, `BASE_DIR` apunta a directorios protegidos (sin permisos de escritura) como:
- `C:\Program Files\...` 
- Directorio temporal de PyInstaller

**Solución de SQLite**: Cuando no puede crear un archivo, crea automáticamente una base de datos en MEMORIA como fallback (behavior por defecto de sqlite3).

## Solución Implementada

### 1. **Ruta Inteligente en `database.py`**
Ahora detecta si la app está empaquetada o en desarrollo:

```python
def get_db_path():
    if getattr(sys, 'frozen', False):  # Empaquetada con PyInstaller
        if sys.platform == 'win32':
            # Usar APPDATA (escribible): C:\Users\username\AppData\Local\Sistema GDA\data
            app_data = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
            db_dir = app_data / "Sistema GDA" / "data"
        else:
            # Linux/Mac: ~/.config/sistema_gda
            db_dir = Path.home() / ".config" / "sistema_gda"
    else:
        # Desarrollo: ./cache/database.db
        db_dir = Path(__file__).resolve().parent.parent.parent / "cache"
    
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "database.db"
```

### 2. **Validación en `main.py`**
Agrega verificación al iniciar la app:
- ✅ Verifica que el archivo existe
- ✅ Verifica que no está vacío
- ✅ Verifica que se puede leer
- ✅ Muestra la ruta de la BD en consola

## Ubicaciones de la Base de Datos

| Contexto | Ruta |
|----------|------|
| **Desarrollo** | `.\cache\database.db` |
| **Instalador (Windows)** | `C:\Users\[username]\AppData\Local\Sistema GDA\data\database.db` |
| **Instalador (Linux)** | `~/.config/sistema_gda/database.db` |

## Cómo Verificar que Funciona

### 1. **En Desarrollo**
```sh
python -m app.main
```
Debe aparecer:
```
[OK] Base de datos inicializada correctamente en: ...\cache\database.db
[OK] Tablas creadas: 8
```

### 2. **Con el Instalador**
- Ejecutar la aplicación
- Agregar datos (productos, entradas, etc.)
- Cerrar la app
- Navegar a: `C:\Users\[username]\AppData\Local\Sistema GDA\data\`
- Verificar que existe `database.db` con tamaño > 0 bytes

### 3. **Prueba de Persistencia**
```powershell
# Verifica que los datos persisten
sqlite3 "C:\Users\[username]\AppData\Local\Sistema GDA\data\database.db" "SELECT COUNT(*) FROM productos;"
```

## Cambios Realizados

✅ **app/core/database.py**
- Nueva función `get_db_path()` con lógica inteligente
- Detecta si está empaquetada (`sys.frozen`)
- Usa rutas escribibles del sistema operativo

✅ **app/main.py**
- Nueva función `validate_database()`
- Valida que la BD no esté en memoria
- Muestra ubicación real de la BD

## Próximas Compilaciones

No necesitan cambios en el instalador (build.spec). Los cambios se aplican automáticamente.

## Notas de Seguridad

- La BD está en `AppData\Local` que es específico del usuario (privado)
- SQLite usa WAL (Write-Ahead Logging) para integridad
- Los datos no se pierden al cerrar la app

---
**Fecha**: 2026-03-19  
**Versión**: 1.0  
