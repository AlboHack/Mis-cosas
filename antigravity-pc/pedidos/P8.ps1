# P8: aplicar los ajustes activos del perfil del Nitro (se corre elevado con Ejecutar-Elevado.ps1)
$raiz = Split-Path (Split-Path $PSScriptRoot)
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $raiz 'antigravity-pc\perfil-nitro\pruebas\Pruebas.ps1') | Select-Object -Last 1
Import-Module (Join-Path $raiz 'antigravity-pc\perfil-nitro\PerfilNitro.psm1') -Force
try { Checkpoint-Computer -Description 'Perfil Nitro P8' -RestorePointType MODIFY_SETTINGS -ErrorAction Stop; 'Punto de restauración creado' } catch { "Punto de restauración: $_" }
Set-Ajustes
Get-EstadoAjustes | Format-Table Id, Activo, Aplicado, Requisito -AutoSize | Out-String -Width 160
Get-ChildItem "$env:LOCALAPPDATA\PerfilNitro\respaldo" | Select-Object -ExpandProperty Name
DISM /Online /Get-ReservedStorageState | Out-String
(Get-MpPreference).ExclusionPath
