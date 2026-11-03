@echo off
:: P13: doble clic de Nicolas. Pide permiso de administrador una vez; la salida queda en Mantenimiento\logs\P13_*.log
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\Ejecutar-Elevado.ps1" -Script "%~dp0P13-admin.ps1" -Nombre P13
pause
