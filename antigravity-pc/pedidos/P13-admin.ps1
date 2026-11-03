# P13: la parte de P10 que exige administrador (solo lectura). Se lanza con P13-admin.bat (doble clic de Nicolás).
'== Salud SMART'
Get-PhysicalDisk | Get-StorageReliabilityCounter | Select-Object DeviceId, Temperature, TemperatureMax, Wear, PowerOnHours, ReadErrorsUncorrected, WriteErrorsUncorrected | Format-Table -AutoSize | Out-String
'== Puntos de restauración y espacio para instantáneas'
Get-ComputerRestorePoint | Select-Object -Last 5 Description, CreationTime | Format-Table | Out-String
vssadmin list shadowstorage | Out-String
'== Volsnap 36 (instantáneas borradas por falta de espacio)'
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Volsnap'; Id=36} -MaxEvents 3 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Message | Format-List | Out-String -Width 220
'== Servicios que no arrancan (7000 / 7009)'
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Service Control Manager'; Id=7000,7009} -MaxEvents 40 -ErrorAction SilentlyContinue | Group-Object Message | Sort-Object Count -Descending | Select-Object -First 6 Count, Name | Format-List | Out-String -Width 220
'== TPM-WMI 1801 / 1803 (certificados de Arranque seguro)'
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-TPM-WMI'; Id=1801,1803} -MaxEvents 2 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id, Message | Format-List | Out-String -Width 220
Confirm-SecureBootUEFI
'== Arranque (ms)'
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Diagnostics-Performance/Operational'; Id=100} -MaxEvents 5 -ErrorAction SilentlyContinue | ForEach-Object { $d = ([xml]$_.ToXml()).Event.EventData.Data; "$($_.TimeCreated) BootTime=$(($d | Where-Object Name -eq 'BootTime').'#text')" }
'== Integridad de Windows'
DISM /Online /Cleanup-Image /CheckHealth | Out-String
(sfc /verifyonly | Out-String) -replace "`0", ''
