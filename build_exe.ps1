# Script para empaquetar Sistema GDA como .exe
# Uso: .\build_exe.ps1

Write-Host "Construyendo Sistema GDA..." -ForegroundColor Cyan

# Verificar si PyInstaller esta instalado
pip show pyinstaller >$null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Instalando PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
    Write-Host "   - Tamaño: $([Math]::Round($exeSize, 2)) MB"
    Write-Host "   - Carpeta dist: $distFolder"
    Write-Host ""
} else {
    Write-Host "❌ Error al compilar. Revisa los mensajes arriba." -ForegroundColor Red
}

# Limpiar builds anteriores
Write-Host "Limpiando compilaciones anteriores..." -ForegroundColor Yellow
if (Test-Path ".\dist") { Remove-Item ".\dist" -Recurse -Force }
if (Test-Path ".\build") { Remove-Item ".\build" -Recurse -Force }

# Ejecutar PyInstaller con el archivo .spec
Write-Host "Ejecutando PyInstaller..." -ForegroundColor Cyan
pyinstaller build.spec --clean -y

# Verificar resultado
if (Test-Path ".\dist\Sistema GDA.exe") {
    Write-Host ""
    Write-Host "EXITO! Tu ejecutable esta listo:" -ForegroundColor Green
    Write-Host "Ubicacion: .\dist\Sistema GDA.exe" -ForegroundColor Cyan
    $exeSize = [Math]::Round((Get-Item ".\dist\Sistema GDA.exe").Length / 1MB, 2)
    Write-Host "Tamano: $exeSize MB" -ForegroundColor Yellow
    Write-Host ""
    
    # Generar instalador NSIS automáticamente
    Write-Host "Generando instalador NSIS..." -ForegroundColor Cyan
    $nsisPath = "C:\Program Files (x86)\NSIS\makensis.exe"
    
    if (Test-Path $nsisPath) {
        & $nsisPath installer\installer.nsi
        
        if (Test-Path ".\installer\Sistema_GDA_v1.0.3_Instalador.exe") {
            Write-Host ""
            Write-Host "EXITO COMPLETO! Instalador listo:" -ForegroundColor Green
            Write-Host "Ubicacion: .\installer\Sistema_GDA_v1.0.3_Instalador.exe" -ForegroundColor Cyan
            $installerSize = [Math]::Round((Get-Item ".\installer\Sistema_GDA_v1.0.3_Instalador.exe").Length / 1MB, 2)
            Write-Host "Tamano: $installerSize MB" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Tu programa esta listo para distribuir!" -ForegroundColor Green
        } else {
            Write-Host "Error al generar el instalador NSIS." -ForegroundColor Red
        }
    } else {
        Write-Host "NSIS no encontrado en: $nsisPath" -ForegroundColor Yellow
        Write-Host "Instala NSIS desde: https://nsis.sourceforge.io/" -ForegroundColor Yellow
    }
}
else {
    Write-Host "Error al compilar. Revisa los mensajes arriba." -ForegroundColor Red
}
