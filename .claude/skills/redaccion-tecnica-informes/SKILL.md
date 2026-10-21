---
name: "redaccion-tecnica-informes"
description: "Usar al planificar, redactar o revisar el contenido de un informe, memoria de cálculo, tarea o trabajo de laboratorio de cualquier ramo (estructura, orden de redacción, análisis de resultados, conclusiones, citas); el formato LaTeX lo cubre latex-utfsm."
---

# Redacción técnica de informes de ingeniería

Adaptado de la skill scientific-writing de K-Dense (esquema primero, orden de redacción, reglas de figuras y citas) a informes de Ingeniería Civil UTFSM. Se excluyen sus generadores de imágenes con IA: toda figura sale de datos o de TikZ/pgfplots. El formato (preámbulo, tablas booktabs, logos, macros) lo define latex-utfsm; esta skill define el contenido.

## Estructura base (ajustar a lo que pida el enunciado)
1. Introducción: problema, alcance y qué se entrega. Sin teoría de relleno.
2. Objetivos: general y específicos, verificables.
3. Marco teórico: solo las ecuaciones que se usan después, con convención de signos y supuestos.
4. Metodología: datos, procedimiento manual, modelo computacional (software, materiales, apoyos, liberaciones, cargas) y criterio de comparación (fórmula del error).
5. Desarrollo y resultados por problema: datos, planteamiento, tablas y figuras, comparación.
6. Análisis de resultados: causas de las diferencias, cuantificadas; efecto de cada acción; casos límite; observación de diseño o de práctica.
7. Conclusiones: respuesta directa a cada objetivo, con números.
8. Referencias y anexos (cálculos manuales, tablas del software).

## Flujo de redacción
1. **Esquema primero**: por sección, viñetas con la idea y el número que la sostiene. Las viñetas no pasan al texto final.
2. **Orden de redacción**: tablas y figuras, metodología, resultados, análisis, conclusiones, introducción y, al final, resumen y título. La introducción se escribe cuando ya se sabe qué se demostró.
3. **Texto corrido**: párrafos con transiciones en introducción, análisis y conclusiones; listas solo para datos, supuestos o procedimientos.
4. **Revisión**: cada objetivo tiene una conclusión; cada figura y tabla se cita en el texto y se entiende sola; los números del texto coinciden con las tablas; no quedan datos pendientes (`\pend`, `\completar`).

## Estilo
- Español técnico chileno, sobrio y directo; sin clichés ("cabe destacar", "en conclusión", "es importante destacar que", "no solo X sino también Y").
- Pasado para lo realizado ("se modeló", "se obtuvo"); presente para hechos establecidos.
- Oraciones de 15 a 25 palabras en promedio; definir cada símbolo y abreviatura la primera vez.
- Separar observación de interpretación: primero el número, luego la causa.
- Precisión coherente con los datos (no reportar 8 cifras si la entrada tiene 3); unidades del ramo (Tonf, m, °C; UF, CLP).
- No sobredimensionar conclusiones: lo verificado para un caso no se generaliza sin decirlo.
- Acortar lo sobreextendido: cada párrafo debe aportar un dato, una causa o una decisión.

## Figuras, tablas y citas
- Tablas para valores precisos; figuras para tendencias y comparaciones; no repetir la misma información en ambas. Pies completos con unidades y convención de signos (ver figuras-ingenieria).
- Citar fuentes primarias: textos, normas con año y cláusula, manuales del software. Estilo APA o IEEE, el que pida el ramo; verificar cada cita contra la fuente.
- Capturas de software con el caso de carga visible y su conversión de signos explicada.
- Si un dato falta o es dudoso, omitir la fila o marcarla; nunca presentar un valor derivado como lectura directa sin decirlo.

## Lista de verificación final
- [ ] Responde todo lo que pide el enunciado, inciso por inciso.
- [ ] Cada diferencia entre métodos está cuantificada y explicada.
- [ ] Convención de signos y unidades declaradas y usadas igual en todo el informe.
- [ ] Números verificados en Python o con la skill verificacion-independiente.
- [ ] Compila sin errores ni `Overfull` y las páginas renderizadas se ven bien.