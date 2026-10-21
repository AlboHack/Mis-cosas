---
name: "figuras-ingenieria"
description: "Usar al crear o corregir gráficos y diagramas técnicos de ingeniería (curvas de ensayo, diagramas M-N-V, deformadas, curvas tensión-deformación, espectros, resultados de laboratorio) en matplotlib o pgfplots para informes y presentaciones."
---

# Figuras técnicas de ingeniería

Adaptado del enfoque de figuras de publicación científica (K-Dense scientific-skills) a informes UTFSM. Una figura debe poder leerse sola y su contenido debe ser verificable contra los datos.

## Antes de dibujar
- Calcular los datos en Python (NumPy/SciPy) y guardarlos en CSV; la figura se genera desde ese archivo, nunca con valores escritos a mano.
- Elegir el tipo según la pregunta: evolución (línea), comparación de pocos casos (barras o puntos), relación entre dos variables (dispersión con ajuste y R²), distribución (histograma o caja).
- Para informes en LaTeX, preferir pgfplots leyendo el CSV (`\addplot table`), con dimensiones parametrizadas por `\pgfmathsetmacro`, siguiendo latex-utfsm. Para presentaciones o exploración, matplotlib exportando a PDF vectorial.

## Reglas
- Ejes con magnitud y unidad entre corchetes: "Desplazamiento $\Delta$ [mm]", "Carga $P$ [Tonf]". Unidades del ramo (Tonf, m, °C, MPa).
- Coma o punto decimal coherente con el informe (con `es-nodecimaldot`, punto).
- Tamaño de letra de la figura igual o algo menor que el texto (8 a 10 pt al tamaño final); exportar al ancho real de uso (p. ej. 0.8\linewidth) para no reescalar fuentes.
- Paleta apta para daltonismo y legible en escala de grises: diferenciar series también por marcador o tipo de línea, no solo por color.
- Datos de ensayo como puntos con barras de error si hay repeticiones; modelos o ajustes como línea continua; indicar n.
- Diagramas de esfuerzos: convención de signos declarada en la leyenda o el pie (M dibujado del lado traccionado; N + tracción), valores en máximos, apoyos y rótulas, y la misma escala entre sistemas que se comparan.
- Deformadas: indicar factor de amplificación y la geometría original en gris.
- Sin título dentro del gráfico si va en LaTeX: el título es el \caption, que dice qué se muestra y la conclusión principal.

## Verificación
- Comprobar 2 o 3 puntos de la figura contra el CSV o el cálculo (máximos, cruces por cero, valor en un apoyo).
- Compilar y renderizar la página; revisar que no haya `Overfull`, texto ilegible ni leyendas que tapen datos.