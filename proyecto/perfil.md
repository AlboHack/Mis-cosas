# Perfil de Nicolás Albornoz: contexto del proyecto

## Formación

- Estudiante de 4° año de Ingeniería Civil, mención Estructural, Universidad Técnica Federico Santa María (UTFSM), Campus San Joaquín, Santiago.
- Áreas de foco: análisis estructural, mecánica de materiales, análisis numérico, mecánica de fluidos, ingeniería de transporte, construcción y administración (FICA) y materiales cementicios.

## Semestre actual (2° semestre 2026)

- Ramos: FICA (CIV222 Fundamentos de Ingeniería de Construcción y Administración), FAE (CIV233 Fundamentos de Análisis Estructural), Fluidos (CIV244 Mecánica de Fluidos), Transporte (CIV386 Ingeniería de Transporte) y Prácticas Obras Civiles (POC_SJ_VV).
- Fechas, evaluaciones y estado por ramo: `universidad/2026-2/Contexto_Semestre_2026-2.md` (se regenera en cada sincronización) y `<ramo>/_contexto/Contexto_Asignatura.md`.

## Experiencia

- Ayudante académico UTFSM (ago–dic 2025): Cálculo Multivariable, Cálculo Vectorial, Ecuaciones Diferenciales Parciales, Mecánica de Fluidos y Tecnología de Materiales.
- Ayudante de investigación experimental, Pontificia Universidad Católica de Chile (dic 2025 – mar 2026): ensayos y procesamiento de datos para una tesis de Magíster sobre caracterización en estado fresco y endurecido de morteros impresos en 3D.
- Concurso Nacional de Sismoresistencia 2026, UTFSM (mar–ago 2026): equipo de Finanzas y Relaciones Exteriores (auspicios corporativos, seguimiento financiero y relaciones externas).
- Profesor particular de Matemática y Física para enseñanza media y preparación PAES.
- Práctica profesional: postulaciones (may–jun 2026) a Hormitek, SMI Ingenieros, Geomot SpA y Wild Lama. Estado: \[actualizar\]

## Herramientas

LaTeX (TikZ, pgfplots, booktabs, siunitx, fancyhdr, plantillas del Depto. de Obras Civiles UTFSM, compilación en Overleaf), SAP2000 v27, AutoCAD, MATLAB, Python (NumPy, SciPy, SymPy), LINGO, lp\_solve, SQL y Excel.

## Equipo de trabajo (nodos)

| Nodo | Dónde | Hace |
|---|---|---|
| Claude Code (claude.ai/code) | Nube; no ve los equipos de Nicolás | Jefe técnico: escribe todo el código en ramas `claude/<tema>` y los pedidos a los nodos |
| Antigravity tablet | Xiaomi Pad 5, Android 13 / HyperOS, `agy` en Termux (`com.agycli`) | Token de Aula, `rclone` a Drive, calendario, `adb`; corre la sincronización semanal; merge squash a `main` si pasan las pruebas |
| Antigravity PC | Acer Nitro 5, Windows 11 | SAP2000 v27, MATLAB R2025a, LINGO, LaTeX local y mantenimiento del equipo |
| Claude (claude.ai, este proyecto) | Navegador | Estudio y trabajo académico; no supervisa a los nodos |

Nicolás autoriza y dice "lee el canal" a cada nodo. Detalle: `antigravity-tablet/`, `antigravity-pc/` y `agentes/antigravity/reglas/04-protocolo-claude.md`.

## Canal y repositorio

- Canal: rama `canal` (nunca se mezcla a `main`), carpeta `agentes/canal/<nodo>/`. Claude escribe `PEDIDOS.md`; el nodo responde en `RESPUESTAS.md` y registra eventos en `BITACORA.md`. Cada archivo lo escribe un solo lado.
- Código: ramas `claude/<tema>` → merge squash a `main` por el nodo con `ALLOW_MAIN_PUSH=1`; el hook `scripts/hooks/pre-push` protege `main`. Cada skill sale como .zip en la release `skills`.
- El repo AlboHack/Mis-cosas es público: sin finanzas personales, memoria del proyecto, tokens ni texto de mensajes privados de Aula.

## Material de los ramos: `universidad/`

- `universidad/2026-2/` es un espejo de Aula (desde 2026-11-03): `<CÓDIGO_NOMBRE_RAMO>/NN Sección[/Módulo]/`, igual que en Aula; lo que Aula retira se borra también aquí.
- Lo generado va en `<ramo>/_contexto/` (`Contexto_Asignatura.md`, `avisos.md`, `cambios_pagina.md`, `pagina_curso.json`). En la raíz del semestre: `Contexto_Semestre_2026-2.md`, `evaluaciones.json`, `evaluaciones_manual.json` y `ultima_sincronizacion.json`.
- Sincronización desde Aula USM: sábados desde las 10:00 en la tablet (cron cada hora; si falla o pasan 7 días, recupera). Respaldo con `rclone copy` en Drive (`gdrive:Universidad/2026-2/<ramo>/`), nunca `sync`.
- Las evaluaciones están en el calendario de la tablet con alarmas a 7 días, 3 días y 1 día.

## Convenciones de trabajo

- Unidades según el ramo: Tonf, m y °C en análisis estructural; UF y CLP en construcción y administración.
- Estructura de informes: logos en `Logo_UTFSM.png` y `Logo depa.png`; capturas de software en `img/` (p. ej. `img/P1_SAP_...`); cálculos manuales escaneados en `anexos/`.
