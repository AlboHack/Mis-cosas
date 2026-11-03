# Estado

Actualizar con fecha en cada cambio. Antes de dar por cierto el estado de una rama: `git log --oneline origin/main..origin/<rama>`.

## 2026-11-03
`main` en `f94f3d4` (sync del 02-nov). Ya integradas: `claude/tareas-aula` (enunciados de entregas, T29) y el latido de sincronización.

| Rama | Estado | Espera |
|---|---|---|
| `claude/espejo-aula` | Sincronización como espejo de Aula; incluye `claude/orden-repo` y `claude/pc-mantenimiento` | P4 de la tablet: pruebas, merge y primera corrida con `--permitir-masivo` |
| `claude/orden-repo` | Ordenamiento: pruebas a `scripts/pruebas/` y aisladas, archivos generados viejos fuera, consejo-tecnico, esta carpeta | Integrada en `claude/espejo-aula` |
| `claude/latex-compaginacion` | Mejora de la skill latex-utfsm (2 commits) | Merge |
| `claude/pc-mantenimiento` | Mantenimiento del Nitro 5 reescrito; 31/31 pruebas en el Nitro (P2 del PC) | Integrada en `claude/espejo-aula` |
| `claude/tareas-aula` | Sin commits fuera de `main` | Se puede borrar |
| `ag/antigravity-pc` | Aporte del PC; su contenido está corregido en `claude/pc-mantenimiento` | — |
| `ag/gemini-cli` | Cliente CDP de Gemini; divergió de `main` | Decisión de Nicolás |
| `claude/mercado`, `datos/mercado` | ETFs y datos de mercado | Decisión de Nicolás |
| `canal` | Conversación Claude ↔ Antigravity | No se mezcla |

## Pedidos abiertos a la tablet (rama `canal`)
- P1: crear `antigravity-tablet/CONTEXTO.md` con equipo, versiones y tareas programadas (esta carpeta ya documenta el proceso; falta lo que solo se ve en la tablet).
- P2: lista de `PLAN` de lo que quiere que Claude programe.
- P3: reemplazado por P4.
- P4: pruebas de `claude/espejo-aula`, merge a `main` y primera corrida sin retiros.

## Espejo de Aula (rama `claude/espejo-aula`)
`universidad/` pasa a ser igual a Aula. Hay carpetas por sección y módulo, se retira lo que Aula quita y lo generado queda en `_contexto/`. Todas las suites pasan fuera de la tablet. Falta la primera corrida real en la tablet, con `--permitir-masivo`: reubica todos los archivos y retira la estructura anterior (Planificacion/Evaluaciones_y_Entregas/Material_y_Apuntes). Nicolás confirmó el espejo exacto con borrados el 2026-11-03.
