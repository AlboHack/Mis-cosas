---
name: "diseno-normativo-chile"
description: "Usar al verificar o diseñar elementos según normativa (hormigón armado, acero, sísmica, cargas, fundaciones, pavimentos, drenaje) con NCh433, NCh1537, NCh430/ACI 318, AISC 360, NCh2369, Manual de Carreteras MOP o REDEVU, en tareas, proyectos o estudio."
---

# Diseño y verificación según normativa chilena

Una verificación normativa vale lo que vale su trazabilidad: cada número debe poder seguirse hasta una cláusula, una fórmula y un dato.

## Reglas
- **La norma manda sobre la memoria.** Antes de usar un coeficiente, factor o fórmula, pedir o leer el texto de la norma (o la versión que use el ramo) y citar norma, año y cláusula. Si no se tiene el texto, decirlo y marcar el valor como "por confirmar" con `\pend`; no inventar números de cláusula ni coeficientes.
- **Versión declarada** de cada documento (p. ej. NCh433 con su modificación y decreto vigente, ACI 318 de referencia de NCh430, año de AISC 360), según indique el curso.
- **Unidades** consistentes y declaradas (Tonf y m, o kN y MPa); revisar conversiones kgf/cm² ↔ MPa.
- **Combinaciones de carga** de la norma que indique el ramo, escritas explícitamente.
- **Primeros principios primero**: antes de la fórmula de la norma, plantear el mecanismo (equilibrio de la sección, compatibilidad de deformaciones, pandeo, transferencia de carga) para saber qué controla.

## Flujo
1. Datos: geometría, materiales (f'c, fy, Fy, Fu), cargas, zona sísmica y tipo de suelo, con su fuente.
2. Demanda: análisis (manual o software) y combinaciones; envolvente de N, V, M.
3. Capacidad: estados límite aplicables (flexión, corte, flexocompresión, pandeo local y global, volcamiento lateral-torsional, aplastamiento, punzonamiento, deformación, cuantías mínimas y máximas, detallamiento).
4. Tabla de verificación por estado límite: demanda, capacidad (φRn), razón D/C, cláusula y estado.
5. Verificación independiente con Python (skill verificacion-independiente): por ejemplo, diagrama P-M por compatibilidad de deformaciones frente al bloque de Whitney, o carga de Euler frente a la curva de columnas de AISC.
6. Criterio: qué controla el diseño, cuánta holgura queda y qué cambiaría si D/C supera 1 o la holgura es menor a 10%.

## Tabla tipo
| Estado límite | Demanda | φRn | D/C | Cláusula | Estado |
|---|---|---|---|---|---|

## Errores frecuentes a revisar
- Mezclar LRFD y ASD, o factores φ de distintas versiones.
- Usar el f'c de diseño como resistencia media de ensayo.
- Omitir efectos de segundo orden o usar una longitud efectiva K·L incorrecta.
- Olvidar la masa sísmica (peso propio más fracción de sobrecarga) o los límites de corte basal mínimo y máximo.
- Reportar cuantías sin verificar mínimos ni espaciamientos de detallamiento.