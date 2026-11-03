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


## Cómo correr lo que necesita administrador (desde 2026-11-03)
Tu sesión no está elevada (DUDA de P8). No escribas `.bat` propios para eso: usa el ayudante del repo. Windows mostrará **un** aviso de permiso (UAC) que Nicolás acepta, y la salida vuelve en tu consola para reportarla literal:
```powershell
cd D:\Mis-cosas; git fetch origin; git checkout claude/perfil-nitro; git pull --ff-only
powershell -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\Ejecutar-Elevado.ps1 -Script antigravity-pc\pedidos\<script>.ps1 -Nombre <Pn>
```

## P8 · cerrado · Aplicar el perfil del Nitro (ajustes activos)
**Forma de ejecutarlo (reemplaza al bloque de abajo):** `Ejecutar-Elevado.ps1 -Script antigravity-pc\pedidos\P8.ps1 -Nombre P8`. Después pedirle a Nicolás que reinicie y anotar `REINICIO`. El `aplicar_p8.bat` que preparaste se puede borrar.
**Actualizado:** la rama ya trae también `inicio-onenote`, `inicio-opera-assistant` e `inicio-wallpaper-engine` (decisión de Nicolás). `Set-Ajustes` los aplica junto con los demás. El plan de energía queda en Alto rendimiento: no tocarlo.
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

## P9 · cerrado · Actualizar el driver de la AMD Radeon Vega 10 (después de P8 y del reinicio)
Nicolás lo pidió (2026-11-03). El driver actual es 27.20.1028.1, de julio de 2020. En el Nitro la Vega 10 maneja la pantalla interna y la GTX 1650 renderiza a través de ella (Optimus): durante la instalación la pantalla parpadeará o quedará en negro unos segundos. **Nicolás debe estar frente al PC.** No tocar el driver de NVIDIA.

### 1. Antes
**Forma de ejecutarlo:** `Ejecutar-Elevado.ps1 -Script antigravity-pc\pedidos\P9-antes.ps1 -Nombre P9` (equivale al bloque de abajo).
```powershell
Checkpoint-Computer -Description 'Antes driver AMD' -RestorePointType MODIFY_SETTINGS
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, DriverDate
pnputil /enum-drivers /class Display | Out-File "$env:USERPROFILE\Mantenimiento\drivers_display_antes.txt"
Get-Content "$env:USERPROFILE\Mantenimiento\drivers_display_antes.txt"
```

### 2. Descarga (navegador)
1. Abrir la página oficial: https://www.amd.com/es/support/downloads/drivers.html/processors/ryzen/ryzen-3000-series/amd-ryzen-7-3750h.html
2. Elegir **Windows 11 - 64-Bit Edition** y descargar **AMD Software: Adrenalin Edition** marcado **WHQL Recommended**. Claude vio 26.5.2; si la página muestra una versión más nueva y también WHQL Recommended, usar esa. No usar versiones "Optional" ni sitios que no sean amd.com.
3. Verificar la firma del instalador descargado:
```powershell
$inst = Get-ChildItem "$env:USERPROFILE\Downloads", "D:\Descargas Opera" -Filter "*adrenalin*.exe" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$inst.FullName; [math]::Round($inst.Length/1MB,1)
Get-AuthenticodeSignature $inst.FullName | Select-Object Status, @{n='Firmante';e={$_.SignerCertificate.Subject}}
```
Seguir solo si `Status` es `Valid` y el firmante es **Advanced Micro Devices**.

### 3. Instalación
Ejecutar el instalador. En las opciones elegir **Solo controlador** (Driver Only) si aparece, o **Mínima**: no instalar el panel completo ni extras. **No** marcar "Restablecimiento de fábrica" (Factory Reset). Al terminar, reiniciar y anotar `REINICIO` en la bitácora.

Si el instalador dice que el equipo no es compatible o pide el driver del fabricante: detenerse y reportar el mensaje literal. La alternativa es el driver de Acer para el Nitro AN515-43 y la decide Claude.

### 4. Después
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, DriverDate, Status
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers' -Name HwSchMode -ErrorAction SilentlyContinue | Select-Object HwSchMode
cd D:\Mis-cosas; Import-Module .\antigravity-pc\perfil-nitro\PerfilNitro.psm1 -Force; Get-EstadoAjustes | Format-Table Id, Aplicado -AutoSize
```
Pedirle a Nicolás que abra SAP2000 v27 con `D:\Modelos RUN\PRACTICA RODRIGO.sdb`, que corra el análisis y confirme que la vista 3D se ve bien. Anotar en la bitácora lo que diga (`NICOLAS`).

### Si algo sale mal
- Pantalla negra que no vuelve en 1 minuto: Nicolás presiona **Win + Ctrl + Shift + B**, que reinicia el driver de video.
- Errores o fallas en SAP2000 o en juegos: Administrador de dispositivos → Adaptadores de pantalla → AMD Radeon → Propiedades → Controlador → **Revertir al controlador anterior**. Si no está disponible: restaurar el punto 'Antes driver AMD'.
Reportar todo literal, incluidos los mensajes del instalador.

## P11 · cerrado · Actualizar la copia instalada del Escritorio (hacer **antes** de P8; no necesita administrador)
La copia de `C:\Users\albor\Mantenimiento` es la de P6 y le falta la purga de memoria de prioridad baja. El instalador la actualiza, agrega el perfil del Nitro con su acceso directo "Perfil Nitro" y conserva `v4.1_retirada\`, `logs\` y los respaldos.
```powershell
cd D:\Mis-cosas; git fetch origin; git checkout claude/perfil-nitro; git pull --ff-only
powershell -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\pedidos\Instalar.ps1
```
Debe mostrar `Purga de prioridad baja: True` y `Mantenimiento: Fallas: 0 | Perfil: Fallas: 0`. Si no, reportar y NO seguir con P8. Reportar la salida literal.

## P12 · cerrado · GTX 1650 permanente para SAP2000 y MATLAB (sin administrador y sin intervención de Nicolás)
Nicolás pidió que quede configurado sin que él haga nada. La preferencia de GPU vive en HKCU: **no usar Ejecutar-Elevado**. Se puede hacer en cualquier momento, también antes de P8.
```powershell
cd D:\Mis-cosas; git fetch origin; git checkout claude/perfil-nitro; git pull --ff-only
powershell -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\pedidos\P12-gpu.ps1
git checkout main
```
El script aplica el ajuste `gpu-dedicada-ingenieria` y lo verifica: si SAP2000 no está abierto, lo abre con `D:\Modelos RUN\PRACTICA RODRIGO.sdb`, espera 40 s, revisa con `nvidia-smi` y los contadores de GPU qué tarjeta usa, y cierra solo esa instancia sin guardar cambios. Si Nicolás está usando SAP2000, lo verifica sin cerrarlo. Reportar la salida literal; en la bitácora anotar `OK` si `SAP2000.exe` aparece en la lista de procesos de `nvidia-smi`, o `ERROR` si no.

## P13 · cerrado · Parte de P10 que exige administrador (un doble clic de Nicolás)
Tu sesión no puede pedir el permiso de Windows (UAC), así que esto lo lanza Nicolás. Pídeselo así, una sola vez: *"Haz doble clic en `D:\Mis-cosas\antigravity-pc\pedidos\P13-admin.bat` y acepta el permiso"*. Antes:
```powershell
cd D:\Mis-cosas; git fetch origin; git checkout claude/perfil-nitro; git pull --ff-only
```
Cuando termine, lee el log y repórtalo literal (es solo lectura; `sfc` tarda unos minutos):
```powershell
Get-Content (Get-ChildItem "$env:USERPROFILE\Mantenimiento\logs\P13_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```
En la misma pasada, en el navegador, abre la página de soporte de Acer del **Nitro AN515-43** y anota sin descargar nada: última versión de BIOS con su fecha y sus notas, y si aparece alguna actualización de firmware o de "Secure Boot".

## P14 · cerrado · Verificar por nombre qué GPU usa SAP2000 (sin intervención)
P12 aplicó la preferencia, pero SAP2000 ya estaba abierto y siguió en otro adaptador: la preferencia rige desde la próxima apertura. Este script **espera solo** a que Nicolás cierre SAP2000 (revisa cada 5 min, hasta 6 h), lo abre con el modelo, identifica la GPU por nombre (DXGI) y lo cierra:
```powershell
cd D:\Mis-cosas; git checkout claude/perfil-nitro; git pull --ff-only
powershell -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\pedidos\P14-verificar-gpu.ps1
git checkout main
```
Reportar literal. Bitácora: `OK` si dice `RESULTADO: SAP2000 usa la GTX 1650`, `ERROR` si no.

## Corrección de lectura de P13 (leer antes de seguir)
`DISM /CheckHealth` dijo **"The component store is repairable"**: eso significa que **encontró daño reparable**, no que esté sano. Y el resultado de `sfc` no aparece en el log, así que no se puede afirmar que no hay archivos dañados. Los Volsnap 36 tampoco son normales: el tope de 2.21 GB borra puntos de restauración recientes. Reportar siempre la salida literal y no interpretarla como OK si no lo dice.

## P15 · cerrado · SAP2000 en modo DirectX (sin administrador y sin intervención)
Buen diagnóstico en P14: `GraphicsMode=GDIPlus` hace que SAP2000 dibuje por software. El script espera a que SAP2000 esté cerrado, respalda el `.ini`, cambia a `GraphicsMode=DirectX` y vuelve a verificar con P14:
```powershell
cd D:\Mis-cosas; git fetch origin; git checkout claude/perfil-nitro; git pull --ff-only
powershell -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\pedidos\P15-sap-directx.ps1
git checkout main
```
Bitácora: `OK` si termina con `RESULTADO: SAP2000 usa la GTX 1650` y el modo gráfico al cerrar sigue en `DirectX`; si SAP2000 no reconoce el valor y lo devuelve a `GDIPlus`, `ERROR` con la salida literal (el respaldo del `.ini` queda en `Mantenimiento\respaldo-ini\`).

## P16 · cerrado · Reparar Windows y proteger los puntos de restauración (un doble clic de Nicolás)
Pídele: *"Haz doble clic en `D:\Mis-cosas\antigravity-pc\pedidos\P16-admin.bat` y acepta el permiso; tarda entre 15 y 30 minutos"*. Hace `DISM /RestoreHealth`, `DISM /CheckHealth`, `sfc /scannow`, sube a 5 GB el espacio de puntos de restauración y deja Google Update en inicio manual. Al terminar, leer el log y reportarlo literal:
```powershell
Get-Content (Get-ChildItem "$env:USERPROFILE\Mantenimiento\logs\P16_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

## P17 · cerrado · Integrar `claude/perfil-nitro` a `main` (sin administrador ni intervención)
P15 y P16 quedaron verificados. Buena solución la de la sangría del `.ini` en P15: el script ya la acepta (commit `44adf4c`). Ahora se integra todo lo del PC a `main`, como indica la regla 04:
```powershell
cd D:\Mis-cosas; git fetch origin; git checkout claude/perfil-nitro; git pull --ff-only
powershell -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\mantenimiento\pruebas\Pruebas.ps1 | Select-Object -Last 1
powershell -NoProfile -ExecutionPolicy Bypass -File antigravity-pc\perfil-nitro\pruebas\Pruebas.ps1 | Select-Object -Last 1
git status --porcelain
git checkout main; git pull --ff-only
git merge --squash claude/perfil-nitro; git commit -m "feat(antigravity-pc): perfil del Nitro, mantenimiento final, pedidos P8-P16"
$env:ALLOW_MAIN_PUSH = '1'; git push origin main; Remove-Item Env:ALLOW_MAIN_PUSH
git log --oneline -1
```
Si alguna prueba no termina en `Fallas: 0` o `git status --porcelain` no sale vacío, reportar y NO hacer el merge. Reportar literal.

## Sin pedidos abiertos (2026-11-03)
Todo lo del PC está en `main` (`a571ce3`). P4 (memoria durante un análisis en SAP2000) queda opcional: hacerlo solo si Nicolás lo pide.
