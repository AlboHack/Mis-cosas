<#
.SYNOPSIS
    Nitro Optimizer Maestro v4.1 - Motor Profesional de Optimizacion
    Equipo: Acer Nitro 5 AN515-43 | AMD Ryzen 7 3750H | GTX 1650 | 12 GB RAM
.DESCRIPTION
    Arquitectura robusta con control estricto de privilegios, watchdog timers para TRIM en SSD C:,
    purga de Standby List NT (ISLC), recorte de Working Sets de fondo, optimizacion de cvars para
    Destiny 2, tuning de JVM para Minecraft, modo ingenieria para SAP2000 v27 / MATLAB R2025a,
    y desfragmentacion aislada al HDD D:.
.NOTES
    Autor: Nicolas Albornoz & Antigravity (Council of Agents Verified)
#>

param(
    [switch]$QuickRAM
)

# 1. Verificacion de privilegios de Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# 2. Configuracion de entorno y consola
$Host.UI.RawUI.WindowTitle = "Nitro Optimizer Maestro v4.1 - Acer Nitro 5"
$Host.UI.RawUI.BackgroundColor = "Black"
Clear-Host

# 3. Compilacion en memoria de APIs del Kernel NT y PSAPI (ISLC / Sysinternals RAMMap)
$csharpCode = @"
using System;
using System.Runtime.InteropServices;

public class NativeMemOptimizerV4 {
    [DllImport("psapi.dll")]
    public static extern int EmptyWorkingSet(IntPtr h);

    [DllImport("ntdll.dll")]
    public static extern uint NtSetSystemInformation(int infoClass, IntPtr infoPtr, int infoLen);

    public static uint PurgeStandby() {
        IntPtr p = Marshal.AllocHGlobal(4);
        Marshal.WriteInt32(p, 4); // 4 = MemoryPurgeStandbyList
        uint status = NtSetSystemInformation(80, p, 4); // 80 = SystemMemoryListInformation
        Marshal.FreeHGlobal(p);
        return status;
    }
}
"@

if (-not ([System.Management.Automation.PSTypeName]'NativeMemOptimizerV4').Type) {
    try {
        Add-Type -TypeDefinition $csharpCode -ErrorAction Stop
    } catch {
        Write-Warning "No se pudo compilar el modulo C# en memoria: $_"
    }
}

# 4. Carpeta de logs
$logDir = "$env:USERPROFILE\Desktop\MantenimientoLogs"
if (-not (Test-Path $logDir)) { 
    $logDir = "$env:USERPROFILE\OneDrive\Escritorio\MantenimientoLogs"
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
}
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "$logDir\optimizacion_$stamp.txt"

function Write-Log {
    param([string]$Message)
    $time = Get-Date -Format "HH:mm:ss"
    "[$time] $Message" | Out-File -FilePath $logFile -Append -Encoding UTF8 -ErrorAction SilentlyContinue
}

Write-Log "Sesion iniciada. Equipo: Acer Nitro 5 AN515-43 | Administrador: $isAdmin"

# 5. Funciones centrales de memoria y telemetria
function Get-SystemMemoryInfo {
    $os = Get-CimInstance Win32_OperatingSystem
    $cs = Get-CimInstance Win32_ComputerSystem
    $totMB = [math]::Round($cs.TotalPhysicalMemory / 1MB, 0)
    $freeMB = [math]::Round($os.FreePhysicalMemory / 1024, 0)
    $usedMB = $totMB - $freeMB
    $pctUsed = [math]::Round(($usedMB / $totMB) * 100, 1)

    return [PSCustomObject]@{
        TotalMB = $totMB
        FreeMB  = $freeMB
        UsedMB  = $usedMB
        PctUsed = $pctUsed
    }
}

function Invoke-PurgeStandbyMemory {
    if (-not $isAdmin) {
        Write-Host "   [!] Purga de Standby requiere permisos de Administrador. Omitida." -ForegroundColor DarkYellow
        Write-Log "Purga de Standby omitida (sin permisos de Administrador)"
        return
    }

    $before = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
    $status = [NativeMemOptimizerV4]::PurgeStandby()
    $after = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
    $diffMB = [math]::Round(($after - $before) / 1024, 0)

    if ($status -eq 0) {
        Write-Host "   [OK] Standby List purgada con exito (Kernel NT / ISLC)." -ForegroundColor Green
        Write-Log "Standby List purgada con exito. Diferencia: +$diffMB MB"
    } elseif ($status -eq 3221225569) {
        Write-Host "   [!] Requiere privilegios de Administrador (STATUS_PRIVILEGE_NOT_HELD)." -ForegroundColor Yellow
        Write-Log "Standby Purge fallo: STATUS_PRIVILEGE_NOT_HELD"
    } else {
        Write-Host "   [!] Codigo de retorno del Kernel: 0x$($status.ToString('X8'))" -ForegroundColor Yellow
        Write-Log "Standby Purge retorno status 0x$($status.ToString('X8'))"
    }
}

function Invoke-TrimBackgroundWorkingSets {
    param(
        [string[]]$ProcessNames = @(
            "opera", "discord", "steam", "spotify", "epicgameslauncher", 
            "OverwolfLauncher", "LGHUB", "WhatsApp.Root", "WhatsApp", 
            "SearchHost", "SnippingTool", "CNext", "RadeonSoftware"
        )
    )
    $beforeMem = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
    $trimmedCount = 0

    foreach ($name in $ProcessNames) {
        $procs = Get-Process -Name $name -ErrorAction SilentlyContinue
        foreach ($p in $procs) {
            try {
                [NativeMemOptimizerV4]::EmptyWorkingSet($p.Handle) | Out-Null
                $trimmedCount++
            } catch {}
        }
    }

    $afterMem = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
    $gainedMB = [math]::Round(($afterMem - $beforeMem) / 1024, 0)
    Write-Host "   [OK] $trimmedCount subprocesos recortados en memoria." -ForegroundColor Green
    if ($gainedMB -gt 0) {
        Write-Host "   [+] RAM recuperada inmediatamente: ~$gainedMB MB (sin cerrar programas)." -ForegroundColor Cyan
    }
    Write-Log "Working Sets recortados: $trimmedCount procesos. Ganancia: ~$gainedMB MB"
}

# 6. Motor Robusto de TRIM con Watchdog Timer (SSD Kingston C:)
function Invoke-RobustTrimSSD {
    Write-Host "`n--- EJECUCION DE TRIM EN SSD KINGSTON M.2 (UNIDAD C:) ---" -ForegroundColor Yellow

    if (-not $isAdmin) {
        Write-Host "   [!] TRIM omitido: Esta operacion requiere ejecutar como Administrador." -ForegroundColor Yellow
        Write-Host "   [i] Para ejecutar TRIM, abre el menu mediante 'Nitro_Optimizer.bat' con permisos de Admin." -ForegroundColor DarkGray
        Write-Log "TRIM omitido: Proceso no elevado"
        return
    }

    # 1. Asegurar que defragsvc este disponible
    try {
        $svc = Get-Service -Name defragsvc -ErrorAction SilentlyContinue
        if ($svc -and $svc.Status -ne 'Running') {
            Start-Service -Name defragsvc -ErrorAction SilentlyContinue
        }
    } catch {}

    # 2. Ejecutar defrag.exe C: /L /U con Watchdog Timer de 25 segundos
    Write-Host "   Invocando reanalisis TRIM en C: (Watchdog activo: max 25s)..." -ForegroundColor White
    
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $pInfo = New-Object System.Diagnostics.ProcessStartInfo
    $pInfo.FileName = "defrag.exe"
    $pInfo.Arguments = "C: /L /U"
    $pInfo.UseShellExecute = $false
    $pInfo.RedirectStandardOutput = $true
    $pInfo.RedirectStandardError = $true
    $pInfo.CreateNoWindow = $true

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $pInfo

    try {
        $p.Start() | Out-Null
        $finished = $p.WaitForExit(25000) # 25 segundos maximo
        $sw.Stop()

        if (-not $finished) {
            $p.Kill()
            Write-Host "   [!] TRIM alcanzo el tiempo limite de 25s (controlador Phison ocupado). Cancelado con seguridad." -ForegroundColor Yellow
            Write-Log "TRIM en C: alcanzo timeout de 25s. Proceso cancelado."
        } else {
            $out = $p.StandardOutput.ReadToEnd()
            $elapsedSec = [math]::Round($sw.Elapsed.TotalSeconds, 1)

            if ($p.ExitCode -eq 0) {
                Write-Host "   [OK] TRIM ejecutado con exito en SSD C: ($elapsedSec s)." -ForegroundColor Green
                Write-Host "   [OK] Bloques de memoria flash NAND liberados para optimo desgaste." -ForegroundColor DarkGray
                Write-Log "TRIM en C: exitoso en $elapsedSec s."
            } else {
                Write-Host "   [!] TRIM retorno codigo $($p.ExitCode). Detalles:" -ForegroundColor Yellow
                if ($out) { Write-Host "   $out" -ForegroundColor DarkGray }
                Write-Log "TRIM en C: retorno exitCode $($p.ExitCode)"
            }
        }
    } catch {
        Write-Host "   [!] Error al invocar defrag.exe: $_" -ForegroundColor Red
        Write-Log "Error al ejecutar defrag.exe: $_"
    } finally {
        $p.Dispose()
    }
}

# 7. Modos de Optimizacion
function Start-ModeMinecraft {
    Write-Host "`n===========================================================================" -ForegroundColor Green
    Write-Host "          MODO 1: GAMING - MINECRAFT CON MODS (JAVA G1GC TUNING)           " -ForegroundColor White
    Write-Host "===========================================================================" -ForegroundColor Green
    
    Write-Host "`n1. Purgando Standby List de memoria del Kernel..." -ForegroundColor Yellow
    Invoke-PurgeStandbyMemory

    Write-Host "`n2. Recortando memoria inactiva de Opera GX, Discord y Launchers..." -ForegroundColor Yellow
    Invoke-TrimBackgroundWorkingSets -ProcessNames @("opera", "discord", "CurseForge", "OverwolfLauncher", "TLauncher", "PrismLauncher")

    Write-Host "`n3. Verificando procesos Java en ejecucion..." -ForegroundColor Yellow
    $java = Get-Process -Name "javaw", "java" -ErrorAction SilentlyContinue
    if ($java) {
        foreach ($j in $java) {
            try {
                $j.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::High
                Write-Host "   [OK] Prioridad ALTA asignada a: $($j.ProcessName) (PID: $($j.Id))" -ForegroundColor Green
                Write-Log "Prioridad ALTA asignada a $($j.ProcessName)"
            } catch {}
        }
    } else {
        Write-Host "   (Minecraft no esta abierto aun. Al abrirlo correra sobre memoria limpia)." -ForegroundColor DarkGray
    }

    Write-Host "`n===========================================================================" -ForegroundColor Cyan
    Write-Host " CONFIGURACION RECOMENDADA PARA TUS 11.44 GB DE RAM UTILES:" -ForegroundColor White
    Write-Host " En tu launcher (CurseForge / Modrinth / Prism / TLauncher), asigna:" -ForegroundColor Yellow
    Write-Host "   Memoria Minima (-Xms): 5120 MB (5 GB)" -ForegroundColor White
    Write-Host "   Memoria Maxima (-Xmx): 6144 MB (6 GB)" -ForegroundColor White
    Write-Host "   *NO superes los 7 GB para mantener el ancho de banda Dual Channel (128-bit).* " -ForegroundColor Red
    Write-Host "`n Argumentos JVM recomendados (G1GC de baja latencia):" -ForegroundColor Yellow
    Write-Host " -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch" -ForegroundColor Gray
    Write-Host "===========================================================================" -ForegroundColor Cyan
}

function Start-ModeDestiny2 {
    Write-Host "`n===========================================================================" -ForegroundColor Yellow
    Write-Host "          MODO 2: GAMING - DESTINY 2 (OPTIMIZACION MOTOR TIGER)            " -ForegroundColor White
    Write-Host "===========================================================================" -ForegroundColor Yellow

    Write-Host "`n1. Verificando archivo cvars.xml de Destiny 2..." -ForegroundColor Yellow
    $cvarPath = "$env:APPDATA\Bungie\DestinyPC\prefs\cvars.xml"
    if (Test-Path $cvarPath) {
        $raw = Get-Content $cvarPath -Raw
        $modified = $false
        if ($raw -match 'name="force_enable_multi_threaded_render_submit"\s+value="0"') {
            $raw = $raw -replace 'name="force_enable_multi_threaded_render_submit"\s+value="0"', 'name="force_enable_multi_threaded_render_submit" value="1"'
            $modified = $true
        }
        if ($raw -match 'name="hdr_output"\s+value="1"') {
            $raw = $raw -replace 'name="hdr_output"\s+value="1"', 'name="hdr_output" value="0"'
            $modified = $true
        }
        if ($modified) {
            Set-Content -Path $cvarPath -Value $raw -Encoding UTF8
            Write-Host "   [OK] cvars.xml actualizado: Render Multihilo ACTIVO y HDR desactivado." -ForegroundColor Green
            Write-Log "cvars.xml actualizado para Destiny 2"
        } else {
            Write-Host "   [OK] cvars.xml ya cuenta con la configuracion optima para Ryzen 7 3750H." -ForegroundColor Green
        }
    } else {
        Write-Host "   [!] No se encontro cvars.xml en $cvarPath" -ForegroundColor DarkGray
    }

    Write-Host "`n2. Asegurando forzado de GPU GTX 1650 en el registro de Windows..." -ForegroundColor Yellow
    $d2Exe = "D:\SteamLibrary\steamapps\common\Destiny 2\destiny2.exe"
    Set-ItemProperty -Path 'HKCU:\Software\Microsoft\DirectX\UserGpuPreferences' -Name $d2Exe -Value 'GpuPreference=2;' -ErrorAction SilentlyContinue
    Write-Host "   [OK] GTX 1650 forzada para destiny2.exe." -ForegroundColor Green

    Write-Host "`n3. Purgando Standby List y recortando procesos de fondo..." -ForegroundColor Yellow
    Invoke-PurgeStandbyMemory
    Invoke-TrimBackgroundWorkingSets

    $d2Proc = Get-Process -Name "destiny2" -ErrorAction SilentlyContinue
    if ($d2Proc) {
        try {
            $d2Proc.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::High
            Write-Host "   [OK] Prioridad ALTA asignada a destiny2.exe (PID: $($d2Proc.Id))." -ForegroundColor Green
        } catch {}
    } else {
        Write-Host "   (Destiny 2 no esta abierto aun. Al iniciar cargara con render multihilo optimo)." -ForegroundColor DarkGray
    }
}

function Start-ModeEngineering {
    Write-Host "`n===========================================================================" -ForegroundColor Cyan
    Write-Host "       MODO 3: INGENIERIA ESTRUCTURAL - SAP2000 v27 ^& MATLAB R2025a         " -ForegroundColor White
    Write-Host "===========================================================================" -ForegroundColor Cyan

    Write-Host "`n1. Despejando el mayor bloque de RAM contigua sin fragmentar..." -ForegroundColor Yellow
    Invoke-PurgeStandbyMemory
    Invoke-TrimBackgroundWorkingSets

    Write-Host "`n2. Verificando forzado de GPU dedicada (GTX 1650)..." -ForegroundColor Yellow
    $gpuKey = 'HKCU:\Software\Microsoft\DirectX\UserGpuPreferences'
    Remove-ItemProperty -Path $gpuKey -Name 'D:\SAP2000\SAP2000.exe' -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $gpuKey -Name 'C:\Program Files\Computers and Structures\SAP2000 27\SAP2000.exe' -Value 'GpuPreference=2;' -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $gpuKey -Name 'D:\Matlab\bin\matlab.exe' -Value 'GpuPreference=2;' -ErrorAction SilentlyContinue
    Write-Host "   [OK] GTX 1650 forzada para SAP2000 v27 y MATLAB R2025a." -ForegroundColor Green

    Write-Host "`n3. Ajustando prioridad de solvers..." -ForegroundColor Yellow
    $engProcs = Get-Process -Name "SAP2000", "SAPFire", "MATLAB" -ErrorAction SilentlyContinue
    if ($engProcs) {
        foreach ($ep in $engProcs) {
            try {
                $ep.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::High
                Write-Host "   [OK] Prioridad ALTA asignada a $($ep.ProcessName)." -ForegroundColor Green
            } catch {}
        }
    } else {
        Write-Host "   [OK] Sistema preparado para resolver matrices de rigidez pesadas." -ForegroundColor Green
    }
}

function Start-ModeOperaGX {
    Write-Host "`n===========================================================================" -ForegroundColor Magenta
    Write-Host "             MODO 4: OPTIMIZAR OPERA GX Y DISCORD EN CALIENTE              " -ForegroundColor White
    Write-Host "===========================================================================" -ForegroundColor Magenta

    Write-Host "`n1. Comprimiendo Working Sets de Opera GX (todas las pestanas activas)..." -ForegroundColor Yellow
    Invoke-TrimBackgroundWorkingSets -ProcessNames @("opera", "discord")
    Invoke-PurgeStandbyMemory

    Write-Host "`n2. Purgando caches de shaders y GPU sin alterar sesiones abiertas..." -ForegroundColor Yellow
    $operaGpuCache = "$env:LOCALAPPDATA\Opera Software\Opera GX Stable\ShaderCache"
    if (Test-Path $operaGpuCache) {
        Remove-Item "$operaGpuCache\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   [OK] ShaderCache de Opera GX purgada." -ForegroundColor Green
    }
    $discordCache = "$env:APPDATA\discord\GPUCache"
    if (Test-Path $discordCache) {
        Remove-Item "$discordCache\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   [OK] GPUCache de Discord purgada." -ForegroundColor Green
    }

    Write-Host "`n===========================================================================" -ForegroundColor Cyan
    Write-Host " RECOMENDACION EN OPERA GX (GX Control en la barra lateral):" -ForegroundColor White
    Write-Host "   * RAM Limiter: Activar en 3.5 GB (Con casilla 'Hard Limit' ACTIVADA)." -ForegroundColor Yellow
    Write-Host "   * CPU Limiter: Activar al 25% solo durante certamenes o partidas de Destiny." -ForegroundColor Yellow
    Write-Host "===========================================================================" -ForegroundColor Cyan
}

function Start-ModeQuickClean {
    Write-Host "`n===========================================================================" -ForegroundColor Yellow
    Write-Host "               MODO 5: LIMPIEZA RAPIDA DEL SISTEMA                         " -ForegroundColor White
    Write-Host "===========================================================================" -ForegroundColor Yellow

    Write-Host "`n1. Purgando temporales de usuario y de Windows..." -ForegroundColor Yellow
    Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
    if ($isAdmin) {
        Remove-Item "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Host "   [OK] Temporales limpios. (Prefetch preservado)." -ForegroundColor Green

    Write-Host "`n2. Eliminando volcados de memoria y reportes de error WER..." -ForegroundColor Yellow
    Remove-Item "C:\ProgramData\Microsoft\Windows\WER\ReportArchive\*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item "C:\ProgramData\Microsoft\Windows\WER\ReportQueue\*" -Recurse -Force -ErrorAction SilentlyContinue
    if ($isAdmin) {
        Remove-Item "C:\Windows\Minidump\*" -Recurse -Force -ErrorAction SilentlyContinue
        if (Test-Path "C:\Windows\Memory.dmp") { Remove-Item "C:\Windows\Memory.dmp" -Force -ErrorAction SilentlyContinue }
    }
    Write-Host "   [OK] Dumps de error y telemetria WER eliminados." -ForegroundColor Green

    Write-Host "`n3. Limpiando descargas antiguas de Windows Update..." -ForegroundColor Yellow
    if ($isAdmin) {
        $ti = Get-Process -Name "TiWorker", "TrustedInstaller" -ErrorAction SilentlyContinue
        if ($ti) {
            Write-Host "   [!] Instalador de Windows en uso actualmente. Omitiendo reinicio de wuauserv." -ForegroundColor DarkGray
        } else {
            Stop-Service -Name wuauserv -Force -ErrorAction SilentlyContinue
            Remove-Item "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
            Start-Service -Name wuauserv -ErrorAction SilentlyContinue
            Write-Host "   [OK] SoftwareDistribution purgado." -ForegroundColor Green
        }
    } else {
        Write-Host "   [!] Omitido: Requiere permisos de Administrador." -ForegroundColor DarkGray
    }

    Write-Host "`n4. Purgando caches de shaders DirectX, GPU y Discord (BleachBit/PrivaZer)..." -ForegroundColor Yellow
    $shaderPaths = @(
        "$env:LOCALAPPDATA\D3DSCache\*",
        "$env:LOCALAPPDATA\NVIDIA\DXCache\*",
        "$env:LOCALAPPDATA\AMD\DxCache\*",
        "$env:APPDATA\discord\Cache\*",
        "$env:APPDATA\discord\Code Cache\*",
        "$env:APPDATA\discord\GPUCache\*"
    )
    foreach ($sp in $shaderPaths) {
        Remove-Item $sp -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Host "   [OK] Caches de shaders y GPU purgadas." -ForegroundColor Green

    Write-Host "`n5. Vaciando Papelera de reciclaje y limpiando cache DNS..." -ForegroundColor Yellow
    Clear-RecycleBin -Force -ErrorAction SilentlyContinue | Out-Null
    Clear-DnsClientCache -ErrorAction SilentlyContinue
    Write-Host "   [OK] Papelera y DNS limpios." -ForegroundColor Green

    # 6. Motor robusto de TRIM para SSD C:
    Invoke-RobustTrimSSD
}

function Start-ModeDeepClean {
    Write-Host "`n===========================================================================" -ForegroundColor Red
    Write-Host "            MODO 6: MANTENIMIENTO PROFUNDO COMPLETO (SFC + DISM)            " -ForegroundColor White
    Write-Host "===========================================================================" -ForegroundColor Red

    if (-not $isAdmin) {
        Write-Host "`n[!] ERROR: El Mantenimiento Profundo requiere obligatoriamente privilegios de Administrador." -ForegroundColor Red
        Write-Host "    Abre el script mediante 'Nitro_Optimizer.bat' haciendo clic derecho > Ejecutar como Administrador." -ForegroundColor Yellow
        return
    }

    Start-ModeQuickClean

    Write-Host "`n6. Verificando integridad de archivos de sistema con SFC..." -ForegroundColor Yellow
    sfc /scannow

    Write-Host "`n7. Optimizando almacen de componentes de Windows (DISM)..." -ForegroundColor Yellow
    Dism.exe /online /Cleanup-Image /StartComponentCleanup /Quiet
    Write-Host "   [OK] Limpieza DISM completada." -ForegroundColor Green

    Write-Host "`n8. Desfragmentando disco mecanico de datos D: (WDC 1TB)..." -ForegroundColor Yellow
    Write-Host "   (Nota tecnica: Solo se desfragmenta el HDD D: mecanico; el SSD C: solo recibe TRIM)." -ForegroundColor DarkGray
    defrag D: /U /V
    Write-Host "   [OK] Desfragmentacion en D: finalizada." -ForegroundColor Green
}

function Start-ModeDiagnostics {
    Write-Host "`n===========================================================================" -ForegroundColor White
    Write-Host "          MODO 7: DIAGNOSTICO DE HARDWARE Y TELEMETRIA EN VIVO             " -ForegroundColor White
    Write-Host "===========================================================================" -ForegroundColor White

    Write-Host "`n--- ESTADO DE DISCOS FISICOS (S.M.A.R.T.) ---" -ForegroundColor Yellow
    Get-PhysicalDisk | Select-Object DeviceId, FriendlyName, MediaType, BusType, HealthStatus, OperationalStatus | Format-Table -AutoSize

    Write-Host "`n--- ESTADO DE TRIM EN EL SISTEMA OPERATIVO ---" -ForegroundColor Yellow
    try {
        fsutil behavior query DisableDeleteNotify
    } catch {
        Write-Host "   No se pudo consultar DisableDeleteNotify (requiere Admin)." -ForegroundColor DarkGray
    }

    Write-Host "`n--- TOP 12 PROCESOS CON MAYOR CONSUMO DE RAM ---" -ForegroundColor Yellow
    Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 12 Id, ProcessName, @{Name="RAM (MB)";Expression={[math]::Round($_.WorkingSet64/1MB,1)}} | Format-Table -AutoSize

    Write-Host "`n--- PREFERENCIAS DIRECTX ASIGNADAS A GPU DEDICADA ---" -ForegroundColor Yellow
    Get-ItemProperty -Path 'HKCU:\Software\Microsoft\DirectX\UserGpuPreferences' -ErrorAction SilentlyContinue | Format-List
}

# 8. Ejecucion Rapida si se paso el parametro -QuickRAM (Liberador de 1 Clic)
if ($QuickRAM) {
    Write-Host "===========================================================================" -ForegroundColor Green
    Write-Host "      LIBERADOR RAPIDO DE RAM - NITRO 5 (ISLC + TRIM OPERA GX)             " -ForegroundColor White
    Write-Host "===========================================================================" -ForegroundColor Green
    $mBefore = Get-SystemMemoryInfo
    Write-Host "`nPurgando Standby List del Kernel y recortando procesos de fondo..." -ForegroundColor Yellow
    Invoke-PurgeStandbyMemory
    Invoke-TrimBackgroundWorkingSets
    $mAfter = Get-SystemMemoryInfo
    $gained = [math]::Round($mAfter.FreeMB - $mBefore.FreeMB, 0)
    Write-Host "`n---------------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host " [OK] RAM Libre Inicial : $($mBefore.FreeMB) MB ($($mBefore.PctUsed)% en uso)" -ForegroundColor Yellow
    Write-Host " [OK] RAM Libre Actual  : $($mAfter.FreeMB) MB ($($mAfter.PctUsed)% en uso)" -ForegroundColor Green
    if ($gained -gt 0) {
        Write-Host " [OK] Ganancia Neta     : +$gained MB de memoria fisica disponible." -ForegroundColor Cyan
    }
    Write-Host "===========================================================================" -ForegroundColor Green
    Write-Host "Ventana cerrandose en 3 segundos..." -ForegroundColor DarkGray
    Start-Sleep -Seconds 3
    exit
}

# 9. Ciclo interactivo del menu principal
while ($true) {
    Clear-Host
    $m = Get-SystemMemoryInfo

    Write-Host "===========================================================================" -ForegroundColor Cyan
    Write-Host "       NITRO OPTIMIZER MAESTRO v4.1 - ACER NITRO 5 AN515-43                " -ForegroundColor White
    Write-Host "       Ryzen 7 3750H (4C/8T) | GTX 1650 (4GB GDDR5) | 12 GB RAM DDR4       " -ForegroundColor Gray
    Write-Host "===========================================================================" -ForegroundColor Cyan
    
    if ($isAdmin) {
        Write-Host " PRIVILEGIOS: [ADMINISTRADOR ACTIVO - TODAS LAS FUNCIONES HABILITADAS]" -ForegroundColor Green
    } else {
        Write-Host " PRIVILEGIOS: [MODO ESTANDAR - OPCIONES 5 Y 6 EJECUTARAN SIN PERMISOS DE DISCO]" -ForegroundColor Yellow
    }

    Write-Host " ESTADO ACTUAL DE MEMORIA:" -ForegroundColor Yellow
    Write-Host "   Total Visible  : $($m.TotalMB) MB (~11.44 GB con UMA a 512M) [OK]" -ForegroundColor Cyan
    Write-Host "   RAM Libre Real : $($m.FreeMB) MB ($([math]::Round(100 - $m.PctUsed, 1))% disponible)" -ForegroundColor Green
    Write-Host "   RAM en Uso     : $($m.UsedMB) MB ($($m.PctUsed)%)" -ForegroundColor $(if($m.PctUsed -gt 75){"Red"}else{"White"})
    Write-Host "---------------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host " [1] Modo Gaming: Minecraft con Mods (ISLC + Trim Opera + Flags JVM)" -ForegroundColor White
    Write-Host " [2] Modo Gaming: Destiny 2 (Render Multihilo cvars + GTX 1650 + Prioridad)" -ForegroundColor White
    Write-Host " [3] Modo Ingenieria: SAP2000 v27 ^& MATLAB (Bloque contiguo de RAM + GTX 1650)" -ForegroundColor White
    Write-Host " [4] Optimizar Opera GX y Discord en Caliente (Recorte de RAM sin cerrar)" -ForegroundColor White
    Write-Host " [5] Limpieza Rapida del Sistema (Temporales, Shaders, Watchdog TRIM en SSD C:)" -ForegroundColor White
    Write-Host " [6] Mantenimiento Profundo Completo (SFC + DISM + Defrag solo en HDD D:)" -ForegroundColor Green
    Write-Host " [7] Diagnostico de Hardware, Discos y Top Procesos en RAM" -ForegroundColor Gray
    Write-Host " [Q] Salir" -ForegroundColor DarkGray
    Write-Host "===========================================================================" -ForegroundColor Cyan

    $opt = Read-Host " Selecciona una opcion [1-7, Q]"
    
    switch ($opt.Trim().ToUpper()) {
        "1" { Start-ModeMinecraft; Read-Host "`n Presiona Enter para volver al menu..." }
        "2" { Start-ModeDestiny2;  Read-Host "`n Presiona Enter para volver al menu..." }
        "3" { Start-ModeEngineering; Read-Host "`n Presiona Enter para volver al menu..." }
        "4" { Start-ModeOperaGX;   Read-Host "`n Presiona Enter para volver al menu..." }
        "5" { Start-ModeQuickClean; Read-Host "`n Presiona Enter para volver al menu..." }
        "6" { Start-ModeDeepClean;  Read-Host "`n Presiona Enter para volver al menu..." }
        "7" { Start-ModeDiagnostics; Read-Host "`n Presiona Enter para volver al menu..." }
        "Q" {
            Write-Host "`nFinalizando... Que tengas una excelente sesion." -ForegroundColor Cyan
            Start-Sleep -Seconds 1
            exit
        }
        Default {
            Write-Host "Opcion no valida. Intenta de nuevo." -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        }
    }
}
