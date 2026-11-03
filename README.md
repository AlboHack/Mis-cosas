# Mis-cosas

Configuración de Claude para Ingeniería Civil UTFSM y automatizaciones de Nicolás. Repositorio público: sin contraseñas, tokens ni finanzas.

## Mapa

| Carpeta o archivo | Qué contiene | Quién lo escribe |
|---|---|---|
| `proyecto/` | Instrucciones y perfil del proyecto de claude.ai | Claude; Nicolás pega las instrucciones en claude.ai |
| `.claude/skills/` | Skills propias (Claude Code las carga solas; claude.ai las recibe como .zip) | Claude |
| `evals/` | Casos con error escondido para probar cambios de instrucciones y skills | Claude |
| `fuentes/` | Repos externos de los que se adaptaron skills, con su versión base | `scripts/revisar_fuentes.py` |
| `utfsm-calc/` | Paquete de cálculo probado (pórticos, fricción, CPM, VPI, laboratorio, LaTeX) | Claude |
| `scripts/` | Sincronización con Aula, Drive y calendario (corre en la tablet por cron) y utilidades del repo | Claude; la tablet ejecuta |
| `scripts/pruebas/` | Pruebas de la sincronización (T2–T30) | Claude; la tablet ejecuta |
| `scripts/hooks/pre-push` | Bloquea pushes a `main` que no sean de la sincronización o de un merge aprobado | — |
| `universidad/2026-2/` | Material y contexto de cada ramo | Solo la sincronización (`chore(sync)`) |
| `agentes/` | Reglas para los nodos Antigravity (tablet y PC) | Claude |
| `antigravity-tablet/` | Cómo funciona el nodo tablet: protocolo, plantilla de pedidos, sincronización con Aula, errores y estado | Claude; AG agrega `CONTEXTO.md` |
| `DECISIONES.md` | Una fila por decisión: qué, por qué y con qué evidencia | Quien decide |
| `REGISTRO_CAMBIOS.md` | Archivos movidos, borrados o renombrados en cada ordenamiento | Claude |

Ramas: `main` estable; `claude/<tema>` trabajo de Claude; `ag/<nodo>` aportes de un nodo Antigravity; `canal` conversación Claude ↔ Antigravity (no se mezcla a `main`).

## Universidad
Cada ramo en `universidad/2026-2/<SIGLA_NOMBRE>/` es un espejo de Aula: una carpeta `NN Sección` por sección, en el orden de Aula, con los archivos tal como los publica el docente (lo que Aula retira se retira aquí). Lo que genera la automatización va en `<ramo>/_contexto/`: `Contexto_Asignatura.md`, `avisos.md`, `cambios_pagina.md` y `pagina_curso.json`. El resumen del semestre está en `Contexto_Semestre_2026-2.md` y las fechas en `evaluaciones.json` (fusión de Aula con `evaluaciones_manual.json`). Archivos de más de 95 MB quedan solo en la tablet y en Drive (GitHub rechaza archivos sobre 100 MB).

## Llevar los cambios a claude.ai
1. Skills: descargar el .zip desde la release [skills](https://github.com/AlboHack/Mis-cosas/releases/tag/skills) y subirlo en claude.ai > Configuración > Capacidades > Skills (reemplaza la versión anterior).
2. Contexto: en el proyecto, Conocimiento > + > GitHub > este repo, seleccionar `proyecto/perfil.md`, `DECISIONES.md`, `utfsm-calc/README.md` y `universidad/2026-2/Contexto_Semestre_2026-2.md`; después de cada cambio, "Sync now".
3. Instrucciones: pegar `proyecto/instrucciones.md` cuando cambie.

Cada lunes una tarea programada de Claude Code revisa las fuentes externas y busca skills nuevas; lo que valga la pena llega como pull request.
