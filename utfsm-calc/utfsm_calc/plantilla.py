"""Copia el formato de la casa a la carpeta de un documento nuevo.

Uso:  python -m utfsm_calc.plantilla CARPETA [--tipo informe|guia|particular]

Deja en CARPETA: utfsm.sty, img/ con los logos y, si no existe, main.tex con el esqueleto del tipo
pedido. `particular` es el material de clases particulares (sin logos, coma decimal).
"""
import os
import shutil
import sys

TEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex")

ESQUELETO = {
    "informe": r"""\documentclass[letterpaper,10pt]{article}
\usepackage{utfsm}
\datos{titulo={Título del informe}, subtitulo={Tarea N}, ramo={CIV-000 Nombre del ramo}, profesor={Nombre}}
\begin{document}
\portada
\tableofcontents
\clearpage
\section{Introducción}

\end{document}
""",
    "guia": r"""\documentclass[letterpaper,10pt]{article}
\usepackage{utfsm}
\datos{titulo={Guía resuelta}, ramo={CIV-000 Nombre del ramo}}
\begin{document}
\section{Problema 1}
\begin{enunciado}{Guía N, Problema 1}
Enunciado textual de la fuente.\par\centering
\begin{tikzpicture}
  \coordinate (A) at (0,0); \coordinate (B) at (6,0); \coordinate (C) at (2,0);
  \draw[barra] (A)--(B); \pic at (A) {apoyo fijo}; \pic at (B) {apoyo movil};
  \draw[carga] (2,1.2)--(C) node[etq,pos=0,above] {$P$};
  \cota{A}{C}{$a$} \cota{C}{B}{$b$}
\end{tikzpicture}
\end{enunciado}

\end{document}
""",
    "particular": r"""\documentclass[letterpaper,11pt]{article}
\usepackage[particular]{utfsm}
\begin{document}
\begin{center}{\LARGE\bfseries Título de la guía}\end{center}
\begin{pregunta}
Texto de la pregunta.
\begin{alternativas}\item uno \item dos \item tres \item cuatro\end{alternativas}
\end{pregunta}

\end{document}
""",
}


def copiar(destino, tipo="informe"):
    """Copia utfsm.sty y los logos a `destino`; crea main.tex si no existe. Devuelve los archivos escritos."""
    os.makedirs(os.path.join(destino, "img"), exist_ok=True)
    hechos = [shutil.copy(os.path.join(TEX_DIR, "utfsm.sty"), destino)]
    if tipo != "particular":
        for f in sorted(os.listdir(os.path.join(TEX_DIR, "img"))):
            hechos.append(shutil.copy(os.path.join(TEX_DIR, "img", f), os.path.join(destino, "img")))
    main = os.path.join(destino, "main.tex")
    if not os.path.exists(main):
        open(main, "w", encoding="utf-8").write(ESQUELETO[tipo]); hechos.append(main)
    return hechos


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return 0
    tipo = a[a.index("--tipo") + 1] if "--tipo" in a else "informe"
    if tipo not in ESQUELETO:
        print("tipo desconocido:", tipo, "| opciones:", ", ".join(ESQUELETO)); return 1
    for f in copiar(a[0], tipo):
        print(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
