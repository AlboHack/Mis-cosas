# Mantenimiento del Nitro 5

Reemplaza a `optimizacion/` (Nitro_Optimizer v4.1 y Desinstalador_Raiz). Doble clic en `Mantenimiento.bat`; acepta `Ram`, `Calculo` o `FinCalculo` como argumento para accesos directos.

| Opción | Qué hace | Cambio respecto de v4.1 |
|---|---|---|
| Sesión de cálculo | Plan Alto rendimiento, GTX 1650 para SAP2000 y MATLAB, prioridad sobre lo normal; al cerrar restaura el plan anterior | Nuevo: el plan de energía pesa más que liberar RAM en un notebook |
| Purgar standby | Solo si standby ≥ 1024 MB y libre < 1024 MB (criterio de ISLC), y solo la caché de prioridad baja, como Mem Reduct por defecto | v4.1 purgaba siempre, aunque sobrara memoria libre. Como administrador la purga funcionaba (P1 del PC); la versión nueva además habilita el privilegio de forma explícita |
| Temporales | Archivos de más de 7 días en TEMP, Windows\Temp y WER; primero simulación | v4.1 vaciaba la papelera sin preguntar y borraba volcados de error |
| Optimizar unidades | Lee si la unidad es SSD (retrim) o HDD (desfragmentar) | v4.1 suponía el tipo por la letra y cortaba el retrim a los 25 s |
| Diagnóstico | Memoria, salud de discos, TRIM, top de procesos, preferencias de GPU | Igual |
| Desinstalar | Desinstalador oficial de cada programa de `programas_a_quitar.json`, residuos solo si ya no está instalado; simulación primero y confirmación por programa | v4.1 terminaba procesos y borraba carpetas y claves por subcadena: "Brave" en el registro borra toda entrada que contenga Brave |

## Lo que se quitó y por qué
- **Recorte de working sets** (`EmptyWorkingSet` sobre Opera, Discord, Steam): manda páginas activas a disco; el programa las vuelve a leer al usarlo y aparecen los tirones que se querían evitar.
- **Borrado de cachés de shaders** (D3DSCache, NVIDIA DXCache, AMD DxCache): obliga a recompilar los shaders en el siguiente arranque del juego, con tirones durante la partida.
- **Prioridad Alta** a juegos y solvers: se usa "sobre lo normal"; Alta puede dejar sin CPU al audio y a la entrada.
- **Ajustes de Destiny 2, Minecraft y Opera GX**: no son mantenimiento del equipo; quedan en `CONTEXTO.md` como configuración.

## Pruebas
`pwsh -File pruebas/Pruebas.ps1` (también con `powershell.exe`). En Windows agrega pruebas de humo contra el sistema real; el workflow `pc-mantenimiento` las corre en un runner Windows con PowerShell 7 y 5.1.
