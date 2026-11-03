@echo off
TITLE Desinstalador de Raiz Quirurgico
setlocal

:: 1. Comprobacion de permisos de Administrador
powershell.exe -NoProfile -Command "if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { exit 1 }"
if %errorlevel% neq 0 (
    echo [!] Solicitando permisos de Administrador para desinstalacion completa...
    powershell.exe -NoProfile -Command "Start-Process powershell.exe -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"\"%~dp0Desinstalador_Raiz_Core.ps1\"\"' -Verb RunAs"
    exit /b
)

:: 2. Si ya esta elevado, ejecutar directamente
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Desinstalador_Raiz_Core.ps1"
