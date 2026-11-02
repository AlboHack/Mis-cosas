---
name: "latex-utfsm"
description: "Usar al generar o corregir LaTeX con formato UTFSM: informes, tablas booktabs/siunitx, TikZ, pgfplots, memorias de cálculo con handcalcs, errores de compilación y paso de PDF, capturas o transcripciones de clases a LaTeX."
---

# LaTeX estándar UTFSM (Depto. de Obras Civiles)

## 1. Preámbulo base
```latex
\documentclass[letterpaper, 10pt]{article}
\usepackage[T1]{fontenc}
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

% Compaginación: títulos nunca solos al pie, sin líneas viudas/huérfanas, floats dentro de su sección
\usepackage{needspace,etoolbox}
\usepackage[section]{placeins}
\pretocmd{\section}{\needspace{8\baselineskip}}{}{}
\pretocmd{\subsection}{\needspace{6\baselineskip}}{}{}
\pretocmd{\subsubsection}{\needspace{5\baselineskip}}{}{}
\widowpenalty=10000 \clubpenalty=10000 \raggedbottom
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

## 8. Revisión de compaginación (obligatoria antes de entregar un PDF)
Todo documento se entrega compilado y revisado. No basta con que compile sin errores.

1. Compilar dos veces (referencias y numeración): `latexmk -pdf -interaction=nonstopmode informe.tex` o `pdflatex` ×2. Si falla, aplicar la sección 7.
2. Guardar en un archivo y correr el revisor de abajo: `python3 revisar_compaginacion.py informe.pdf informe.log` (necesita `pdfplumber`, `pdftoppm` y Pillow; si falta `pdfplumber`: `pip install --break-system-packages -q pdfplumber`). Detecta:
   - título de sección huérfano al pie (menos de 4 líneas de su contenido en la misma página);
   - leyenda de tabla o figura al pie, separada de su contenido;
   - páginas vacías o casi vacías (float que no cupo);
   - texto fuera del margen (en el PDF y como `Overfull \hbox` > 1 pt en el log, con la línea del .tex);
   - referencias o citas indefinidas (`??`), floats perdidos, caracteres no soportados.
3. Mirar `paginas.png` (miniaturas de todas las páginas, generadas por el revisor) con la herramienta de lectura de imágenes: confirmar a la vista orden, márgenes, que cada figura y tabla esté cerca de donde se cita y que ninguna ecuación o tabla quede cortada. Abrir a tamaño completo cualquier página dudosa (`pdftoppm -r 110 -f N -l N -png informe.pdf pag`).
4. Corregir y repetir 1–3 hasta `RESULTADO: OK` y revisión visual sin observaciones. Correcciones según el hallazgo:
   - Título huérfano: subir el `\needspace` de ese nivel o poner `\needspace{10\baselineskip}` justo antes de ese título. Nunca `\newpage` manual salvo como último recurso.
   - Leyenda separada o float lejos de su cita: `[htbp]` (no `[h]` solo); `\FloatBarrier` al final de la subsección; `[H]` (paquete `float`) solo si el float debe ir exactamente ahí.
   - Página casi vacía: el float es demasiado alto; reducir `width` o `height` (`width=0.8\linewidth`), partir la figura o permitir `[p]`.
   - Tabla que no cabe en una página: `longtable` (repite encabezado). Tabla ancha: `tabularx` o `\resizebox{\linewidth}{!}{...}` como último recurso.
   - Texto fuera del margen: ecuación larga con `multline` o `split`; URL o palabra larga con `\url{}` o `\-`; `\sloppy` solo en ese párrafo.
   - `??`: compilar de nuevo; si persiste, el `\label` falta o está antes del `\caption`.
5. Al entregar, informar en una línea: páginas, `RESULTADO: OK` del revisor y que se revisó la vista de miniaturas. Si algo quedó sin resolver, decir qué y en qué página.

### revisar_compaginacion.py
```python
#!/usr/bin/env python3
"""Revisión de compaginación de un PDF compilado desde LaTeX (+ su .log).

Uso: python3 revisar_compaginacion.py informe.pdf [informe.log]
Detecta: títulos huérfanos al pie de página, leyendas de tabla/figura separadas de su contenido,
páginas casi vacías, texto que se sale del margen y avisos del log (Overfull, referencias
indefinidas, floats perdidos). Genera paginas.png (miniaturas de todas las páginas) para revisión visual.
"""
import re
import subprocess
import sys
from collections import Counter

import pdfplumber

TITULO = re.compile(r"^(\d+(\.\d+){0,3}|[A-Z]\.?\d*|Anexo\s+\w+|Ap[ée]ndice\s+\w+)\s+\S")
LEYENDA = re.compile(r"^(Tabla|Figura|Cuadro|Gr[áa]fico)\s+\d+(\.\d+)?[:.]")


def lineas(pagina):
    palabras = pagina.extract_words(extra_attrs=["size", "fontname"], keep_blank_chars=False, use_text_flow=True)
    filas = {}
    for w in palabras:
        filas.setdefault(round(w["top"] / 2.5), []).append(w)
    out = []
    for k in sorted(filas):
        ws = sorted(filas[k], key=lambda w: w["x0"])
        out.append({"texto": " ".join(w["text"] for w in ws), "top": min(w["top"] for w in ws),
                    "bottom": max(w["bottom"] for w in ws), "x0": min(w["x0"] for w in ws),
                    "x1": max(w["x1"] for w in ws), "size": max(w["size"] for w in ws),
                    "negrita": any("Bold" in w["fontname"] or "BX" in w["fontname"] for w in ws)})
    return out


def revisar(pdf_path):
    hallazgos = []
    with pdfplumber.open(pdf_path) as pdf:
        tam = Counter()
        paginas = []
        for p in pdf.pages:
            ls = lineas(p)
            for l in ls:
                tam[round(l["size"], 1)] += len(l["texto"])
            paginas.append((p, ls))
        cuerpo = tam.most_common(1)[0][0] if tam else 10
        n = len(paginas)
        for i, (p, ls) in enumerate(paginas, 1):
            # quitar pie de página (número de página u otra línea corta en el 6% inferior)
            cont = [l for l in ls if not (l["top"] > p.height * 0.94 and len(l["texto"]) <= 40)]
            if not cont:
                if i < n:
                    hallazgos.append((i, "PÁGINA VACÍA", ""))
                continue
            alto_util = p.height * 0.80
            fondo = max(l["bottom"] for l in cont)
            limite_der = p.width - 0.6 * 72  # 0.6 pulgadas del borde
            for j, l in enumerate(cont):
                es_titulo = (l["size"] > cuerpo + 0.5 or l["negrita"]) and TITULO.match(l["texto"]) and len(l["texto"]) < 90
                resto = cont[j + 1:]
                if es_titulo and len(resto) < 4 and i < n:
                    hallazgos.append((i, "TÍTULO HUÉRFANO al pie (su contenido sigue en la página siguiente)", l["texto"][:70]))
                if LEYENDA.match(l["texto"]) and not resto and i < n and l["top"] > p.height * 0.7:
                    hallazgos.append((i, "LEYENDA al pie, posible separación de su tabla/figura", l["texto"][:70]))
                if l["x1"] > limite_der:
                    hallazgos.append((i, "TEXTO FUERA DEL MARGEN derecho", l["texto"][:70]))
            ocupado = fondo - min(l["top"] for l in cont)
            if i < n and ocupado < 0.35 * alto_util:
                hallazgos.append((i, f"PÁGINA CASI VACÍA ({ocupado / alto_util:.0%} usada): suele ser un float que no cupo", ""))
    return hallazgos, n


def revisar_log(log_path):
    h = []
    texto = open(log_path, encoding="latin-1").read()
    for m in re.finditer(r"Overfull \\hbox \((\d+\.?\d*)pt too wide\)[^\n]*lines? (\d+)", texto):
        if float(m.group(1)) > 1.0:
            h.append(("log", f"OVERFULL {m.group(1)}pt (texto se sale del margen)", f"línea {m.group(2)} del .tex"))
    for patron, msg in [(r"Reference `([^']+)' on page \d+ undefined", "REFERENCIA INDEFINIDA"),
                        (r"Citation `([^']+)' on page \d+ undefined", "CITA INDEFINIDA"),
                        (r"Float too large", "FLOAT DEMASIADO GRANDE"), (r"Float\(s\) lost", "FLOATS PERDIDOS"),
                        (r"Missing character: There is no (\S+)", "CARÁCTER NO SOPORTADO")]:
        for m in re.finditer(patron, texto):
            h.append(("log", msg, m.group(1) if m.groups() else ""))
    return sorted(set(h))


def miniaturas(pdf_path, salida="paginas.png", cols=4):
    try:
        from PIL import Image
        import glob, os, tempfile
        d = tempfile.mkdtemp()
        subprocess.run(["pdftoppm", "-r", "45", "-png", pdf_path, os.path.join(d, "p")], check=True)
        imgs = [Image.open(f) for f in sorted(glob.glob(os.path.join(d, "p*.png")))]
        w, h = imgs[0].size
        filas = (len(imgs) + cols - 1) // cols
        hoja = Image.new("RGB", (cols * (w + 10), filas * (h + 10)), "gray")
        for k, im in enumerate(imgs):
            hoja.paste(im, ((k % cols) * (w + 10), (k // cols) * (h + 10)))
        hoja.save(salida)
        return salida
    except Exception as e:
        return f"(sin miniaturas: {e})"


if __name__ == "__main__":
    pdf = sys.argv[1]
    log = sys.argv[2] if len(sys.argv) > 2 else pdf[:-4] + ".log"
    hallazgos, n = revisar(pdf)
    try:
        hallazgos_log = revisar_log(log)
    except FileNotFoundError:
        hallazgos_log = [("log", "sin .log", log)]
    print(f"{pdf}: {n} páginas")
    for pag, tipo, txt in hallazgos:
        print(f"  pág. {pag}: {tipo}" + (f" -> «{txt}»" if txt else ""))
    for _, tipo, txt in hallazgos_log:
        print(f"  {tipo}" + (f" -> {txt}" if txt else ""))
    print(f"Miniaturas: {miniaturas(pdf)}")
    total = len(hallazgos) + len([h for h in hallazgos_log if h[1] != 'sin .log'])
    print("RESULTADO: OK" if total == 0 else f"RESULTADO: {total} problema(s)")
    sys.exit(0 if total == 0 else 1)
```
