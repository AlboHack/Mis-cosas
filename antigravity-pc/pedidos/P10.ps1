# P10: inventario de drivers y salud del equipo (solo lectura; se corre elevado). No imprime el número de serie.
'== Drivers'
Get-CimInstance Win32_PnPSignedDriver | Where-Object { $_.DeviceName -and ($_.Manufacturer -notmatch '^(Microsoft|\(Standard)' -or $_.DeviceClass -in 'DISPLAY','NET','BLUETOOTH','MEDIA','HDC','SCSIADAPTER','SYSTEM') } |
  Sort-Object DeviceClass, DeviceName | Select-Object DeviceClass, DeviceName, Manufacturer, DriverVersion, @{n='Fecha';e={if ($_.DriverDate) { $_.DriverDate.ToString('yyyy-MM-dd') }}} |
  Format-Table -AutoSize | Out-String -Width 260
'== Drivers ofrecidos por Windows Update'
try { $r = (New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher().Search("IsInstalled=0 and Type='Driver'"); $r.Updates | Select-Object Title, DriverVerDate | Format-Table -AutoSize | Out-String -Width 200 } catch { "Windows Update: $_" }
'== Equipo, BIOS, RAM y discos'
(Get-CimInstance Win32_ComputerSystem).Model
Get-CimInstance Win32_BIOS | Select-Object SMBIOSBIOSVersion, ReleaseDate | Format-List | Out-String
Get-CimInstance Win32_PhysicalMemory | Select-Object BankLabel, DeviceLocator, @{n='GB';e={$_.Capacity/1GB}}, Speed, ConfiguredClockSpeed, Manufacturer, PartNumber | Format-Table -AutoSize | Out-String -Width 200
Get-PhysicalDisk | Select-Object FriendlyName, BusType, MediaType, @{n='GB';e={[math]::Round($_.Size/1GB)}} | Format-Table -AutoSize | Out-String
Get-PhysicalDisk | Get-StorageReliabilityCounter | Select-Object DeviceId, Temperature, TemperatureMax, Wear, PowerOnHours, ReadErrorsUncorrected, WriteErrorsUncorrected | Format-Table -AutoSize | Out-String
'== Batería (mWh y ciclos)'
"Diseño: $((Get-CimInstance -Namespace root\wmi BatteryStaticData -ErrorAction SilentlyContinue).DesignedCapacity)"
"Carga completa actual: $((Get-CimInstance -Namespace root\wmi BatteryFullChargedCapacity -ErrorAction SilentlyContinue).FullChargedCapacity)"
"Ciclos: $((Get-CimInstance -Namespace root\wmi BatteryCycleCount -ErrorAction SilentlyContinue).CycleCount)"
'== Errores del sistema (30 días)'
Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2; StartTime=(Get-Date).AddDays(-30)} -MaxEvents 500 -ErrorAction SilentlyContinue | Group-Object ProviderName, Id | Sort-Object Count -Descending | Select-Object -First 15 Count, Name | Format-Table -AutoSize | Out-String -Width 200
'Kernel-Power 41:'; Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-Kernel-Power'; Id=41} -MaxEvents 5 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty TimeCreated
'WHEA:'; Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-WHEA-Logger'} -MaxEvents 5 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id | Format-Table | Out-String
'== Arranque (ms)'
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Diagnostics-Performance/Operational'; Id=100} -MaxEvents 5 -ErrorAction SilentlyContinue | ForEach-Object { $d = ([xml]$_.ToXml()).Event.EventData.Data; "$($_.TimeCreated) BootTime=$(($d | Where-Object Name -eq 'BootTime').'#text')" }
'== Integridad, restauración y Defender'
DISM /Online /Cleanup-Image /CheckHealth | Out-String
(sfc /verifyonly | Out-String) -replace "`0", ''
Get-ComputerRestorePoint | Select-Object -Last 3 Description, CreationTime | Format-Table | Out-String
Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled, AntivirusSignatureLastUpdated, QuickScanAge, FullScanAge | Format-List | Out-String
