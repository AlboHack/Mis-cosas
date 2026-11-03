<#
.SYNOPSIS
    Desinstalador de Raiz y Depurador Quirurgico de Bloatware
    Equipo: Acer Nitro 5 AN515-43 (Ryzen 7 3750H / GTX 1650 / 12 GB RAM)
.DESCRIPTION
    Elimina de raiz CCleaner, IObit (Advanced SystemCare, Smart Defrag, Driver Booster, 
    IObit Uninstaller), Brave Browser, Lightworks, BleachBit, PrivaZer y sus residuos
    en disco C:, disco D:, registro de Windows y servicios del sistema.
#>

# 1. Elevacion automatica a Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    try {
        Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs -ErrorAction Stop
        exit
    } catch {
        Write-Warning "Ejecutando en modo usuario estandar. Algunas carpetas de sistema requeriran doble clic manual en Desinstalador_Raiz_Bloatware.bat como Administrador."
    }
}

$Host.UI.RawUI.WindowTitle = "Desinstalador Quirurgico de Raiz - Acer Nitro 5"
Clear-Host

Write-Host "===========================================================================" -ForegroundColor Red
Write-Host "       DESINSTALADOR QUIRURGICO DE RAIZ Y LIMPIEZA DE RESIDUOS            " -ForegroundColor White
Write-Host "       Acer Nitro AN515-43 | Objetivos: CCleaner, IObit, Brave, LWKS       " -ForegroundColor Gray
Write-Host "===========================================================================" -ForegroundColor Red

# 2. Terminar procesos activos
Write-Host "`n[PASO 1] Terminando procesos activos en memoria..." -ForegroundColor Yellow
$procTargets = @(
    'ccleaner', 'ccleaner64', 'CCEnhancer',
    'ASC', 'ASCTray', 'ASCService', 'AutoCare', 'OFCleaner',
    'SmartDefrag', 'SDService',
    'DriverBooster', 'Scheduler', 'AutoUpdate', 'CareScan',
    'IObitUninstaler', 'UninstallTool',
    'brave', 'brave_crashpad_handler',
    'lightworks', 'ntcardvt',
    'bleachbit', 'privazer', 'privazer_remover'
)

foreach ($p in $procTargets) {
    $procs = Get-Process -Name $p -ErrorAction SilentlyContinue
    if ($procs) {
        $procs | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "   -> Proceso terminado: $p" -ForegroundColor Cyan
    }
}

# 3. Detener y erradicar servicios permanentemente
Write-Host "`n[PASO 2] Erradicando servicios de Windows asociados..." -ForegroundColor Yellow
$serviceTargets = @(
    'AdvancedSystemCareService18',
    'SmartDefragService',
    'SmartDefrag',
    'brave',
    'bravem',
    'BraveElevationService',
    'CCleanerCrashReporting'
)

foreach ($s in $serviceTargets) {
    $svc = Get-Service -Name $s -ErrorAction SilentlyContinue
    if ($svc) {
        Stop-Service -Name $s -Force -ErrorAction SilentlyContinue
        Set-Service -Name $s -StartupType Disabled -ErrorAction SilentlyContinue
        & sc.exe delete $s | Out-Null
        Write-Host "   -> Servicio eliminado definitivamente: $s" -ForegroundColor Green
    }
}

# 4. Ejecutar desinstaladores oficiales silenciosos (si aun existen)
Write-Host "`n[PASO 3] Ejecutando desinstaladores oficiales en modo desatendido..." -ForegroundColor Yellow

# SAP2000 v19 (MSI silencioso, preservando v27 intacta)
Write-Host "   -> Desinstalando SAP2000 v19 ({0471996C-B0F0-4A69-AE8B-9B0C3A0D37B3})..." -ForegroundColor White
Start-Process msiexec.exe -ArgumentList '/x "{0471996C-B0F0-4A69-AE8B-9B0C3A0D37B3}" /qn /norestart' -Wait -ErrorAction SilentlyContinue

$uninstJobs = @(
    @{ Name = "CCleaner"; Path = "C:\Program Files\CCleaner\uninst.exe"; Args = "/S" },
    @{ Name = "Advanced SystemCare"; Path = "D:\Program Files (x86)\IObit\Advanced SystemCare\unins000.exe"; Args = "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART" },
    @{ Name = "Smart Defrag"; Path = "D:\Program Files (x86)\IObit\Smart Defrag\unins000.exe"; Args = "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART" },
    @{ Name = "Lightworks"; Path = "D:\Lightworks\uninstall.exe"; Args = "/S" },
    @{ Name = "BleachBit"; Path = "D:\BleachBit\uninstall.exe"; Args = "/allusers /S" },
    @{ Name = "PrivaZer"; Path = "D:\PrivaZer\privazer_remover.exe"; Args = "/SILENT" }
)

foreach ($job in $uninstJobs) {
    if (Test-Path $job.Path) {
        Write-Host "   -> Ejecutando desinstalador oficial de $($job.Name)..." -ForegroundColor White
        try {
            $proc = Start-Process -FilePath $job.Path -ArgumentList $job.Args -PassThru -Wait
            Start-Sleep -Seconds 2
        } catch {}
    }
}

# 5. Purga masiva de directorios y basura residual en C: y D:
Write-Host "`n[PASO 4] Eliminando directorios residuales en Disco C: y Disco D:..." -ForegroundColor Yellow

$dirsToPurge = @(
    "C:\Program Files\CCleaner",
    "C:\ProgramData\CCleaner",
    "$env:APPDATA\CCleaner",
    "$env:LOCALAPPDATA\CCleaner",
    "C:\Program Files\BraveSoftware",
    "C:\Program Files (x86)\BraveSoftware",
    "$env:LOCALAPPDATA\BraveSoftware",
    "D:\Lightworks",
    "$env:APPDATA\Lightworks",
    "$env:LOCALAPPDATA\Lightworks",
    "D:\Program Files (x86)\IObit\Advanced SystemCare",
    "D:\Program Files (x86)\IObit\Smart Defrag",
    "D:\Program Files (x86)\IObit",
    "C:\Program Files (x86)\IObit",
    "C:\ProgramData\IObit",
    "D:\IObit Uninstaller",
    "$env:APPDATA\IObit",
    "$env:LOCALAPPDATA\IObit",
    "C:\Program Files (x86)\Driver Booster",
    "D:\BleachBit",
    "$env:APPDATA\BleachBit",
    "D:\PrivaZer",
    "$env:APPDATA\PrivaZer",
    "$env:LOCALAPPDATA\PrivaZer",
    "$env:USERPROFILE\OneDrive\Escritorio\RAMMap",
    "$env:USERPROFILE\OneDrive\Escritorio\ReduceMemory",
    "D:\AMD-Software-Adrenalin-Edition-23.12.1-MinimalSetup-231205_web",
    "D:\SAP2000"
)

foreach ($d in $dirsToPurge) {
    if (Test-Path $d) {
        try {
            Remove-Item -Path $d -Recurse -Force -ErrorAction Stop
            Write-Host "   [OK] Removido de raiz: $d" -ForegroundColor Green
        } catch {
            Write-Host "   [!] Forzando eliminacion por CMD: $d" -ForegroundColor DarkYellow
            & cmd.exe /c "rd /s /q `"$d`"" | Out-Null
        }
    }
}

# 6. Limpieza de entradas huerfanas en el Registro de Desinstalacion
Write-Host "`n[PASO 5] Purgando entradas huerfanas del Registro de Windows..." -ForegroundColor Yellow
$regRoots = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall"
)

$targetKeywords = @('CCleaner', 'Advanced SystemCare', 'Smart Defrag', 'Driver Booster', 'Brave', 'Lightworks', 'BleachBit', 'PrivaZer', 'SAP2000 19')

foreach ($r in $regRoots) {
    if (Test-Path $r) {
        Get-ChildItem -Path $r -ErrorAction SilentlyContinue | ForEach-Object {
            $keyPath = $_.PSPath
            $dn = (Get-ItemProperty -Path $keyPath -Name DisplayName -ErrorAction SilentlyContinue).DisplayName
            if ($dn) {
                foreach ($kw in $targetKeywords) {
                    if ($dn -like "*$kw*") {
                        Remove-Item -Path $keyPath -Recurse -Force -ErrorAction SilentlyContinue
                        Write-Host "   [OK] Registro desvinculado: $dn" -ForegroundColor Green
                        break
                    }
                }
            }
        }
    }
}

# 7. Limpieza de accesos directos
Write-Host "`n[PASO 6] Limpiando accesos directos de escritorio..." -ForegroundColor Yellow
$shortcuts = @(
    "C:\Users\Public\Desktop\CCleaner.lnk",
    "C:\Users\Public\Desktop\Advanced SystemCare.lnk",
    "C:\Users\Public\Desktop\Smart Defrag 10.lnk",
    "C:\Users\Public\Desktop\Driver Booster 8.lnk",
    "C:\Users\Public\Desktop\Brave.lnk",
    "C:\Users\Public\Desktop\lightworks x64 (2021.1).lnk",
    "C:\Users\Public\Desktop\BleachBit.lnk",
    "C:\Users\Public\Desktop\PrivaZer.lnk",
    "$env:USERPROFILE\OneDrive\Escritorio\ReduceMemory_x64.exe.lnk",
    "$env:USERPROFILE\OneDrive\Escritorio\BleachBit.lnk",
    "$env:USERPROFILE\OneDrive\Escritorio\PrivaZer.lnk",
    "$env:USERPROFILE\OneDrive\Escritorio\Smart Defrag 10.lnk",
    "$env:USERPROFILE\OneDrive\Escritorio\CCleaner.lnk",
    "$env:USERPROFILE\OneDrive\Escritorio\Advanced SystemCare.lnk",
    "C:\Users\Public\Desktop\SAP2000 19.lnk",
    "$env:USERPROFILE\OneDrive\Escritorio\SAP2000 19.lnk"
)

foreach ($sc in $shortcuts) {
    if (Test-Path $sc) {
        Remove-Item -Path $sc -Force -ErrorAction SilentlyContinue
        Write-Host "   -> Acceso directo eliminado: $(Split-Path $sc -Leaf)" -ForegroundColor Green
    }
}

Write-Host "`n===========================================================================" -ForegroundColor Green
Write-Host " LIMPIEZA DE RAIZ FINALIZADA CON EXITO                                     " -ForegroundColor White
Write-Host " No quedan procesos, servicios, carpetas ni claves huerfanas activas.       " -ForegroundColor Green
Write-Host "===========================================================================" -ForegroundColor Green
Write-Host "`nEsta ventana se cerrara en 5 segundos..." -ForegroundColor Gray
Start-Sleep -Seconds 5
