"""Estilo de la casa para planillas de cubicación y presupuesto (openpyxl) y auditor de la planilla.

Uso:  from estilo import *   ->  titulo(), encabezado(), celda(), imprimir(), propiedades(), nombre()
      python estilo.py archivo.xlsx   ->  auditoría (lista de problemas; código de salida 1 si hay)
"""
import re
import sys
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.properties import PageSetupProperties

FUENTE = "Arial"
C = dict(marino="1F3864", acero="2E5D8A", tinte="D6E4F7", texto="262626", gris="595959", borde="BFBFBF",
         entrada="0000FF", vinculo="008000", fondo_entrada="FFF2CC",
         ok_f="E2EFDA", ok_t="375623", mal_f="FFC7CE", mal_t="9C0006", aviso_f="FFEB9C", aviso_t="7D6608")
LETRA = {"entrada": C["entrada"], "formula": "000000", "vinculo": C["vinculo"], "texto": C["texto"]}
FMT = {"cant": "#,##0.00", "cant3": "#,##0.000", "pct": "0.0%", "dif": "+0.0%;-0.0%;0.0%", "clp": "$#,##0",
       "clp_s": "$#,##0;-$#,##0;-", "ent": "0", "kgm": "#,##0.000"}
PROHIBIDAS = ("XLOOKUP", "XMATCH", "LET(", "LAMBDA", "FILTER(", "SORT(", "UNIQUE(", "SEQUENCE(", "IFERROR(", "INDIRECT(", "OFFSET(")
_fino = Side(style="thin", color=C["borde"])
_linea = Border(bottom=_fino)
_total = Border(top=Side(style="thin", color="000000"), bottom=Side(style="double", color="000000"))


def tipo_de(valor, nombres=()):
    """Clasifica el contenido: fórmula con '!' o con un nombre definido -> vinculo; '=' -> formula; número -> entrada."""
    if isinstance(valor, str) and valor.startswith("="):
        fichas = set(re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", valor))
        return "vinculo" if ("!" in valor or fichas & set(nombres)) else "formula"
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return "entrada"
    return "texto"


NOMBRES = set()  # se llena con nombre(); celda() lo usa para pintar de verde las fórmulas que usan nombres


def celda(ws, ref, valor=None, tipo=None, fmt=None, negrita=False, alin=None, fondo=None, total=False, envolver=False):
    """Escribe una celda con letra según su tipo (entrada azul, fórmula negra, vínculo verde, texto gris oscuro)."""
    c = ws[ref]
    if valor is not None:
        c.value = valor
    t = tipo or tipo_de(c.value, NOMBRES)
    c.font = Font(name=FUENTE, size=10, color=LETRA[t], bold=negrita or total)
    if t == "entrada" and fondo is None:
        c.fill = PatternFill("solid", fgColor=C["fondo_entrada"])
    elif fondo:
        c.fill = PatternFill("solid", fgColor=fondo)
    if fmt:
        c.number_format = FMT.get(fmt, fmt)
    c.border = _total if total else _linea
    h = alin or ("left" if t == "texto" else "right")
    c.alignment = Alignment(horizontal=h, vertical="center", wrap_text=envolver)
    return c


def titulo(ws, texto, subtitulo, ncol, color_pestana=None):
    """Filas 1-2: título y subtítulo; fila 3 vacía. El encabezado de la tabla va en la fila 4."""
    ws["A1"] = texto
    ws["A1"].font = Font(name=FUENTE, size=14, bold=True, color=C["marino"])
    ws["A2"] = subtitulo
    ws["A2"].font = Font(name=FUENTE, size=9, italic=True, color=C["gris"])
    ws.row_dimensions[1].height = 24
    for col in range(1, ncol + 1):
        ws.cell(1, col).border = Border(bottom=Side(style="medium", color=C["marino"]))
    ws.sheet_view.showGridLines = False
    if color_pestana:
        ws.sheet_properties.tabColor = color_pestana


def encabezado(ws, fila, textos, anchos, alto=30):
    """Encabezado de tabla: fondo marino, letra blanca; texto a la izquierda y números a la derecha se fijan en los datos."""
    for j, (t, a) in enumerate(zip(textos, anchos), 1):
        c = ws.cell(fila, j, t)
        c.font = Font(name=FUENTE, size=10, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=C["marino"])
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[c.column_letter].width = a
    ws.row_dimensions[fila].height = alto


def nota(ws, ref, texto, ncol=None, alto=None):
    c = ws[ref]
    c.value = texto
    c.font = Font(name=FUENTE, size=8, italic=True, color=C["gris"])
    c.alignment = Alignment(wrap_text=True, vertical="top")
    if ncol:
        ws.merge_cells(start_row=c.row, start_column=1, end_row=c.row, end_column=ncol)
    if alto:
        ws.row_dimensions[c.row].height = alto


def imprimir(ws, area, fila_titulos, horizontal=True, nombre_doc="&F"):
    """Carta, ajuste a una página de ancho, filas de encabezado repetidas, pie 'Página N de M'."""
    ws.print_area = area
    ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
    ws.page_setup.orientation = "landscape" if horizontal else "portrait"
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    if fila_titulos:
        ws.print_title_rows = f"{fila_titulos}:{fila_titulos}"
    ws.page_margins.left = ws.page_margins.right = 0.5
    ws.page_margins.top, ws.page_margins.bottom = 0.6, 0.7
    ws.oddFooter.left.text, ws.oddFooter.center.text, ws.oddFooter.right.text = nombre_doc, "Página &P de &N", "&A"
    for p in (ws.oddFooter.left, ws.oddFooter.center, ws.oddFooter.right):
        p.size, p.font = 8, "Arial"
    ws.print_options.horizontalCentered = True


def propiedades(wb, titulo_doc, asunto, autor="Nicolás Albornoz"):
    wb.properties.title, wb.properties.subject, wb.properties.creator = titulo_doc, asunto, autor
    wb.properties.lastModifiedBy = autor


def nombre(wb, nom, hoja, ref):
    """Nombre definido de libro: nombre('L_eje', 'Datos', '$C$5')."""
    NOMBRES.add(nom)
    dn = DefinedName(nom, attr_text=f"'{hoja}'!{ref}")
    if hasattr(wb.defined_names, "add"):
        wb.defined_names.add(dn)
    else:
        wb.defined_names[nom] = dn


def condicional_estado(ws, rango, celda_ref, verde, rojo, amarillo=None):
    """Formato condicional por texto (sin colores fijos en la celda)."""
    from openpyxl.formatting.rule import FormulaRule
    pares = [(verde, "ok"), (rojo, "mal"), (amarillo, "aviso")]
    for texto, k in [p for p in pares if p[0]]:
        ws.conditional_formatting.add(rango, FormulaRule(
            formula=[f'ISNUMBER(SEARCH("{texto}",{celda_ref}))'],
            fill=PatternFill("solid", bgColor=C[k + "_f"]), font=Font(color=C[k + "_t"], bold=(k == "mal"))))


# --------------------------------------------------------------------------- auditoría
def auditar(ruta):
    """Revisa reglas medibles de la casa. Devuelve lista de problemas (vacía = OK)."""
    from openpyxl import load_workbook
    wb = load_workbook(ruta)
    prob = []
    nombres = list(wb.defined_names.keys()) if hasattr(wb.defined_names, "keys") else [d.name for d in wb.defined_names]
    if not wb.properties.title or not wb.properties.creator:
        prob.append("Libro: faltan propiedades (título o autor)")
    for ws in wb.worksheets:
        if ws.sheet_state != "visible":
            continue
        h = ws.title
        if ws.title.lower().startswith("sheet") or ws.title.lower().startswith("hoja"):
            prob.append(f"{h}: nombre de hoja por defecto")
        if ws.page_setup.paperSize is None or not ws.print_area:
            prob.append(f"{h}: sin área de impresión o sin tamaño de papel")
        if not (ws.sheet_properties.pageSetUpPr and ws.sheet_properties.pageSetUpPr.fitToPage):
            prob.append(f"{h}: sin ajuste a una página de ancho")
        if "&P" not in (ws.oddFooter.center.text or ""):
            prob.append(f"{h}: pie sin número de página")
        if ws.sheet_properties.tabColor is None:
            prob.append(f"{h}: sin color de pestaña")
        if ws.max_row > 30 and ws.freeze_panes is None:
            prob.append(f"{h}: tabla larga sin panel congelado")
        for fila in ws.iter_rows():
            for c in fila:
                v = c.value
                if v is None or c.coordinate in ("A1", "A2"):
                    continue
                t = tipo_de(v, nombres)
                if t == "texto":
                    continue
                if isinstance(v, str):
                    up = v.upper()
                    for p in PROHIBIDAS:
                        if p in up:
                            prob.append(f"{h}!{c.coordinate}: función no permitida {p.rstrip('(')}")
                texto_res = isinstance(v, str) and re.search(r'"[A-Za-zÁÉÍÓÚáéíóú]', v)
                if c.number_format == "General" and not texto_res and not (isinstance(v, int) and abs(v) < 100):
                    prob.append(f"{h}!{c.coordinate}: número o fórmula con formato General")
                col = (c.font.color.rgb if c.font and c.font.color and isinstance(c.font.color.rgb, str) else "FF000000")[-6:]
                if col.upper() != LETRA[t].upper():
                    prob.append(f"{h}!{c.coordinate}: letra {col} no corresponde a {t} ({LETRA[t]})")
    return prob


if __name__ == "__main__":
    p = auditar(sys.argv[1])
    print("\n".join(p) if p else "AUDITORIA: OK")
    sys.exit(1 if p else 0)
