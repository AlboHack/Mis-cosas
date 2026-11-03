<#
Mantenimiento del Acer Nitro 5 (Windows 11). Reemplaza a optimizacion/ (Nitro_Optimizer v4.1).
Toda acción que borra o cambia el sistema acepta -WhatIf; la lógica de decisión es pura y se prueba
en pruebas/Pruebas.ps1 (Linux y Windows) y en el workflow pc-mantenimiento (runner Windows real).
#>
Set-StrictMode -Version Latest
$EsWindows = [System.Environment]::OSVersion.Platform -eq 'Win32NT'

# ---------------------------------------------------------------- registro
$script:DirLog = if ($EsWindows) { Join-Path $env:LOCALAPPDATA 'Mantenimiento\logs' } else { Join-Path ([IO.Path]::GetTempPath()) 'Mantenimiento' }

function Write-Registro {
    param([Parameter(Mandatory)][string]$Mensaje)
    if (-not (Test-Path $script:DirLog)) { New-Item -ItemType Directory -Path $script:DirLog -Force | Out-Null }
    $archivo = Join-Path $script:DirLog ("{0:yyyyMMdd}.log" -f (Get-Date))
    "[{0:HH:mm:ss}] {1}" -f (Get-Date), $Mensaje | Add-Content -Path $archivo -Encoding UTF8
}

function Test-Administrador {
    if (-not $EsWindows) { return $false }
    ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

# ---------------------------------------------------------------- lógica pura
function Test-PurgaConveniente {
    # Criterio de ISLC: purgar solo con standby grande y memoria libre escasa. Fuera de ese caso,
    # la standby es caché útil que Windows entrega al instante y purgarla obliga a releer del disco.
    param(
        [Parameter(Mandatory)][double]$StandbyMB,
        [Parameter(Mandatory)][double]$LibreMB,
        [double]$UmbralStandbyMB = 1024,
        [double]$UmbralLibreMB = 1024
    )
    ($StandbyMB -ge $UmbralStandbyMB) -and ($LibreMB -lt $UmbralLibreMB)
}

function Split-LineaComando {
    # Separa ejecutable y argumentos de una UninstallString del registro.
    param([Parameter(Mandatory)][string]$Linea)
    $l = $Linea.Trim()
    if ($l.StartsWith('"')) {
        $fin = $l.IndexOf('"', 1)
        return [pscustomobject]@{ Archivo = $l.Substring(1, $fin - 1); Argumentos = $l.Substring($fin + 1).Trim() }
    }
    $m = [regex]::Match($l, '^(.+?\.exe)(\s+.*)?$', 'IgnoreCase')
    if ($m.Success) { return [pscustomobject]@{ Archivo = $m.Groups[1].Value; Argumentos = $m.Groups[2].Value.Trim() } }
    [pscustomobject]@{ Archivo = $l; Argumentos = '' }
}

function Get-ComandoDesinstalacion {
    # Prioridad: MSI (msiexec /x silencioso) > QuietUninstallString > UninstallString + argumentos de silencio.
    param([Parameter(Mandatory)]$Entrada, [string]$ArgsSilencio = '')
    $us = [string]$Entrada.UninstallString
    $guid = [regex]::Match($us, '\{[0-9A-Fa-f\-]{36}\}')
    if ($us -match '(?i)msiexec' -and $guid.Success) {
        return [pscustomobject]@{ Archivo = 'msiexec.exe'; Argumentos = "/x $($guid.Value) /qn /norestart" }
    }
    $quiet = $Entrada.PSObject.Properties['QuietUninstallString']
    if ($quiet -and $quiet.Value) { return Split-LineaComando $quiet.Value }
    if (-not $us) { return $null }
    $c = Split-LineaComando $us
    if ($ArgsSilencio -and $c.Argumentos -notlike "*$ArgsSilencio*") { $c.Argumentos = ("$($c.Argumentos) $ArgsSilencio").Trim() }
    $c
}

function Test-Protegido {
    param([Parameter(Mandatory)][string]$Nombre, [string[]]$Protegidos = @())
    foreach ($p in $Protegidos) { if ($Nombre -match $p) { return $true } }
    $false
}

function Find-ProgramaRegistrado {
    # Patrón anclado (^...) sobre DisplayName; un programa protegido nunca coincide.
    param([object[]]$Entradas = @(), [Parameter(Mandatory)][string]$Patron, [string[]]$Protegidos = @())
    @($Entradas | Where-Object { $_ -and $_.DisplayName -match $Patron -and -not (Test-Protegido $_.DisplayName $Protegidos) })
}

function Test-RutaResiduoSegura {
    # Un residuo es una carpeta bajo la raíz de una unidad que no es de sistema ni de perfil.
    param([Parameter(Mandatory)][string]$Ruta)
    $r = $Ruta.TrimEnd('\', '/')
    $partes = @($r -split '[\\/]' | Where-Object { $_ })
    if ($partes.Count -lt 2 -or $r -match '%') { return $false }
    if ($partes[1] -eq 'Users' -and $partes.Count -le 3) { return $false }
    $hojas = 'Program Files', 'Program Files (x86)', 'ProgramData', 'Windows', 'Users', 'AppData', 'Local',
             'Roaming', 'Escritorio', 'Desktop', 'OneDrive', 'Documents', 'Documentos', 'Mis-cosas'
    -not ($hojas -contains $partes[-1])
}

function Select-ArchivosAntiguos {
    param([object[]]$Archivos = @(), [Parameter(Mandatory)][datetime]$Limite)
    @($Archivos | Where-Object { -not $_.PSIsContainer -and $_.LastWriteTime -lt $Limite })
}

# ---------------------------------------------------------------- memoria
function Get-EstadoMemoria {
    # Win32_PerfRawData_PerfOS_Memory no depende del idioma de Windows (Get-Counter sí).
    $m = Get-CimInstance Win32_PerfRawData_PerfOS_Memory
    $standby = $m.StandbyCacheNormalPriorityBytes + $m.StandbyCacheReserveBytes + $m.StandbyCacheCoreBytes
    [pscustomobject]@{
        DisponibleMB = [double]$m.AvailableMBytes
        LibreMB      = [math]::Round($m.FreeAndZeroPageListBytes / 1MB, 0)
        StandbyMB    = [math]::Round($standby / 1MB, 0)
        CommitMB     = [math]::Round($m.CommittedBytes / 1MB, 0)
        LimiteMB     = [math]::Round($m.CommitLimit / 1MB, 0)
    }
}

$script:CodigoNativo = @'
using System;
using System.Runtime.InteropServices;
public static class MemoriaNt {
    [DllImport("ntdll.dll")] static extern uint RtlAdjustPrivilege(int p, bool enable, bool thread, out bool prev);
    [DllImport("ntdll.dll")] static extern uint NtSetSystemInformation(int clase, ref int info, int largo);
    // SeProfileSingleProcessPrivilege (13) viene deshabilitado incluso en un token de administrador.
    public static uint PurgarStandby() {
        bool prev;
        uint st = RtlAdjustPrivilege(13, true, false, out prev);
        if (st != 0) return st;
        int orden = 4; // MemoryPurgeStandbyList
        return NtSetSystemInformation(80, ref orden, 4); // SystemMemoryListInformation
    }
}
'@

function Invoke-PurgaStandby {
    [CmdletBinding(SupportsShouldProcess)]
    param([switch]$Forzar)
    $antes = Get-EstadoMemoria
    if (-not $Forzar -and -not (Test-PurgaConveniente -StandbyMB $antes.StandbyMB -LibreMB $antes.LibreMB)) {
        Write-Host "Purga innecesaria: standby $($antes.StandbyMB) MB, libre $($antes.LibreMB) MB."
        return $antes
    }
    if (-not (Test-Administrador)) { throw 'La purga de standby requiere administrador.' }
    if (-not $PSCmdlet.ShouldProcess('lista standby', 'Purgar')) { return $antes }
    if (-not ('MemoriaNt' -as [type])) { Add-Type -TypeDefinition $script:CodigoNativo }
    $st = [MemoriaNt]::PurgarStandby()
    if ($st -ne 0) { throw ('NtSetSystemInformation devolvió 0x{0:X8}' -f $st) }
    $despues = Get-EstadoMemoria
    Write-Registro "Purga standby: libre $($antes.LibreMB) -> $($despues.LibreMB) MB"
    $despues
}

# ---------------------------------------------------------------- GPU, prioridad y energía
function Set-GpuAltoRendimiento {
    # Preferencia de Configuración > Pantalla > Gráficos (GpuPreference=2: GPU dedicada).
    [CmdletBinding(SupportsShouldProcess)]
    param([Parameter(Mandatory)][string[]]$Ejecutables)
    $clave = 'HKCU:\Software\Microsoft\DirectX\UserGpuPreferences'
    foreach ($exe in $Ejecutables) {
        if (-not (Test-Path $exe)) { Write-Warning "No existe: $exe"; continue }
        if ($PSCmdlet.ShouldProcess($exe, 'GpuPreference=2')) {
            if (-not (Test-Path $clave)) { New-Item -Path $clave -Force | Out-Null }
            New-ItemProperty -Path $clave -Name $exe -Value 'GpuPreference=2;' -PropertyType String -Force | Out-Null
            Write-Registro "GPU dedicada: $exe"
        }
    }
}

function Set-PrioridadProcesos {
    [CmdletBinding(SupportsShouldProcess)]
    param([Parameter(Mandatory)][string[]]$Nombres, [string]$Prioridad = 'AboveNormal')
    foreach ($p in Get-Process -Name $Nombres -ErrorAction SilentlyContinue) {
        if ($PSCmdlet.ShouldProcess("$($p.ProcessName) ($($p.Id))", "Prioridad $Prioridad")) {
            $p.PriorityClass = $Prioridad
        }
    }
}

$script:ArchivoPlan = Join-Path $script:DirLog 'plan_energia_anterior.txt'

function Start-SesionCalculo {
    # Plan Alto rendimiento mientras dura el cálculo; Stop-SesionCalculo restaura el plan anterior.
    [CmdletBinding(SupportsShouldProcess)]
    param([string[]]$Ejecutables = @(
        'C:\Program Files\Computers and Structures\SAP2000 27\SAP2000.exe', 'D:\Matlab\bin\matlab.exe'))
    $actual = [regex]::Match((powercfg /getactivescheme), '[0-9a-f\-]{36}').Value
    if ($PSCmdlet.ShouldProcess('plan de energía', 'Alto rendimiento')) {
        if (-not (Test-Path $script:ArchivoPlan)) {
            New-Item -ItemType Directory -Path $script:DirLog -Force | Out-Null
            $actual | Set-Content $script:ArchivoPlan
        }
        powercfg /setactive SCHEME_MIN | Out-Null
        Write-Registro "Sesión de cálculo: plan $actual -> Alto rendimiento"
    }
    Set-GpuAltoRendimiento -Ejecutables $Ejecutables
    Set-PrioridadProcesos -Nombres 'SAP2000', 'SAPFire', 'MATLAB'
    if ((Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue).BatteryStatus -eq 1) {
        Write-Warning 'El notebook está a batería: conéctalo antes de un cálculo largo.'
    }
}

function Stop-SesionCalculo {
    [CmdletBinding(SupportsShouldProcess)]
    param()
    if (-not (Test-Path $script:ArchivoPlan)) { Write-Host 'No hay sesión de cálculo abierta.'; return }
    $anterior = (Get-Content $script:ArchivoPlan -Raw).Trim()
    if ($PSCmdlet.ShouldProcess('plan de energía', "Restaurar $anterior")) {
        powercfg /setactive $anterior | Out-Null
        Remove-Item $script:ArchivoPlan
        Write-Registro "Sesión de cálculo cerrada: plan $anterior"
    }
}

# ---------------------------------------------------------------- limpieza y discos
function Clear-Temporales {
    # Borra solo archivos con más de $Dias días: lo reciente puede estar en uso por un instalador.
    # No toca la papelera, las cachés de shaders (su borrado provoca tirones al recompilar) ni los volcados.
    [CmdletBinding(SupportsShouldProcess)]
    param([int]$Dias = 7)
    $carpetas = @($env:TEMP, 'C:\ProgramData\Microsoft\Windows\WER\ReportArchive', 'C:\ProgramData\Microsoft\Windows\WER\ReportQueue')
    if (Test-Administrador) { $carpetas += 'C:\Windows\Temp' }
    $limite = (Get-Date).AddDays(-$Dias)
    $bytes = 0; $n = 0
    foreach ($c in $carpetas | Where-Object { $_ -and (Test-Path $_) }) {
        $viejos = Select-ArchivosAntiguos -Archivos @(Get-ChildItem $c -Recurse -Force -File -ErrorAction SilentlyContinue) -Limite $limite
        foreach ($a in $viejos) {
            if ($PSCmdlet.ShouldProcess($a.FullName, 'Borrar')) {
                try { Remove-Item $a.FullName -Force -ErrorAction Stop; $bytes += $a.Length; $n++ } catch { }
            }
        }
    }
    Write-Registro "Temporales: $n archivos, $([math]::Round($bytes / 1MB, 1)) MB"
    [pscustomobject]@{ Archivos = $n; MB = [math]::Round($bytes / 1MB, 1) }
}

function Get-TipoUnidad {
    param([Parameter(Mandatory)][string]$Letra)
    $disco = Get-Partition -DriveLetter $Letra.TrimEnd(':') | Get-Disk
    (Get-PhysicalDisk | Where-Object DeviceId -eq "$($disco.Number)").MediaType
}

function Invoke-OptimizarUnidad {
    # SSD: solo retrim. HDD: desfragmentación. El tipo se lee del disco, no se supone por la letra.
    [CmdletBinding(SupportsShouldProcess)]
    param([Parameter(Mandatory)][string]$Letra)
    $tipo = Get-TipoUnidad $Letra
    $arg = switch ($tipo) { 'SSD' { "$($Letra): /L /U" } 'HDD' { "$($Letra): /U /V" } default { $null } }
    if (-not $arg) { Write-Warning "Tipo de unidad desconocido ($tipo) en $($Letra):; no se optimiza."; return }
    if ($PSCmdlet.ShouldProcess("$($Letra): ($tipo)", "defrag $arg")) {
        $p = Start-Process defrag.exe -ArgumentList $arg -NoNewWindow -PassThru -Wait
        Write-Registro "defrag $arg -> código $($p.ExitCode)"
        $p.ExitCode
    }
}

function Get-Diagnostico {
    [pscustomobject]@{
        Memoria  = Get-EstadoMemoria
        Discos   = Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus, OperationalStatus
        TrimNTFS = (fsutil behavior query DisableDeleteNotify | Select-String 'NTFS') -join ''
        Procesos = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 ProcessName, Id,
                   @{ n = 'MB'; e = { [math]::Round($_.WorkingSet64 / 1MB, 0) } }
        GpuPrefs = Get-ItemProperty 'HKCU:\Software\Microsoft\DirectX\UserGpuPreferences' -ErrorAction SilentlyContinue
    }
}

# ---------------------------------------------------------------- desinstalación
function Get-ProgramasInstalados {
    $raices = 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
              'HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
              'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'
    @(Get-ItemProperty $raices -ErrorAction SilentlyContinue | Where-Object { $_.PSObject.Properties['DisplayName'] -and $_.DisplayName })
}

function Uninstall-Programas {
    # Lee programas_a_quitar.json. Corre el desinstalador oficial de cada programa activo y después
    # borra solo los residuos listados, si el programa ya no figura en el registro. Usar primero con -WhatIf.
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
    param([string]$Config = (Join-Path $PSScriptRoot 'programas_a_quitar.json'), [object[]]$Instalados)
    $cfg = Get-Content $Config -Raw -Encoding UTF8 | ConvertFrom-Json
    if (-not $PSBoundParameters.ContainsKey('Instalados')) { $Instalados = Get-ProgramasInstalados }
    foreach ($prog in @($cfg.programas | Where-Object activo)) {
        foreach ($e in Find-ProgramaRegistrado -Entradas $Instalados -Patron $prog.patron -Protegidos $cfg.protegidos) {
            $cmd = Get-ComandoDesinstalacion -Entrada $e -ArgsSilencio $prog.silencio
            if (-not $cmd) { Write-Warning "$($e.DisplayName): sin UninstallString"; continue }
            if ($PSCmdlet.ShouldProcess($e.DisplayName, "$($cmd.Archivo) $($cmd.Argumentos)")) {
                $p = Start-Process -FilePath $cmd.Archivo -ArgumentList $cmd.Argumentos -PassThru -Wait
                Write-Registro "Desinstalado $($e.DisplayName): código $($p.ExitCode)"
            }
        }
    }
    # Un residuo compartido (p. ej. %ProgramData%\IObit) se conserva mientras otro programa que lo usa siga instalado.
    $siguen = @(if (-not $WhatIfPreference) { Get-ProgramasInstalados })
    $ocupadas = @($cfg.programas | Where-Object { @(Find-ProgramaRegistrado -Entradas $siguen -Patron $_.patron).Count } |
                  ForEach-Object { @($_.residuos) })
    foreach ($prog in @($cfg.programas | Where-Object activo)) {
        if (@(Find-ProgramaRegistrado -Entradas $siguen -Patron $prog.patron).Count) {
            Write-Warning "$($prog.nombre) sigue instalado; no se borran sus residuos."; continue
        }
        foreach ($r in @($prog.residuos | Where-Object { $ocupadas -notcontains $_ })) {
            $ruta = [Environment]::ExpandEnvironmentVariables($r)
            if (-not (Test-RutaResiduoSegura $ruta)) { Write-Warning "Ruta rechazada por seguridad: $ruta"; continue }
            if ((Test-Path $ruta) -and $PSCmdlet.ShouldProcess($ruta, 'Borrar residuo')) {
                Remove-Item $ruta -Recurse -Force
                Write-Registro "Residuo borrado: $ruta"
            }
        }
    }
}

Export-ModuleMember -Function Test-PurgaConveniente, Split-LineaComando, Get-ComandoDesinstalacion, Test-Protegido,
    Find-ProgramaRegistrado, Test-RutaResiduoSegura, Select-ArchivosAntiguos, Get-EstadoMemoria, Invoke-PurgaStandby,
    Set-GpuAltoRendimiento, Set-PrioridadProcesos, Start-SesionCalculo, Stop-SesionCalculo, Clear-Temporales,
    Get-TipoUnidad, Invoke-OptimizarUnidad, Get-Diagnostico, Get-ProgramasInstalados, Uninstall-Programas,
    Test-Administrador, Write-Registro
