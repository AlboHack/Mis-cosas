---
name: "latex-utfsm"
description: "Usar al generar o corregir LaTeX con formato UTFSM: informes, tablas booktabs/siunitx, TikZ, pgfplots, memorias de cálculo con handcalcs, errores de compilación y paso de PDF, capturas o transcripciones de clases a LaTeX."
---

# LaTeX estándar UTFSM (Depto. de Obras Civiles)

## 1. Preámbulo base
```latex
\documentclass[letterpaper, 10pt]{article}
\usepackage[spanish,es-noshorthands,es-nodecimaldot]{babel}
\usepackage{amsmath,booktabs,siunitx,graphicx,xcolor,fancyhdr}
\usepackage{tikz,pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{arrows.meta,patterns,decorations.pathmorphing,calc,babel}

\newcommand{\logoUTFSM}[1]{\IfFileExists{Logo_UTFSM.png}{\includegraphics[#1]{Logo_UTFSM.png}}{\fbox{\scriptsize Logo UTFSM}}}
\newcommand{\logoDepa}[1]{\IfFileExists{Logo depa.png}{\includegraphics[#1]{Logo depa.png}}{\fbox{\scriptsize Logo Depto.}}}
\newcommand{\EI}{E\!I}
\newcommand{\EA}{E\!A}
\newcommand{\gC}{\,^{\circ}\mathrm{C}}
\newcommand{\pend}{\textcolor{red}{\textbf{??}}}
\newcommand{\completar}[1]{\textcolor{red}{[\textit{#1}]}}
```
Punto decimal en todo el documento, también en siunitx (sin `output-decimal-marker={,}`).

## 2. Gráficos: calcular primero, graficar después
Calcular en Python las coordenadas exactas (diagramas $N, V, M$; elástica $v(x)$; perfiles $u(y)$; LE/LP; $q(k)$; curvas S) e incrustarlas en:
```latex
\addplot table [row sep=\\] { x y \\ ... };
```
No dibujar curvas "a mano" con funciones aproximadas.

## 3. Esquemas TikZ paramétricos
- Definir la geometría al inicio de cada `tikzpicture` con `\pgfmathsetmacro` (`\L`, `\H`, `\q`).
- Ubicar nudos con `\coordinate (A) at (0,0);` y construir todo a partir de ellos.
- Reemplazar capturas estáticas de enrejados, vigas o volúmenes de control por esquemas paramétricos.

## 4. Tipografía científica
- Matrices y vectores en negrita recta: `\mathbf{K}\mathbf{u} = \mathbf{F}`, con `bmatrix`.
- Tablas solo con booktabs (`\toprule`, `\midrule`, `\bottomrule`), sin líneas verticales, y columnas `S` de siunitx.

## 5. Memorias de cálculo y tablas desde Python (utfsm-calc)
El número del informe debe ser el número verificado: el LaTeX se genera desde el mismo código, no se transcribe. Solo para memorias e informes, no para el chat.
- Fórmula, sustitución y resultado: `handcalc = latex.hc_setup()` y luego `@handcalc(jupyter_display=False, precision=4)` sobre una función que termina en `return locals()`; devuelve `(latex, valores)`.
- Condiciones para que funcione (probadas): el código va en un archivo .py, porque handcalcs lee el código fuente y falla con `python -` o heredoc; cada asignación lleva espacios alrededor del `=` (`delta = P*L**3/(3*EI)`), porque sin ellos solo imprime el resultado.
- Limitaciones: una sola precisión por función (con 4 decimales, un valor menor que 5·10⁻⁵ sale como 0: pasar EI ya formado o usar cm⁴); sin notación científica, que convierte también 10 en 1.0000×10¹; solo sentencias de una línea; sin unidades (van en el texto o en la tabla).
- Comparación teórico/software: `latex.tabla_comparacion([(nombre, teorico, software)], caption, label)`; escribe `---` en el error cuando el teórico es 0.
- Pendientes antes de entregar: `latex.pendientes('informe.tex')` lista cada `\pend` y `\completar{}` con su línea.

## 6. pdf2tex: PDF, capturas o transcripciones a LaTeX
1. Separar la derivación teórica de los pasos de software (p. ej. secuencia de modelación en SAP2000).
2. Describir cada diagrama o DCL con su geometría y cargas, y reconstruirlo en TikZ paramétrico.
3. Estructurar el resultado como apunte académico o plantilla de tarea, marcando con `\completar{}` lo que no se pueda leer con certeza.

## 7. latex-rescue: errores de compilación
1. Ir al primer error del log, no al último.
2. Revisar en orden: paquete faltante, llave o entorno sin cerrar, conflicto de shorthands de babel con TikZ (falta `\usetikzlibrary{babel}` o `es-noshorthands`), separador decimal en siunitx o pgfplots.
3. Entregar la corrección como bloque de código exacto indicando dónde va.