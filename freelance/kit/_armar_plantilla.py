from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment

F = "Arial"; AZUL = Font(name=F, size=10, color="0000FF"); NEG = Font(name=F, size=10)
B = Font(name=F, size=10, bold=True); TIT = Font(name=F, size=14, bold=True)
ENC = PatternFill("solid", fgColor="3B4674"); ENCF = Font(name=F, size=10, bold=True, color="FFFFFF")
AMAR = PatternFill("solid", fgColor="FFFF99"); GRIS = PatternFill("solid", fgColor="F2F2F2")
fino = Side(style="thin", color="BFBFBF"); BOR = Border(left=fino, right=fino, top=fino, bottom=fino)
N = 25  # filas de trabajo por hoja

def enc(ws, fila, textos, anchos):
    for j, (t, a) in enumerate(zip(textos, anchos), 1):
        c = ws.cell(fila, j, t); c.font = ENCF; c.fill = ENC; c.border = BOR
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.column_dimensions[c.column_letter].width = a
    ws.row_dimensions[fila].height = 32

def celda(ws, ref, v=None, entrada=False, fmt=None, negr=False):
    c = ws[ref]
    if v is not None: c.value = v
    c.font = AZUL if entrada else (B if negr else NEG); c.border = BOR
    if entrada: c.fill = AMAR
    if fmt: c.number_format = fmt
    return c

wb = Workbook()
# ---------------- Léeme
L = wb.active; L.title = "Leeme"; L.column_dimensions["A"].width = 30; L.column_dimensions["B"].width = 18; L.column_dimensions["C"].width = 80
L["A1"] = "Cubicación y presupuesto por análisis de precios unitarios (APU)"; L["A1"].font = TIT
datos = [("Proyecto", "Ejemplo: vivienda 1 piso"), ("Cliente", ""), ("Planos y revisión", ""), ("Fecha", ""), ("Elaboró", "Nicolás Albornoz")]
for i, (k, v) in enumerate(datos, 3):
    L[f"A{i}"] = k; L[f"A{i}"].font = B; celda(L, f"B{i}", v, entrada=True)
L["A9"] = "Parámetros"; L["A9"].font = B
par = [("Leyes sociales sobre mano de obra", 0.30, "Ejemplo. Definir con el cliente o su contador."),
       ("Gastos generales", 0.12, "Ejemplo. Definir con el cliente."),
       ("Utilidad", 0.10, "Ejemplo. Definir con el cliente."),
       ("IVA", 0.19, "Tasa general de IVA en Chile."),
       ("Tolerancia de control", 0.05, "Diferencia máxima aceptada entre script y medición manual.")]
for i, (k, v, nota) in enumerate(par, 10):
    L[f"A{i}"] = k; L[f"A{i}"].font = NEG; celda(L, f"B{i}", v, entrada=True, fmt="0.0%"); L[f"C{i}"] = nota; L[f"C{i}"].font = NEG
L["A16"] = "Cómo usar"; L["A16"].font = B
uso = ["Celdas amarillas con letra azul: se llenan. Celdas con letra negra: fórmulas, no se tocan.",
       "1. Cubicacion: una fila por partida. El código de ítem (columna A) enlaza las tres hojas.",
       "2. APU: una fila por insumo, con el mismo código de ítem. Rendimiento = cantidad de insumo por unidad de partida.",
       "3. Presupuesto: se calcula solo. Revisar que cada ítem tenga precio unitario distinto de cero.",
       "4. Control: copiar la cantidad del script y la medición manual de las partidas más caras (al menos 15 %).",
       "Las filas de ejemplo traen precios ficticios. Borrarlas antes de usar: ningún precio de este archivo es real.",
       "Nota de alcance para toda entrega: cubicación referencial elaborada desde los planos recibidos; "
       "no reemplaza un proyecto ni un presupuesto firmado por un profesional competente."]
for i, t in enumerate(uso, 17):
    L[f"A{i}"] = t; L[f"A{i}"].font = NEG

# ---------------- Cubicación
C = wb.create_sheet("Cubicacion")
enc(C, 1, ["Ítem", "Partida", "Unidad", "Origen de la medida", "N.º de veces", "Largo", "Ancho", "Alto / espesor",
           "Cantidad parcial", "Descuentos (vanos)", "Cantidad neta", "Pérdida", "Cantidad final"],
    [8, 34, 9, 22, 9, 10, 10, 10, 12, 12, 12, 9, 12])
ej = [("1.1", "Hormigón G25 fundación corrida", "m3", "Script, capa FUNDACIONES", 1, 42.0, 0.5, 0.6, 0, 0.05),
      ("1.2", "Moldaje fundación", "m2", "Script, capa FUNDACIONES", 2, 42.0, None, 0.6, 0, 0.0),
      ("2.1", "Radier e = 10 cm", "m2", "Script, capa LOSA", 1, 6.0, 4.0, None, 0, 0.03)]
for r in range(2, 2 + N):
    e = ej[r - 2] if r - 2 < len(ej) else (None,) * 10
    for col, v in zip("ABCD", e[:4]): celda(C, f"{col}{r}", v, entrada=True)
    for col, v in zip("EFGH", e[4:8]): celda(C, f"{col}{r}", v, entrada=True, fmt="#,##0.00")
    celda(C, f"I{r}", f'=IF(A{r}="","",IF(E{r}="",1,E{r})*IF(F{r}="",1,F{r})*IF(G{r}="",1,G{r})*IF(H{r}="",1,H{r}))', fmt="#,##0.00")
    celda(C, f"J{r}", e[8], entrada=True, fmt="#,##0.00")
    celda(C, f"K{r}", f'=IF(A{r}="","",I{r}-N(J{r}))', fmt="#,##0.00")
    celda(C, f"L{r}", e[9], entrada=True, fmt="0.0%")
    celda(C, f"M{r}", f'=IF(A{r}="","",K{r}*(1+N(L{r})))', fmt="#,##0.00")
C["I1"].comment = Comment("Producto de las dimensiones informadas; una dimensión vacía cuenta como 1.", "Plantilla")
C.freeze_panes = "C2"

# ---------------- APU
A = wb.create_sheet("APU")
enc(A, 1, ["Ítem", "Tipo", "Insumo", "Unidad", "Rendimiento (por unidad de partida)", "Precio unitario ($)",
           "Fuente del precio y fecha", "Subtotal ($)"], [8, 16, 34, 9, 16, 14, 38, 14])
eja = [("1.1", "Material", "Hormigón G25 premezclado", "m3", 1.0, 95000, "EJEMPLO FICTICIO"),
       ("1.1", "Mano de obra", "Cuadrilla de hormigonado", "HH", 1.6, 6500, "EJEMPLO FICTICIO"),
       ("1.1", "Equipo", "Vibrador de inmersión", "h", 0.3, 4000, "EJEMPLO FICTICIO"),
       ("1.2", "Material", "Tablero y madera de moldaje", "m2", 1.0, 7000, "EJEMPLO FICTICIO"),
       ("1.2", "Mano de obra", "Carpintero y ayudante", "HH", 0.9, 6500, "EJEMPLO FICTICIO"),
       ("2.1", "Material", "Hormigón G20 premezclado", "m3", 0.10, 90000, "EJEMPLO FICTICIO"),
       ("2.1", "Mano de obra", "Cuadrilla de radier", "HH", 0.5, 6500, "EJEMPLO FICTICIO")]
NA = 60
for r in range(2, 2 + NA):
    e = eja[r - 2] if r - 2 < len(eja) else (None,) * 7
    for col, v in zip("ABCD", e[:4]): celda(A, f"{col}{r}", v, entrada=True)
    celda(A, f"E{r}", e[4], entrada=True, fmt="#,##0.000"); celda(A, f"F{r}", e[5], entrada=True, fmt="$#,##0")
    celda(A, f"G{r}", e[6], entrada=True)
    celda(A, f"H{r}", f'=IF(A{r}="","",N(E{r})*N(F{r}))', fmt="$#,##0")
A["B1"].comment = Comment("Escribir exactamente: Material, Mano de obra o Equipo.", "Plantilla")
A.freeze_panes = "A2"
RA = f"$2:${1+NA}"
rng = lambda col: f"APU!${col}$2:${col}${1+NA}"

# ---------------- Presupuesto
P = wb.create_sheet("Presupuesto")
enc(P, 1, ["Ítem", "Partida", "Unidad", "Cantidad", "Materiales ($/u)", "Mano de obra ($/u)", "Leyes sociales ($/u)",
           "Equipos ($/u)", "Precio unitario directo ($)", "Total ($)"], [8, 34, 9, 12, 14, 14, 14, 14, 16, 16])
for r in range(2, 2 + N):
    k = r  # misma fila que Cubicacion
    celda(P, f"A{r}", f'=IF(Cubicacion!A{k}="","",Cubicacion!A{k})')
    celda(P, f"B{r}", f'=IF(A{r}="","",Cubicacion!B{k})'); celda(P, f"C{r}", f'=IF(A{r}="","",Cubicacion!C{k})')
    celda(P, f"D{r}", f'=IF(A{r}="","",Cubicacion!M{k})', fmt="#,##0.00")
    celda(P, f"E{r}", f'=IF(A{r}="","",SUMIFS({rng("H")},{rng("A")},A{r},{rng("B")},"Material"))', fmt="$#,##0")
    celda(P, f"F{r}", f'=IF(A{r}="","",SUMIFS({rng("H")},{rng("A")},A{r},{rng("B")},"Mano de obra"))', fmt="$#,##0")
    celda(P, f"G{r}", f'=IF(A{r}="","",F{r}*Leeme!$B$10)', fmt="$#,##0")
    celda(P, f"H{r}", f'=IF(A{r}="","",SUMIFS({rng("H")},{rng("A")},A{r},{rng("B")},"Equipo"))', fmt="$#,##0")
    celda(P, f"I{r}", f'=IF(A{r}="","",E{r}+F{r}+G{r}+H{r})', fmt="$#,##0")
    celda(P, f"J{r}", f'=IF(A{r}="","",D{r}*I{r})', fmt="$#,##0")
f0 = 2 + N + 1
res = [("Costo directo", f"=SUM(J2:J{1+N})"), ("Gastos generales", f"=J{f0}*Leeme!$B$11"),
       ("Utilidad", f"=J{f0}*Leeme!$B$12"), ("Neto", f"=J{f0}+J{f0+1}+J{f0+2}"),
       ("IVA", f"=J{f0+3}*Leeme!$B$13"), ("Total", f"=J{f0+3}+J{f0+4}")]
for i, (t, fx) in enumerate(res):
    celda(P, f"I{f0+i}", t, negr=True); celda(P, f"J{f0+i}", fx, fmt="$#,##0", negr=True)
celda(P, f"B{f0}", "Insumos de APU sin partida en Cubicacion (debe ser 0):", negr=True)
celda(P, f"D{f0}", f'=SUMPRODUCT(({rng("A")}<>"")*(COUNTIF($A$2:$A${1+N},{rng("A")})=0))', fmt="0")
P.freeze_panes = "C2"

# ---------------- Control
K = wb.create_sheet("Control")
enc(K, 1, ["Ítem", "Partida", "Cantidad por script", "Cantidad por medición manual", "Diferencia", "Estado"], [8, 34, 16, 18, 12, 12])
ejk = [("2.1", "Radier e = 10 cm", 24.0, 24.0)]
for r in range(2, 2 + N):
    e = ejk[r - 2] if r - 2 < len(ejk) else (None,) * 4
    celda(K, f"A{r}", e[0], entrada=True); celda(K, f"B{r}", e[1], entrada=True)
    celda(K, f"C{r}", e[2], entrada=True, fmt="#,##0.00"); celda(K, f"D{r}", e[3], entrada=True, fmt="#,##0.00")
    celda(K, f"E{r}", f'=IF(OR(C{r}="",D{r}=""),"",IF(D{r}=0,"",ABS(C{r}-D{r})/D{r}))', fmt="0.0%")
    celda(K, f"F{r}", f'=IF(E{r}="","",IF(E{r}<=Leeme!$B$14,"OK","REVISAR"))')
celda(K, f"B{3+N}", "Partidas controladas", negr=True); celda(K, f"C{3+N}", f'=COUNT(E2:E{1+N})', fmt="0")
celda(K, f"B{4+N}", "Partidas por revisar", negr=True); celda(K, f"C{4+N}", f'=COUNTIF(F2:F{1+N},"REVISAR")', fmt="0")
wb.save("plantilla_cubicacion_APU.xlsx")
