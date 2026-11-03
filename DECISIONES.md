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
| 2026-10-27 | Drive: solo el árbol `gdrive:Universidad/2026-2/<ramo>/<subcarpeta>`, copiado en cada corrida y verificado archivo por archivo; se eliminan el ZIP semanal y la carpeta `Deltas` | Nicolás quiere cada archivo en su ramo; el ZIP duplicaba el material y confundía dónde quedó lo nuevo | T29 |

## 2026-11-02 — Enunciados de entregas (mod_assign)
- Motivo: la Tarea 2 de FICA (CIV222, vence 2026-11-09 23:59 -03:00) es una entrega cuyo enunciado va como `introattachments`; `core_course_get_contents` no lo lista y no se descargaba.
- Cambio: `mod_assign_get_assignments` (solo lectura) a la lista blanca; `agregar_enunciados_de_entregas` los suma al módulo como archivos y el flujo normal los descarga. Falla de la llamada = aviso, no aborta. Prueba T29 (`test_enunciados.py`).
- Corrección de pruebas: `scripts/test_t2_real.py` utilizaba mocks HTML de web scraping obsoletos (anteriores a la migración REST API de Moodle), provocando `JSONDecodeError` al invocar `sincronizar_aula_semanal.py`. Se actualizó para simular respuestas JSON de Moodle WebService REST (`core_webservice_get_site_info`, `core_course_get_contents`, etc.), logrando 100% PASS en `test_aceptacion.py`.

## 2026-11-02 — Clasificación contextual por módulo/archivo y reubicación automática
- Motivo: Profesores de FICA y FAE suben tareas, controles, pautas y apuntes dentro de la sección "Información General". La clasificación anterior basada únicamente en `section_name` enviaba todo a `Planificacion/Información General/`. En particular, el enunciado de la Tarea 2 de FICA (`CIV222 2026-20 Ejercicio Gestión de Costos.pdf`) y las tareas/controles quedaban fuera de `Evaluaciones_y_Entregas/`.
- Cambio: `determine_subfolder` ahora recibe `mod` y `filename`. Clasifica `modname == 'assign'` o palabras clave de evaluación en `Evaluaciones_y_Entregas/`, y apuntes/guías en `Material_y_Apuntes/`. `run_sync` detecta archivos existentes en carpetas previas incorrectas y los reubica (`shutil.move`) actualizando manifest, repo git y Drive sin re-descargas.


## 2026-11-03 — Integración del nodo Antigravity PC en AlboHack/Mis-cosas (`antigravity-pc/`)
- Motivo: Consolidación del ecosistema distribuido de Nicolás (Claude en navegador Brave como arquitecto y desarrollador de producción, Antigravity Tablet para automatizaciones móviles/Aula/cuentas, y Antigravity PC para ejecución nativa en Windows 11, cálculo estructural de alto impacto en SAP2000 v27 / MATLAB R2025a y mantenimiento del hardware).
- Cambio: Creación del directorio raíz `antigravity-pc/` con `CONTEXTO.md`, `README.md` y la suite de optimización (`optimizacion/`) con documentación técnica de la ingeniería inversa aplicada (purga de Standby List del Kernel NT clase 80, recorte en caliente de Working Sets, motor de TRIM con Watchdog Timer de 25s en SSD C: y enrutamiento forzado a la GTX 1650).
