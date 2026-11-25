function Get-UrlMargia {
    param([string]$RaizMargia)
    $puertoMargia = '3000'
    $rutaEnvMargia = Join-Path $RaizMargia '.env'
    if (Test-Path -LiteralPath $rutaEnvMargia) {
        foreach ($lineaMargia in (Get-Content -LiteralPath $rutaEnvMargia)) {
            if ($lineaMargia -match '^MARGIA_PORT=(\d+)$') { $puertoMargia = $Matches[1] }
        }
    }
    if ($env:MARGIA_PORT) { $puertoMargia = $env:MARGIA_PORT }
    $numeroPuertoMargia = 0
    if (-not [int]::TryParse($puertoMargia, [ref]$numeroPuertoMargia) -or $numeroPuertoMargia -lt 1 -or $numeroPuertoMargia -gt 65535) {
        throw 'MARGIA_PORT debe ser un puerto entre 1 y 65535.'
    }
    return "http://localhost:$numeroPuertoMargia"
}
