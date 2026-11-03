<#
Instala o actualiza en %USERPROFILE%\Mantenimiento la versión de una rama: mantenimiento, perfil del Nitro
y Ejecutar-Elevado. Conserva v4.1_retirada\, logs\ y los respaldos. No necesita administrador.
Uso: powershell -ExecutionPolicy Bypass -File antigravity-pc\pedidos\Instalar.ps1 [-Rama origin/main] [-Destino ...] [-SinAccesos]
#>
param(
    [string]$Rama = 'origin/claude/perfil-nitro',
    [string]$Destino = (Join-Path $env:USERPROFILE 'Mantenimiento'),
    [switch]$SinAccesos
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path (Split-Path $PSScriptRoot)
$tmp = Join-Path $env:TEMP ("instalar_" + [guid]::NewGuid())
New-Item -ItemType Directory $tmp | Out-Null
try {
    git -C $repo fetch -q origin
    git -C $repo archive -o "$tmp\a.zip" $Rama antigravity-pc/mantenimiento antigravity-pc/perfil-nitro antigravity-pc/Ejecutar-Elevado.ps1
    if ($LASTEXITCODE) { throw "git archive falló ($LASTEXITCODE)" }
    "Versión: $Rama $(git -C $repo rev-parse --short $Rama)"
    Expand-Archive "$tmp\a.zip" -DestinationPath $tmp -Force
    New-Item -ItemType Directory $Destino -Force | Out-Null
    Copy-Item "$tmp\antigravity-pc\mantenimiento\*" $Destino -Recurse -Force
    New-Item -ItemType Directory (Join-Path $Destino 'perfil-nitro') -Force | Out-Null
    Copy-Item "$tmp\antigravity-pc\perfil-nitro\*" (Join-Path $Destino 'perfil-nitro') -Recurse -Force
    Copy-Item "$tmp\antigravity-pc\Ejecutar-Elevado.ps1" $Destino -Force
    "Purga de prioridad baja: $([bool](Select-String -Path (Join-Path $Destino 'Mantenimiento.psm1') -Pattern 'int orden = 5' -Quiet))"
    $f1 = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Destino 'pruebas\Pruebas.ps1') | Select-Object -Last 1
    $f2 = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Destino 'perfil-nitro\pruebas\Pruebas.ps1') | Select-Object -Last 1
    "Mantenimiento: $f1 | Perfil: $f2"
    if (-not $SinAccesos) {
        $esc = if (Test-Path "$env:USERPROFILE\OneDrive\Escritorio") { "$env:USERPROFILE\OneDrive\Escritorio" } else { [Environment]::GetFolderPath('Desktop') }
        $ws = New-Object -ComObject WScript.Shell
        foreach ($a in @(@('Mantenimiento', 'Mantenimiento.bat', ''), @('Liberar RAM', 'Mantenimiento.bat', 'Ram'),
                         @('Iniciar calculo', 'Mantenimiento.bat', 'Calculo'), @('Terminar calculo', 'Mantenimiento.bat', 'FinCalculo'),
                         @('Perfil Nitro', 'perfil-nitro\Perfil.bat', ''))) {
            $l = $ws.CreateShortcut("$esc\$($a[0]).lnk"); $l.TargetPath = Join-Path $Destino $a[1]; $l.Arguments = $a[2]
            $l.WorkingDirectory = Split-Path (Join-Path $Destino $a[1]); $l.Save()
        }
        Get-ChildItem $esc -Filter *.lnk | Where-Object Name -match 'Mantenimiento|Liberar RAM|calculo|Perfil Nitro' | Select-Object -ExpandProperty Name
    }
    Get-ChildItem $Destino -Directory | Select-Object -ExpandProperty Name
} finally {
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
