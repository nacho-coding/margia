$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'configuracion.ps1')
Push-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
try {
    docker compose ps
    docker compose exec -T backend python -m pytest -q -p no:cacheprovider
    if ($LASTEXITCODE -ne 0) { throw 'Han fallado las pruebas de backend.' }
    docker compose exec -T backend ruff check --no-cache .
    if ($LASTEXITCODE -ne 0) { throw 'Ha fallado el análisis Python.' }
    $urlMargia = Get-UrlMargia -RaizMargia (Split-Path -Parent $PSScriptRoot)
    $saludMargia = Invoke-RestMethod -Uri "$urlMargia/api/v1/health"
    if ($saludMargia.estado -ne 'listo') { throw 'La API no está lista.' }
    Write-Host 'Salud y pruebas del backend correctas. Frontend: npm ci, npm run lint, npm run typecheck y npm run test:e2e desde frontend.'
} finally { Pop-Location }
