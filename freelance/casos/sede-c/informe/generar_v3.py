"""Genera valores y tablas del informe v3 desde correcciones.py (mismos números que la planilla v5)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cubicacion_sedeC as c
import correcciones as k

v = k.v6
pp = {p[0]: p for p in c.partidas}
items = [p[0] for p in c.partidas if p[0] in v]
TOL = 0.05
causa = {"2.3": "C", "2.4": "E", "2.9": "C", "3.1": "C", "3.2": "E", "3.3": "C", "3.4": "E", "3.5": "E",
         "3.6": "C", "5.5": "C", "8.1": "E", "10.3": "R", "11.1": "E"}
nom = {"C": "Criterio", "E": "Error ppto.", "R": "Sin resolver"}
base = {"2.1": "M", "2.2": "M", "2.3": "I", "2.4": "M", "2.5": "I", "2.6": "I", "2.7": "I", "2.8": "M", "2.9": "I",
        "3.1": "M", "3.2": "S", "3.3": "M/S", "3.4": "E", "3.5": "E", "3.6": "E", "5.5": "M", "7.1": "M", "8.1": "S",
        "10.3": "M", "11.1": "M"}


def u(x):
    return x.replace("m2", "m$^2$").replace("m3", "m$^3$")


filas, dentro = [], 0
for it in items:
    p = pp[it]
    d = p[3] / v[it] - 1
    dentro += abs(d) <= TOL
    filas.append(f"{it} & {p[1]} & {u(p[2])} & \\num{{{p[3]:.2f}}} & \\num{{{v[it]:.2f}}} & {100*d:+.1f} & {base[it]} & "
                 f"{nom.get(causa.get(it), '') if abs(d) > TOL or it == '3.1' else ''}\\\\")
T1 = r"""\begin{table}
\centering\small
\begin{tabular}{llcSSrcl}
\toprule
Ítem & Partida & Unidad & {Presupuesto} & {Cubicación} & {Dif. [\%]} & Base & Causa\\
\midrule
""" + "\n".join(filas) + r"""
\bottomrule
\end{tabular}
\caption{Presupuesto tipo frente a la cubicación independiente (v6). Diferencia positiva: el presupuesto cubica más.}
\label{tab:comp}
\end{table}
"""
open("tabla_comp.tex", "w").write(T1)

L, Hl = k.L, k.H_lad
rec = [("3.1", "Sin descontar vanos: $L\\times2.40$", L * Hl),
       ("2.3", "Sobreexcavación de 5\\,\\%", v["2.3"] * 1.05),
       ("2.9", "Moldaje neto $\\times1.07$", v["2.9"] * 1.07),
       ("3.3", "Todos $\\phi$10: 85 barras de \\SI{3.30}{m}", 85 * 3.30 * 0.617),
       ("3.6", "Tablero de \\SI{0.40}{m} por cara", 2 * 0.40 * L),
       ("5.5", "Vertientes de \\SI{12.50}{m}$\\times$\\SI{3.50}{m}", 12.5 * 7.0),
       ("2.4", "Huella completa $\\times0.15$ en m$^2$", k.hu * 0.15),
       ("3.2", "10 filas $\\times$ \\SI{0.50}{kg/m}: doble de la masa real", 10 * 0.5 * L),
       ("3.4", "Cadena solo en el perímetro, muro de \\SI{0.14}{m}", 0.14 * 0.30 * 31.01),
       ("3.5", "4\\,$\\phi$10 sin estribos ni traslapos", 4 * 0.617 * L),
       ("8.1", "Repite la cifra de canales", 26.0),
       ("11.1", "Cerámica en todo el interior", k.ix * k.iy)]
fr = []
for it, crit, q in rec:
    fr.append(f"{it} & {pp[it][1]} & {nom[causa[it]]} & {crit} & \\num{{{q:.2f}}} & \\num{{{pp[it][3]:.2f}}} & {100*(q/pp[it][3]-1):+.1f}\\\\")
T2 = r"""\begin{table}
\centering\small
\begin{tabularx}{\linewidth}{lp{2.9cm}lXS[table-format=3.2]S[table-format=3.2]r}
\toprule
Ítem & Partida & Causa & Criterio que reproduce la cifra & {Reconstr.} & {Ppto.} & {Dif. [\%]}\\
\midrule
""" + "\n".join(fr) + r"""
\bottomrule
\end{tabularx}
\caption{Reconstrucción de las cifras del presupuesto: todas salvo el cielo (\SI{53.3}{m^2}, sin resolver) se reproducen dentro de $\pm2$\,\%.}
\label{tab:conc}
\end{table}
"""
open("tabla_conc.tex", "w").write(T2)

v3 = {p[0]: p[4] for p in c.partidas}
v3["3.6"], v3["3.1"] = 2 * 0.30 * L, L * Hl - c.A_vanos
corr = [("2.4", "Relleno sobre la huella; EETT 2.4 lo define como base del radier (interior)", "Revisor"),
        ("11.1", "Cerámica en todo el interior; EETT 11.2: solo cocina y baño", "Revisor"),
        ("3.3", "Doble conteo de $\\phi$8; faltaban +5\\,\\% de patas y la penetración de 40\\,$d$ en fundación (NCh 353 6.2.8)", "Revisor, ciega, NCh 353"),
        ("3.2", "Sin descontar vanos y con alambre de 4.2 mm (EETT: 4 mm)", "Revisor"),
        ("3.6", "Faltaban fondos bajo dinteles y tapas de extremos", "Revisor"),
        ("8.1", "Se tomó la cota del alero como largo de bajada", "Revisor"),
        ("3.1", "Vanos descontados al 100\\,\\%; NCh 353 no descuenta los menores a \\SI{1.5}{m^2}", "NCh 353, revisor"),
        ("3.5", "Sin traslapos de 40\\,$d$ ni +5\\,\\% de patas", "NCh 353, revisor")]
fc = [f"{it} & {pp[it][1]} & \\num{{{v3[it]:.2f}}} & \\num{{{v[it]:.2f}}} & {m} & {q}\\\\" for it, m, q in corr]
T3 = r"""\begin{table}
\centering\small
\begin{tabularx}{\linewidth}{lp{2.9cm}S[table-format=3.2]S[table-format=3.2]Xp{2.3cm}}
\toprule
Ítem & Partida & {Antes} & {Ahora} & Motivo & Detectado por\\
\midrule
""" + "\n".join(fc) + r"""
\bottomrule
\end{tabularx}
\caption{Correcciones a la cubicación propia tras la revisión en frío y la lectura de NCh 353.}
\label{tab:corr}
\end{table}
"""
open("tabla_corr.tex", "w").write(T3)

sob = (186.5 - v["3.2"]) * pp["3.2"][5]
fal = -((1.28 - v["3.4"]) * pp["3.4"][5] + (93 - v["3.5"]) * pp["3.5"][5])
vals = dict(vLeje=f"{L:.2f}", vDentro=str(dentro), vTotal=str(len(items)), vSob=f"{sob/1e3:.0f}", vFal=f"{fal/1e3:.0f}",
            vLad=f"{v['3.1']:.2f}", vLadPilar=f"{L*Hl-k.desc353(1):.2f}", vFcad=f"{v['3.5']:.1f}", vTens=f"{v['3.3']:.1f}",
            vEsc=f"{v['3.2']:.1f}", vEscKgm=f"{k.kg_esc_m:.3f}", vLesc=f"{k.L_esc:.1f}", vHcad=f"{v['3.4']:.2f}",
            vMcad=f"{v['3.6']:.2f}", vTecho=f"{v['5.5']:.2f}", vRell=f"{v['2.4']:.2f}")
open("valores.tex", "w").write("\n".join(f"\\newcommand{{\\{a}}}{{{b}}}" for a, b in vals.items()) + "\n")
print(vals)
