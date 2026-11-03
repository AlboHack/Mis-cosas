# P9 (antes de instalar el driver AMD): punto de restauración y copia de la lista de drivers de video
try { Checkpoint-Computer -Description 'Antes driver AMD' -RestorePointType MODIFY_SETTINGS -ErrorAction Stop; 'Punto de restauración creado' } catch { "Punto de restauración: $_" }
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, DriverDate | Format-Table -AutoSize | Out-String
$f = Join-Path $env:USERPROFILE 'Mantenimiento\drivers_display_antes.txt'
pnputil /enum-drivers /class Display | Out-File $f -Encoding UTF8
Get-Content $f
