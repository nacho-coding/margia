param([switch]$Confirmar)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'configuracion.ps1')
if (-not $Confirmar) {
    $respuestaMargia = Read-Host 'Se borrará exclusivamente el estado de esta demo, incluidas decisiones. Escribe RESTABLECER DEMO'
    if ($respuestaMargia -cne 'RESTABLECER DEMO') { throw 'Restablecimiento cancelado.' }
}
$urlMargia = Get-UrlMargia -RaizMargia (Split-Path -Parent $PSScriptRoot)
$respuestaReset = Invoke-RestMethod -Uri "$urlMargia/api/v1/demo/reset" -Method Post -ContentType 'application/json' -Body '{"confirmacion":"RESTABLECER DEMO"}'
$respuestaReset | Select-Object estado,snapshot,checksum,segundos
