# Perfil del Nitro 5

Ajustes de Windows elegidos para este equipo: notebook, 12 GB de RAM, SSD de 120 GB para el sistema, HDD para datos, GTX 1650 con Optimus. Cada ajuste está en `ajustes.json` con su fuente, el motivo para el Nitro y su riesgo. Se aplica con respaldo del valor real previo y se puede deshacer uno por uno.

Doble clic en `Perfil.bat`: muestra qué está aplicado, simula, aplica (primero crea un punto de restauración) o deshace por id.

## Fuentes revisadas
| Repositorio | Licencia | Qué se tomó |
|---|---|---|
| [ChrisTitusTech/winutil](https://github.com/ChrisTitusTech/winutil) `config/tweaks.json` | MIT | Diseño (cada ajuste como dato con valor original), agrupación de svchost para 12 GB o menos, telemetría, distribución P2P, apps en segundo plano, modo de juego, almacenamiento reservado, efectos visuales |
| [farag2/Sophia-Script-for-Windows](https://github.com/farag2/Sophia-Script-for-Windows) `Sophia.psm1` | MIT | HAGS solo con GPU dedicada y WDDM ≥ 2.7 |
| [henrypp/memreduct](https://github.com/henrypp/memreduct) `src/main.c`, `main.h` | GPL-3.0 (solo referencia) | La purga completa de standby y la de la lista modificada están marcadas como causantes de congelamientos (`REDUCT_MASK_FREEZES`); por defecto purga solo la standby de prioridad baja. `mantenimiento/` pasó a usar esa purga |
| [hellzerg/optimizer](https://github.com/hellzerg/optimizer) | GPL-3.0 (solo referencia) | Revisado; sin ajustes nuevos para este equipo |

## Lo que se descartó
- **Plan Ultimate Performance:** winutil lo marca "NOT FOR LAPTOPS". En su lugar, `mantenimiento/` sube a Alto rendimiento solo durante una sesión de cálculo.
- **Apagar la hibernación por completo:** en un notebook se pierde la hibernación con batería. Se usa `hiberfil` reducido, que conserva el inicio rápido.
- **Deshabilitar Windows Search:** el repo y MATLAB están en D: y la búsqueda se volvería lenta. Se decide con los datos de la auditoría.
- **Recortar la memoria de los procesos y borrar las cachés de shaders:** ver `mantenimiento/README.md`.

## Resultado de la auditoría (P7, 2026-11-03)
| Dato | Valor | Consecuencia |
|---|---|---|
| Espacio libre en C: | 30.5 GB de 110 | El almacenamiento reservado sigue activo; no hace falta liberar esos 7 GB |
| Hibernación | Apagada, sin `hiberfil.sys` | `hibernacion-reducida` queda inactivo: la reactivaría |
| Archivo de paginación | 8.5 GB asignados, pico de 1.3 GB | Se deja administrado por Windows, en el SSD |
| Ya aplicados | telemetría, apps en segundo plano, HAGS, modo de juego | — |
| Por aplicar (activos) | `svchost-agrupado`, `entrega-p2p`, `inicio-reducememory` | Pedido P8 |
| Modo gráfico de SAP2000 | P14: `GraphicsMode=GDIPlus` en `SAP2000v27.ini`: dibujaba con Microsoft Basic Render Driver (software), sin GPU | P15 lo pasa a DirectX y verifica por nombre |
| Integridad (P13) | DISM: "The component store is repairable" (hay daño reparable); límite de instantáneas 2.21 GB con 3 borrados (Volsnap 36); Google Update agota 30 s al arranque | P16: RestoreHealth, sfc /scannow, límite de 5 GB, `servicio-google-update-manual` |
| Arranque seguro (P13) | KEK 2023 sin aprovisionar; BIOS V1.12 es la última de Acer | Sin acción posible: Windows sigue arrancando, pero no recibirá futuras actualizaciones de Arranque seguro que requieran el KEK nuevo [Por verificar alcance] |
| GPU de SAP2000 | P12: SAP2000 abierto antes del ajuste seguía en un adaptador sin uso de VRAM, no en la NVIDIA | `gpu-dedicada-ingenieria` aplicado; P14 verifica por nombre (DXGI) al reabrir |
| Arranque | ReduceMemory, Enviar a OneNote, Opera GX Browser Assistant, Wallpaper Engine | `inicio-*`: los dos primeros se eliminan del arranque con respaldo; los dos últimos se deshabilitan como en el Administrador de tareas (decisión de Nicolás). Discord, LGHUB, audio y Riot Vanguard se mantienen |
| Driver AMD Vega 10 | 27.20.1028.1, julio de 2020 | Actualizar a mano desde AMD (Ryzen 7 3750H) [Por verificar la última versión disponible] |
| Plan de energía | Alto rendimiento fijo | Se mantiene (decisión de Nicolás) |
| Defender | 349 MB; modelos en `D:\Modelos RUN` | `defender-modelos-sap` inactivo hasta que Nicolás decida |
