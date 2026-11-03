# Casos de prueba de la configuración

Cada caso es un mensaje realista con un error escondido y una lista de verificación. Sirven para saber si un cambio en instrucciones o skills mejora o empeora el comportamiento, con evidencia y no por impresión.

## Cómo se corren
1. Un agente independiente recibe `proyecto/instrucciones.md` como si fuera su system prompt y el mensaje del caso, sin ver la lista de verificación.
2. Otro paso (o Claude) contrasta la respuesta con la lista: cada ítem pasa o falla.
3. Se anota el resultado en la tabla de abajo. Un cambio que hace fallar un caso que antes pasaba se revierte o se corrige.

## Historial
| Fecha | Versión instrucciones | Caso | Resultado | Fallas encontradas |
|---|---|---|---|---|
| 2026-10-21 | v1 | 01-portico-rotula | pasa lo esencial | convención M en columnas; orden regla 4 vs 6a; coma decimal en tabla; etiquetas 6d; regla 8 ambigua |
| 2026-10-21 | v2 | 02-friccion-transicion | pasa lo esencial | orden 6a/6b; alcance regla 4; decimal fuera de LaTeX; falta juez cuando no hay segundo método |
| 2026-10-21 | v3 | 01 y 02 | pasan todos los ítems; usó comparar_portico, tabla_comparacion y friccion (lanzó el error de transición) | portico sin docstring; convención de momentos de reacción; orden de la regla 6 en respuestas cortas |
| 2026-10-21 | v4 | — | pegada en el proyecto el 2026-10-21; casos pendientes de correr | — |
| 2026-10-21 | v4 + consejo-tecnico | 03-consejo-ajuste-friccion | pasa lo esencial: primera línea rechaza la recta única (b = +0.03 con datos ideales), veredicto por régimen, minoría y decisión de Nicolás, usó ajuste_lineal | Blasius en Re = 4000 y 9000 no aparece como valor; rango de Blasius sin [Por verificar]; rondas no visibles (ítem 4 reescrito) |
