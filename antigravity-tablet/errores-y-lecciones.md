# Errores pasados y lecciones

## Errores que no deben repetirse
| Error | Corrección | Prueba |
|---|---|---|
| `rclone sync` podía borrar respaldos en Drive | Siempre `rclone copy` | T18 |
| Las pruebas escribían en las carpetas de datos reales | Rutas por variables de entorno y guardia de aislamiento | T13 |
| `test_t2_real` y `test_t3_real` reescribían `Contexto_Asignatura.md` y `.contexto_estado.json` reales de los 5 ramos (el generador de contexto tomaba la ruta del repo por defecto) | Fijan `SYNC_REPO_DIR` y `SYNC_ROOT_DIR` antes de cargar la sync (2026-11-03) | 0 archivos reales modificados al correr `test_aceptacion.py` |
| El hook partía mal rutas con espacios o tildes | `git -c core.quotepath=off diff --name-only -z` | T19 |
| Rutas obsoletas en el manifiesto tras borrar duplicados (115 archivos falsos pendientes) | Reparación buscando por hash; desde el espejo de Aula, el archivo se copia a su carpeta sin descargar | T26 |
| La deduplicación por hash dejaba un archivo de Aula fuera de su sección si su contenido ya existía en otra | Cada archivo de Aula en su propia ruta (espejo) | T15 |
| Commit desde un clon sin checkout: borraría todo el repo | Nunca hacer commit sin árbol de trabajo completo | — |

## Trabajar con AG
- Es lento si se le deja razonar: consultaba a Gemini y escribía informes largos. Pedidos cerrados, comandos literales, reporte con formato y máximo de líneas ([plantilla-prompt.md](plantilla-prompt.md)).
- Sus números se verifican: la Tarea 2 de FICA no vencía el 10-nov sino el 09-nov 23:59 (timestamp `1794279540`, UTC−3).
- Cuando programa por su cuenta aparecen fallas que nadie revisó (ver la suite de optimización del PC reescrita en `antigravity-pc/mantenimiento/`): las ideas van como `PLAN`.
