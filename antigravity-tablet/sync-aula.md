# Sincronización con Aula USM

Script principal: [`scripts/sincronizar_aula_semanal.py`](../scripts/sincronizar_aula_semanal.py). Corre en la tablet; las rutas por defecto (`/storage/emulated/0/Download/Universidad/...`, `~/Mis-cosas`) se cambian con variables `SYNC_*`.

## Cada corrida
1. **Token.** Se lee de `~/.moodle_token`. El login de Aula es por Microsoft SSO: el token sale por `launch.php` y lo renueva [`scripts/renovar_token_aula.py`](../scripts/renovar_token_aula.py) desde una pestaña de Aula abierta en Brave (CDP, puerto 9222). Si expiró, la corrida falla pidiendo a Nicolás renovarlo. El token se enmascara en los logs.
2. **Lista blanca.** `MoodleAPIClient.ALLOWED_FUNCTIONS` solo admite lectura: `core_webservice_get_site_info`, `core_course_get_contents`, `core_calendar_get_calendar_events`, `mod_forum_get_forums_by_courses`, `mod_forum_get_forum_discussions`, `mod_forum_get_discussion_posts`, `core_message_get_conversations`, `core_message_get_conversation_messages`, `mod_assign_get_assignments`. Cualquier otra lanza `WhitelistViolationError`.
3. **Ramos.** FICA CIV222 = 62177, FAE CIV233 = 62178, Fluidos CIV244 = 62182, Transporte CIV386 = 62192, Prácticas POC = 5623.
4. **Plan y ejecución.** Manifiesto por URL (timemodified, tamaño, sha256, ruta) y caché de hashes. Repara rutas obsoletas buscando por hash, sin volver a descargar. Si hay más de 20 archivos pendientes, corta sin tocar nada (salvo `--permitir-masivo`). Rechaza descargas que sean HTML de login o PDF/Office con cabecera incorrecta. Una versión modificada en Aula se guarda y la anterior queda como `<nombre>_vAAAAMMDD`.
5. **Destino.** `universidad/2026-2/<RAMO>/`, repartido por `determine_subfolder` en `Planificacion/`, `Evaluaciones_y_Entregas/` y `Material_y_Apuntes/` según palabras clave del módulo, del archivo y de la sección. Mueve archivos ya bajados si su carpeta cambió. Esta estructura no es la de Aula: ver [estado.md](estado.md).
6. **Drive.** `rclone copy` (nunca `sync`) a `gdrive:Universidad/2026-2/<ramo>/<subcarpeta>`.
7. **Repo.** `git pull --rebase --autostash`, copia de los archivos nuevos (menos de 50 MB) a `universidad/2026-2/`, commit `chore(sync): actualizacion semanal incremental (FECHA)` y push a `main`.
8. **Evaluaciones y calendario.** Fusiona la API con `universidad/2026-2/evaluaciones_manual.json` en `evaluaciones.json`; [`scripts/sincronizar_calendario_android.py`](../scripts/sincronizar_calendario_android.py) mapea eventos por UID y pone 3 recordatorios por evaluación.
9. **Novedades.** [`scripts/aula_novedades.py`](../scripts/aula_novedades.py): foros (solo docentes y ayudantes) a `avisos.md`; foto de la página en `pagina_curso.json` y diferencias en `cambios_pagina.md`; mensajes privados solo en la tablet (al repo llega el conteo); alerta "⚠ POSIBLE CAMBIO DE EVALUACIÓN".
10. **Contexto.** [`scripts/generar_contexto_ramos.py`](../scripts/generar_contexto_ramos.py) escribe `Contexto_Asignatura.md` por ramo y `Contexto_Semestre_2026-2.md`.
11. **Latido.** `universidad/2026-2/ultima_sincronizacion.json` en cada corrida que llega a esa etapa.

## Programación
- [`scripts/instalar_programacion.sh`](../scripts/instalar_programacion.sh) (idempotente) instala con cronie `7 * * * *` → [`scripts/programador_sync.py`](../scripts/programador_sync.py), y agrega a `~/.bashrc` el arranque de `crond` si no corre: `com.agycli` no recibe BOOT_COMPLETED.
- `programador_sync.py` lanza [`scripts/sincronizar_sabados.sh`](../scripts/sincronizar_sabados.sh) si es sábado desde las 10:00 sin corrida exitosa ese día, o si la última exitosa tiene 7 días o más. Tras un fallo reintenta pasadas 6 h. Estado en `~/.sync_programador.json`.
- `sincronizar_sabados.sh` toma `termux-wake-lock` y lo libera al salir.
- En Android se desactivó el phantom process killer: `settings put global settings_enable_monitor_phantom_procs false` [según la sesión de claude.ai; no está en el repo].

## Pruebas (`scripts/pruebas/`)
| Archivo | Cubre | Dónde corre |
|---|---|---|
| `test_aceptacion.py` | T2, T3, T6, T8 y calendario | Solo tablet (necesita `rclone`) |
| `test_aceptacion_token.py` | T2', T3', T9'–T18, T20, T26, avisos; T13 verifica que el repo real no cambie | Tablet; aquí falla T13 si el repo tiene cambios sin commit |
| `test_novedades.py`, `test_programador.py` (T28), `test_pre_push.py` (T19), `test_enunciados.py` (T29) | Novedades, programador, hook, enunciados de entregas | Cualquier equipo |
| `test_t2_real.py`, `test_t3_real.py` | Corridas de `run_sync()` con API simulada; los llama `test_aceptacion.py` | Cualquier equipo |

Las pruebas aíslan sus rutas con variables de entorno (`SYNC_ROOT_DIR`, `SYNC_REPO_DIR`, `SYNC_LOG_FILE`, `CALENDAR_EVALUACIONES_FILE`, `SYNC_PROGRAMADOR_ESTADO`, etc.).
