# Script para empaquetar Sistema GDA como .exe
# Uso: .\build_exe.ps1

param(
    [switch]$OneFile = $true,
    [switch]$Windowed = $true
)

Write-Host "🔨 Construyendo Sistema GDA..." -ForegroundColor Cyan

# Verificar si PyInstaller está instalado
$pyinstallerCheck = pip show pyinstaller 2>$null
if (-not $pyinstallerCheck) {
    Write-Host "📦 Instalando PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
    Write-Host "   - Tamaño: $([Math]::Round($exeSize, 2)) MB"
    Write-Host "   - Carpeta dist: $distFolder"
    Write-Host ""
} else {
    Write-Host "❌ Error al compilar. Revisa los mensajes arriba." -ForegroundColor Red
}

# Variables
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$mainFile = Join-Path $projectRoot "app\main.py"
$icon = Join-Path $projectRoot "resources\icon-app.ico"
$distFolder = Join-Path $projectRoot "dist"
$buildArgs = @(
    $mainFile,
    "--name", "Sistema GDA",
    "--icon", $icon,
    "--distpath", $distFolder,
    "--specpath", (Join-Path $projectRoot "build_specs"),
    "--buildpath", (Join-Path $projectRoot "build_temp"),
    "--add-data", "app/styles;app/styles",
    "--add-data", "resources;resources",
    "--hidden-import=PySide6",
    "--hidden-import=openpyxl",
    "--hidden-import=matplotlib"
)

if ($OneFile) {
    $buildArgs += "--onefile"
    Write-Host "📦 Modo: Ejecutable único" -ForegroundColor Green
} else {
    Write-Host "📦 Modo: Carpeta con archivos" -ForegroundColor Green
}

if ($Windowed) {
    $buildArgs += "--windowed"
}

# Ejecutar PyInstaller
Write-Host "⚙️  Ejecutando PyInstaller..." -ForegroundColor Cyan
& pyinstaller @buildArgs

# Verificar resultado
if (Test-Path (Join-Path $distFolder "Sistema GDA.exe")) {
    Write-Host ""
    Write-Host "✅ ¡ÉXITO! Tu ejecutable está listo:" -ForegroundColor Green
    Write-Host ""
    Write-Host "📂 Ubicación: $(Join-Path $distFolder 'Sistema GDA.exe')" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 Información de compilación:" -ForegroundColor Yellow
    $exeSize = (Get-Item (Join-Path $distFolder "Sistema GDA.exe")).Length / 1MB
    Write-Host "   - Tamaño: $([Math]::Round($exeSize, 2)) MB"
    Write-Host "   - Carpeta dist: $distFolder"
    Write-Host ""
} else {
    Write-Host "❌ Error al compilar. Revisa los mensajes arriba." -ForegroundColor Red
}
