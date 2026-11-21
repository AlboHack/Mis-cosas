"""Cubicación independiente de la obra gruesa de la Sede Social Tipo C (FSPR 2023) y comparación con su
presupuesto tipo (Anexo 3.3). Todas las longitudes salen del DXF extraído del PDF (sedeC_planta.dxf) o de
cotas leídas en la lámina; los supuestos están marcados con S (supuesto) e I (inferido del presupuesto).

Ejecutar:  python cubicacion_sedeC.py   -> imprime la tabla y escribe resultados.json
"""
import json, math
import ezdxf

# ------------------------------------------------------------------ 1. Geometría medida (DXF, metros)
from pathlib import Path
AQUI = Path(__file__).resolve().parent
doc = ezdxf.readfile(AQUI / "sedeC_planta.dxf")
lin = [e for e in doc.modelspace().query('LINE[layer=="MUROS_CORTE"]')]
xs = sorted({round(e.dxf.start.x, 3) for e in lin} | {round(e.dxf.end.x, 3) for e in lin})
ys = sorted({round(e.dxf.start.y, 3) for e in lin} | {round(e.dxf.end.y, 3) for e in lin})
X_EXT0, X_EXT1 = 0.0, 5.301            # caras exteriores de muros laterales
Y_EXT0, Y_EXT1 = 0.0, 10.504           # cara exterior muro de acceso / muro del fondo
T = 0.15                               # espesor de muro (medido 0.148-0.151; cota 0.15)
Y_VEST = -1.151                        # término de los muros del vestíbulo
MACHON = 0.501                         # saliente de machones respecto de la cara exterior
N_MACHON = 8
assert X_EXT1 in xs and Y_EXT1 in ys and Y_VEST in ys, "la geometría del DXF no coincide con la esperada"

ext_x, ext_y = X_EXT1 - X_EXT0, Y_EXT1 - Y_EXT0
int_x, int_y = ext_x - 2 * T, ext_y - 2 * T
L_perim = 2 * ((ext_x - T) + (ext_y - T))                 # eje del muro perimetral
L_vest = 2 * (abs(Y_VEST) + T / 2)                         # dos muros de vestíbulo, desde el eje del muro de acceso
L_mach = N_MACHON * MACHON                                 # machones, desde la cara exterior (el tramo dentro del muro ya está en L_perim)
L_eje = L_perim + L_vest + L_mach
A_huella = ext_x * ext_y + ext_x * abs(Y_VEST) + N_MACHON * MACHON * T
A_int = int_x * int_y

# Segundo método para L_eje: caras de muro (sin duplicados, sin flechas de cota ni tapas < 0.16 m) / 2 + anchos de vanos
_caras = set()
for e in lin:
    a, b = (round(e.dxf.start.x, 3), round(e.dxf.start.y, 3)), (round(e.dxf.end.x, 3), round(e.dxf.end.y, 3))
    if a[0] != b[0] and a[1] != b[1]:
        continue                                          # trazos inclinados: flechas de cota
    _caras.add(tuple(sorted((a, b))))
L_caras = sum(math.dist(a, b) for a, b in _caras if math.dist(a, b) >= 0.16)

# Vanos (planta) y alturas (elevaciones / cortes)
V_GRANDE = (8, 0.601, 1.80)     # 4 por lado; ancho de planta, alto 0.60 -> 2.40 en elevación
V_CHICA = (2, 0.399, 0.60)      # 1 por lado; 40 x 60 según partida 15.2 del presupuesto
PUERTA = (1, 1.299, 2.10)       # acceso; alto 2.10 (nivel en elevación frontal)
A_vanos = sum(n * a * h for n, a, h in (V_GRANDE, V_CHICA, PUERTA))

H_MURO = 2.70                   # NPT +-0.00 a +2.70 (corte BB)
H_CADENA = 0.30                 # EETT 3.4: cadena 15 x 30 cm; coincide con dintel de ventanas a +2.40
PEND_CORTE = 0.398              # medida en el corte BB (dx/dy de cuerdas superiores)
TECHO = (12.85, 6.50)           # proyección de techumbre (cotas, verificadas en DXF)

# ------------------------------------------------------------------ 2. Cantidades
F_B, F_H, EMPL = 0.40, 0.60, 0.05      # I: fundación corrida 0.40 x 0.60, emplantillado 5 cm
SC_B, SC_H = 0.15, 0.20                 # I: sobrecimiento 0.15 x 0.20
HILADA = 0.071 + 0.013                  # S: ladrillo 7.1 cm + junta 1.3 cm
KG_ESC = 1.35 / 5.0                     # escalerilla 4.2 mm, 1.35 kg por tira de 5 m (ficha comercial)
filas_esc = math.floor((H_MURO - H_CADENA) / (3 * HILADA))   # EETT: cada 3 hiladas
L_bajadas = 4 * 3.15                    # S: 4 bajadas desde alero (+3.15) a terreno

# Cadena (EETT 3.4): 6 fe 10 + estribos fe 6 a 0.20; estribo de (0.11 + 0.26) x 2 + 0.10 de ganchos
KG_M = {6: 0.222, 8: 0.395, 10: 0.617, 12: 0.888}
KG_CAD_MIN = 6 * KG_M[10] + ((0.11 + 0.26) * 2 + 0.10) * KG_M[6] / 0.20
KG_CAD_12 = 6 * KG_M[12] + ((0.11 + 0.26) * 2 + 0.10) * KG_M[6] / 0.15          # lectura EETT 3.5
# Tensores (EETT 3.3): fe 8 a 0.60 máx. a lo largo del muro; fe 10 en bordes de vanos y en encuentros en T y L
N_T8 = math.ceil(L_eje / 0.60)
N_T10 = 2 * (V_GRANDE[0] + V_CHICA[0] + PUERTA[0]) + 4 + N_MACHON + 2      # vanos, esquinas, machones, vestíbulo
L_TENS = round(0.60 + 0.20 + H_MURO, 2)                                    # empotrado en cimiento + sobrecimiento + muro
KG_TENS = (N_T8 * KG_M[8] + N_T10 * KG_M[10]) * L_TENS
techo_inc = TECHO[0] * TECHO[1] * math.sqrt(1 + PEND_CORTE**2)
techo_60 = TECHO[0] * TECHO[1] * math.sqrt(1 + 0.60**2)

partidas = [  # item, descripción, unidad, presupuesto, cubicado, P.U. presupuesto, fórmula, base
 ("2.1", "Nivelación y trazado", "m2", 62.70, A_huella, 5000, "huella con vestíbulo y machones", "medido"),
 ("2.2", "Escarpe e = 0.15 m", "m3", 9.40, A_huella * 0.15, 5000, "huella x 0.15", "medido"),
 ("2.3", "Excavación de fundaciones", "m3", 10.25, F_B * (F_H + EMPL) * L_eje, 15000, "0.40 x 0.65 x L eje", "I"),
 ("2.4", "Relleno estabilizado e = 0.15 m", "m3", 9.40, A_huella * 0.15, 27000, "huella x 0.15 (presupuesto dice m2)", "medido"),
 ("2.5", "Emplantillado H-5", "m3", 0.76, F_B * EMPL * L_eje, 70000, "0.40 x 0.05 x L eje", "I"),
 ("2.6", "Fundaciones H-25", "m3", 9.20, F_B * F_H * L_eje, 144000, "0.40 x 0.60 x L eje", "I"),
 ("2.7", "Sobrecimientos", "m3", 1.15, SC_B * SC_H * L_eje, 144000, "0.15 x 0.20 x L eje", "I"),
 ("2.8", "Radier e = 0.08 m", "m3", 4.26, A_int * 0.08, 126000, "interior bruto x 0.08", "medido"),
 ("2.9", "Moldaje sobrecimientos", "m2", 16.00, 2 * SC_H * L_eje, 5400, "2 caras x 0.20 x L eje", "I"),
 ("3.1", "Ladrillo gran titán", "m2", 90.00, L_eje * (H_MURO - H_CADENA) - A_vanos, 36750, "L eje x 2.40 - vanos", "EETT"),
 ("3.2", "Escalerilla", "kg", 186.50, filas_esc * L_eje * 1.10 * KG_ESC, 3150, f"{filas_esc} filas x L eje x 1.10 x 0.27 kg/m", "S"),
 ("3.4", "Hormigón cadena", "m3", 1.28, 0.15 * H_CADENA * L_eje, 157500, "0.15 x 0.30 x L eje", "EETT"),
 ("3.6", "Moldaje cadena", "m2", 30.00, 2 * H_CADENA * L_eje, 18000, "2 caras x 0.30 x L eje", "EETT"),
 ("3.5", "Enfierradura cadena", "kg", 93.00, KG_CAD_MIN * L_eje, 3525, "6 fe 10 + E fe 6 a 0.20 (EETT 3.4), sin traslapos", "EETT"),
 ("3.3", "Tensores", "kg", 174.00, KG_TENS, 3900, f"{N_T8} fe 8 + {N_T10} fe 10, largo {L_TENS} m", "S"),
 ("5.5", "Cubierta OSB 11 mm", "m2", 87.50, techo_inc, 4810, "12.85 x 6.50 x sqrt(1 + 0.398^2)", "medido"),
 ("5.7", "Zinc-aluminio ondulado", "m2", 87.50, techo_inc, 7020, "ídem (sin traslapos)", "medido"),
 ("7.1", "Canales", "ml", 26.00, 2 * TECHO[0], 9720, "2 x 12.85", "medido"),
 ("8.1", "Bajadas AALL", "ml", 26.00, L_bajadas, 5160, "4 x 3.15", "S"),
 ("10.3", "Cielo yeso-cartón", "m2", 53.30, A_int, 7500, "interior bruto", "medido"),
 ("11.1", "Cerámica 30 x 30", "m2", 51.00, A_int, 6500, "interior bruto", "medido"),
]

# ------------------------------------------------------------------ 3. Chequeos independientes
chequeos = {
 "L_eje (geometría)": L_eje,
 "L_eje (caras / 2 + vanos, segundo método)": L_caras / 2 + sum(n * a for n, a, h in (V_GRANDE, V_CHICA, PUERTA)),
 "L implícito por emplantillado (0.76 / 0.40 / 0.05)": 0.76 / (F_B * EMPL),
 "Ancho implícito de cadena = 2V/M (1.28 m3, 30 m2)": 2 * 1.28 / 30.0,
 "Ancho implícito de sobrecimiento = 2V/M (1.15 m3, 16 m2)": 2 * 1.15 / 16.0,
 "Escalerilla del presupuesto en metros (186.5 / 0.27)": 186.5 / KG_ESC,
 "Ladrillo sin descontar cadena (L x 2.70 - vanos)": L_eje * H_MURO - A_vanos,
 "Cubierta con pendiente 60 %": techo_60,
 "Pendiente implícita en el presupuesto (87.5 m2)": math.sqrt((87.5 / (TECHO[0] * TECHO[1]))**2 - 1),
 "Ladrillo con muro desde +0.10 (sensibilidad)": L_eje * (H_MURO - H_CADENA - 0.10) - A_vanos,
 "Área de vanos": A_vanos,
 "Filas de escalerilla": filas_esc,
 "Enfierradura cadena con 6 fe 12 + E a 0.15 (EETT 3.5)": KG_CAD_12 * L_eje,
 "Enfierradura cadena mínima (4 fe 10 + E a 0.20) sobre perímetro": (4 * 0.617 + ((0.11 + 0.26) * 2 + 0.10) * 0.222 / 0.20) * L_perim,
 "Hormigón cadena solo en perímetro + vestíbulo": 0.15 * 0.30 * (L_perim + L_vest),
}

if __name__ == "__main__":
    print(f"L_perim {L_perim:.2f}  L_vest {L_vest:.2f}  L_mach {L_mach:.2f}  L_eje {L_eje:.2f} m")
    print(f"huella {A_huella:.2f} m2  interior {int_x:.3f} x {int_y:.3f} = {A_int:.2f} m2")
    for k, v in chequeos.items():
        print(f"  {k:55s} {v:10.3f}")
    print(f"\n{'ítem':5s} {'partida':32s} {'un':3s} {'ppto':>8s} {'cubic.':>8s} {'dif %':>7s} {'impacto $':>11s} base")
    tot = 0; filas = []
    for it, des, un, pp, cu, pu, form, base in partidas:
        dif = 100 * (pp / cu - 1)          # >0: el presupuesto cubica más que la medición
        imp = (pp - cu) * pu
        tot += imp
        filas.append(dict(item=it, partida=des, unidad=un, presupuesto=pp, cubicado=round(cu, 2),
                          dif_pct=round(dif, 1), impacto=round(imp), formula=form, base=base, pu=pu))
        print(f"{it:5s} {des:32s} {un:3s} {pp:8.2f} {cu:8.2f} {dif:+7.1f} {imp:+11,.0f} {base}")
    print(f"Impacto neto de las diferencias (presupuesto - cubicación) x P.U. = {tot:+,.0f} CLP")
    json.dump(dict(geom=dict(L_perim=L_perim, L_vest=L_vest, L_mach=L_mach, L_eje=L_eje, A_huella=A_huella,
                             A_int=A_int, int_x=int_x, int_y=int_y, A_vanos=A_vanos, techo_inc=techo_inc,
                             techo_60=techo_60, filas_esc=filas_esc),
                   chequeos=chequeos, partidas=filas, impacto_total=tot),
              open(AQUI / "resultados.json", "w"), ensure_ascii=False, indent=1)
