param([switch]$SinBuild)
$ErrorActionPreference = 'Stop'
$raizMargia = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'configuracion.ps1')
Push-Location -LiteralPath $raizMargia
try {
    if (-not (Test-Path -LiteralPath '.env')) {
        $bytesMargia = New-Object byte[] 32
        $rngMargia = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        $rngMargia.GetBytes($bytesMargia)
        $rngMargia.Dispose()
        $claveMargia = [BitConverter]::ToString($bytesMargia).Replace('-', '').ToLowerInvariant()
        @("POSTGRES_PASSWORD=$claveMargia", 'MARGIA_PORT=3000', 'DEMO_CORTE=2026-10-31') | Set-Content -LiteralPath '.env' -Encoding utf8
        Write-Host 'Configuración local creada. La clave permanece en .env, excluido de Git.'
    }
    docker info --format '{{.ServerVersion}}'
    if ($LASTEXITCODE -ne 0) { throw 'Inicia Docker Desktop y vuelve a ejecutar este script.' }
    if ($SinBuild) { docker compose up -d --wait --wait-timeout 300 }
    else { docker compose up -d --build --wait --wait-timeout 300 }
    if ($LASTEXITCODE -ne 0) { throw 'El arranque no ha completado. Revisa docker compose logs --tail 80.' }
    $urlMargia = Get-UrlMargia -RaizMargia $raizMargia
    Write-Host "MARGIA disponible en $urlMargia · Datos 100 % sintéticos."
} finally { Pop-Location }
