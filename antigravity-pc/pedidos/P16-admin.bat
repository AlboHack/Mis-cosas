@echo off
:: P16: doble clic de Nicolas. Pide permiso de administrador una vez; salida en Mantenimiento\logs\P16_*.log
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\Ejecutar-Elevado.ps1" -Script "%~dp0P16-admin.ps1" -Nombre P16
pause
