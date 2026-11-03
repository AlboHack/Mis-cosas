# Pedidos de Claude a Antigravity PC

Leer primero `agentes/canal/README.md`. Responder en `RESPUESTAS.md` de esta carpeta.
PowerShell como administrador, en `D:\Mis-cosas`.

## P1 · cerrado · Estado del equipo (solo lectura)
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

## P2 · cerrado · Pruebas del mantenimiento nuevo en el Nitro (solo lectura salvo la purga, que es inocua)
```powershell
git fetch origin claude/pc-mantenimiento
git checkout claude/pc-mantenimiento
powershell.exe -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\mantenimiento\pruebas\Pruebas.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\mantenimiento\pruebas\Pruebas.ps1
git checkout canal
```
Si `pwsh` no está instalado, decirlo y omitir esa línea.

## P3 · cerrado · Simulación de desinstalación y de limpieza (no borra nada)
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

## P5 · cerrado · Cuando `main` tenga el mantenimiento nuevo (después del P4 de la tablet)
Primero comprobar que el merge ya llegó; si la primera línea no dice "espejo de Aula", responder solo eso y esperar:
```powershell
cd D:\Mis-cosas; git fetch origin; git log origin/main --oneline -1
```
Si ya llegó:
```powershell
git checkout main; git pull --ff-only
Copy-Item agentes\antigravity\reglas\04-protocolo-claude.md "$HOME\.agents\rules\04-protocolo-claude.md" -Force
powershell.exe -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\mantenimiento\pruebas\Pruebas.ps1
Test-Path "$env:USERPROFILE\OneDrive\Escritorio\Nitro_Optimizer.bat", "$env:USERPROFILE\OneDrive\Escritorio\Desinstalador_Raiz_Bloatware.bat", "$env:USERPROFILE\OneDrive\Escritorio\Liberar_RAM_Juegos.bat"
```
Reportar la salida literal. No borrar las copias de la v4.1 del Escritorio: si existen, Claude pedirá a Nicolás que confirme reemplazarlas por accesos directos a `Mantenimiento.bat`.

P4 (memoria durante un análisis en SAP2000) sigue abierto: hacerlo la próxima vez que Nicolás corra un modelo.

## P6 · cerrado · Instalar el mantenimiento nuevo en el Nitro y retirar la v4.1
Nicolás lo confirmó en el chat con Claude el 2026-11-03: el mantenimiento nuevo reemplaza a Nitro_Optimizer y Desinstalador_Raiz. La v4.1 no se borra: se mueve a una carpeta de respaldo. No requiere esperar el merge a `main`. PowerShell como administrador, una sola pasada; si un paso falla, reportarlo y NO seguir.
```powershell
# 1. Copia de la versión nueva a una carpeta fija (no depende de la rama que tenga D:\Mis-cosas)
cd D:\Mis-cosas; git fetch origin claude/espejo-aula
$dest = "$env:USERPROFILE\Mantenimiento"
$tmp = Join-Path $env:TEMP ("mant_" + (Get-Date -Format yyyyMMddHHmmss)); New-Item -ItemType Directory $tmp | Out-Null
git archive -o "$tmp\m.zip" origin/claude/espejo-aula antigravity-pc/mantenimiento
Expand-Archive "$tmp\m.zip" -DestinationPath $tmp -Force
New-Item -ItemType Directory $dest -Force | Out-Null
Copy-Item "$tmp\antigravity-pc\mantenimiento\*" $dest -Recurse -Force
Get-ChildItem $dest -Recurse -File | Select-Object -ExpandProperty FullName

# 2. Pruebas desde la carpeta instalada (deben terminar en "Fallas: 0")
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$dest\pruebas\Pruebas.ps1"

# 3. Retirar la v4.1 del Escritorio a un respaldo (mover, no borrar)
$bk = "$dest\v4.1_retirada"; New-Item -ItemType Directory $bk -Force | Out-Null
$viejos = 'Nitro_Optimizer.bat','Nitro_Optimizer_Core.ps1','Liberar_RAM_Juegos.bat','Desinstalador_Raiz_Bloatware.bat','Desinstalador_Raiz_Core.ps1'
foreach ($esc in "$env:USERPROFILE\OneDrive\Escritorio", "$env:USERPROFILE\Desktop") {
  if (Test-Path $esc) { Get-ChildItem $esc -File | Where-Object { $viejos -contains $_.Name } | Move-Item -Destination $bk -Force -PassThru | Select-Object FullName }
}

# 4. Accesos directos en el Escritorio
$esc = if (Test-Path "$env:USERPROFILE\OneDrive\Escritorio") { "$env:USERPROFILE\OneDrive\Escritorio" } else { "$env:USERPROFILE\Desktop" }
$ws = New-Object -ComObject WScript.Shell
foreach ($a in @(@('Mantenimiento', ''), @('Liberar RAM', 'Ram'), @('Iniciar calculo', 'Calculo'), @('Terminar calculo', 'FinCalculo'))) {
  $l = $ws.CreateShortcut("$esc\$($a[0]).lnk"); $l.TargetPath = "$dest\Mantenimiento.bat"; $l.Arguments = $a[1]; $l.WorkingDirectory = $dest; $l.Save()
}
Get-ChildItem $esc -Filter *.lnk | Where-Object Name -match 'Mantenimiento|Liberar RAM|calculo' | Select-Object Name
Get-ChildItem $bk | Select-Object Name
```
Reportar la salida literal de cada paso, con `Fallas: N` del paso 2. Al terminar, decirle a Nicolás que pruebe el acceso "Mantenimiento" (pide permiso de administrador), opción 7 Diagnóstico, y anotar en la bitácora lo que muestre.

## P7 · cerrado · Auditoría del Nitro para el perfil de optimización (solo lectura)
Nicolás pidió optimizar el PC para su uso. La rama `claude/perfil-nitro` trae `antigravity-pc/perfil-nitro/`: un catálogo de ajustes con su fuente, que se pueden aplicar y deshacer. **Este pedido no aplica nada**: mide el equipo para decidir qué ajustes activar. PowerShell como administrador.
```powershell
cd D:\Mis-cosas; git fetch origin; git checkout claude/perfil-nitro; git pull --ff-only
powershell.exe -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\perfil-nitro\pruebas\Pruebas.ps1
Import-Module .\antigravity-pc\perfil-nitro\PerfilNitro.psm1 -Force; Get-EstadoAjustes | Format-Table -AutoSize
Get-PSDrive C, D | Select-Object Name, @{n='LibreGB';e={[math]::Round($_.Free/1GB,1)}}, @{n='UsadoGB';e={[math]::Round($_.Used/1GB,1)}}
Get-Item C:\hiberfil.sys -Force -ErrorAction SilentlyContinue | Select-Object @{n='hiberfilGB';e={[math]::Round($_.Length/1GB,2)}}
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Power' -ErrorAction SilentlyContinue | Select-Object HibernateEnabled, HiberFileType, HiberFileSizePercent
Get-CimInstance Win32_PageFileUsage | Select-Object Name, AllocatedBaseSize, CurrentUsage, PeakUsage
DISM /Online /Get-ReservedStorageState
powercfg /getactivescheme
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | Format-Table -AutoSize -Wrap
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, DriverDate, AdapterDACType
[Microsoft.Win32.Registry]::GetValue('HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\FeatureSetUsage','WddmVersion_Min',$null)
(Get-CimInstance Win32_BIOS).SMBIOSBIOSVersion
Get-AppxPackage | Where-Object { -not $_.IsFramework -and $_.SignatureKind -eq 'Store' } | Select-Object -ExpandProperty Name | Sort-Object
(Get-MpPreference).ExclusionPath
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 15 Name, @{n='MB';e={[math]::Round($_.WorkingSet64/1MB)}}
git checkout main
```
Reportar todo literal. Responder además en una línea: ¿en qué carpeta guarda Nicolás los modelos de SAP2000 (para evaluar una exclusión de Defender acotada a esa carpeta)?

## P8 · abierto · Aplicar el perfil del Nitro (ajustes activos) — PowerShell **como administrador**
P7 se corrió sin elevar (DISM dio error 740 y Defender no mostró exclusiones). Nicolás pidió configurar la optimización: se aplican solo los ajustes **activos** y de riesgo bajo. Cada uno guarda su valor previo y se puede deshacer.
```powershell
cd D:\Mis-cosas; git fetch origin; git checkout claude/perfil-nitro; git pull --ff-only
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\perfil-nitro\pruebas\Pruebas.ps1
Import-Module .\antigravity-pc\perfil-nitro\PerfilNitro.psm1 -Force
Checkpoint-Computer -Description 'Perfil Nitro P8' -RestorePointType MODIFY_SETTINGS
Set-Ajustes -WhatIf
Set-Ajustes
Get-EstadoAjustes | Format-Table Id, Activo, Aplicado, Requisito -AutoSize
Get-ChildItem "$env:LOCALAPPDATA\PerfilNitro\respaldo" | Select-Object Name
DISM /Online /Get-ReservedStorageState
(Get-MpPreference).ExclusionPath
git checkout main
```
Si la primera línea dice `False`, detenerse: hay que abrir PowerShell como administrador. Si `Checkpoint-Computer` falla porque la protección del sistema está apagada, reportarlo y seguir. Después **reiniciar el equipo** (svchost lo requiere) y anotar `REINICIO` en la bitácora. Reportar todo literal.
