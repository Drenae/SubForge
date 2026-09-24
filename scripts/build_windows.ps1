$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
& (Join-Path $PSScriptRoot 'prepare_windows_tools.ps1')
Push-Location $projectRoot
try {
    $python = Join-Path $projectRoot '.venv\Scripts\python.exe'
    $flet = Join-Path $projectRoot '.venv\Scripts\flet.exe'
    if (-not (Test-Path $python) -or -not (Test-Path $flet)) { throw 'Environnement Flet introuvable dans .venv.' }
    & $python -m pip install -e $projectRoot
    if ($LASTEXITCODE -ne 0) { throw 'Installation des dépendances du projet échouée.' }
    & $flet build windows
    if ($LASTEXITCODE -ne 0) { throw 'Build Windows échoué.' }
} finally {
    Pop-Location
}
