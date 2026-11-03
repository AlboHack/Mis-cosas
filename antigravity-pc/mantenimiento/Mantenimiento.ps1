# Menú del mantenimiento. Se abre con Mantenimiento.bat (pide administrador).
param([ValidateSet('', 'Ram', 'Calculo', 'FinCalculo')][string]$Modo = '')
Import-Module (Join-Path $PSScriptRoot 'Mantenimiento.psm1') -Force

function Mostrar-Memoria {
    $m = Get-EstadoMemoria
    "Disponible {0} MB | libre {1} MB | standby {2} MB | commit {3}/{4} MB" -f $m.DisponibleMB, $m.LibreMB, $m.StandbyMB, $m.CommitMB, $m.LimiteMB
}

switch ($Modo) {
    'Ram'        { Invoke-PurgaStandby | Out-Null; Mostrar-Memoria; Start-Sleep 3; return }
    'Calculo'    { Start-SesionCalculo; return }
    'FinCalculo' { Stop-SesionCalculo; return }
}

$opciones = [ordered]@{
    '1' = @('Iniciar sesión de cálculo (SAP2000 / MATLAB)', { Start-SesionCalculo })
    '2' = @('Cerrar sesión de cálculo (restaura el plan de energía)', { Stop-SesionCalculo })
    '3' = @('Purgar standby si conviene', { Invoke-PurgaStandby | Out-Null })
    '4' = @('Temporales de más de 7 días: ver qué se borraría', { Clear-Temporales -WhatIf | Out-Null })
    '5' = @('Temporales de más de 7 días: borrar', { Clear-Temporales | Format-List })
    '6' = @('Optimizar C: (retrim) y D: (desfragmentar)', { 'C', 'D' | ForEach-Object { Invoke-OptimizarUnidad $_ } })
    '7' = @('Diagnóstico', { $d = Get-Diagnostico; $d.Discos | Format-Table; $d.Procesos | Format-Table; $d.TrimNTFS })
    '8' = @('Desinstalar programas de la lista: simulación', { Uninstall-Programas -WhatIf })
    '9' = @('Desinstalar programas de la lista: ejecutar (pide confirmar cada uno)', { Uninstall-Programas })
}

while ($true) {
    Clear-Host
    "Mantenimiento Nitro 5 | administrador: $(Test-Administrador)"
    Mostrar-Memoria
    ''
    foreach ($k in $opciones.Keys) { " [$k] $($opciones[$k][0])" }
    ' [Q] Salir'
    $op = (Read-Host 'Opción').Trim().ToUpper()
    if ($op -eq 'Q') { break }
    if ($opciones.Contains($op)) {
        try { & $opciones[$op][1] } catch { Write-Host "ERROR: $_" -ForegroundColor Red; Write-Registro "ERROR opción ${op}: $_" }
        Read-Host 'Enter para volver'
    }
}
