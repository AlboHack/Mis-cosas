# Suite de Optimización de Hardware y Memoria — Acer Nitro 5

Documentación técnica e ingeniería inversa de los scripts desarrollados para optimizar el rendimiento de la CPU Ryzen 7 3750H, la GPU GTX 1650 y los 12 GB de RAM en modo asimétrico (Flex Mode).

---

## 1. Módulos y Scripts Disponibles

| Archivo | Propósito | Privilegios Requeridos |
|---|---|---|
| **`Nitro_Optimizer.bat`** | Lanzador interactivo con menú de 7 modos de operación | Autoeleva con UAC a Administrador |
| **`Nitro_Optimizer_Core.ps1`** | Motor principal (v4.1) con compilación C# en memoria | Administrador (para llamadas a nivel de disco y kernel) |
| **`Liberar_RAM_Juegos.bat`** | Atajo de 1 clic para liberar memoria de forma instantánea antes de jugar | Autoeleva con UAC |
| **`Desinstalador_Raiz_Bloatware.bat`** | Eliminador de carpetas y claves protegidas de bloatware | Autoeleva con UAC |
| **`Desinstalador_Raiz_Core.ps1`** | Desinstalador desatendido de software residual (CCleaner, IObit, Brave, etc.) | Administrador |

---

## 2. Fundamentos de Ingeniería Inversa Implementados

### A. Purga de la Standby List del Kernel NT (Algoritmo ISLC / RAMMap)
En Windows, los archivos leídos quedan retenidos en la lista de espera (*Standby List*), lo que genera microcongelamientos (*stuttering*) en juegos y simulaciones numéricas pesadas cuando el Administrador de Memoria de Windows intenta desalojarla en caliente.
- **Implementación nativa:** Compilación en memoria mediante `Add-Type` de una rutina C# que invoca directamente a la API no documentada del kernel en `ntdll.dll`:
  ```csharp
  [DllImport("ntdll.dll")]
  public static extern uint NtSetSystemInformation(int infoClass, IntPtr infoPtr, int infoLen);
  ```
  Se invoca la clase `80` (`SystemMemoryListInformation`) con el código de operación `4` (`MemoryPurgeStandbyList`). Devuelve `0x00000000` (`STATUS_SUCCESS`) liberando la memoria en microsegundos sin requerir ejecutables externos residentes.

### B. Recorte de Working Sets sin Terminar Procesos
Para navegadores con múltiples pestañas (Opera GX) o clientes de mensajería (Discord, WhatsApp), cerrar el proceso interrumpe la sesión de trabajo.
- **Implementación:** Se invoca `EmptyWorkingSet` de `psapi.dll` sobre los identificadores de proceso (`Process.Handle`). Windows transfiere las páginas inactivas al área de respaldo, reduciendo el consumo privado activo de ~6 GB a menos de 1.5 GB de forma transparente.

### C. Motor de TRIM con Watchdog Timer de 25s (SSD Kingston C:)
- **Problema previo:** El cmdlet `Optimize-Volume` invoca la interfaz WMI RPC `MSFT_Volume`. Si el controlador Phison S11 del SSD Kingston SA400 está ocupado o la sesión carece del token de seguridad elevado, el proceso se congela de 30 a 45 segundos antes de fallar con el error `0x89000024`.
- **Solución v4.1:** Se utiliza la utilidad nativa `defrag.exe C: /L /U` controlada por un temporizador `System.Diagnostics.Process` con `WaitForExit(25000)`. Si la operación supera los 25 segundos, el temporizador interrumpe la llamada de forma limpia sin bloquear la consola.

### D. Enrutamiento Forzado de GPU Dedicada en DirectX
Para evitar que la pantalla MUXless conmute de forma errónea a la Radeon Vega 10 durante cálculo o render pesado:
- Clave de registro: `HKCU:\Software\Microsoft\DirectX\UserGpuPreferences`
- Directiva: `GpuPreference=2;` (Alto Rendimiento / GTX 1650)
- Aplicado a: `destiny2.exe`, `SAP2000.exe` (v27), `matlab.exe` y entornos Java (`javaw.exe`).

### E. Optimización de cvars para Destiny 2 (Motor Tiger)
En `%APPDATA%\Bungie\DestinyPC\prefs\cvars.xml`:
- `force_enable_multi_threaded_render_submit = 1`: Fuerza al motor gráfico a distribuir el submission de comandos DirectX 11 en los 8 hilos del Ryzen 7 3750H, eliminando cuellos de botella monohilo.
- `hdr_output = 0`: Desactiva cálculos de rango dinámico redundantes en pantallas de 8 bits.

### F. Flags de JVM para Minecraft con Mods en Flex Mode (DDR4 2400 MHz)
Debido a la configuración de 12 GB (4 GB + 8 GB):
- **Zona simétrica:** Los primeros 8 GB operan en Dual Channel real (128-bit de ancho de banda).
- **Zona asimétrica:** Los últimos 4 GB operan en Single Channel (64-bit, mitad de velocidad de transferencia).
- **Regla:** Asignar como máximo 6 GB a la máquina virtual Java (`-Xms5120M -Xmx6144M`) para asegurar que todo el heap resida en el bloque simétrico de alta velocidad.
- **Argumentos de baja pausa (G1GC):**
  ```text
  -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch
  ```
