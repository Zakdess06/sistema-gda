; Instalador para Sistema GDA
; Este archivo puede compilarse con NSIS: https://nsis.sourceforge.io/

!include "MUI2.nsh"
!include "x64.nsh"

; Configuración Administrativa
SetCompress off
Unicode true
RequestExecutionLevel admin

; Configuración del Instalador
Name "Sistema GDA v1.1.0"
OutFile "Sistema_GDA_v1.1.0_Instalador.exe"
InstallDir "$PROGRAMFILES\SistemaGDA"
InstallDirRegKey HKCU "Software\SistemaGDA" "Install_Dir"

; Mostrar detalles
ShowInstDetails show
ShowUninstDetails show

; ===== Páginas del Instalador =====
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Idioma
!insertmacro MUI_LANGUAGE "Spanish"

; ===== Archivos de Instalación =====
Section "Instalar Sistema GDA"
  SectionIn RO
  
  ; Establecer carpeta de salida
  SetOutPath "$INSTDIR"
  
  ; Copiar ejecutable
  File "..\dist\Sistema GDA.exe"
  
  ; Crear accesos directos en el menú Inicio
  CreateDirectory "$SMPROGRAMS\SistemaGDA"
  CreateShortcut "$SMPROGRAMS\SistemaGDA\Sistema GDA.lnk" "$INSTDIR\Sistema GDA.exe" "" "$INSTDIR\Sistema GDA.exe" 0
  CreateShortcut "$SMPROGRAMS\SistemaGDA\Desinstalar.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  
  ; Crear acceso directo en el Escritorio
  CreateShortcut "$DESKTOP\Sistema GDA.lnk" "$INSTDIR\Sistema GDA.exe" "" "$INSTDIR\Sistema GDA.exe" 0
  
  ; Crear carpetas de datos necesarias
  CreateDirectory "$APPDATA\SistemaGDA"
  CreateDirectory "$APPDATA\SistemaGDA\cache"
  CreateDirectory "$APPDATA\SistemaGDA\backups"
  
  ; Registrar en el registro de Windows
  WriteRegStr HKCU "Software\SistemaGDA" "Install_Dir" "$INSTDIR"
  
  ; Crear desinstalador
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Registrar para desinstalar desde Panel de Control (opcional)
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SistemaGDA" "DisplayName" "Sistema GDA"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SistemaGDA" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SistemaGDA" "InstallLocation" "$INSTDIR"
  
SectionEnd

; ===== Sección de Desinstalación =====
Section "Uninstall"
  
  ; Eliminar accesos directos
  Delete "$SMPROGRAMS\SistemaGDA\Sistema GDA.lnk"
  Delete "$SMPROGRAMS\SistemaGDA\Desinstalar.lnk"
  RMDir "$SMPROGRAMS\SistemaGDA"
  
  Delete "$DESKTOP\Sistema GDA.lnk"
  
  ; Eliminar archivos de instalación
  Delete "$INSTDIR\Sistema GDA.exe"
  Delete "$INSTDIR\uninstall.exe"
  RMDir "$INSTDIR"

  ; Eliminar datos persistentes (cache, backups, DB) en APPDATA
  RMDir /r "$APPDATA\SistemaGDA\cache"
  RMDir /r "$APPDATA\SistemaGDA\backups"
  RMDir /r "$APPDATA\SistemaGDA"
  
  ; Limpiar registry
  DeleteRegKey HKCU "Software\SistemaGDA"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SistemaGDA"
  
SectionEnd

; ===== Funciones =====
Function .onInit
  ; Verificar archivos necesarios
  IfFileExists "..\dist\Sistema GDA.exe" file_found file_not_found
  
  file_found:
    Return
  
  file_not_found:
    MessageBox MB_ICONEXCLAMATION|MB_YESNO "No se encontró el archivo ejecutable.$\nDebes ejecutar build_exe.ps1 primero.$\n¿Deseas continuar de todas formas?" IDYES continue IDNO abort
    continue:
      Return
    abort:
      Quit
FunctionEnd
