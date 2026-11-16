"""Pruebas del revisor de compaginación: cada una reproduce una falla real de un informe o guía."""
import os
import shutil
import subprocess

import pytest

from utfsm_calc import compaginacion as cp
from utfsm_calc import plantilla

sin_tex = not shutil.which("pdflatex") or not subprocess.run(
    ["kpsewhich", "spanish.ldf"], capture_output=True).stdout.strip()
pytestmark = pytest.mark.skipif(sin_tex, reason="requiere pdflatex y babel-spanish")

LIPSUM = "\\usepackage{lipsum}\n"


def doc(tmp_path, cuerpo, nombre="d.tex", pre=""):
    plantilla.copiar(str(tmp_path), "informe")
    ruta = tmp_path / nombre
    ruta.write_text("\\documentclass[letterpaper,10pt]{article}\n\\usepackage[sinmarca]{utfsm}\n" + LIPSUM + pre
                    + "\\begin{document}\n" + cuerpo + "\n\\end{document}\n", encoding="utf-8")
    return str(ruta)


def fig(cuerpo):
    return "\\begin{tikzpicture}\n" + cuerpo + "\n\\end{tikzpicture}\n"


def test_etiquetas_superpuestas_y_trazo_sobre_etiqueta(tmp_path):
    # DCL de nudo dibujado sin reglas (informe Tarea 2 FAE, punto 5.3.2)
    t = doc(tmp_path, fig(r"""\coordinate (O) at (0,0);
      \draw[-{Stealth},thick] (O)--(2,0) node[midway] {$N_{BC}$};
      \draw[-{Stealth},thick] (O)--(1.6,1.2) node[above right] {$N_{BD}$};
      \node at (2.05,1.35) {$N_{BE}=12.5$};"""))
    prob, _, n = cp.revisar_figuras(t, eco=lambda *_: None)
    assert n == 1
    assert any("ETIQUETAS SUPERPUESTAS" in p for p in prob)
    assert any("TRAZO SOBRE ETIQUETA" in p and "NBC" in p for p in prob)


def test_macros_de_la_casa_no_chocan(tmp_path):
    t = doc(tmp_path, fig(r"""\coordinate (O) at (0,0); \coordinate (X) at (1,0); \coordinate (D) at (36.87:1);
      \tramobarra{O}{0} \tramobarra{O}{36.87} \tramobarra{O}{180} \node[nudo] at (O) {};
      \fuerzasale{O}{0}{$N_{BC}$} \fuerzasale{O}{36.87}{$N_{BD}$} \fuerzasale{O}{180}{$N_{AB}$}
      \fuerzaentra{O}{90}{$P=10$ T} \angulo{X}{O}{D}{$36.9^\circ$} \node[etq] at (250:5mm) {$B$};""")
        + fig(r"""\coordinate (A) at (0,0); \coordinate (B) at (6,0); \coordinate (C) at (2,0);
      \draw[barra] (A)--(B); \pic at (A) {apoyo fijo}; \pic at (B) {apoyo movil};
      \cargadist{C}{B}{$q=4$ T/m} \draw[carga] (1,1.2)--(1,0) node[etq,pos=0,above] {$5$ T};
      \cota{A}{C}{$2$ m} \cota{C}{B}{$4$ m} \node[etq,above left] at (A) {$A$};"""))
    prob, _, n = cp.revisar_figuras(t, eco=lambda *_: None)
    assert n == 2 and prob == []


def test_leyenda_sobre_los_datos(tmp_path):
    # Tarea 2 FICA, figura 5: la leyenda tapaba el gráfico
    datos = r"\addplot coordinates {(1,0.95)(2,0.9)(3,0.85)(4,0.6)}; \legend{SPI acumulado del proyecto}"
    malo = doc(tmp_path, fig(r"\begin{axis}[width=8cm,height=5cm,legend pos=north west]" + datos + r"\end{axis}"), "malo.tex")
    bueno = doc(tmp_path, fig(r"\begin{axis}[utfsm]" + datos + r"\end{axis}"), "bueno.tex")
    assert any("CAJA OPACA TAPA CURVAS" in p for p in cp.revisar_figuras(malo, eco=lambda *_: None)[0])
    assert cp.revisar_figuras(bueno, eco=lambda *_: None)[0] == []


def test_recorte_no_da_falso_positivo(tmp_path):
    # líneas largas recortadas (achurado de un apoyo): fuera del recorte no se ven ni tapan nada
    t = doc(tmp_path, fig(r"""\begin{scope}\clip (0,0) rectangle (1,0.3);
      \foreach \x in {-2,-1.8,...,3} \draw (\x,-2)--(\x+4,2);\end{scope}
      \node[etq] at (2.5,1.2) {etiqueta lejos del recorte};"""))
    assert cp.revisar_figuras(t, eco=lambda *_: None)[0] == []


def test_anticorte_mueve_el_punto_y_es_repetible(tmp_path):
    # Tarea 2 FAE: "el punto 4 de metodología está cortado por un salto de página"
    t = doc(tmp_path, "\n".join([r"\section{Uno}\lipsum[1-5]", r"\section{Metodología}\lipsum[6]",
                                 r"\subsection{Sistema base}\lipsum[7-9]", r"\subsection{Flexibilidades}\lipsum[10-12]",
                                 r"\section{Resultados}", r"\subsection{Reacciones}\lipsum[1-2]"]))
    ok, pdf, _ = cp.compilar(t, "utfsm-marcas")
    geo, tit, fin, _, _ = cp.leer_marcas(pdf[:-4] + ".marcas")
    assert cp.puntos_cortados(geo, tit, fin, cp.fondo_de_paginas(pdf, geo))      # antes: hay puntos cortados
    geo, tit, fin, _, _, pdf, _ = cp.anticorte(t, eco=lambda *_: None)
    assert cp.puntos_cortados(geo, tit, fin, cp.fondo_de_paginas(pdf, geo)) == []
    primero = open(t, encoding="utf-8").read()
    assert "% anticorte" in primero
    cp.anticorte(t, eco=lambda *_: None)
    assert open(t, encoding="utf-8").read() == primero                           # segunda corrida: mismo .tex


def test_caja_partida_y_caja_demasiado_alta(tmp_path):
    # Resumen FICA C2: cuadros tcolorbox partidos que el revisor antiguo no veía
    partida = doc(tmp_path, r"\lipsum[1-5]\begin{tcolorbox}[breakable]\lipsum[6-8]\end{tcolorbox}", "partida.tex")
    alta = doc(tmp_path, r"\begin{nota}\lipsum[1-12]\end{nota}", "alta.tex")
    p1, _ = cp.revisar(partida, eco=lambda *_: None)
    p2, _ = cp.revisar(alta, eco=lambda *_: None)
    assert any("CAJA PARTIDA" in p for p in p1)
    assert any("SE SALE POR ABAJO" in p for p in p2)


def test_pregunta_con_alternativas_no_se_parte(tmp_path):
    # guías de clases particulares: cada pregunta con sus alternativas en la misma página
    preg = r"\begin{pregunta}\lipsum[2]\begin{alternativas}\item a \item b \item c \item d\end{alternativas}\end{pregunta}"
    t = doc(tmp_path, preg * 9)
    prob, _ = cp.revisar(t, eco=lambda *_: None)
    assert prob == []
    import pdfplumber
    with pdfplumber.open(t[:-4] + ".pdf") as pdf:
        for p in pdf.pages:                                  # ninguna página empieza con alternativas sueltas
            primera = [w["text"] for w in p.extract_words() if w["top"] > 100][:1]
            assert primera and not primera[0].startswith(("A)", "B)", "C)", "D)"))


def test_ejemplo_de_la_casa_pasa_limpio(tmp_path):
    plantilla.copiar(str(tmp_path), "guia")
    t = shutil.copy(os.path.join(cp.TEX_DIR, "ejemplo.tex"), tmp_path / "ejemplo.tex")
    prob, _ = cp.revisar(str(t), eco=lambda *_: None)
    assert prob == []


def test_particular_y_titulos_en_archivos_incluidos(tmp_path):
    plantilla.copiar(str(tmp_path), "particular")
    os.makedirs(tmp_path / "partes")
    (tmp_path / "partes" / "p1.tex").write_text("\n".join([r"\section{Uno}\lipsum[1-5]", r"\section{Dos}\lipsum[6]",
                                                 r"\subsection{Dos uno}\lipsum[7-9]", r"\section{Tres}\lipsum[1]"]), encoding="utf-8")
    t = tmp_path / "g.tex"
    t.write_text("\\documentclass[letterpaper,11pt]{article}\n\\usepackage[particular]{utfsm}\n\\usepackage{lipsum}\n"
                 "\\begin{document}\nPrecio: $\\num{3.5}$ y $2,5$.\n\\input{partes/p1}\n\\end{document}\n", encoding="utf-8")
    prob, _ = cp.revisar(str(t), eco=lambda *_: None)
    assert prob == []
    assert "% anticorte" in (tmp_path / "partes" / "p1.tex").read_text(encoding="utf-8")   # marca en el archivo incluido
    import pdfplumber
    with pdfplumber.open(str(t)[:-4] + ".pdf") as pdf:
        texto = pdf.pages[0].extract_text()
    assert "3,5" in texto and "Clases particulares" in texto                               # coma decimal y encabezado


def test_documento_sin_utfsm_sty(tmp_path):
    # informes anteriores con preámbulo propio: el revisor inyecta las marcas y agrega needspace solo si hace falta
    t = tmp_path / "viejo.tex"
    t.write_text("\n".join([r"\documentclass[letterpaper,10pt]{article}", r"\usepackage[T1]{fontenc}",
                            r"\usepackage[spanish,es-noshorthands,es-nodecimaldot]{babel}", r"\usepackage{tikz,lipsum}",
                            r"\begin{document}", r"\section{Uno}", r"\lipsum[1-5]", r"\section{Dos}", r"\lipsum[6]",
                            r"\subsection{Dos uno}", r"\lipsum[7-9]", r"\section{Tres}", r"\lipsum[1]", r"\end{document}"]),
                 encoding="utf-8")
    geo, tit, fin, _, _, pdf, _ = cp.anticorte(str(t), eco=lambda *_: None)
    assert cp.puntos_cortados(geo, tit, fin, cp.fondo_de_paginas(pdf, geo)) == []
    ls = t.read_text(encoding="utf-8").split("\n")
    assert r"\usepackage{needspace}% anticorte" in ls
    for i, l in enumerate(ls):                               # cada marca queda justo antes de un título
        if l.startswith(r"\Needspace"):
            assert ls[i + 1].startswith((r"\section", r"\subsection"))
    assert subprocess.run(["pdflatex", "-interaction=nonstopmode", "viejo.tex"], cwd=tmp_path, capture_output=True).returncode == 0
