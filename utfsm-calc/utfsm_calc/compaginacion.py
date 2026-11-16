"""Revisor de compaginación y de figuras para documentos LaTeX.

Uso:  python -m utfsm_calc.compaginacion informe.tex [--sin-anticorte] [--max 12]

1. Anticorte: ningún punto numerado (sección, subsección, subsubsección) que quepa en una página
   queda partido entre dos. Mide la posición exacta de cada título con marcas que inyecta al
   compilar (no toca el preámbulo) e inserta `\\Needspace{<alto>pt}% anticorte` antes del título.
   La marca es condicional: si después se edita el texto y el punto ya cabe, no fuerza el salto.
2. Páginas: cajas tcolorbox partidas, contenido que se sale por abajo, títulos huérfanos, leyendas
   separadas, texto fuera del margen, referencias indefinidas. Genera paginas-N.png.
3. Figuras: compila cada tikzpicture en una página propia y detecta etiquetas superpuestas, trazos
   que cruzan una etiqueta y cajas opacas (leyendas) que tapan curvas. Genera figuras-N.png para la
   revisión visual a tamaño legible.

Termina con `RESULTADO: OK` o con el número de problemas. Requiere latexmk o pdflatex, pdftoppm,
pdfplumber y Pillow.
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

TEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex")
SP = 65536.0
MARCA = re.compile(r"^\\Needspace\{[\d.]+pt\}% anticorte\n", re.M)
TITULO_CMD = re.compile(r"\\(?:sub){0,2}section\b")
MAGENTA = (1.0, 0.0, 0.6)


# ---------------------------------------------------------------- compilación
def compilar(tex, paquete=None, jobname=None, pasadas=2):
    """Compila `tex` en su carpeta. `paquete` (utfsm-marcas o utfsm-figs) se inyecta sin tocar el .tex."""
    carpeta, nombre = os.path.split(os.path.abspath(tex))
    base = jobname or nombre[:-4]
    env = dict(os.environ, TEXINPUTS=TEX_DIR + os.pathsep + os.environ.get("TEXINPUTS", ""))
    pre = rf"\AddToHook{{begindocument/before}}{{\RequirePackage{{{paquete}}}}}" if paquete else ""
    if shutil.which("latexmk") and not jobname:
        cmd = ["latexmk", "-pdf", "-g", "-interaction=nonstopmode", "-halt-on-error"]
        cmd += [f"-usepretex={pre}"] if pre else []
        subprocess.run(cmd + [nombre], cwd=carpeta, env=env, capture_output=True, timeout=900)
    else:
        arg = rf"{pre}\input{{{nombre}}}"
        for _ in range(pasadas):
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"-jobname={base}", arg],
                           cwd=carpeta, env=env, capture_output=True, timeout=900)
    pdf = os.path.join(carpeta, base + ".pdf")
    log = os.path.join(carpeta, base + ".log")
    ok = os.path.exists(pdf) and not re.search(r"^! ", open(log, encoding="latin-1").read(), re.M)
    return ok, pdf, log


def primer_error(log):
    t = open(log, encoding="latin-1").read()
    m = re.search(r"^! .*(?:\n.*){0,4}", t, re.M)
    return m.group(0) if m else "(sin PDF y sin error en el log)"


# ---------------------------------------------------------------- marcas
def leer_marcas(ruta):
    """Devuelve geometría (pt desde el borde inferior), títulos, fin de documento y cajas partidas."""
    geo, tit, fin, ci, cf = None, [], None, {}, {}
    for l in open(ruta, encoding="latin-1"):
        p = l.split()
        if not p:
            continue
        if p[0] == "G":
            alto, th, off = (float(x[:-2]) for x in p[1:4])
            geo = dict(top=alto - off, bot=alto - off - th, th=th)
        elif p[0] == "T":
            m = re.search(r"\[(.*?)\]\[(.*?)\]", l)
            tit.append(dict(pag=int(p[1]), y=int(p[2]) / SP, nivel=p[3], linea=int(p[4]),
                            archivo=os.path.join(m.group(1), m.group(2)) if m.group(2) else ""))
        elif p[0] == "Z":
            fin = dict(pag=int(p[1]), y=int(p[2]) / SP)
        elif p[0] == "CI":
            m = re.search(r"\[(.*?)\]\[(.*?)\]", l)
            ci[p[3]] = dict(pag=int(p[1]), y=int(p[2]) / SP, linea=int(p[4]),
                            archivo=os.path.join(m.group(1), m.group(2)) if m.group(2) else "")
        elif p[0] == "CF":
            cf[p[3]] = dict(pag=int(p[1]), y=int(p[2]) / SP)
    return geo, tit, fin, ci, cf


def fondo_de_paginas(pdf, geo):
    """Altura (pt desde abajo) de la última línea de texto dentro de la caja de texto de cada página."""
    import pdfplumber
    out = {}
    with pdfplumber.open(pdf) as doc:
        for i, p in enumerate(doc.pages, 1):
            ys = [p.height - w["bottom"] for w in p.extract_words() if p.height - w["bottom"] > geo["bot"] - 3]
            out[i] = min(ys) if ys else geo["top"]
    return out


def puntos_cortados(geo, tit, fin, fondo):
    """Lista de (título cabeza de cadena, alto necesario en pt): puntos partidos que caben en una página
    y títulos que quedaron solos al pie."""
    res = []
    for i, h in enumerate(tit):
        s = tit[i + 1] if i + 1 < len(tit) else fin
        if s is None:
            continue
        pe, ye = s["pag"], s["y"]
        if pe > h["pag"] and h["y"] - fondo.get(h["pag"], geo["bot"]) < 30:   # título huérfano al pie
            k = i
            while k > 0 and tit[k - 1]["pag"] == tit[k]["pag"] and tit[k - 1]["y"] - tit[k]["y"] < 50:
                k -= 1
            res.append((tit[k], tit[k]["y"] - geo["bot"] + 60)); continue
        if i + 1 < len(tit) and geo["top"] - ye < 30:      # el título siguiente abre página
            pe, ye = pe - 1, fondo.get(pe - 1, geo["bot"])
        if pe <= h["pag"]:
            continue
        k = i                                               # título padre pegado encima: se mueven juntos
        while k > 0 and tit[k - 1]["pag"] == tit[k]["pag"] and tit[k - 1]["y"] - tit[k]["y"] < 50:
            k -= 1
        alto = (tit[k]["y"] - geo["bot"]) + (pe - h["pag"] - 1) * geo["th"] + (geo["top"] - ye) + 30
        if alto <= 0.97 * geo["th"]:
            res.append((tit[k], alto))
    return res


def _ruta(tex, archivo):
    if not archivo or os.path.basename(archivo) == os.path.basename(tex):
        return os.path.abspath(tex)
    r = os.path.join(os.path.dirname(os.path.abspath(tex)), archivo)
    return r if os.path.exists(r) else r + ".tex"


def anticorte(tex, nmax=12, eco=print):
    """Inserta marcas \\Needspace hasta que ningún punto que quepa en una página quede partido."""
    src = open(tex, encoding="utf-8").read()
    for inc in re.findall(r"\\(?:input|include)\{([^}]+)\}", src):   # parte de cero en cada corrida
        r = _ruta(tex, inc)
        if os.path.exists(r):
            t = open(r, encoding="utf-8").read()
            if MARCA.search(t):
                open(r, "w", encoding="utf-8").write(MARCA.sub("", t))
    if MARCA.search(src):
        open(tex, "w", encoding="utf-8").write(MARCA.sub("", src))
    src = open(tex, encoding="utf-8").read()
    pre = src.split(r"\begin{document}")[0]
    pre += "".join(open(_ruta(tex, x), encoding="utf-8").read() for x in re.findall(r"\\input\{([^}]+)\}", pre) if os.path.exists(_ruta(tex, x)))
    if "needspace" not in pre and not re.search(r"\\usepackage(\[[^\]]*\])?\{utfsm\}", pre) and r"\begin{document}" in src:
        open(tex, "w", encoding="utf-8").write(src.replace(r"\begin{document}", "\\usepackage{needspace}% anticorte\n\\begin{document}", 1))
    movidos = 0
    for it in range(1, nmax + 1):
        ok, pdf, log = compilar(tex, "utfsm-marcas")
        if not ok:
            eco("ERROR DE COMPILACIÓN:\n" + primer_error(log)); return None
        geo, tit, fin, ci, cf = leer_marcas(pdf[:-4] + ".marcas")
        if geo is None or not tit:
            eco("Anticorte: el documento no tiene títulos numerados que medir."); return geo, tit, fin, ci, cf, pdf, log
        cortados = puntos_cortados(geo, tit, fin, fondo_de_paginas(pdf, geo))
        if not cortados:
            eco(f"Anticorte: ningún punto cortado ({movidos} marca(s), {it} compilación(es)).")
            return geo, tit, fin, ci, cf, pdf, log
        por_archivo = {}
        for h, alto in cortados:
            por_archivo.setdefault(_ruta(tex, h["archivo"]), {})[h["linea"]] = alto
        for ruta, lineas in por_archivo.items():
            ls = open(ruta, encoding="utf-8").read().split("\n")
            for n in sorted(lineas, reverse=True):
                j = n - 1                                   # línea del título: buscar el comando hacia arriba
                while j > max(0, n - 6) and not TITULO_CMD.search(ls[j]):
                    j -= 1
                if not TITULO_CMD.search(ls[j]):
                    j = n - 1
                alto = lineas[n]
                if j > 0 and MARCA.match(ls[j - 1] + "\n"):   # ya tenía marca y sigue cortado: subirla
                    previo = float(re.search(r"[\d.]+", ls[j - 1]).group(0))
                    ls[j - 1] = f"\\Needspace{{{max(alto, previo * 1.1 + 10):.0f}pt}}% anticorte"
                else:
                    ls.insert(j, f"\\Needspace{{{alto:.0f}pt}}% anticorte"); movidos += 1
            open(ruta, "w", encoding="utf-8").write("\n".join(ls))
    eco(f"Anticorte: se alcanzó el máximo de {nmax} iteraciones; quedan puntos cortados.")
    return geo, tit, fin, ci, cf, pdf, log


# ---------------------------------------------------------------- páginas


def _lineas(pagina):
    filas = {}
    for w in pagina.extract_words(use_text_flow=True):
        filas.setdefault(round(w["top"] / 2.5), []).append(w)
    out = []
    for k in sorted(filas):
        ws = sorted(filas[k], key=lambda w: w["x0"])
        out.append(dict(texto=" ".join(w["text"] for w in ws), top=min(w["top"] for w in ws),
                        bottom=max(w["bottom"] for w in ws), x1=max(w["x1"] for w in ws)))
    return out


def revisar_paginas(pdf, geo=None):
    """Heurísticas sobre el PDF: leyendas separadas de su figura o tabla, margen derecho, páginas vacías."""
    import pdfplumber
    prob, avis = [], []
    with pdfplumber.open(pdf) as doc:
        paginas = [(p, _lineas(p)) for p in doc.pages]
        n = len(paginas)
        for i, (p, ls) in enumerate(paginas, 1):
            arriba = p.height - geo["top"] - 2 if geo else p.height * 0.10      # bajo el encabezado
            abajo = p.height - geo["bot"] + 2 if geo else p.height * 0.94       # sobre el pie
            cont = [l for l in ls if arriba <= l["top"] and l["bottom"] <= abajo]
            if not cont:
                if i < n:
                    prob.append(f"pág. {i}: PÁGINA VACÍA")
                continue
            # la leyenda de una figura va debajo de ella y la de una tabla, encima
            if i > 1 and re.match(r"^(Figura|Gr[áa]fico)\s+\d+(\.\d+)?[:.]", cont[0]["texto"]):
                prob.append(f"pág. {i}: LEYENDA separada de su figura (abre la página) -> «{cont[0]['texto'][:60]}»")
            if i < n and re.match(r"^(Tabla|Cuadro)\s+\d+(\.\d+)?[:.]", cont[-1]["texto"]):
                prob.append(f"pág. {i}: LEYENDA separada de su tabla (cierra la página) -> «{cont[-1]['texto'][:60]}»")
            for l in cont:
                if l["x1"] > p.width - 0.6 * 72:
                    prob.append(f"pág. {i}: TEXTO FUERA DEL MARGEN derecho -> «{l['texto'][:60]}»")
            usado = (max(l["bottom"] for l in cont) - min(l["top"] for l in cont)) / (abajo - arriba)
            if 1 < i < n and usado < 0.35:
                avis.append(f"pág. {i}: página usada al {usado:.0%} (figura muy alta, o punto movido por anticorte)")
    return prob, avis, n


def revisar_log(log):
    prob = []
    t = open(log, encoding="latin-1").read()
    for m in re.finditer(r"Overfull \\hbox \((\d+\.?\d*)pt too wide\)[^\n]*lines? (\d+)", t):
        if float(m.group(1)) > 1.0:
            prob.append(f"OVERFULL {m.group(1)}pt (texto fuera del margen) -> línea {m.group(2)} del .tex")
    for m in re.finditer(r"Overfull \\vbox \((\d+\.?\d*)pt too high\) has occurred while \\output is active", t):
        if float(m.group(1)) > 5.0:
            prob.append(f"CONTENIDO SE SALE POR ABAJO de la página ({m.group(1)}pt): caja o figura más alta que el "
                        "espacio disponible; reducirla o declarar la caja `breakable`")
    for patron, msg in [(r"Reference `([^']+)' on page \d+ undefined", "REFERENCIA INDEFINIDA"),
                        (r"Citation `([^']+)' on page \d+ undefined", "CITA INDEFINIDA"),
                        (r"Float too large", "FLOAT DEMASIADO GRANDE"), (r"Float\(s\) lost", "FLOATS PERDIDOS"),
                        (r"Missing character: There is no (\S+) in font (?!nullfont)", "CARÁCTER NO SOPORTADO")]:
        for m in re.finditer(patron, t):
            prob.append(msg + (f" -> {m.group(1)}" if m.groups() else ""))
    return sorted(set(prob))


def revisar_cajas(geo, ci, cf):
    prob, avis = [], []
    for k, a in ci.items():
        b = cf.get(k)
        if not b or b["pag"] == a["pag"]:
            continue
        alto = (a["y"] - geo["bot"]) + (b["pag"] - a["pag"] - 1) * geo["th"] + (geo["top"] - b["y"])
        donde = f"págs. {a['pag']}-{b['pag']}, termina en la línea {a['linea']}" + (f" de {a['archivo']}" if a["archivo"] else "")
        if alto <= 0.95 * geo["th"]:
            prob.append(f"CAJA PARTIDA que cabe en una página ({donde}): quitarle `breakable` o usar las cajas de utfsm.sty")
        else:
            avis.append(f"caja de más de una página ({donde}): inevitable, revisar dónde corta")
    return prob, avis


def hojas(pdf, prefijo, dpi, ancho_max=1700, alto_max=2200, rotulos=None, paginas=None):
    """Compone hojas de contacto <prefijo>-N.png con las páginas del PDF, por filas. Devuelve las rutas."""
    from PIL import Image, ImageDraw
    d = tempfile.mkdtemp()
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", pdf, os.path.join(d, "p")], check=True)
    archivos = sorted(glob.glob(os.path.join(d, "p*.png")))
    sel = [(k, Image.open(a)) for k, a in enumerate(archivos, 1) if paginas is None or k in paginas]
    carpeta = os.path.dirname(pdf)
    for viejo in glob.glob(os.path.join(carpeta, prefijo + "-*.png")):
        os.remove(viejo)
    grupos, filas, fila, x, y, alto_fila = [], [], [], 0, 0, 0
    for k, im in sel:                                       # filas hasta ancho_max; hojas hasta alto_max
        if im.width > ancho_max:
            im = im.resize((ancho_max, int(im.height * ancho_max / im.width)))
        if fila and x + im.width + 12 > ancho_max:
            filas.append((fila, alto_fila)); y += alto_fila; fila, x, alto_fila = [], 0, 0
            if y + im.height + 28 > alto_max:
                grupos.append(filas); filas, y = [], 0
        fila.append((k, im, x)); x += im.width + 12; alto_fila = max(alto_fila, im.height + 28)
    if fila:
        filas.append((fila, alto_fila))
    if filas:
        grupos.append(filas)
    rutas = []
    for g, filas in enumerate(grupos, 1):
        ancho = max(x0 + im.width + 12 for fila, _ in filas for _, im, x0 in fila)
        hoja = Image.new("RGB", (ancho, sum(a for _, a in filas)), (120, 120, 120))
        dib, y = ImageDraw.Draw(hoja), 0
        for fila, alto in filas:
            for k, im, x0 in fila:
                hoja.paste(im, (x0 + 6, y + 20))
                dib.text((x0 + 8, y + 4), rotulos.get(k, str(k)) if rotulos else f"pag. {k}", fill="white")
            y += alto
        ruta = os.path.join(carpeta, f"{prefijo}-{g}.png")
        hoja.save(ruta); rutas.append(ruta)
    shutil.rmtree(d, ignore_errors=True)
    return rutas


# ---------------------------------------------------------------- figuras
def _color(c):
    if c is None:
        return None
    if not isinstance(c, (list, tuple)):
        c = [c]
    try:
        return tuple(round(float(x), 2) for x in c)
    except (TypeError, ValueError):
        return None                                         # patrón u otro espacio de color


def _cromatico(c):
    return c is not None and len(c) >= 3 and max(c) - min(c) > 0.15


def _corta(p, q, r):
    """¿El segmento p-q cruza el rectángulo r=(x0,y0,x1,y1)? (Liang-Barsky)"""
    x0, y0, x1, y1 = r
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for d, a, b in ((dx, p[0] - x0, x1 - p[0]), (dy, p[1] - y0, y1 - p[1])):
        if abs(d) < 1e-9:
            if a < 0 or b < 0:
                return False
        else:
            ta, tb = -a / d, b / d
            if ta > tb:
                ta, tb = tb, ta
            t0, t1 = max(t0, ta), min(t1, tb)
            if t0 > t1:
                return False
    return True


def _nucleo(ch):
    """Zona central del carácter (de la línea base a la altura de la x): lo que no puede quedar tapado."""
    x0, y0, x1, y1 = ch.bbox
    a, b = ch.matrix[:2]
    if abs(a) >= abs(b):
        h = y1 - y0
        return (x0 + 0.3, y0 + 0.28 * h, x1 - 0.3, y1 - 0.25 * h)
    w = x1 - x0
    return (x0 + 0.25 * w, y0 + 0.3, x1 - 0.28 * w, y1 - 0.3)


def _paginas_crudas(pdf):
    """Páginas pdfminer con sus objetos en el orden en que se dibujan (sin agrupar texto). Cada trazo
    o relleno lleva `.clip`: el rectángulo de recorte vigente (pdfminer no aplica los recortes; sin
    esto, el achurado de un apoyo o una curva recortada por el eje parecerían cruzar etiquetas)."""
    from pdfminer.converter import PDFPageAggregator
    from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
    from pdfminer.pdfpage import PDFPage
    from pdfminer.utils import apply_matrix_pt

    class Disp(PDFPageAggregator):
        clip = None

        def paint_path(self, *a, **k):
            n = len(self.cur_item._objs)
            super().paint_path(*a, **k)
            for o in self.cur_item._objs[n:]:
                o.clip = self.clip

    class Interp(PDFPageInterpreter):
        def init_state(self, ctm):
            super().init_state(ctm)
            self._clip, self._pend, self._pila = None, None, []
            self.device.clip = None

        def do_q(self):
            super().do_q(); self._pila.append(self._clip)

        def do_Q(self):
            super().do_Q()
            self._clip = self._pila.pop() if self._pila else None
            self.device.clip = self._clip

        def do_W(self):
            pts = [apply_matrix_pt(self.ctm, (op[i], op[i + 1])) for op in self.curpath for i in range(1, len(op) - 1, 2)]
            if pts:
                self._pend = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))

        do_W_a = do_W

        def _aplicar(self):
            if self._pend:
                c, n = self._clip, self._pend
                self._clip = n if c is None else (max(c[0], n[0]), max(c[1], n[1]), min(c[2], n[2]), min(c[3], n[3]))
                self.device.clip, self._pend = self._clip, None

    def _envolver(f):                                       # el recorte rige tras pintar la ruta
        def op(self):                                       # (pdfminer cuenta los argumentos: solo self)
            f(self); self._aplicar()
        return op

    for nombre in ("n", "S", "s", "f", "F", "f_a", "B", "B_a", "b", "b_a"):
        setattr(Interp, "do_" + nombre, _envolver(getattr(PDFPageInterpreter, "do_" + nombre)))

    rm = PDFResourceManager()
    dev = Disp(rm, laparams=None)
    it = Interp(rm, dev)
    with open(pdf, "rb") as f:
        for pg in PDFPage.get_pages(f):
            it.process_page(pg)
            yield dev.get_result()


def _inter(r, c):
    """Intersección de r con el recorte c (None = sin recorte); None si queda vacía."""
    if c is None:
        return r
    x0, y0, x1, y1 = max(r[0], c[0]), max(r[1], c[1]), min(r[2], c[2]), min(r[3], c[3])
    return (x0, y0, x1, y1) if x1 > x0 and y1 > y0 else None


def _tam(ch):
    """Alto del carácter en pt; en texto girado el alto de la letra queda en el ancho de su caja."""
    a, b = ch.matrix[:2]
    return (ch.y1 - ch.y0) if abs(a) >= abs(b) else (ch.x1 - ch.x0)


def analizar_figura(pagina):
    """Problemas y avisos de una página del pase de figuras. utfsm-figs.sty rodea cada nodo con un
    trazo magenta invisible, dibujado justo después de su texto: eso delimita cada etiqueta."""
    from pdfminer.layout import LTChar, LTCurve, LTContainer
    chars, etqs, cajas, trazos, rellenos, achurados, sueltos = [], [], [], [], [], [], []

    def recorrer(o):
        for it in o:
            if isinstance(it, LTChar):
                if it.get_text().strip():
                    chars.append(it); sueltos.append(it)
            elif isinstance(it, LTCurve):
                z = len(trazos) + len(rellenos) + len(cajas)
                sc = _color(it.stroking_color)
                if it.stroke and sc == MAGENTA and it.linewidth < 0.1:
                    if it.x1 - it.x0 > 0.5 and it.y1 - it.y0 > 0.5:
                        x0, y0, x1, y1 = it.bbox
                        cajas.append(dict(r=it.bbox, z=z))
                        cs = [c for c in sueltos if x0 - 1 <= (c.x0 + c.x1) / 2 <= x1 + 1 and y0 - 1 <= (c.y0 + c.y1) / 2 <= y1 + 1]
                        if cs:
                            ext = (min(c.x0 for c in cs), min(c.y0 for c in cs), max(c.x1 for c in cs), max(c.y1 for c in cs))
                            etqs.append(dict(txt="".join(c.get_text() for c in cs)[:28], ext=ext,
                                             nuc=[_nucleo(c) for c in cs], z=z))
                        sueltos.clear()
                    continue
                clip = getattr(it, "clip", None)
                if it.stroke:
                    trazos.append(dict(pts=list(it.pts), z=z, w=it.linewidth, c=sc, clip=clip))
                if it.fill and _inter(it.bbox, clip):
                    (rellenos if _color(it.non_stroking_color) is not None else achurados).append(dict(r=_inter(it.bbox, clip), z=z))
            elif isinstance(it, LTContainer):
                recorrer(it)

    recorrer(pagina)
    prob, avis = [], []
    for i, a in enumerate(etqs):                            # A. etiqueta sobre etiqueta
        for b in etqs[i + 1:]:
            if min(a["ext"][2], b["ext"][2]) < max(a["ext"][0], b["ext"][0]) or min(a["ext"][3], b["ext"][3]) < max(a["ext"][1], b["ext"][1]):
                continue
            if any(min(m[2], n[2]) - max(m[0], n[0]) > 0.5 and min(m[3], n[3]) - max(m[1], n[1]) > 0.5
                   for m in a["nuc"] for n in b["nuc"]):
                prob.append(f"ETIQUETAS SUPERPUESTAS: «{a['txt']}» y «{b['txt']}»")
    for e in etqs:                                          # B. trazo que cruza una etiqueta
        for t in trazos:
            nuc = [m for m in (_inter(m, t["clip"]) for m in e["nuc"]) if m]
            if not any(_corta(p, q, m) for p, q in zip(t["pts"], t["pts"][1:]) for m in nuc):
                continue
            tapado = any(f["z"] > t["z"] and f["r"][0] <= e["ext"][0] + 0.5 and f["r"][1] <= e["ext"][1] + 0.5
                         and f["r"][2] >= e["ext"][2] - 0.5 and f["r"][3] >= e["ext"][3] - 0.5 for f in rellenos)
            if not tapado:
                prob.append(f"TRAZO SOBRE ETIQUETA: una línea cruza «{e['txt']}»"); break
    for e in etqs:                                          # B2. etiqueta sobre un achurado (apoyo, empotramiento)
        if any(min(m[2], f["r"][2]) - max(m[0], f["r"][0]) > 0.5 and min(m[3], f["r"][3]) - max(m[1], f["r"][1]) > 0.5
               for f in achurados for m in e["nuc"]):
            prob.append(f"ETIQUETA SOBRE ACHURADO: «{e['txt']}» pisa el achurado de un apoyo")
    for f in rellenos:                                      # C. caja opaca grande (leyenda) sobre curvas
        x0, y0, x1, y1 = f["r"]
        if (x1 - x0) * (y1 - y0) < 900 or not any(abs(c["r"][0] - x0) < 1.5 and abs(c["r"][2] - x1) < 1.5
                                                 and abs(c["r"][1] - y0) < 1.5 and abs(c["r"][3] - y1) < 1.5 for c in cajas):
            continue
        r = (x0 + 2, y0 + 2, x1 - 2, y1 - 2)
        if any(t["z"] < f["z"] and (t["w"] >= 0.6 or _cromatico(t["c"])) and _inter(r, t["clip"])
               and any(_corta(p, q, _inter(r, t["clip"])) for p, q in zip(t["pts"], t["pts"][1:])) for t in trazos):
            dentro = [e["txt"] for e in etqs if x0 <= e["ext"][0] and e["ext"][2] <= x1 and y0 <= e["ext"][1] and e["ext"][3] <= y1]
            prob.append("CAJA OPACA TAPA CURVAS" + (f" (¿leyenda «{dentro[0]}…» sobre los datos?)" if dentro else "")
                        + ": sacarla del área de dibujo (pgfplots: estilo `utfsm`)")
    chico = [_tam(ch) for ch in chars if _tam(ch) < 4.8]
    if chico:
        avis.append(f"texto de {min(chico):.1f} pt (ilegible impreso)")
    return sorted(set(prob)), avis


def revisar_figuras(tex, eco=print):
    """Compila el pase de figuras, analiza cada tikzpicture y deja figuras-N.png. Devuelve (problemas, avisos, n)."""
    base = os.path.basename(tex)[:-4] + "-figs"
    ok, pdf, log = compilar(tex, "utfsm-figs", jobname=base, pasadas=1)
    carpeta = os.path.dirname(os.path.abspath(tex))
    if not os.path.exists(pdf):
        if "No pages of output" in open(log, encoding="latin-1").read():
            return [], [], 0
        return [], ["pase de figuras sin PDF: revisar las figuras a mano -> " + primer_error(log).split("\n")[0]], 0
    origen = [l.split() for l in open(os.path.join(carpeta, base + ".figuras"), encoding="latin-1") if l.strip()]
    prob, avis, rotulos, propias = [], [], {}, []
    for k, pagina in enumerate(_paginas_crudas(pdf), 1):
        if k > len(origen) or origen[k - 1][0] != "tikzpicture":
            continue                                        # dibujo interno de tcolorbox
        n = len(propias) + 1
        propias.append(k)
        m = re.search(r"\[(.*?)\]\[(.*?)\]", " ".join(origen[k - 1]))
        donde = f"F{n} (línea {origen[k - 1][1]}" + (f" de {m.group(2)}" if m and m.group(2) and m.group(2) != os.path.basename(tex) else "") + ")"
        rotulos[k] = f"F{n}  L{origen[k - 1][1]}"
        p, a = analizar_figura(pagina)
        prob += [f"{donde}: {x}" for x in p]
        avis += [f"{donde}: {x}" for x in a]
    if propias:
        rutas = hojas(pdf, os.path.basename(tex)[:-4] + "-figuras", 110, rotulos=rotulos, paginas=set(propias))
        eco("Figuras: " + ", ".join(os.path.basename(r) for r in rutas))
    for ext in (".aux", ".log", ".figuras", ".out", ".toc", ".pdf", ".lof", ".lot"):
        try:
            os.remove(os.path.join(carpeta, base + ext))
        except OSError:
            pass
    return prob, avis, len(propias)


# ---------------------------------------------------------------- principal
def revisar(tex, con_anticorte=True, nmax=12, eco=print):
    """Corre todo sobre `tex`. Devuelve (problemas, avisos)."""
    if not shutil.which("kpsewhich") or not subprocess.run(["kpsewhich", "spanish.ldf"], capture_output=True).stdout.strip():
        eco("Aviso: falta babel-spanish (apt-get update && apt-get install -y texlive-lang-spanish).")
    if con_anticorte:
        r = anticorte(tex, nmax, eco)
    else:
        ok, pdf, log = compilar(tex, "utfsm-marcas")
        r = (leer_marcas(pdf[:-4] + ".marcas") + (pdf, log)) if ok else eco("ERROR DE COMPILACIÓN:\n" + primer_error(log))
    if r is None:
        return ["no compila"], []
    geo, tit, fin, ci, cf, pdf, log = r
    prob, avis, n = revisar_paginas(pdf, geo)
    prob += revisar_log(log)
    if geo:
        p, a = revisar_cajas(geo, ci, cf)
        prob += p; avis += a
        if tit:
            for h, _ in puntos_cortados(geo, tit, fin, fondo_de_paginas(pdf, geo)):
                prob.append(f"PUNTO CORTADO o título solo al pie (pág. {h['pag']}, línea {h['linea']} del .tex)")
    pf, af, nf = revisar_figuras(tex, eco)
    prob += pf; avis += af
    rutas = hojas(pdf, os.path.basename(tex)[:-4] + "-paginas", 45, alto_max=1700)
    eco(f"{os.path.basename(pdf)}: {n} páginas, {nf} figuras TikZ. Páginas: " + ", ".join(os.path.basename(x) for x in rutas))
    try:
        os.remove(pdf[:-4] + ".marcas")
    except OSError:
        pass
    for x in prob:
        eco("  PROBLEMA  " + x)
    for x in avis:
        eco("  aviso     " + x)
    eco("RESULTADO: OK" if not prob else f"RESULTADO: {len(prob)} problema(s)")
    return prob, avis


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return 0
    nmax = int(a[a.index("--max") + 1]) if "--max" in a else 12
    prob, _ = revisar(a[0], "--sin-anticorte" not in a, nmax)
    return 1 if prob else 0


if __name__ == "__main__":
    sys.exit(main())
