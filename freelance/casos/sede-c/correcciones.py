"""Cubicación v4: correcciones de la revisión en frío (agentes A, B, C), calculadas en Python por un camino
distinto de la planilla. Fuente para la hoja Control y para la conciliación."""
import math
import cubicacion_sedeC as c

L = round(c.L_eje, 3)
hu = round(c.A_huella, 3)
ix, iy = round(c.int_x, 3), round(c.int_y, 3)
H_lad = c.H_MURO - c.H_CADENA                       # 2.40: ladrillo bajo la cadena (elevación: achurado hasta +2.40)
vg, vc, pu = (8, 0.601, 1.80, 0.60), (2, 0.399, 0.80, 1.60), (1, 1.299, 2.10, 0.0)   # n, b, h, antepecho
A_vanos = sum(n * b * h for n, b, h, _ in (vg, vc, pu))

# Escalerilla: fila cada 3 hiladas de 7.1 + 1.0 cm; descuenta las filas que cruzan vanos; fe 4 (EETT 3.2)
s_esc = 3 * (0.071 + 0.010)
filas = [k * s_esc for k in range(1, 50) if k * s_esc < H_lad]
cruce = sum(n * b * sum(1 for z in filas if ant < z < ant + h) for n, b, h, ant in (vg, vc, pu))
L_esc = len(filas) * L - cruce
kg_esc_m = (2 + 0.085 / 0.25) * math.pi / 4 * 0.004 ** 2 * 7850
escalerilla = L_esc * kg_esc_m

tensores = (38 * 0.395 + 40 * 0.617) * c.L_TENS     # 38 fe 8 + 40 fe 10, contados panel por panel (A y C)
mold_cad = 2 * c.H_CADENA * L + (vg[0] * vg[1] + vc[0] * vc[1]) * 0.15 + 10 * 0.15 * c.H_CADENA
v4 = {
    "2.1": hu, "2.2": hu * 0.15, "2.3": L * 0.40 * 0.65, "2.4": ix * iy * 0.15, "2.5": L * 0.40 * 0.05,
    "2.6": L * 0.40 * 0.60, "2.7": L * 0.15 * 0.20, "2.8": ix * iy * 0.08, "2.9": 2 * L * 0.20,
    "3.1": L * H_lad - A_vanos, "3.2": escalerilla, "3.3": tensores, "3.4": L * 0.15 * 0.30,
    "3.5": L * (6 * 0.617 + 0.84 * 0.222 / 0.20), "3.6": mold_cad,
    "5.5": 12.85 * 6.50 * math.sqrt(1 + c.PEND_CORTE ** 2), "7.1": 2 * 12.85, "8.1": 4 * 3.90,
    "10.3": ix * iy, "11.1": 4.25 + 3.70,
}

if __name__ == "__main__":
    print(f"filas escalerilla {len(filas)}, cruce {cruce:.3f} m, L_esc {L_esc:.2f} m, {kg_esc_m:.4f} kg/m")
    for k, v in v4.items():
        print(k, round(v, 3))


# ---------------------------------------------------------------- v5: criterios NCh 353 (vía guía Mineduc) [Por verificar]
def f_vano(area, pilar=0):
    """Fracción de descuento de un vano en albañilería de ladrillo a máquina."""
    if area < 1.5:
        return 0.5 * pilar
    if area <= 3:
        return 0.5 + 0.25 * pilar
    return 1.0


def desc353(pilar=0):
    return sum(n * b * h * f_vano(b * h, pilar) for n, b, h, _ in (vg, vc, pu))


F_PATAS, N_ANC, TRASL_D = 0.05, 8, 40
kg_cad5 = (6 * (1 + N_ANC * TRASL_D * 0.010 / L) * 0.617 + 0.84 * 0.222 / 0.20) * (1 + F_PATAS)
v5 = dict(v4)
v5["3.1"] = L * H_lad - desc353()
v5["3.3"] = v4["3.3"] * (1 + F_PATAS)
v5["3.5"] = L * kg_cad5


# ---------------------------------------------------------------- v6: NCh353 6.2.8, penetración de verticales en fundación = 40 d
L_T8, L_T10 = 40 * 0.008 + 0.20 + c.H_MURO, 40 * 0.010 + 0.20 + c.H_MURO
v6 = dict(v5)
v6["3.3"] = (38 * L_T8 * 0.395 + 40 * L_T10 * 0.617) * (1 + F_PATAS)
