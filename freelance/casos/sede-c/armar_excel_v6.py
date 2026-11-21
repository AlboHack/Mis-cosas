"""SedeC_cubicacion_v6.xlsx: datos con fuente y base, cubicación con fórmulas sobre nombres, comparación y control."""
import sys
from openpyxl import Workbook
from openpyxl.comments import Comment
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "kit"))
from estilo import celda, titulo, encabezado, nota, imprimir, propiedades, nombre, condicional_estado, C as COL
import cubicacion_sedeC as c
import correcciones as cv4

SAL = "SedeC_cubicacion_v6.xlsx"
PROY = "Sede Social Tipo C, albañilería armada (FSPR 2023), 62.63 m²"
SUB = f"{PROY} · Cubicación independiente v6 (NCh 353, revisada en frío) · N. Albornoz · 2026-11-20"
F0 = 5  # primera fila de datos; encabezado en la fila 4
wb = Workbook()
propiedades(wb, "Cubicación independiente Sede Social Tipo C", "Comparación con el presupuesto tipo FSPR 2023")

# ------------------------------------------------------------------ Datos (cada número de entrada una sola vez)
D = wb.active
D.title = "Datos"
titulo(D, "Datos de entrada", SUB, 6, COL["acero"])
encabezado(D, 4, ["Nombre", "Parámetro", "Valor", "Unidad", "Base", "Fuente o método"], [13, 36, 11, 8, 7, 84])
M, E, I, S = "M", "E", "I", "S"
datos = [  # nombre, parámetro, valor (número o fórmula), unidad, base, fuente, formato
    ("L_eje", "Largo de muros por eje", round(c.L_eje, 3), "m", M,
     "DXF 1:50: perímetro 31.01 + vestíbulo 2.45 + 8 machones de 0.501 desde la cara", "cant"),
    ("A_huella", "Huella exterior", round(c.A_huella, 3), "m²", M, "Polígono exterior de muros en el DXF", "cant3"),
    ("Int_x", "Interior libre, dirección x", round(c.int_x, 3), "m", M, "Entre caras interiores en el DXF", "cant3"),
    ("Int_y", "Interior libre, dirección y", round(c.int_y, 3), "m", M, "Entre caras interiores en el DXF", "cant3"),
    ("H_muro", "Altura de muro sobre sobrecimiento", c.H_MURO, "m", M, "Elevaciones 1:100 (escala 2k verificada)", "cant"),
    ("H_cadena", "Altura de cadena", c.H_CADENA, "m", E, "EETT 3.4; coincide con el dintel de ventanas a +2.40", "cant"),
    ("b_cadena", "Ancho de cadena", 0.15, "m", E, "EETT 3.4 (sección 0.15 x 0.30)", "cant"),
    ("n_vg", "Ventanas grandes, cantidad", c.V_GRANDE[0], "un", M, "Planta y elevaciones; coincide con el presupuesto", "ent"),
    ("b_vg", "Ventana grande, ancho", c.V_GRANDE[1], "m", M, "DXF", "cant3"),
    ("h_vg", "Ventana grande, alto", c.V_GRANDE[2], "m", M, "Elevaciones", "cant"),
    ("n_vc", "Ventanas chicas, cantidad", c.V_CHICA[0], "un", M, "Planta y elevaciones", "ent"),
    ("b_vc", "Ventana chica, ancho", c.V_CHICA[1], "m", M, "DXF; partida 15.2 indica 40 x 60", "cant3"),
    ("h_vc", "Ventana chica, alto", 0.80, "m", M, "Elevación: jambas de +1.60 a +2.40 (la partida 15.2 dice 40 x 60)", "cant"),
    ("ant_vg", "Antepecho ventana grande", 0.60, "m", M, "Elevación (+0.60)", "cant"),
    ("ant_vc", "Antepecho ventana chica", 1.60, "m", M, "Elevación (+1.60)", "cant"),
    ("b_puerta", "Puerta de acceso, ancho", c.PUERTA[1], "m", M, "DXF", "cant3"),
    ("h_puerta", "Puerta de acceso, alto", c.PUERTA[2], "m", M, "Elevaciones", "cant"),
    ("A_vanos", "Área de vanos", "=n_vg*b_vg*h_vg+n_vc*b_vc*h_vc+b_puerta*h_puerta", "m²", M, "Suma de los vanos anteriores", "cant3"),
    ("pilar_vano", "Vanos con pilar (1 = sí, 0 = no)", 0, "-", S, "Albañilería armada: jambas con tensores, sin pilares [Por verificar]", "ent"),
    ("A_desc353", "Descuento de vanos en albañilería", "=n_vg*b_vg*h_vg*IF(b_vg*h_vg<1.5,0.5*pilar_vano,IF(b_vg*h_vg<=3,0.5+0.25*pilar_vano,1))+n_vc*b_vc*h_vc*IF(b_vc*h_vc<1.5,0.5*pilar_vano,IF(b_vc*h_vc<=3,0.5+0.25*pilar_vano,1))+b_puerta*h_puerta*IF(b_puerta*h_puerta<1.5,0.5*pilar_vano,IF(b_puerta*h_puerta<=3,0.5+0.25*pilar_vano,1))", "m²", E, "NCh 353, tabla de vanos para ladrillo a máquina: <1.5 m² 0 %, 1.5 a 3 m² 50 %, >3 m² 100 % [Por verificar contra la norma]", "cant3"),
    ("e_escarpe", "Espesor de escarpe", 0.15, "m", E, "Descripción de la partida 2.2", "cant"),
    ("e_relleno", "Espesor de relleno estabilizado", 0.15, "m", E, "EETT 2.4: base del radier, 15 cm", "cant"),
    ("e_radier", "Espesor de radier", 0.08, "m", E, "Descripción de la partida 2.8", "cant"),
    ("b_fund", "Ancho de fundación corrida", 0.40, "m", I, "Sin plano de fundaciones; sección típica inferida", "cant"),
    ("h_fund", "Alto de fundación corrida", 0.60, "m", I, "Sin plano de fundaciones; sección típica inferida", "cant"),
    ("h_exc", "Profundidad de excavación", "=h_fund+e_empl", "m", I, "h_fund + e_empl", "cant"),
    ("e_empl", "Espesor de emplantillado", 0.05, "m", E, "Mínimo de EETT 2.6 (5 a 10 cm)", "cant"),
    ("b_sc", "Ancho de sobrecimiento", 0.15, "m", I, "Igual al muro; 2V/M del presupuesto da 0.144 m", "cant"),
    ("h_sc", "Alto de sobrecimiento", 0.20, "m", I, "Sección típica inferida", "cant"),
    ("m_fe6", "Masa nominal fe 6", 0.222, "kg/m", E, "Tabla de masas nominales (ρ = 7850 kg/m³)", "kgm"),
    ("m_fe8", "Masa nominal fe 8", 0.395, "kg/m", E, "Tabla de masas nominales (ρ = 7850 kg/m³)", "kgm"),
    ("m_fe10", "Masa nominal fe 10", 0.617, "kg/m", E, "Tabla de masas nominales (ρ = 7850 kg/m³)", "kgm"),
    ("n_cad", "Barras longitudinales de cadena", 6, "un", E, "EETT 3.4: 6 fe 10", "ent"),
    ("L_estribo", "Largo de estribo de cadena", 0.84, "m", E, "(0.11 + 0.26) x 2 + 0.10 de ganchos; sección EETT 3.4", "cant"),
    ("s_estribo", "Espaciamiento de estribos", 0.20, "m", E, "EETT 3.4: E fe 6 a 0.20", "cant"),
    ("d_cad", "Diámetro de barra de cadena", 0.010, "m", E, "EETT 3.4: fe 10", "cant3"),
    ("traslapo_d", "Traslapo en diámetros", 40, "d", E, "EETT 3.5: empalmes no menores a 40 d", "ent"),
    ("n_anc_cad", "Anclajes y empalmes por línea de barra", 8, "un", M, "6 encuentros + 2 empalmes en laterales de 11.65 m (revisor externo)", "ent"),
    ("f_patas", "Trabas y patas no dibujadas", 0.05, "-", E, "NCh 353: +5 % del peso si los planos no las indican [Por verificar]", "pct"),
    ("kg_cad", "Acero de cadena por metro", "=(n_cad*(1+n_anc_cad*traslapo_d*d_cad/L_eje)*m_fe10+L_estribo*m_fe6/s_estribo)*(1+f_patas)", "kg/m", E, "Barras con traslapos + estribos, +5 % patas (NCh 353)", "kgm"),
    ("n_t8", "Tensores fe 8", 38, "un", M, "Contados panel por panel a 0.60 m máx. (EETT 3.3); dos revisores independientes", "ent"),
    ("n_t10", "Tensores fe 10", 40, "un", M, "Encuentros T y L, extremos libres y jambas (EETT 3.3); dos revisores", "ent"),
    ("hilada", "Altura de hilada", 0.081, "m", E, "Ladrillo 7.1 cm (EETT 3) + junta 1.0 cm [junta supuesta]", "cant3"),
    ("s_esc", "Separación de filas de escalerilla", "=3*hilada", "m", E, "Cada 3 hiladas (EETT 3.2)", "cant3"),
    ("H_lad", "Altura de albañilería bajo cadena", "=H_muro-H_cadena", "m", M, "Elevación: achurado de ladrillo hasta +2.40", "cant"),
    ("filas_esc", "Filas de escalerilla", "=INT(H_lad/s_esc)", "un", E, "Filas bajo la cadena", "ent"),
    ("L_esc", "Largo neto de escalerilla", "=filas_esc*L_eje-(n_vg*b_vg*(INT(H_lad/s_esc)-INT(ant_vg/s_esc))+n_vc*b_vc*(INT(H_lad/s_esc)-INT(ant_vc/s_esc))+b_puerta*INT(h_puerta/s_esc))", "m", M, "Filas x L_eje menos los tramos que cruzan vanos", "cant"),
    ("d_esc", "Diámetro de alambre de escalerilla", 0.004, "m", E, "EETT 3.2: tipo Acma de 4 mm", "cant3"),
    ("trav", "Travesaño de escalerilla (largo / paso)", 0.34, "-", S, "0.085 m cada 0.25 m [ficha Acma por verificar]", "cant"),
    ("kg_esc", "Masa de escalerilla por metro", "=(2+trav)*PI()/4*d_esc^2*7850", "kg/m", S, "2 alambres + travesaños, ρ = 7850 kg/m³", "kgm"),
    ("n_tapas", "Tapas de cadena en extremos libres", 10, "un", M, "Extremos de muro en planta (dos revisores)", "ent"),
    ("A_mold_cad", "Moldaje de cadena", "=2*H_cadena*L_eje+(n_vg*b_vg+n_vc*b_vc)*b_cadena+n_tapas*b_cadena*H_cadena", "m²", E, "2 caras + fondo sobre ventanas (la cadena es dintel) + tapas", "cant"),
    ("a_cocina", "Superficie de cocina", 4.25, "m²", M, "Cuadro de recintos del plano", "cant"),
    ("a_bano", "Superficie de baño", 3.70, "m²", M, "Cuadro de recintos del plano", "cant"),
    ("pen_d", "Penetración de verticales en fundación", 40, "d", E, "NCh353 6.2.8: 40 d si los planos no la precisan", "ent"),
    ("L_t8", "Largo de tensor fe 8", "=pen_d*0.008+h_sc+H_muro", "m", E, "40 d + sobrecimiento + muro hasta coronamiento de cadena", "cant"),
    ("L_t10", "Largo de tensor fe 10", "=pen_d*0.010+h_sc+H_muro", "m", E, "40 d + sobrecimiento + muro hasta coronamiento de cadena", "cant"),
    ("techo_x", "Techumbre, largo en planta", c.TECHO[0], "m", M, "DXF y elevaciones", "cant"),
    ("techo_y", "Techumbre, ancho en planta", c.TECHO[1], "m", M, "DXF y elevaciones", "cant"),
    ("pend", "Pendiente de cubierta", c.PEND_CORTE, "-", M, "Medida en el corte: 39.8 % (el plano rotula 60 %)", "pct"),
    ("n_canal", "Canales", 2, "un", M, "Techumbre a dos aguas", "ent"),
    ("n_bajada", "Bajadas de aguas lluvia", 4, "un", S, "Sin plano de aguas lluvia", "ent"),
    ("L_bajada", "Largo de bajada", 3.90, "m", S, "Alero +3.15 a terreno -0.15, más 0.60 de desvío bajo el alero", "cant"),
    ("Tolerancia", "Tolerancia de comparación", 0.05, "-", S, "Criterio del análisis: diferencia aceptada con el presupuesto", "pct"),
    ("Tol_control", "Tolerancia de control", 0.001, "-", S, "Diferencia aceptada entre la planilla y el script de Python", "pct"),
]
for k, (nom, par, val, un, base, fuente, fmt) in enumerate(datos):
    r = F0 + k
    nombre(wb, nom, "Datos", f"$C${r}")
for k, (nom, par, val, un, base, fuente, fmt) in enumerate(datos):
    r = F0 + k
    celda(D, f"A{r}", nom, tipo="texto")
    celda(D, f"B{r}", par, tipo="texto")
    celda(D, f"C{r}", val, fmt=fmt)
    celda(D, f"D{r}", un, tipo="texto", alin="center")
    celda(D, f"E{r}", base, tipo="texto", alin="center")
    celda(D, f"F{r}", fuente, tipo="texto")
UD = F0 + len(datos) - 1
condicional_estado(D, f"E{F0}:E{UD}", f"$E{F0}", "M", "S", "I")
nota(D, f"A{UD+2}", "Base: M = medido en el PDF vectorial; E = documento (EETT o presupuesto tipo); I = inferido sin plano; "
     "S = supuesto del análisis. Letra azul con fondo crema: entrada. Negro: fórmula. Verde: vínculo a otra hoja o a un nombre.", 6, 26)
D.freeze_panes = f"C{F0}"
imprimir(D, f"A1:F{UD+2}", 4)

# ------------------------------------------------------------------ Cubicación
K = wb.create_sheet("Cubicacion")
titulo(K, "Cubicación por partida", SUB, 13, COL["marino"])
encabezado(K, 4, ["Ítem", "Partida", "Unidad", "Origen de la medida", "N.º de veces", "Largo (m)", "Ancho (m) o factor",
                  "Alto o espesor (m)", "Cantidad parcial", "Descuentos (vanos)", "Cantidad neta", "Pérdida", "Cantidad final"],
           [7, 28, 7, 46, 8, 10, 11, 10, 11, 11, 11, 8, 11], alto=42)
filas = [  # item, partida, un, origen, veces, largo, ancho, alto, descuento
    ("2.1", "Nivelación y trazado", "m²", "Huella medida", 1, "=A_huella", None, None, 0),
    ("2.2", "Escarpe", "m³", "Huella x e_escarpe", 1, "=A_huella", None, "=e_escarpe", 0),
    ("2.3", "Excavación de fundaciones", "m³", "L_eje x b_fund x h_exc (sección inferida)", 1, "=L_eje", "=b_fund", "=h_exc", 0),
    ("2.4", "Relleno estabilizado", "m³", "Interior libre x e_relleno (base del radier, EETT 2.4)", 1, "=Int_x", "=Int_y", "=e_relleno", 0),
    ("2.5", "Emplantillado H-5", "m³", "L_eje x b_fund x e_empl (inferido)", 1, "=L_eje", "=b_fund", "=e_empl", 0),
    ("2.6", "Fundaciones H-25", "m³", "L_eje x b_fund x h_fund (inferido)", 1, "=L_eje", "=b_fund", "=h_fund", 0),
    ("2.7", "Sobrecimientos", "m³", "L_eje x b_sc x h_sc (inferido)", 1, "=L_eje", "=b_sc", "=h_sc", 0),
    ("2.8", "Radier", "m³", "Interior libre x e_radier", 1, "=Int_x", "=Int_y", "=e_radier", 0),
    ("2.9", "Moldaje sobrecimientos", "m²", "2 caras x L_eje x h_sc", 2, "=L_eje", None, "=h_sc", 0),
    ("3.1", "Ladrillo gran titán", "m²", "L_eje x H_lad - descuento de vanos NCh 353", 1, "=L_eje", None, "=H_lad", "=A_desc353"),
    ("3.2", "Escalerilla", "kg", "L_esc x kg_esc (factor en kg/m), sin traslapos", 1, "=L_esc", "=kg_esc", None, 0),
    ("3.4", "Hormigón cadena", "m³", "L_eje x b_cadena x H_cadena (EETT 3.4)", 1, "=L_eje", "=b_cadena", "=H_cadena", 0),
    ("3.6", "Moldaje cadena", "m²", "Caras + fondos sobre ventanas + tapas (A_mold_cad)", 1, "=A_mold_cad", None, None, 0),
    ("3.5", "Enfierradura cadena", "kg", "L_eje x kg_cad (traslapos 40 d y +5 % patas)", 1, "=L_eje", "=kg_cad", None, 0),
    ("3.3", "Tensores", "kg", "Largo: kg netos (n L m por diámetro); factor: 1 + f_patas", 1,
     "=n_t8*L_t8*m_fe8+n_t10*L_t10*m_fe10", "=1+f_patas", None, 0),
    ("5.5", "Cubierta OSB 11 mm", "m²", "Proyección x √(1 + pend²)", 1, "=techo_x", "=techo_y", "=SQRT(1+pend^2)", 0),
    ("7.1", "Canales", "ml", "n_canal x largo de techumbre", "=n_canal", "=techo_x", None, None, 0),
    ("8.1", "Bajadas de aguas lluvia", "ml", "n_bajada x L_bajada (supuesto)", "=n_bajada", "=L_bajada", None, None, 0),
    ("10.3", "Cielo yeso-cartón", "m²", "Interior libre", 1, "=Int_x", "=Int_y", None, 0),
    ("11.1", "Cerámica 30 x 30", "m²", "Cocina + baño (EETT 11.2)", 1, "=a_cocina+a_bano", None, None, 0),
]
fila_cub = {}
for k, f in enumerate(filas):
    r = F0 + k
    fila_cub[f[0]] = r
    it, par, un, ori, vec, la, an, al, desc = f
    celda(K, f"A{r}", it, tipo="texto")
    celda(K, f"B{r}", par, tipo="texto")
    celda(K, f"C{r}", un, tipo="texto", alin="center")
    celda(K, f"D{r}", ori, tipo="texto")
    celda(K, f"E{r}", vec, fmt="0")
    for col, v in zip("FGH", (la, an, al)):
        celda(K, f"{col}{r}", v, fmt="cant3") if v is not None else celda(K, f"{col}{r}", tipo="texto")
    celda(K, f"I{r}", f"=N(E{r})*IF(F{r}=\"\",1,F{r})*IF(G{r}=\"\",1,G{r})*IF(H{r}=\"\",1,H{r})", fmt="cant")
    celda(K, f"J{r}", desc, fmt="cant")
    celda(K, f"K{r}", f"=I{r}-N(J{r})", fmt="cant")
    celda(K, f"L{r}", 0, fmt="pct")
    celda(K, f"M{r}", f"=K{r}*(1+N(L{r}))", fmt="cant", negrita=True)
UK = F0 + len(filas) - 1
K[f"L{F0}"].comment = Comment("Pérdida 0 %: cantidades geométricas netas, comparables con el presupuesto tipo.", "N. Albornoz")
nota(K, f"A{UK+2}", "Las dimensiones vienen de la hoja Datos por nombre (letra verde): un cambio en Datos actualiza todas "
     "las partidas que lo usan. Criterio NCh 353: sin pérdidas (van al APU); fierro con traslapos y patas; vanos de albañilería por tabla.", 13, 26)
K.freeze_panes = f"C{F0}"
imprimir(K, f"A1:M{UK+2}", 4)

# ------------------------------------------------------------------ Comparación
P = wb.create_sheet("Comparacion")
titulo(P, "Comparación con el presupuesto tipo", SUB, 10, COL["ok_t"])
encabezado(P, 4, ["Ítem", "Partida", "Unidad", "Presupuesto tipo", "Cubicación", "Diferencia", "Estado frente a la tolerancia",
                  "P.U. presupuesto ($)", "Efecto en costo ($)", "Base de la cubicación"], [7, 28, 7, 12, 12, 11, 12, 14, 15, 30], alto=42)
base_txt = {"medido": "Medido", "I": "Medido x sección inferida", "S": "Medido x supuesto", "EETT": "Medido x EETT"}
r = F0
fila_comp = {}
for it, des, un, pp, cu, pu, form, base in c.partidas:
    if it not in fila_cub:
        continue
    fila_comp[it] = r
    celda(P, f"A{r}", it, tipo="texto")
    celda(P, f"B{r}", des, tipo="texto")
    celda(P, f"C{r}", un.replace("m2", "m²").replace("m3", "m³"), tipo="texto", alin="center")
    celda(P, f"D{r}", pp, fmt="cant")
    celda(P, f"E{r}", f"=Cubicacion!M{fila_cub[it]}", fmt="cant")
    celda(P, f"F{r}", f"=D{r}/E{r}-1", fmt="dif")
    celda(P, f"G{r}", f'=IF(ABS(F{r})<=Tolerancia,"Dentro","Fuera")', alin="center")
    celda(P, f"H{r}", pu, fmt="clp")
    celda(P, f"I{r}", f"=(D{r}-E{r})*H{r}", fmt="clp_s")
    celda(P, f"J{r}", base_txt[base], tipo="texto")
    r += 1
UP = r - 1
condicional_estado(P, f"G{F0}:G{UP}", f"$G{F0}", "Dentro", "Fuera")
condicional_estado(P, f"J{F0}:J{UP}", f"$J{F0}", None, "supuesto", "inferida")
nota(P, f"A{UP+2}", "Diferencia = presupuesto / cubicación - 1; positiva: el presupuesto tipo cubica más. Precios unitarios del "
     "presupuesto tipo (2023). Los efectos no se suman: mezclan signos y partidas con base inferida o supuesta, y su suma no "
     "mide un sobrecosto. La causa de cada diferencia está en la hoja Conciliacion.", 10, 38)
P.freeze_panes = f"C{F0}"
imprimir(P, f"A1:J{UP+2}", 4)

# ------------------------------------------------------------------ Control
Q = wb.create_sheet("Control")
titulo(Q, "Control de cálculo", SUB, 8, COL["aviso_t"])
encabezado(Q, 4, ["Ítem", "Magnitud", "Método 1", "Método 2", "Diferencia", "Tolerancia", "Estado", "Métodos comparados"],
           [7, 30, 12, 12, 11, 11, 11, 62], alto=30)
ctrl = [("-", "Largo de muros por eje (m)", "=L_eje", 37.32, "=Tolerancia",
         "Ejes del DXF frente a recubicación ciega desde el PDF (otro analista)"),
        ("-", "Largo de muros por eje (m)", "=L_eje", 37.31, "=Tolerancia",
         "Ejes del DXF frente a área rasterizada de muros / espesor (revisor externo)")]
for it, des, un, pp, cu, pu, form, base in c.partidas:
    if it in fila_cub:
        ctrl.append((it, f"{des} ({un.replace('m2', 'm²').replace('m3', 'm³')})", f"=Cubicacion!M{fila_cub[it]}",
                     round(cv4.v6[it], 9), "=Tol_control", "Planilla (fórmulas sobre Datos) frente a correcciones.py"))
for k, (it, mag, m1, m2, tol, met) in enumerate(ctrl):
    r = F0 + k
    celda(Q, f"A{r}", it, tipo="texto")
    celda(Q, f"B{r}", mag, tipo="texto")
    celda(Q, f"C{r}", m1, fmt="cant3")
    celda(Q, f"D{r}", m2, fmt="cant3")
    celda(Q, f"E{r}", f"=ABS(C{r}-D{r})/D{r}", fmt="0.00%")
    celda(Q, f"F{r}", tol, fmt="0.0%")
    celda(Q, f"G{r}", f'=IF(E{r}<=F{r},"OK","REVISAR")', alin="center")
    celda(Q, f"H{r}", met, tipo="texto")
UQ = F0 + len(ctrl) - 1
condicional_estado(Q, f"G{F0}:G{UQ}", f"$G{F0}", "OK", "REVISAR")
nota(Q, f"A{UQ+2}", "Método 2 en azul: valor copiado del script de Python, calculado por un camino distinto de la planilla. "
     "Las dos primeras filas son controles geométricos independientes; las demás controlan que la planilla reproduzca el script.", 8, 26)
Q.freeze_panes = f"C{F0}"
imprimir(Q, f"A1:H{UQ+2}", 4)

# ------------------------------------------------------------------ Conciliación
import math
v = cv4.v6
Lr, Hl = cv4.L, cv4.H_lad
CR, ER, SR = "Criterio de cubicación", "Error del presupuesto", "Sin resolver"
conc = [  # ítem, causa, criterio que reproduce la cifra del presupuesto, cantidad reconstruida, evidencia
    ("2.3", CR, "Sobreexcavación de 5 % sobre la sección neta", v["2.3"] * 1.05, "Margen de obra; NCh 353 solo admite sobreancho si hay moldaje y la EETT 2.3 pide hormigón contra terreno"),
    ("2.4", ER, "Huella completa x 0.15 y unidad m² (debe ser m³ sobre el interior)", cv4.hu * 0.15, "EETT 2.4: relleno = base del radier"),
    ("2.9", CR, "Moldaje neto x 1.07 (encuentros y reposición)", v["2.9"] * 1.07, "Factor deducido [Por verificar]"),
    ("3.1", CR, "Ladrillo sin descontar vanos: L_eje x 2.40", Lr * Hl, "NCh 353 no descuenta vanos < 1.5 m² y la puerta al 50 %: la cubicación v5 queda a 1.6 % del presupuesto"),
    ("3.2", ER, "10 filas x 0.50 kg/m x L_eje: doble de la masa real del alambre de 4 mm", 10 * 0.50 * Lr, "Presupuesto: 2.07 kg/m²; FSPR 2019 sede y capilla: 1.03 a 1.13 kg/m²"),
    ("3.3", CR, "Todos fe 10: 63 + 22 barras x 3.30 m, sin ganchos", 85 * 3.30 * 0.617, "Criterio conservador; EETT 3.3 admite fe 8 en tensores corrientes"),
    ("3.4", ER, "Cadena solo en el perímetro (31.01 m) con muro de 0.14 m", 0.14 * 0.30 * 31.01, "Incoherente con el moldaje (30 m² implica el largo completo)"),
    ("3.5", ER, "4 fe 10 x L_eje, sin estribos ni empalmes", 4 * 0.617 * Lr, "EETT 3.4 pide 6 fe 10 + E fe 6 a 0.20; con traslapos de 40 d y +5 % de patas (NCh 353) la cubicación es la de la columna D"),
    ("3.6", CR, "Tablero de 0.40 m por cara (0.10 m apoyado en el muro)", 2 * 0.40 * Lr, "Práctica de obra [Por verificar]; la capilla FSPR 2019 trae 29.76 m²"),
    ("5.5", CR, "12.50 m x 2 faldones de 3.50 m, sin traslapos", 12.50 * 2 * 3.50, "NCh 353: vertientes sin traslapos; confirma la pendiente de 40 %; difiere solo en el largo (12.50 frente a 12.85 m)"),
    ("8.1", ER, "Repite la cifra de canales (26 ml)", 26.0, "4 bajadas medidas en el corte: 10.4 a 15.6 ml"),
    ("10.3", SR, "53.3 m² se repite en cielo y poliestireno; no coincide con el interior medido", 53.3, "Interior libre 51.03 m²; con muro de 0.14 m, 51.33 m²"),
    ("11.1", ER, "Cerámica en todo el interior", cv4.ix * cv4.iy, "EETT 11.2: solo cocina y baño (7.95 m²)"),
]
N_ = wb.create_sheet("Conciliacion")
titulo(N_, "Conciliación: causa de cada diferencia con el presupuesto tipo", SUB, 10, COL["aviso_t"])
encabezado(N_, 4, ["Ítem", "Partida", "Presupuesto tipo", "Cubicación neta", "Diferencia", "Causa",
                   "Criterio que reproduce la cifra del presupuesto", "Cantidad reconstruida", "Dif. con el presupuesto",
                   "Evidencia"], [6, 24, 10, 10, 9, 20, 40, 11, 10, 44], alto=42)
for k, (it, causa, crit, rec, evid) in enumerate(conc):
    rr = F0 + k
    fc = fila_comp[it]
    celda(N_, f"A{rr}", it, tipo="texto")
    celda(N_, f"B{rr}", {p[0]: p[1] for p in c.partidas}[it], tipo="texto")
    celda(N_, f"C{rr}", f"=Comparacion!D{fc}", fmt="cant")
    celda(N_, f"D{rr}", f"=Comparacion!E{fc}", fmt="cant")
    celda(N_, f"E{rr}", f"=Comparacion!F{fc}", fmt="dif")
    celda(N_, f"F{rr}", causa, tipo="texto")
    celda(N_, f"G{rr}", crit, tipo="texto", envolver=True)
    celda(N_, f"H{rr}", round(rec, 4), fmt="cant")
    celda(N_, f"I{rr}", f"=H{rr}/C{rr}-1", fmt="dif")
    celda(N_, f"J{rr}", evid, tipo="texto", envolver=True)
    N_.row_dimensions[rr].height = 40
UN = F0 + len(conc) - 1
condicional_estado(N_, f"F{F0}:F{UN}", f"$F{F0}", "Criterio", "Error", "Sin resolver")
# Correcciones propias v3 -> v4
v3 = {p[0]: p[4] for p in c.partidas}
v3["3.6"], v3["3.1"] = 2 * 0.30 * Lr, Lr * Hl - c.A_vanos
corr = [("2.4", "Área de la huella en vez del interior: el relleno es base del radier (EETT 2.4)", "Revisor externo"),
        ("11.1", "Todo el interior en vez de cocina y baño (EETT 11.2)", "Revisor externo"),
        ("3.3", "Doble conteo de fe 8; faltaban +5 % de patas (NCh 353 6.2.4) y penetración de 40 d en fundación (6.2.8) en vez de 0.60 m supuesto", "Revisor, recubicación ciega y NCh 353"),
        ("3.2", "Escalerilla sin descontar vanos, con 4.2 mm (EETT: 4 mm) y +10 %", "Revisor externo"),
        ("3.6", "Faltaban fondos de cadena sobre ventanas y tapas en extremos libres", "Revisor externo"),
        ("8.1", "3.15 m es la cota del alero, no el largo de la bajada", "Revisor externo"),
        ("3.1", "Vanos descontados al 100 %; NCh 353 no descuenta los < 1.5 m² (y ventana chica de 0.80 m)", "Literatura (NCh 353) y revisor"),
        ("3.5", "Enfierradura sin traslapos de 40 d ni +5 % de patas (NCh 353, EETT 3.5)", "Literatura y revisor")]
f1 = UN + 3
celda(N_, f"A{f1}", "Correcciones a la cubicación propia (v3 a v5): revisión en frío y NCh 353", tipo="texto", negrita=True)
encabezado(N_, f1 + 1, ["Ítem", "Partida", "v3", "v5", "Cambio", "Detectado por", "Motivo"], [6, 26, 11, 11, 10, 21, 44], alto=22)
for k, (it, mot, quien) in enumerate(corr):
    rr = f1 + 2 + k
    celda(N_, f"A{rr}", it, tipo="texto")
    celda(N_, f"B{rr}", {f[0]: f[1] for f in filas}[it], tipo="texto")
    celda(N_, f"C{rr}", round(v3[it], 4), fmt="cant")
    celda(N_, f"D{rr}", f"=Cubicacion!M{fila_cub[it]}", fmt="cant")
    celda(N_, f"E{rr}", f"=D{rr}/C{rr}-1", fmt="dif")
    celda(N_, f"F{rr}", quien, tipo="texto", envolver=True)
    celda(N_, f"G{rr}", mot, tipo="texto", envolver=True)
    N_.merge_cells(f"G{rr}:J{rr}")
    N_.row_dimensions[rr].height = 26
UC = f1 + 1 + len(corr)
nota(N_, f"A{UC+2}", "Criterio de cubicación: la cifra del presupuesto se reproduce con un criterio legítimo (NCh 353, práctica de obra). "
     "Error del presupuesto: la cifra solo se explica con una cantidad que no corresponde a la geometría ni a las EETT, una unidad "
     "equivocada o una cifra repetida. Cantidades reconstruidas calculadas en Python (armar_excel_v6.py) desde los datos medidos.", 10, 30)
N_.freeze_panes = f"C{F0}"
imprimir(N_, f"A1:J{UC+2}", 4)

# ------------------------------------------------------------------ Resumen (primera hoja)
R = wb.create_sheet("Resumen", 0)
titulo(R, "Cubicación independiente y revisión del presupuesto tipo", "Ejercicio de portafolio sobre documentos públicos; no oficial", 4, COL["marino"])
for col, w in zip("ABCD", (34, 16, 12, 52)):
    R.column_dimensions[col].width = w
filas_r = [
    ("Proyecto", PROY), ("Mandante del diseño", "Fondo Social Presidente de la República (FSPR), documentos públicos 2023"),
    ("Documentos", "Anexo 5.3 Planimetría (lámina 1/1), Anexo 3.3 Presupuesto tipo, EETT (22 p.)"),
    ("Elaboró", "Nicolás Albornoz"), ("Fecha", "2026-11-20"),
]
for k, (a, b) in enumerate(filas_r, 4):
    celda(R, f"A{k}", a, tipo="texto", negrita=True)
    celda(R, f"B{k}", b, tipo="texto")
    R.merge_cells(f"B{k}:D{k}")
encabezado(R, 10, ["Resultado", "Valor", "Unidad", "Origen"], [34, 16, 12, 52], alto=22)
res = [("Largo de muros por eje", "=L_eje", "m", "Datos", "cant"),
       ("Huella exterior", "=A_huella", "m²", "Datos", "cant"),
       ("Partidas comparadas", f"=COUNTA(Comparacion!A{F0}:A{UP})", "un", "Comparacion", "0"),
       ("Partidas dentro de la tolerancia (5 %)", f'=COUNTIF(Comparacion!G{F0}:G{UP},"Dentro")', "un", "Comparacion", "0"),
       ("Partidas fuera de la tolerancia", f'=COUNTIF(Comparacion!G{F0}:G{UP},"Fuera")', "un", "Comparacion: revisar hallazgos", "0"),
       ("Controles en estado OK", f'=COUNTIF(Control!G{F0}:G{UQ},"OK")', "un", f"Control: de {len(ctrl)}", "0"),
       ("Controles por revisar", f'=COUNTIF(Control!G{F0}:G{UQ},"REVISAR")', "un", "Control: debe ser 0", "0")]
for k, (a, f, u, o, fmt) in enumerate(res, 11):
    celda(R, f"A{k}", a, tipo="texto")
    celda(R, f"B{k}", f, fmt=fmt, negrita=True)
    celda(R, f"C{k}", u, tipo="texto", alin="center")
    celda(R, f"D{k}", o, tipo="texto")
fh = 11 + len(res) + 1
celda(R, f"A{fh}", "Hallazgos principales", tipo="texto", negrita=True)
pu_ = {p[0]: p[5] for p in c.partidas}
sob = (186.5 - v["3.2"]) * pu_["3.2"]
fal = (1.28 - v["3.4"]) * pu_["3.4"] + (93 - v["3.5"]) * pu_["3.5"]
hall = [f"Escalerilla sobrepresupuestada en ${sob:,.0f} y cadena (hormigón y acero) subpresupuestada en ${-fal:,.0f}: "
        "el capítulo 3 parece razonable, pero la distribución entre partidas no lo es.",
        "Con NCh 353 (vanos menores a 1.5 m² sin descuento; fierro con traslapos y patas) el ladrillo queda a 1.6 % del presupuesto; "
        "excavación, moldajes y tensores se explican por criterio de obra; el resto son errores del presupuesto (hoja Conciliacion).",
        "Pendiente de cubierta: el plano rotula 60 %; corte, elevaciones y el propio presupuesto (faldón de 3.50 m) dan 40 %.",
        "EETT contradictorias: cadena con fe 10 a 0.20 frente a fe 12 a 0.15; ladrillo de 14 cm frente a muro dibujado de 15 cm; "
        "sobrecimiento armado con 4 fe 12 sin partida propia [Por verificar si va en el precio unitario]; encuentros con fe 10 donde "
        "NCh1928 exigiría 12 mm [Por verificar con el texto de la norma].",
        "Revisión en frío y texto de NCh 353: 8 partidas corregidas a la cubicación propia, listadas en Conciliacion."]
for k, t in enumerate(hall, fh + 1):
    celda(R, f"A{k}", "• " + t, tipo="texto", envolver=True)
    R.merge_cells(f"A{k}:D{k}")
    R.row_dimensions[k].height = 40
fa = fh + len(hall) + 2
nota(R, f"A{fa}", "Alcance: cubicación referencial elaborada desde los planos públicos recibidos; no reemplaza un proyecto ni "
     "un presupuesto firmado por un profesional competente. Supuestos e inferencias declarados en Datos (columna Base). "
     "Colores: azul con fondo crema = entrada; negro = fórmula; verde = vínculo a otra hoja o a un nombre de Datos.", 4, 52)
imprimir(R, f"A1:D{fa}", None, horizontal=False)
wb.move_sheet("Conciliacion", offset=-(len(wb.sheetnames) - 2))
wb.active = 0
wb.save(SAL)
print("ok", SAL, "filas cubicación", len(filas), "comparación", UP - F0 + 1, "control", len(ctrl))
