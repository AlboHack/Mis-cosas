# Pruebas sin dependencias (Pester no está en todos los equipos). Uso: pwsh -File pruebas/Pruebas.ps1
# Sale con código 1 si alguna falla. En Windows agrega pruebas de humo contra el sistema real.
$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot
Import-Module (Join-Path $raiz 'Mantenimiento.psm1') -Force
$script:fallas = 0

function Probar([string]$Nombre, [scriptblock]$Bloque) {
    try {
        if (& $Bloque) { Write-Host "OK    $Nombre" } else { Write-Host "FALLA $Nombre"; $script:fallas++ }
    } catch { Write-Host "FALLA $Nombre -> $_"; $script:fallas++ }
}

# --- sintaxis de todos los scripts
# Solo los archivos propios: instalada, la carpeta también guarda v4.1_retirada\ y el perfil del Nitro
foreach ($f in @('Mantenimiento.ps1', 'Mantenimiento.psm1', 'pruebas\Pruebas.ps1') | ForEach-Object { Get-Item (Join-Path $raiz $_) }) {
    Probar "sintaxis $($f.Name)" {
        $err = $null
        [System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$null, [ref]$err) | Out-Null
        -not $err
    }
    Probar "UTF-8 con BOM $($f.Name) (PowerShell 5.1 lee sin BOM como ANSI)" {
        $b = [IO.File]::ReadAllBytes($f.FullName); $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF
    }
}

# --- purga: criterio ISLC
Probar 'purga con standby grande y libre escaso' { Test-PurgaConveniente -StandbyMB 3000 -LibreMB 400 }
Probar 'sin purga con libre suficiente' { -not (Test-PurgaConveniente -StandbyMB 3000 -LibreMB 2000) }
Probar 'sin purga con standby chica' { -not (Test-PurgaConveniente -StandbyMB 500 -LibreMB 400) }
Probar 'borde: standby = umbral purga, libre = umbral no' {
    (Test-PurgaConveniente -StandbyMB 1024 -LibreMB 1023) -and -not (Test-PurgaConveniente -StandbyMB 1024 -LibreMB 1024)
}

# --- líneas de desinstalación
Probar 'ruta entre comillas con argumentos' {
    $c = Split-LineaComando '"C:\Program Files\CCleaner\uninst.exe" /S'
    $c.Archivo -eq 'C:\Program Files\CCleaner\uninst.exe' -and $c.Argumentos -eq '/S'
}
Probar 'ruta sin comillas con espacios' {
    $c = Split-LineaComando 'D:\Program Files (x86)\IObit\Smart Defrag\unins000.exe /X'
    $c.Archivo -eq 'D:\Program Files (x86)\IObit\Smart Defrag\unins000.exe' -and $c.Argumentos -eq '/X'
}
Probar 'MSI /I se convierte en /x silencioso' {
    $c = Get-ComandoDesinstalacion ([pscustomobject]@{ UninstallString = 'MsiExec.exe /I{0471996C-B0F0-4A69-AE8B-9B0C3A0D37B3}' })
    $c.Archivo -eq 'msiexec.exe' -and $c.Argumentos -eq '/x {0471996C-B0F0-4A69-AE8B-9B0C3A0D37B3} /qn /norestart'
}
Probar 'QuietUninstallString tiene prioridad' {
    $e = [pscustomobject]@{ UninstallString = '"C:\a\u.exe"'; QuietUninstallString = '"C:\a\u.exe" /quiet' }
    (Get-ComandoDesinstalacion $e -ArgsSilencio '/S').Argumentos -eq '/quiet'
}
Probar 'agrega silencio sin duplicarlo' {
    $a = (Get-ComandoDesinstalacion ([pscustomobject]@{ UninstallString = '"C:\a\u.exe" /S' }) -ArgsSilencio '/S').Argumentos
    $b = (Get-ComandoDesinstalacion ([pscustomobject]@{ UninstallString = '"C:\a\u.exe"' }) -ArgsSilencio '/S').Argumentos
    $a -eq '/S' -and $b -eq '/S'
}

# --- coincidencia de programas
$reg = @('SAP2000 19', 'SAP2000 27', 'Brave', 'BraveSoftware Update', 'CCleaner', 'IObit Smart Defrag') |
    ForEach-Object { [pscustomobject]@{ DisplayName = $_ } }
Probar 'SAP2000 19 no toca SAP2000 27' {
    $r = @(Find-ProgramaRegistrado $reg '^SAP2000 19'); $r.Count -eq 1 -and $r[0].DisplayName -eq 'SAP2000 19'
}
Probar 'protegido nunca coincide' { @(Find-ProgramaRegistrado $reg '^SAP2000' -Protegidos '^SAP2000 2[0-9]').Count -eq 1 }
Probar '^Brave$ no toca BraveSoftware Update' { @(Find-ProgramaRegistrado $reg '^Brave$').Count -eq 1 }
Probar 'patrón con prefijo opcional' { @(Find-ProgramaRegistrado $reg '^(IObit )?Smart Defrag').Count -eq 1 }

# --- rutas de residuos
Probar 'rechaza raíces y carpetas de sistema o perfil' {
    -not ((('C:\', 'D:', 'C:\Windows', 'C:\Program Files', 'C:\Users', 'C:\Users\Nico', 'C:\Users\Nico\AppData\Roaming',
            'D:\Mis-cosas', 'C:\Users\Nico\OneDrive\Escritorio', '%APPDATA%\x') | ForEach-Object { Test-RutaResiduoSegura $_ }) -contains $true)
}
Probar 'acepta carpetas de programa' {
    -not ((('D:\Lightworks', 'C:\ProgramData\CCleaner', 'C:\Users\Nico\AppData\Local\PrivaZer') |
            ForEach-Object { Test-RutaResiduoSegura $_ }) -contains $false)
}

# --- configuración
$cfg = Get-Content (Join-Path $raiz 'programas_a_quitar.json') -Raw -Encoding UTF8 | ConvertFrom-Json
Probar 'todos los patrones anclados con ^' { -not ($cfg.programas | Where-Object { -not $_.patron.StartsWith('^') }) }
Probar 'ningún programa activo coincide con un protegido' {
    -not ($cfg.programas | Where-Object { $_.activo -and (Test-Protegido $_.nombre $cfg.protegidos) })
}
Probar 'Brave inactivo hasta que Nicolás decida' { -not ($cfg.programas | Where-Object nombre -eq 'Brave').activo }
Probar 'residuos seguros con un perfil típico' {
    $env:APPDATA = 'C:\Users\Nico\AppData\Roaming'; $env:LOCALAPPDATA = 'C:\Users\Nico\AppData\Local'; $env:ProgramData = 'C:\ProgramData'
    -not ($cfg.programas.residuos | Where-Object { -not (Test-RutaResiduoSegura ([Environment]::ExpandEnvironmentVariables($_))) })
}
Probar 'simulación de desinstalación no ejecuta nada' {
    $falsos = @([pscustomobject]@{ DisplayName = 'CCleaner'; UninstallString = '"C:\no\existe.exe"' })
    Uninstall-Programas -Instalados $falsos -WhatIf 6>$null 3>$null
    $true
}

# --- humo en Windows real (runner de GitHub o el Nitro)
if ([System.Environment]::OSVersion.Platform -eq 'Win32NT') {
    Probar 'estado de memoria legible' { $m = Get-EstadoMemoria; $m.DisponibleMB -gt 0 -and $m.StandbyMB -ge 0 }
    Probar 'temporales en simulación' { (Clear-Temporales -WhatIf).Archivos -eq 0 }
    Probar 'programas instalados legibles' { @(Get-ProgramasInstalados).Count -gt 0 }
    if (Test-Administrador) {
        Probar 'purga forzada devuelve STATUS_SUCCESS' { $null -ne (Invoke-PurgaStandby -Forzar) }
    }
}

Write-Host "`nFallas: $script:fallas"
exit [int]($script:fallas -gt 0)
