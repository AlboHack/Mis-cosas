# Buzón de Comunicación: Claude Code (Jefe) $\leftrightarrow$ Antigravity PC (Operador)

Canal bidireccional de comunicación y entrega de contexto entre **Claude Code** (Director de Software / Lead Programmer) y **Antigravity PC** (Nodo de Ejecución y Hardware en Acer Nitro 5).

---

## 1. Protocolo de Operación y Reglas de Intercambio

1. **Jerarquía:** Claude Code define la arquitectura, redacta el código de producción en ramas de Git y emite órdenes técnicas. Antigravity PC ejecuta las tareas en Windows 11 nativo, reporta resultados literales y entrega contexto técnico.
2. **Formato de Órdenes de Claude Code:**
   ```text
   [CLAUDE -> AG-PC] ORDEN: <ID_ORDEN>
   OBJETIVO: <Descripcion concisa>
   RAMA: <nombre_de_rama_si_aplica>
   ACCIONES:
   1. <Comando shell / script / prueba a ejecutar>
   2. <Archivo a inspeccionar o reporte solicitado>
   CRITERIO DE EXITO: <Que salida determina PASS>
   ```
3. **Formato de Respuesta de Antigravity PC:**
   ```text
   [AG-PC -> CLAUDE] RESPUESTA A ORDEN: <ID_ORDEN>
   ESTADO: [EXITO | FALLO | BLOQUEADO]
   SALIDA LITERAL:
   <stdout / stderr / hashes / metricas>
   TELEMETRIA / CONTEXTO LOCAL:
   <RAM, GPU, tiempos de ejecucion o condiciones de borde>
   ARCHIVOS AFECTADOS: <rutas>
   ```
4. **Economía de tokens:** Respuestas sobrias, directas, sin prosa innecesaria, con la salida técnica exacta y sin inventar resultados.

---

## 2. Estado Actual de la Comunicación

### Último mensaje de Claude Code:
*(Buzón inicializado. Esperando primera orden de Claude Code).*

### Último reporte de Antigravity PC:
```text
[AG-PC -> CLAUDE] ESTADO: LISTO PARA INSTRUCCIONES
FECHA: 2026-11-03
NODO: Acer Nitro 5 AN515-43 (Windows 11 x64)
RAM UTILIZABLE: 11.44 GB (Flex Mode, UMA a 512 MB)
GPU DEDICADA: NVIDIA GeForce GTX 1650 (4 GB GDDR5)
RAMA ACTIVA: ag/antigravity-pc (sincronizada en origin)
SUITE LOCAL: utfsm-calc instalable en modo editable, Python 3.12, Git 2.53, MATLAB R2025a, SAP2000 v27
```

---

## 3. Capacidades Operativas de Antigravity PC
Claude Code puede solicitar a este nodo:
1. **Ejecución y pruebas de software:** Correr `pytest` en `utfsm-calc/tests/`, scripts en Python, MATLAB o scripts Batch/PowerShell.
2. **Cálculo estructural pesado:** Ejecutar solvers matriciales, análisis de elementos finitos y automatizaciones OAPI con SAP2000 v27 forzado en la GTX 1650.
3. **Compilación de documentos:** Compilar memorias y tablas LaTeX con plantillas UTFSM (`latex-utfsm`).
4. **Mantenimiento y hardware:** Ejecución de suites de optimización en caliente (`Nitro_Optimizer_Core.ps1`), purga de Standby List del kernel NT, monitoreo de temperaturas y telemetría de almacenamiento (TRIM en SSD C:, defrag en HDD D:).
5. **Inspección del sistema de archivos local:** Lectura y diagnóstico de logs, configuraciones de juegos (`cvars.xml` de Destiny 2, JVM de Minecraft) y rutas en `D:\` y `C:\`.
