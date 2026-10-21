# utfsm-calc

Funciones recurrentes de Nicolás Albornoz (Ingeniería Civil UTFSM), probadas contra soluciones cerradas (`pytest tests`).

Instalación: `pip install --break-system-packages git+https://github.com/<usuario>/utfsm-calc`

| Módulo | Función | Qué hace |
|---|---|---|
| estructuras | `portico(nudos, elems, apoyos, cargas_nudo, resortes={}, extra_dofs=0)` | Rigidez directa 2D; rótulas, resortes, q local, gradiente térmico (`kappa0`) |
| estructuras | `portico_pynite(...)` | Mismo modelo resuelto con Pynite (juez independiente; sin `kappa0`) |
| estructuras | `comparar_portico(...)` | Ambos, tabla por nudo y máximo error relativo |
| fluidos | `friccion(Re, eps_D)`, `colebrook`, `swamee_jain` | Darcy f; laminar o Colebrook; en transición (2300–4000) lanza error con ambas cotas |
| gestion | `cpm({id: (dur, [pred])})` | ES, EF, LS, LF, holgura, ruta crítica, duración |
| gestion | `vpi(flujos, r, t0=1)` | Suma explícita de flujos descontados |
| laboratorio | `ajuste_lineal(x, y)` | m, b, R², errores estándar, IC 95 % |
| laboratorio | `propagar('expr', valores, incert)` | Propagación lineal con SymPy y contribución por variable |
| latex | `hc_setup()` | Decorador handcalcs configurado (`equation*`, punto decimal) |
| latex | `tabla_comparacion([(nombre, teo, sw)])` | Tabla booktabs/siunitx; `---` si el teórico es 0 |
| latex | `pendientes('informe.tex')` | Lista de `\pend` y `\completar{}` con número de línea |

Convenciones: giro antihorario +, w hacia arriba, N > 0 tracción. `elems`: `dict(i, j, E, A, I, q=0, hinge_end=None|'i'|'j', kappa0=0)`; `apoyos`: `{nudo: [0, 1, 2]}` (u, w, θ); `resortes`: `{(nudo, gdl): k}`.
