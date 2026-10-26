# Decisiones de configuración

| Fecha | Decisión | Por qué | Evidencia |
|---|---|---|---|
| 2026-10-21 | Código recurrente en el paquete utfsm-calc, no pegado en las skills | Cargar una skill cargaba cientos de líneas de código y cada chat lo reescribía | 7 pruebas contra soluciones cerradas |
| 2026-10-21 | Pynite como juez independiente de pórticos | Coincide con el núcleo propio en la sexta cifra, incluida una rótula | Caso 01 |
| 2026-10-21 | anastruct descartado | Con una rótula interna se desvía 12 % | Caso 01 |
| 2026-10-21 | handcalcs para memorias de cálculo | El número del informe sale del código verificado | Compilado con pdflatex |
| 2026-10-21 | Punto decimal en todo | El preámbulo usa es-nodecimaldot | Falla de coma en caso 01 (v1) |
| 2026-10-21 | `friccion` lanza error en 2300 < Re < 4000 | Colebrook en transición sobrestima h_f hasta 93 % | Caso 02 |
| 2026-10-21 | profundizar-prompt y buscar-y-evaluar-skills solo a pedido | Cargaban unas 1 400 palabras en cada tarea | Reglas 4 y 5 de las instrucciones |
| 2026-10-21 | Fuentes externas registradas en `fuentes/` con revisión de cambios (`scripts/revisar_fuentes.py`) | Portar mejoras de los repos originales sin perder las adaptaciones | Base fijada en los commits de hoy |
| 2026-10-21 | Nueva skill interrogar-planteamiento, adaptada de grilling | Decisiones de modelo implícitas son la causa típica de diferencias con SAP2000 | Pendiente de caso de prueba |
| 2026-10-21 | writing-for-agents copiada sin cambios para editar skills en este repo | Principios de una sola fuente de verdad y divulgación progresiva | Licencia MIT incluida |
| 2026-10-21 | verification-before-completion (superpowers) no se adopta | verificacion-independiente ya la cubre con contenido de ingeniería | Solo registrada en fuentes para comparar |
| 2026-10-21 | pdf de Anthropic solo como referencia | Licencia propietaria: no se copia a un repo público | — |

| 2026-10-26 | Reparto de la automatización: Claude escribe y prueba el código en ramas `claude/...`; Antigravity lo ejecuta en la tablet (adb, rclone, calendario reales), hace el merge squash y reporta | Pedido de Nicolás; las fallas del día (pruebas sobre datos reales, commits directos a main, `rclone sync`) salieron del código escrito sin revisión | Iteraciones del 25 y 26-oct |
| 2026-10-26 | Respaldo en Drive con `rclone copy`, nunca `sync` | `sync` replica en Drive cualquier pérdida local | T18 |
| 2026-10-26 | Hook `scripts/hooks/pre-push` en vez de la skill git-guardrails | git-guardrails es un hook de Claude Code y no corre en Antigravity; el hook de git corre con cualquier agente | T19 |
| 2026-10-26 | Skills para Antigravity: tdd y diagnosing-bugs (mattpocock/skills@5beb35b); strategic-compact descartada | Instrucciones puras y portables; strategic-compact depende de hooks de Claude Code | Lectura de cada SKILL.md |
| 2026-10-26 | Novedades de Aula: foros (solo docentes y ayudantes, con sus respuestas), cambios en la página de cada ramo y mensajes privados; detector de posibles cambios de evaluación | Las reprogramaciones llegan por foro, por texto en la página o por mensaje, no por el calendario de Aula | T21–T25 |
| 2026-10-26 | Mensajes privados solo en la tablet; textos y nombres de estudiantes fuera del repo | El repo es público: son conversaciones personales y datos de terceros | T21, T23 |
| 2026-10-26 | Programación: cron (cronie) cada hora + `programador_sync.py` que decide si corresponde (sábado ≥ 10:00, o 7 días sin corrida exitosa) con reintento cada 6 h; crond se relanza desde `~/.bashrc` | com.agycli no recibe BOOT_COMPLETED (Termux:Boot no aplica); la recuperación cubre tablet apagada o crond detenido por HyperOS. Se descarta el programador de Antigravity: depende de una sesión del agente y no es determinístico | T28 |
