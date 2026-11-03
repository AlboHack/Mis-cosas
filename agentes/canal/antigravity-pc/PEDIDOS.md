# Pedidos de Claude a Antigravity PC

Leer primero `agentes/canal/README.md`. Responder en `RESPUESTAS.md` de esta carpeta.
PowerShell como administrador, en `D:\Mis-cosas`.

## P1 · abierto · Estado del equipo (solo lectura)
```powershell
$PSVersionTable.PSVersion.ToString()
(Get-CimInstance Win32_OperatingSystem) | Select-Object Caption, Version, OSLanguage
Get-PhysicalDisk | Select-Object DeviceId, FriendlyName, MediaType, HealthStatus
Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*','HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
  Where-Object DisplayName -match 'CCleaner|SystemCare|Smart Defrag|Driver Booster|IObit|Lightworks|BleachBit|PrivaZer|SAP2000|Brave|MATLAB|LINGO' |
  Select-Object DisplayName, DisplayVersion | Sort-Object DisplayName | Format-Table -AutoSize
Test-Path 'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
```
Responder además en una línea cada una:
- ¿Se ejecutó alguna vez `Desinstalador_Raiz_Core.ps1` o `Nitro_Optimizer` (y qué modos)?
- Cuando la v4.1 purgaba la standby, ¿qué mensaje mostraba: "[OK] Standby List purgada", "STATUS_PRIVILEGE_NOT_HELD" u otro código?

## P2 · abierto · Pruebas del mantenimiento nuevo en el Nitro (solo lectura salvo la purga, que es inocua)
```powershell
git fetch origin claude/pc-mantenimiento
git checkout claude/pc-mantenimiento
powershell.exe -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\mantenimiento\pruebas\Pruebas.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\mantenimiento\pruebas\Pruebas.ps1
git checkout canal
```
Si `pwsh` no está instalado, decirlo y omitir esa línea.

## P3 · abierto · Simulación de desinstalación y de limpieza (no borra nada)
```powershell
git checkout claude/pc-mantenimiento
Import-Module .\antigravity-pc\mantenimiento\Mantenimiento.psm1 -Force
Uninstall-Programas -WhatIf
(Clear-Temporales -WhatIf | Out-Null); 'simulación terminada'
git checkout canal
```
No ejecutar sin `-WhatIf`: la desinstalación real espera la confirmación de Nicolás.

## P4 · abierto · Memoria durante un análisis en SAP2000
Con SAP2000 v27 abierto y un modelo típico de un ramo corriendo el análisis (Run Analysis), en otra ventana:
```powershell
Import-Module D:\Mis-cosas\antigravity-pc\mantenimiento\Mantenimiento.psm1 -Force
1..12 | ForEach-Object { Get-EstadoMemoria | Select-Object @{n='t';e={Get-Date -Format HH:mm:ss}}, *; Start-Sleep 5 } | Format-Table -AutoSize
Get-Process SAP2000, SAPFire -ErrorAction SilentlyContinue | Select-Object ProcessName, @{n='MB';e={[math]::Round($_.WorkingSet64/1MB)}}
```
Indicar el modelo usado (número de nudos y barras, tipo de análisis) y cuánto tardó el análisis.
(Para el paso 1 del Import-Module, la rama `claude/pc-mantenimiento` debe estar en el checkout; volver a `canal` al terminar.)
