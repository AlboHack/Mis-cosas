# Puntos de mejora del Nitro 5 (AN515-43)

Lista viva. Cada punto indica de dónde sale, qué dato lo decide y su estado. Lo que se aplica por software va al catálogo `perfil-nitro/ajustes.json`; lo físico o lo que necesita el sitio del fabricante va como pedido al nodo PC.

## 1. Repositorios conocidos (aplicado o en el catálogo)
| Punto | Fuente | Estado |
|---|---|---|
| Telemetría, apps en segundo plano, HAGS, modo de juego | winutil, Sophia Script | Aplicados (P7) |
| Agrupar svchost para ≤ 12 GB, sin P2P de actualizaciones | winutil | P8 |
| Programas de arranque innecesarios | Auditoría P7 | P8 |
| Purga de memoria solo de prioridad baja | Mem Reduct (`REDUCT_MASK_FREEZES`) | Aplicado en `mantenimiento/` |
| Apps preinstaladas sin uso (Bing Search, Dev Home, Power Automate, People, Correo y Calendario antiguos, Start Experiences, Acer Registration) | Listas `AppxDefault` de winutil y de Win11Debloat | Pendiente de decisión de Nicolás; se pueden reinstalar desde la Tienda |

## 2. De nicho, específicos de este equipo
| Punto | Por qué | Dato que lo decide | Estado |
|---|---|---|---|
| Driver de la Vega 10 de 2020 | Maneja la pantalla interna (Optimus); un driver de 6 años arrastra errores corregidos | Versión en la página de AMD | P9 |
| BIOS V1.12 | Acer publica correcciones de ventiladores y estabilidad por BIOS; hay reportes de BIOS problemáticas para el AN515-43 en el foro de Acer | Última versión y notas en la página de Acer del modelo | P10 (solo consultar) |
| SSD Kingston A400 de 120 GB (SATA, sin DRAM) | Sin caché DRAM, se pone lento cuando se llena; mantener más de 20 % libre | Espacio libre (hoy 30.5 GB, 27 %) y desgaste SMART | P10 |
| Límite de temperatura del procesador con RyzenAdj (`--tctl-temp`) | FlyGoat/RyzenAdj soporta la familia Picasso (`FAM_PICASSO` en `lib/api.c`); bajar el límite reduce ruido y caídas de frecuencia por calor. Vuelve a valores de fábrica al reiniciar | Temperaturas reales bajo carga (SAP2000, juego) | Pendiente: en Windows usa el driver WinRing0, que Defender marca como vulnerable. Solo si las temperaturas lo justifican [Por verificar] |
| RAM 12 GB en configuración asimétrica | Según Crucial, el AN515-43 tiene 2 ranuras y admite hasta 32 GB DDR4; 2 × 8 GB iguales dan doble canal completo | `Win32_PhysicalMemory`: ranuras, módulos y velocidad | P10 |
| Reemplazar el SSD de 120 GB por un NVMe de 500 GB a 1 TB | Mayor mejora práctica posible: más espacio y velocidad para Windows, SAP2000 y MATLAB | Tipo de ranura M.2 (NVMe o solo SATA) en el manual de servicio del modelo [Por verificar] | Pendiente de datos |

## 3. Típicos de cualquier PC
| Punto | Cómo se revisa | Estado |
|---|---|---|
| Drivers al día (chipset, Wi-Fi, Bluetooth, audio, touchpad, NVIDIA) | Inventario completo y lo que ofrece Windows Update | P10 |
| Salud de los discos | Temperatura, desgaste, horas de uso y errores SMART | P10 |
| Salud de la batería | Capacidad de diseño frente a capacidad actual y ciclos | P10 |
| Errores del sistema | Apagados inesperados (Kernel-Power 41), errores de hardware (WHEA), errores más repetidos en 30 días | P10 |
| Integridad de Windows | `DISM /CheckHealth` y `sfc /verifyonly` | P10 |
| Puntos de restauración activos | Protección del sistema encendida en C: | P10 |
| Defender al día | Firmas y fecha del último análisis | P10 |
| Tiempo de arranque | Diagnóstico de arranque de Windows (evento 100) | P10, antes y después de P8 |
| Limpieza de polvo y pasta térmica | Notebook de unos 6 años: ventiladores con polvo y pasta seca suben la temperatura y bajan el rendimiento | Físico, lo decide Nicolás según temperaturas |
| Respaldo de los archivos personales | El repo y Drive cubren `universidad/`; `D:\Modelos RUN` y los documentos personales no | Pendiente de decisión |

## Fuentes
- [ChrisTitusTech/winutil](https://github.com/ChrisTitusTech/winutil), [Raphire/Win11Debloat](https://github.com/Raphire/Win11Debloat), [farag2/Sophia-Script-for-Windows](https://github.com/farag2/Sophia-Script-for-Windows) (MIT)
- [henrypp/memreduct](https://github.com/henrypp/memreduct), [FlyGoat/RyzenAdj](https://github.com/FlyGoat/RyzenAdj) (GPL-3.0 / LGPL-3.0, solo referencia)
- [Crucial: compatibilidad del Acer Nitro 5 AN515-43](https://crucial.com/scanview/c2bd4d7c31d926c3)
- [Foro de Acer: problemas con BIOS del AN515-43](https://community.acer.com/en/discussion/714909/nitro-an515-43-bios-update-has-ruined-my-daughters-laptop)
