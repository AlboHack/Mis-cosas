---
name: "verificacion-independiente"
description: "Usar cuando haya que confirmar con un segundo método independiente un resultado de cualquier ramo (estructuras, sísmica, geotecnia, fluidos, hidráulica, transporte, gestión) obtenido a mano, en planilla o en software (SAP2000, ETABS, EPANET, HEC-RAS), o calcular valores esperados antes de modelar."
---

# Verificación independiente

Un resultado está cerrado cuando dos métodos independientes coinciden dentro de una tolerancia declarada. El cálculo manual y el software no bastan si comparten el mismo error de modelo; el tercer juez es un cálculo propio en Python, con otro método o desde otro principio. Si no existe un método realmente distinto (p. ej. Hagen-Poiseuille vs. f = 64/Re), el juez es un chequeo independiente: régimen, equilibrio global o caso límite, y se dice.

## Cuándo usar
- Antes de modelar: valores esperados para detectar errores de modelo (signo de gradiente, liberaciones, apoyos, corte activado, unidades, condiciones de borde).
- Después: explicar cualquier diferencia manual vs. software mayor a 0.1 % (o a la tolerancia del ramo).
- En certamen o estudio: comprobar un ejercicio resuelto a mano.

## Herramienta
Paquete utfsm-calc (instalación en las instrucciones del proyecto). Las funciones ya están probadas contra soluciones cerradas; se llaman con los datos, no se reescriben.
- Pórtico plano: `comparar_portico(nudos, elems, apoyos, cargas_nudo, resortes)` resuelve con el núcleo de rigidez propio y con Pynite e imprime la tabla por nudo. Gradiente térmico (`kappa0`): solo `portico`, porque Pynite no lo modela.
- `elems`: `dict(i, j, E, A, I, q=0, hinge_end=None|'i'|'j', kappa0=0)`; `q` local, positiva hacia +w local; `kappa0 > 0` si la fibra inferior se alarga. `apoyos`: `{nudo: [0, 1, 2]}` para u, w, θ. `resortes`: `{(nudo, gdl): k}`. `portico` necesita `extra_dofs` igual al número de extremos liberados; `comparar_portico` lo calcula solo.
- Fricción: `friccion(Re, eps_D)`; en transición (2300 < Re < 4000) lanza un error con la cota laminar y la de Colebrook, para obligar a elegir y justificar. Contraste turbulento: `swamee_jain`.
- CPM: `cpm({id: (dur, [pred])})`; VPI: `vpi(flujos, r)`.
- Laboratorio: `ajuste_lineal(x, y)`, `propagar('expr', valores, incert)`.
- Si el paquete no se puede instalar, escribir código propio y verificarlo primero con un caso cerrado (voladizo PL³/3EI) y equilibrio global.

## Procedimiento
1. **Declarar** convención (N > 0 tracción; M > 0 tracciona la fibra inferior en vigas y la interior del marco en columnas; giro antihorario +), unidades y supuestos (Euler-Bernoulli, corte despreciado o no, EA finita o no).
2. **Mismos datos que el resultado a contrastar**: E del programa (A36 en SAP2000: 20 394 324 T/m²), A e I exactos, mismas cargas, apoyos y liberaciones.
3. **Juez independiente** según la tabla por área.
4. **Descomponer diferencias**: activar y desactivar efectos (axial, corte, I redondeada, resorte, pérdidas menores) y atribuir cada parte en una tabla "Manual / corrección 1 / corrección 2 / corregido / software". Revisar antes que nada $GA_v$ (SAP2000 incluye deformación por corte) y $EA$.
5. **Convención del software** al reportar: en SAP2000, U3 negativo hacia abajo, U1 negativo hacia la izquierda, R2 = −θ antihorario en la vista XZ.
6. **Tolerancia**: sexta cifra cuando los supuestos son idénticos; si no, explicar la causa.

## Jueces por área
| Área | Juez independiente |
|---|---|
| Análisis estructural | `comparar_portico`; equilibrio global; trabajo virtual vs. flexibilidad; simetría y antisimetría |
| Enrejados | método de nudos vs. cortes de Ritter; matriz de equilibrio en NumPy |
| Dinámica y sísmica | `scipy.linalg.eigh(K, M)`; cociente de Rayleigh; masas modales efectivas cerca de 100 %; Newmark vs. espectro |
| Hormigón y acero | fibras en Python vs. bloque de Whitney; P-M por barrido del eje neutro; Euler vs. curva AISC |
| Geotecnia | Terzaghi vs. Meyerhof o Vesić; casos límite; kPa vs. T/m² |
| Fluidos e hidráulica | régimen (Re) antes de la correlación; continuidad y energía; `friccion` vs. `swamee_jain`; Hardy Cross vs. EPANET; paso estándar propio vs. HEC-RAS |
| Transporte | q = k·v; w = Δq/Δk; curvas recalculadas con el Manual de Carreteras |
| Gestión y FICA | `cpm`; `vpi`; UF↔CLP con valor y fecha declarados |
| Laboratorio | datos crudos; `propagar`; residuos de `ajuste_lineal` |

## Antecedentes
- El núcleo de rigidez reprodujo hasta la sexta cifra las tablas de SAP2000 del pórtico del Problema 2 de la Tarea 1 de FAE (U3(D) = −0.008327, −0.010319 y −0.018743 m en los incisos a, b y c) y confirmó el signo del gradiente +160 °C/m.
- 21-10-2026: pórtico con empotramiento, rótula en el extremo j de la viga, carga distribuida, carga lateral y resorte. Núcleo y Pynite coincidieron en la sexta cifra (u_C = 7.172815·10⁻³ m; R_zA = 4.675167 Tonf).
- Descartado: anastruct 1.7.0. Con una rótula interna se desvió 12 % de ese valor. No usar como juez.

## Entrega
Tabla del juez frente al resultado contrastado, error relativo y una línea de diagnóstico. Para informes, `latex.tabla_comparacion`. El script va en un archivo para que Nicolás lo vuelva a correr.