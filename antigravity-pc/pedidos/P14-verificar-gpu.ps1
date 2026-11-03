# P14: verifica por nombre qué GPU usa SAP2000. Espera a que Nicolás lo cierre (hasta 6 h), lo abre con el modelo,
# lo revisa y lo cierra. No necesita administrador ni intervención.
param([int]$EsperaMaxMin = 360)
$raiz = Split-Path (Split-Path $PSScriptRoot)
Import-Module (Join-Path $raiz 'antigravity-pc\perfil-nitro\PerfilNitro.psm1') -Force
'== Adaptadores (DXGI)'
Get-AdaptadoresGpu | Format-Table -AutoSize | Out-String -Width 200
$limite = (Get-Date).AddMinutes($EsperaMaxMin)
while ((Get-Process SAP2000 -ErrorAction SilentlyContinue) -and (Get-Date) -lt $limite) { Start-Sleep -Seconds 300 }
if (Get-Process SAP2000 -ErrorAction SilentlyContinue) { 'SAP2000 siguió abierto todo el plazo: verificación pendiente.'; return }
$p = Start-Process 'C:\Program Files\Computers and Structures\SAP2000 27\SAP2000.exe' -ArgumentList '"D:\Modelos RUN\PRACTICA RODRIGO.sdb"' -PassThru
Start-Sleep -Seconds 45
'== GPU usada por SAP2000 (PID ' + $p.Id + ')'
$g = @(Get-GpuDeProceso -ProcesoId $p.Id)
$g | Format-Table -AutoSize | Out-String -Width 200
if ($g | Where-Object Adaptador -match 'NVIDIA') { 'RESULTADO: SAP2000 usa la GTX 1650' } else { 'RESULTADO: SAP2000 NO usa la GTX 1650' }
$null = $p.CloseMainWindow(); Start-Sleep -Seconds 10
if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force }
'SAP2000 de la prueba cerrado (el modelo no se modificó).'
