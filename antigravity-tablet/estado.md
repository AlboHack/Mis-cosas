# Estado

Actualizar con fecha en cada cambio. Antes de dar por cierto el estado de una rama: `git log --oneline origin/main..origin/<rama>`.

## 2026-11-03
`main` en `f94f3d4` (sync del 02-nov). Ya integradas: `claude/tareas-aula` (enunciados de entregas, T29) y el latido de sincronización.

| Rama | Estado | Espera |
|---|---|---|
| `claude/orden-repo` | Ordenamiento: pruebas a `scripts/pruebas/` y aisladas, archivos generados viejos fuera, consejo-tecnico, esta carpeta | P3 de la tablet (pruebas) y confirmación de Nicolás para el merge (incluye borrados) |
| `claude/latex-compaginacion` | Mejora de la skill latex-utfsm (2 commits) | Merge |
| `claude/pc-mantenimiento` | Mantenimiento del Nitro 5 reescrito, CI en Windows verde | P2 del PC |
| `claude/tareas-aula` | Sin commits fuera de `main` | Se puede borrar |
| `ag/antigravity-pc` | Aporte del PC; su contenido está corregido en `claude/pc-mantenimiento` | — |
| `ag/gemini-cli` | Cliente CDP de Gemini; divergió de `main` | Decisión de Nicolás |
| `claude/mercado`, `datos/mercado` | ETFs y datos de mercado | Decisión de Nicolás |
| `canal` | Conversación Claude ↔ Antigravity | No se mezcla |

## Pedidos abiertos a la tablet (rama `canal`)
- P1: crear `antigravity-tablet/CONTEXTO.md` con equipo, versiones y tareas programadas (esta carpeta ya documenta el proceso; falta lo que solo se ve en la tablet).
- P2: lista de `PLAN` de lo que quiere que Claude programe.
- P3: pruebas de `claude/orden-repo` sin merge.

## Pendiente de diseño
`universidad/` debe quedar igual a Aula. Hoy no lo es: `determine_subfolder` reparte los archivos en tres categorías propias por palabras clave y mueve los que cambia de categoría, de modo que un mismo archivo puede aparecer en otra carpeta que la de Aula, y los archivos sobre 50 MB no llegan al repo.
