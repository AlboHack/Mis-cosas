# P15: SAP2000 en modo gráfico DirectX (estaba en GDIPlus, que dibuja por software sin GPU) y verificación.
# No necesita administrador. Espera a que SAP2000 esté cerrado: si se edita el .ini con SAP2000 abierto, lo sobrescribe al salir.
param([int]$EsperaMaxMin = 360)
$ini = Join-Path $env:LOCALAPPDATA 'Computers and Structures\SAP2000 27\SAP2000v27.ini'
$limite = (Get-Date).AddMinutes($EsperaMaxMin)
while ((Get-Process SAP2000 -ErrorAction SilentlyContinue) -and (Get-Date) -lt $limite) { Start-Sleep -Seconds 300 }
if (Get-Process SAP2000 -ErrorAction SilentlyContinue) { 'SAP2000 siguió abierto todo el plazo: cambio pendiente.'; return }
if (-not (Test-Path $ini)) { "No existe $ini"; return }
$resp = Join-Path $env:USERPROFILE ("Mantenimiento\respaldo-ini\SAP2000v27_{0:yyyyMMdd_HHmmss}.ini" -f (Get-Date))
New-Item -ItemType Directory (Split-Path $resp) -Force | Out-Null
Copy-Item $ini $resp
"Respaldo: $resp"
'Antes: ' + (Select-String -Path $ini -Pattern '^[ \t]*GraphicsMode=' | ForEach-Object Line)
$txt = [IO.File]::ReadAllText($ini)
$enc = if ($txt.Length -gt 0 -and [IO.File]::ReadAllBytes($ini)[0] -eq 0xFF) { [Text.Encoding]::Unicode } else { [Text.Encoding]::Default }
$txt = [IO.File]::ReadAllText($ini, $enc)
# CSI indenta las claves con espacios ('   GraphicsMode=GDIPlus'): se acepta y se conserva la sangría
if ($txt -match '(?m)^[ \t]*GraphicsMode=') { $txt = [regex]::Replace($txt, '(?m)^([ \t]*)GraphicsMode=[^\r\n]*', '${1}GraphicsMode=DirectX') }
else { "No hay línea GraphicsMode en el .ini: no se cambia nada."; return }
[IO.File]::WriteAllText($ini, $txt, $enc)
'Después: ' + (Select-String -Path $ini -Pattern '^[ \t]*GraphicsMode=' -Encoding $(if ($enc -eq [Text.Encoding]::Unicode) { 'Unicode' } else { 'Default' }) | ForEach-Object Line)
& (Join-Path $PSScriptRoot 'P14-verificar-gpu.ps1') -EsperaMaxMin 0
'Modo gráfico al cerrar: ' + (Select-String -Path $ini -Pattern '^[ \t]*GraphicsMode=' -Encoding $(if ($enc -eq [Text.Encoding]::Unicode) { 'Unicode' } else { 'Default' }) | ForEach-Object Line)
