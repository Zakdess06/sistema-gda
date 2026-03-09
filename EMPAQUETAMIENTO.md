# 📦 Guía de Empaquetamiento - Sistema GDA

## 🚀 Opción 1: Ejecutable Rápido (.exe) - ⭐ RECOMENDADO

### Paso 1: Instalar PyInstaller
```powershell
pip install pyinstaller
```

### Paso 2: Ejecutar el script de compilación
```powershell
# Navega a la carpeta del proyecto
cd c:\Users\emman\OneDrive\Escritorio\TRABAJOS\sistema_gda

# Ejecuta el script
.\build_exe.ps1
```

**Opciones disponibles:**
```powershell
.\build_exe.ps1 -OneFile $true -Windowed $true  # Ejecutable único y sin consola
```

### Paso 3: Resultado
- ✅ Ejecutable listo en: `dist/Sistema GDA.exe`
- 📊 Tamaño: ~150-200 MB (incluye todas las dependencias)
- ⚡ Se ejecuta sin necesidad de Python instalado

---

## 📦 Opción 2: Instalador Windows (NSIS)

Crea una experiencia más profesional con menú de instalación.

### Requisitos
1. Descargar **NSIS** desde: https://nsis.sourceforge.io/
2. Instalar NSIS

### Script NSIS

Crea un archivo `installer.nsi` en la carpeta `installer/`:

```nsis
; Instalador para Sistema GDA
; Basado en NSIS

!include "MUI2.nsh"

; Configuración
Name "Sistema GDA v1.0"
OutFile "Sistema_GDA_Instalador.exe"
InstallDir "$PROGRAMFILES\SistemaGDA"
InstallDirRegKey HKCU "Software\SistemaGDA" "InstallPath"

; Mostrar detalles de instalación
ShowInstDetails show
ShowUninstDetails show

; Páginas del instalador
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Spanish"

; Sección de instalación
Section "Sistema GDA"
  SetOutPath "$INSTDIR"
  
  ; Copiar el ejecutable
  File "..\\dist\\Sistema GDA.exe"
  
  ; Crear accesos directos
  CreateDirectory "$SMPROGRAMS\\SistemaGDA"
  CreateShortcut "$SMPROGRAMS\\SistemaGDA\\Sistema GDA.lnk" "$INSTDIR\\Sistema GDA.exe"
  CreateShortcut "$DESKTOP\\Sistema GDA.lnk" "$INSTDIR\\Sistema GDA.exe"
  
  ; Registrar desinstalador
  CreateDirectory "$INSTDIR\\Uninstall"
  WriteUninstaller "$INSTDIR\\Uninstall\\Uninstall.exe"
  CreateShortcut "$SMPROGRAMS\\SistemaGDA\\Uninstall.lnk" "$INSTDIR\\Uninstall\\Uninstall.exe"
  
  ; Registrar en registry
  WriteRegStr HKCU "Software\\SistemaGDA" "InstallPath" "$INSTDIR"
SectionEnd

; Sección de desinstalación
Section "Uninstall"
  RMDir /r "$INSTDIR"
  RMDir /r "$SMPROGRAMS\\SistemaGDA"
  Delete "$DESKTOP\\Sistema GDA.lnk"
  DeleteRegKey HKCU "Software\\SistemaGDA"
SectionEnd
```

### Compilar instalador
```powershell
# Primero, construir el exe
.\build_exe.ps1

# Luego, compilar con NSIS
& "C:\Program Files (x86)\NSIS\makensis.exe" ".\installer\installer.nsi"
```

---

## 🐍 Opción 3: Distribución como Wheel (Desarrolladores)

```powershell
pip install wheel
python setup.py bdist_wheel
```

El archivo .whl se crea en: `dist/`

---

## 📋 Checklist de Empaquetamiento

- [ ] Actualizar versión en `setup.py`
- [ ] Revisar `requirements.txt` (todas las dependencias)
- [ ] Tener `icon-app.ico` en `resources/`
- [ ] Probar el .exe en una máquina sin Python
- [ ] Verificar que todas las carpetas se copian (`resources/`, etc.)
- [ ] Crear un icono de acceso directo
- [ ] Documentar pasos de instalación para usuarios

---

## 🐛 Solución de Problemas

### "PyInstaller no encontrado"
```powershell
pip install pyinstaller
```

### "El .exe no se ejecuta"
Revisa los logs en la consola de PyInstaller. Usualmente es por:
- Dependencias faltantes en `--hidden-import`
- Archivos no incluidos con `--add-data`

### "El .exe es muy grande"
Es normal (150+ MB). Incluye Python + todas las librerías. 
Para reducir tamaño:
```powershell
.\build_exe.ps1 -OneFile $false  # Crear carpeta en lugar de un archivo
```

### "La aplicación se abre y se cierra inmediatamente"
Usa sin `--windowed` para ver los errores en la consola:
```powershell
pyinstaller app\main.py --windowed $false
```

---

## 📞 Próximos Pasos Recomendados

1. **Crear un instalador NSIS** para distribución profesional
2. **Versionado**: Actualizar versiones en `setup.py` y `config.json`
3. **Certificado digital** (opcional): Firmar el .exe para evitar advertencias
4. **Testing**: Probar en máquina limpia sin Python

---

**¿Necesitas ayuda con algún paso?** 😊
