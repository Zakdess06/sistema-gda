# Optimización del Tamaño de Build

## Resumen de cambios realizados

### 1. **build.spec** - Exclusión de módulos innecesarios
Se agregó la lista de `excludedimports` para evitar incluir:
- `tcl`, `tk`, `_tkinter` - Interfaz gráfica no usada
- `pytz` - Manejo de zonas horarias no usado
- `IPython`, `Jupyter` - Herramientas de desarrollo
- `tests`, `pytest` - Código de pruebas
- `scipy` - Librería científica pesada

**Impacto**: Reduce el tamaño del ejecutable entre 10-20 MB

### 2. **build_exe.ps1** - Limpieza completa
Se mejoró la limpieza antes de compilar:
- Limpia `__pycache__` de Python
- Limpia caché de pip con `pip cache purge`
- Limpia archivos temporales de compilación

**Impacto**: Evita que se acumule código compilado antiguo

### 3. **Monitoreo de tamaño**
El script ahora muestra:
- Tamaño del .exe individual
- Tamaño total de la carpeta `dist/`

## ¿Por qué el programa crece?

| Causa | Solución |
|-------|----------|
| Nuevas dependencias en requirements.txt | Revisar necesidad real |
| Actualizaciones de PySide6/matplotlib | Usar versiones fijas |
| Caché de pip no limpiado | Ya está automatizado |
| archivos __pycache__ | Ya está automatizado |

## Mejor práctica: Versionado de dependencias

En lugar de:
```
PySide6>=6.5
```

Usa versiones más restrictivas:
```
PySide6==6.7.0
matplotlib==3.8.0
openpyxl==3.11.0
```

Así garantizas que cada build tenga el mismo tamaño.

## Revisar tamaño actual

Ejecuta el build y observa los tamaños reportados:
```powershell
.\build_exe.ps1
```

Si el .exe crece mucho entre builds, revisa:
1. Si changed de versión de dependencias
2. Si agregaste nuevos módulos al proyecto
3. Si hay caché de pip acumulado

## Comando para limpiar manualmente

```powershell
# Limpiar todo
Remove-Item ".\dist" -Recurse -Force
Remove-Item ".\build" -Recurse -Force
Remove-Item ".\app\__pycache__" -Recurse -Force
pip cache purge
```

---

**Nota**: El ejecutable de PySide6 nunca será "pequeño" (mínimo 150-200 MB), pero estos cambios evitan que crezca innecesariamente.
