---
name: "profundizar-prompt"
description: "Usar solo cuando Nicolás pida profundizar, mejorar o reescribir un prompt, o una versión más profunda de una tarea. El bloque breve de inicio de tarea lo cubre la regla 4 de las instrucciones."
---

# Profundizar un encargo

El objetivo es una versión más profunda de la tarea, no una más larga. No se agregan entregables ni secciones: se cambia el estándar con que se hace y se juzga lo que ya se pidió.

## Alcance
Entregar el análisis completo y el prompt reescrito, sin ejecutar la tarea hasta que Nicolás lo pida. En tareas normales no se carga esta skill: la regla 4 de las instrucciones pide la versión breve de las cuatro preguntas.

## Las cuatro preguntas
Responder cada una con ejemplos concretos del área del encargo (ingeniería estructural, fluidos, transporte, construcción y FICA, LaTeX, Python):

1. **Qué haría un profesional de primer nivel que no se está pidiendo.** No tareas extra, sino el criterio que aplicaría: casos límite, verificaciones de orden de magnitud, supuestos explícitos, revisión normativa (NCh433, NCh1537, NCh430, ACI 318, AISC 360, Manual de Carreteras MOP, REDEVU) o sensibilidad a los parámetros.
2. **El material más crudo del que partiría.** En vez del resumen o la fórmula ya digerida: el enunciado original, los datos de ensayo sin procesar, la norma en su texto, el modelo de SAP2000, la planilla de cubicación o la ecuación de equilibrio desde primeros principios.
3. **Los métodos y herramientas específicos que usaría.** Por nombre: trabajo virtual, rigidez directa, Mohr, Simpson, propagación de incertidumbre, CPM/PERT, VPI; SymPy, NumPy, SciPy, SAP2000, pgfplots.
4. **Qué, aparte de Claude o de Nicolás, mostraría que el resultado es correcto.** Un juez externo verificable: un segundo método independiente, un script que reproduzca los números, la salida de SAP2000, un ensayo, una solución publicada, la compilación sin errores o una norma con valor límite.

Si alguna respuesta es genérica ("revisar bien", "usar buenas prácticas"), reemplazarla por una acción comprobable.

## Reescritura del prompt
Redactar el prompt nuevo para pedir exactamente lo identificado:
- mantener el mismo alcance y los mismos entregables del original;
- pedir partir del material crudo del punto 2;
- nombrar los métodos y herramientas del punto 3;
- fijar como criterio de aceptación el juez externo del punto 4, con tolerancia numérica cuando corresponda;
- declarar convención de signos, unidades y formato de salida (LaTeX según latex-utfsm, verificación en Python).

Entregar: las cuatro respuestas, el prompt reescrito en un bloque listo para copiar y una línea sobre qué cambió respecto del original.

## Al cerrar la tarea
Verificar el resultado contra el juez externo del punto 4 y decir en una línea si lo cumplió.