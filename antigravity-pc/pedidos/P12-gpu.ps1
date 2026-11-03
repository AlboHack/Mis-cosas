# P12: GTX 1650 permanente para SAP2000 y MATLAB, y verificación sin intervención de Nicolás.
# No necesita administrador (la preferencia vive en HKCU). Abre SAP2000 solo si no estaba abierto, y cierra solo esa instancia.
$raiz = Split-Path (Split-Path $PSScriptRoot)
Import-Module (Join-Path $raiz 'antigravity-pc\perfil-nitro\PerfilNitro.psm1') -Force
Set-Ajustes -Ids gpu-dedicada-ingenieria
'== Preferencias de GPU por programa'
Get-ItemProperty 'HKCU:\Software\Microsoft\DirectX\UserGpuPreferences' | Format-List | Out-String -Width 220

$exe = 'C:\Program Files\Computers and Structures\SAP2000 27\SAP2000.exe'
$modelo = 'D:\Modelos RUN\PRACTICA RODRIGO.sdb'
$abierto = Get-Process SAP2000 -ErrorAction SilentlyContinue | Select-Object -First 1
$propio = $null
if ($abierto) { "SAP2000 ya estaba abierto (PID $($abierto.Id)): se verifica esa instancia y no se cierra."; $sap = $abierto }
else {
    $propio = Start-Process $exe -ArgumentList "`"$modelo`"" -PassThru
    "SAP2000 abierto para la prueba (PID $($propio.Id)); esperando 40 s a que cargue el modelo..."
    Start-Sleep -Seconds 40
    $sap = $propio
}
'== nvidia-smi'
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) { nvidia-smi | Out-String -Width 200 } else { 'nvidia-smi no está disponible' }
'== Motores de GPU usados por SAP2000 (instancias del contador)'
Get-Counter '\GPU Engine(*)\Utilization Percentage' -ErrorAction SilentlyContinue | ForEach-Object CounterSamples |
    Where-Object InstanceName -match "pid_$($sap.Id)_" | Select-Object InstanceName, @{n='Uso';e={[math]::Round($_.CookedValue,1)}} | Format-Table -AutoSize | Out-String -Width 220
'== Memoria dedicada por adaptador (luid)'
Get-Counter '\GPU Adapter Memory(*)\Dedicated Usage' -ErrorAction SilentlyContinue | ForEach-Object CounterSamples |
    Select-Object InstanceName, @{n='MB';e={[math]::Round($_.CookedValue/1MB)}} | Format-Table -AutoSize | Out-String -Width 200
if ($propio) {
    $null = $propio.CloseMainWindow(); Start-Sleep -Seconds 10
    if (-not $propio.HasExited) { Stop-Process -Id $propio.Id -Force }
    'SAP2000 de la prueba cerrado (el modelo no se modificó).'
}
