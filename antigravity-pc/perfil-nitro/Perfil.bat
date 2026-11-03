@echo off
:: Abre el menu del perfil del Nitro como administrador.
powershell.exe -NoProfile -Command "Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0Perfil.ps1\"'"
