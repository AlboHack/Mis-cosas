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

## Pendiente de la auditoría (P7 del PC)
Espacio libre en C:, tamaño de `hiberfil.sys`, programas que arrancan con Windows, apps preinstaladas, versión de los drivers de NVIDIA y AMD, y consumo de Defender durante un análisis en SAP2000. Con esos datos se decide sobre el almacenamiento reservado, los efectos visuales y las exclusiones de Defender. [Por verificar] el valor de `HiberFileType` para el modo reducido se confirma en el Nitro.
