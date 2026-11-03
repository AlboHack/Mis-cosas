@echo off
:: Abre el menu como administrador. Argumento opcional: Ram, Calculo o FinCalculo (para accesos directos).
powershell.exe -NoProfile -Command "Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0Mantenimiento.ps1\" %1'"
