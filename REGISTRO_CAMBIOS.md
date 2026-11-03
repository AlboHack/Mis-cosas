# Registro de cambios de estructura

Qué archivos se movieron, borraron o renombraron en cada ordenamiento. El porqué de cada decisión está en `DECISIONES.md`. Todo lo borrado se recupera con `git show <commit>^:<ruta>`.

## 2026-11-03 · Ordenamiento general (rama `claude/orden-repo`)

### Archivos generados viejos que ningún script mantiene (no vienen de Aula)
| Borrado | Reemplazo vigente |
|---|---|
| `universidad/2026-2/README.md` (foto del 2026-10-25) | `Contexto_Semestre_2026-2.md` (generado en cada sincronización) |
| `Evaluaciones_2026-2.json` (12 evaluaciones) | `evaluaciones.json` (15, generado desde Aula y `evaluaciones_manual.json`) |
| `Resumen_Evaluaciones_Semestre.txt` | `evaluaciones.json` y `Contexto_Semestre_2026-2.md` |
| `evaluaciones_universidad_2026_2.ics` | calendario nativo de `scripts/sincronizar_calendario_android.py` |
| `<ramo>/00_Descripcion_y_Fechas.txt`, `00_Descripcion_y_Programa.txt`, `00_Contenido_Completo_HTML_Moodle.txt` (5 ramos, 15 archivos) | `<ramo>/Contexto_Asignatura.md` |

### Scripts
| Antes | Después |
|---|---|
| `scripts/test_*.py` (8 archivos) | `scripts/pruebas/test_*.py`; rutas internas ajustadas. Mismos resultados antes y después en las 6 suites que corren sin la tablet |
| `scripts/pruebas/test_t2_real.py`, `test_t3_real.py` | Aislados: antes `test_aceptacion.py` reescribía `Contexto_Asignatura.md` y `.contexto_estado.json` reales de los 5 ramos, y la siguiente sincronización los habría subido con datos de prueba |

Los scripts de producción de la sincronización no se movieron: el cron de la tablet los llama por ruta.

### Revertido el mismo día
Las listas de notas y los 3 archivos repetidos que había borrado se restauraron, y se quitó el filtro de datos de terceros: Nicolás decidió que `universidad/` refleje Aula tal cual. `scripts/sincronizar_aula_semanal.py` quedó idéntico al de `main`.

### Integrado desde otras ramas
- `claude/eager-bohr-l1tnf2`: skill consejo-tecnico, caso 03, workflow skills-zip, `scripts/empaquetar_skills.sh`, fuentes del consejo.

### Documentación
- `antigravity-tablet/` nueva: README, protocolo, plantilla de pedidos, sincronización con Aula, errores y lecciones, estado.
- `README.md`: mapa completo del repo, de las ramas y de `universidad/`.
- `DECISIONES.md`: un solo formato (tabla cronológica); las dos entradas del 2026-11-02 que estaban como secciones pasaron a filas sin perder texto.

### Pendiente, no hecho en este ordenamiento
| Qué | Por qué no | Decide |
|---|---|---|
| Libros con derechos de autor (PMBOK, Sapag, Serpell, Campero y Alarcón, Hendrickson, Solminihac) | Sacarlos o hacer privado el repo | Nicolás |
| Ramas `claude/mercado` y `datos/mercado` | Datos de inversiones en un repo público, contra la regla de CLAUDE.md | Nicolás |
| Rama `ag/gemini-cli` | Divergió de `main` (borra 121 archivos); el cliente de Gemini no está en `main` | Nicolás |
| Ramas `claude/latex-compaginacion` y `claude/pc-mantenimiento` | Esperan su revisión y prueba propias | Antigravity / Nicolás |
| Rama `claude/tareas-aula` | Ya está entera en `main`; se puede borrar | — |
