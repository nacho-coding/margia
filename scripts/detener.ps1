$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
try {
    docker compose down
    if ($LASTEXITCODE -ne 0) { throw 'No se ha podido detener MARGIA.' }
    Write-Host 'Aplicación detenida. Los datos y decisiones se conservan en el volumen.'
} finally { Pop-Location }
