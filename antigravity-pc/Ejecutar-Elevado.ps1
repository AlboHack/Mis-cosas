<#
Corre un script como administrador desde una sesión sin elevar (Antigravity) y devuelve su salida.
Windows muestra un aviso de permiso (UAC) que Nicolás acepta; la salida queda en un log que este
script imprime al terminar.
Uso: powershell -ExecutionPolicy Bypass -File antigravity-pc\Ejecutar-Elevado.ps1 -Script <ruta.ps1> [-Nombre P8]
#>
param(
    [Parameter(Mandatory)][string]$Script,
    [string]$Nombre = 'elevado'
)
$Script = (Resolve-Path $Script).Path
$dirLog = Join-Path $env:USERPROFILE 'Mantenimiento\logs'
New-Item -ItemType Directory -Path $dirLog -Force | Out-Null
$log = Join-Path $dirLog ("{0}_{1:yyyyMMdd_HHmmss}.log" -f $Nombre, (Get-Date))
$envoltura = Join-Path $env:TEMP ("elevado_{0}.ps1" -f [guid]::NewGuid())
@"
Start-Transcript -Path '$log' -Force | Out-Null
try { Set-Location '$(Split-Path $Script)'; & '$Script' } catch { Write-Host "ERROR: `$_" }
finally { Stop-Transcript | Out-Null }
"@ | Set-Content $envoltura -Encoding UTF8
try {
    $p = Start-Process powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$envoltura`""
    "Código de salida: $($p.ExitCode)"
} catch {
    "ERROR: no se aceptó el permiso de administrador ($_)"
} finally {
    Remove-Item $envoltura -ErrorAction SilentlyContinue
}
if (Test-Path $log) { Get-Content $log } else { "Sin log: el script elevado no llegó a correr." }
