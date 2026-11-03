# P16 (administrador, doble clic de Nicolás): reparar el almacén de componentes, verificar archivos de sistema,
# subir a 5 GB el espacio de puntos de restauración y aplicar el servicio de Google Update en manual.
'== DISM RestoreHealth (puede tardar 10-20 min)'
DISM /Online /Cleanup-Image /RestoreHealth | Out-String
'== DISM CheckHealth después'
DISM /Online /Cleanup-Image /CheckHealth | Out-String
'== sfc /scannow'
(sfc /scannow | Out-String) -replace "`0", ''
'== Espacio para puntos de restauración'
vssadmin resize shadowstorage /for=C: /on=C: /maxsize=5GB | Out-String
vssadmin list shadowstorage | Out-String
'== Perfil: Google Update en manual'
$raiz = Split-Path (Split-Path $PSScriptRoot)
Import-Module (Join-Path $raiz 'antigravity-pc\perfil-nitro\PerfilNitro.psm1') -Force
Set-Ajustes -Ids servicio-google-update-manual
Get-Service gupdate -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType | Format-Table | Out-String
