# Menú del perfil del Nitro. Se abre con Perfil.bat (pide administrador).
Import-Module (Join-Path $PSScriptRoot 'PerfilNitro.psm1') -Force
while ($true) {
    Clear-Host
    'Perfil del Nitro 5'
    Get-EstadoAjustes | Format-Table Id, Activo, Aplicado, Requisito, Riesgo -AutoSize | Out-String -Width 200
    ' [1] Simular los ajustes activos (no cambia nada)'
    ' [2] Aplicar los ajustes activos (crea punto de restauración y respaldo de cada valor)'
    ' [3] Aplicar un ajuste por id'
    ' [4] Deshacer un ajuste por id'
    ' [Q] Salir'
    $op = (Read-Host 'Opción').Trim().ToUpper()
    try {
        switch ($op) {
            '1' { Set-Ajustes -WhatIf }
            '2' { Checkpoint-Computer -Description 'Perfil Nitro' -RestorePointType MODIFY_SETTINGS -ErrorAction SilentlyContinue; Set-Ajustes }
            '3' { Set-Ajustes -Ids (Read-Host 'id') }
            '4' { Undo-Ajustes -Ids (Read-Host 'id') }
            'Q' { return }
        }
    } catch { Write-Host "ERROR: $_" -ForegroundColor Red }
    Read-Host 'Enter para volver'
}
