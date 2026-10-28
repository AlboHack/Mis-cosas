#!/usr/bin/env python3
"""Análisis de riesgo y tendencia de ETFs a partir de mercado/datos/<TICKER>.csv (formato Stooq).

Todo es estadística descriptiva del pasado más distribuciones empíricas de retornos: sirve para
medir riesgo y comparar, NO para predecir el precio de un día concreto.

Uso:  python3 mercado/analizar.py [--horizonte 20] [--rf 0.04] [--salida mercado/informe.md]
"""
import argparse
import csv
import glob
import os
from datetime import date

import numpy as np

DIAS_ANIO = 252


def leer(ruta):
    fechas, cierres = [], []
    with open(ruta, newline="") as f:
        for fila in csv.DictReader(f):
            try:
                c = float(fila["Close"])
            except (KeyError, ValueError):
                continue
            if c > 0:
                fechas.append(date.fromisoformat(fila["Date"]))
                cierres.append(c)
    orden = np.argsort(fechas)
    return [fechas[i] for i in orden], np.array(cierres)[orden]


def retorno(p, dias):
    return p[-1] / p[-1 - dias] - 1 if len(p) > dias else np.nan


def cagr(p, anios):
    d = int(anios * DIAS_ANIO)
    return (p[-1] / p[-1 - d]) ** (1 / anios) - 1 if len(p) > d else np.nan


def max_drawdown(p):
    pico = np.maximum.accumulate(p)
    return float((p / pico - 1).min())


def metricas(f, p, horizonte, rf):
    r = np.diff(np.log(p))
    r1 = r[-DIAS_ANIO:]
    vol = r1.std(ddof=1) * np.sqrt(DIAS_ANIO)
    baja = r1[r1 < 0].std(ddof=1) * np.sqrt(DIAS_ANIO) if (r1 < 0).sum() > 2 else np.nan
    c1 = retorno(p, DIAS_ANIO)
    m50 = p[-50:].mean() if len(p) >= 50 else np.nan
    m200 = p[-200:].mean() if len(p) >= 200 else np.nan
    # distribución empírica de retornos a 'horizonte' días (ventanas solapadas, últimos 5 años)
    p5 = p[-(5 * DIAS_ANIO + horizonte):]
    rh = p5[horizonte:] / p5[:-horizonte] - 1
    var95 = np.percentile(rh, 5)
    cvar95 = rh[rh <= var95].mean()
    out = {
        "ultimo": p[-1], "fecha": f[-1],
        "r1m": retorno(p, 21), "r3m": retorno(p, 63), "r6m": retorno(p, 126), "r12m": c1,
        "cagr3": cagr(p, 3), "cagr5": cagr(p, 5),
        "vol": vol, "vol_baja": baja,
        "sharpe": (c1 - rf) / vol if vol > 0 else np.nan,
        "sortino": (c1 - rf) / baja if baja and baja > 0 else np.nan,
        "mdd5": max_drawdown(p[-5 * DIAS_ANIO:]), "dd_actual": p[-1] / p[-DIAS_ANIO:].max() - 1,
        "sobre_m50": p[-1] > m50, "sobre_m200": p[-1] > m200, "m50_sobre_m200": m50 > m200,
        "h_p_neg": float((rh < 0).mean()), "h_p_m5": float((rh < -0.05).mean()), "h_p_m10": float((rh < -0.10).mean()),
        "h_p5": float(np.percentile(rh, 5)), "h_p50": float(np.median(rh)), "h_p95": float(np.percentile(rh, 95)),
        "var95": float(var95), "cvar95": float(cvar95), "n_ventanas": len(rh),
    }
    # tendencia: 0–4 puntos (precio>MM50, precio>MM200, MM50>MM200, retorno 6m > 0)
    out["tendencia"] = int(out["sobre_m50"]) + int(out["sobre_m200"]) + int(out["m50_sobre_m200"]) + int(out["r6m"] > 0)
    return out


def pct(x, d=1):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x * 100:.{d}f}%"


def alinear_retornos(datos, a, b):
    fa, pa = datos[a]
    fb, pb = datos[b]
    comunes = sorted(set(fa) & set(fb))[-(DIAS_ANIO + 1):]
    ia = {d: i for i, d in enumerate(fa)}
    ib = {d: i for i, d in enumerate(fb)}
    xa = np.array([pa[ia[d]] for d in comunes])
    xb = np.array([pb[ib[d]] for d in comunes])
    return np.diff(np.log(xa)), np.diff(np.log(xb))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos"))
    ap.add_argument("--horizonte", type=int, default=20, help="días hábiles hasta la venta")
    ap.add_argument("--rf", type=float, default=0.04, help="tasa libre de riesgo anual [supuesto]")
    ap.add_argument("--salida", default=None)
    a = ap.parse_args()

    datos = {}
    for ruta in sorted(glob.glob(os.path.join(a.datos, "*.csv"))):
        f, p = leer(ruta)
        if len(p) > DIAS_ANIO + a.horizonte:
            datos[os.path.basename(ruta)[:-4]] = (f, p)
    if "VOO" not in datos:
        raise SystemExit("Falta mercado/datos/VOO.csv (referencia).")

    res = {}
    for t in datos:
        m = metricas(*datos[t], a.horizonte, a.rf)
        if t == "VOO":
            m["corr_voo"], m["beta_voo"] = 1.0, 1.0
        else:
            ra, rb = alinear_retornos(datos, t, "VOO")
            m["corr_voo"] = float(np.corrcoef(ra, rb)[0, 1])
            m["beta_voo"] = float(np.cov(ra, rb)[0, 1] / np.var(rb, ddof=1))
        res[t] = m

    L = [f"# Informe de ETFs — datos al {max(m['fecha'] for m in res.values())}", "",
         f"Horizonte de riesgo: {a.horizonte} días hábiles. Tasa libre de riesgo supuesta: {a.rf:.1%}. "
         "Estadística del pasado (5 años de ventanas solapadas); no es una predicción.", "",
         "## Rendimiento y riesgo (últimos 12 meses salvo indicación)", "",
         "| ETF | Último | 1m | 3m | 6m | 12m | CAGR 3a | CAGR 5a | Vol | Sharpe | Sortino | Máx. caída 5a | Desde máx. 12m | Corr VOO | Beta VOO |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for t, m in sorted(res.items(), key=lambda kv: -kv[1]["sharpe"] if not np.isnan(kv[1]["sharpe"]) else 0):
        L.append(f"| {t} | {m['ultimo']:.2f} | {pct(m['r1m'])} | {pct(m['r3m'])} | {pct(m['r6m'])} | {pct(m['r12m'])} | "
                 f"{pct(m['cagr3'])} | {pct(m['cagr5'])} | {pct(m['vol'])} | {m['sharpe']:.2f} | {m['sortino']:.2f} | "
                 f"{pct(m['mdd5'])} | {pct(m['dd_actual'])} | {m['corr_voo']:.2f} | {m['beta_voo']:.2f} |")
    L += ["", "## Tendencia (0–4: precio>MM50, precio>MM200, MM50>MM200, 6m>0)", "",
          "| ETF | Puntaje | >MM50 | >MM200 | MM50>MM200 | 6m |", "|---|---|---|---|---|---|"]
    for t, m in sorted(res.items(), key=lambda kv: (-kv[1]["tendencia"], -kv[1]["r6m"])):
        s = lambda b: "sí" if b else "no"
        L.append(f"| {t} | {m['tendencia']} | {s(m['sobre_m50'])} | {s(m['sobre_m200'])} | {s(m['m50_sobre_m200'])} | {pct(m['r6m'])} |")
    L += ["", f"## Distribución histórica del retorno a {a.horizonte} días (VaR/CVaR al 95%)", "",
          "| ETF | P(<0) | P(<−5%) | P(<−10%) | P5 | Mediana | P95 | VaR95 | CVaR95 | Ventanas |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for t, m in sorted(res.items(), key=lambda kv: kv[1]["cvar95"], reverse=True):
        L.append(f"| {t} | {pct(m['h_p_neg'], 0)} | {pct(m['h_p_m5'], 0)} | {pct(m['h_p_m10'], 0)} | {pct(m['h_p5'])} | "
                 f"{pct(m['h_p50'])} | {pct(m['h_p95'])} | {pct(m['var95'])} | {pct(m['cvar95'])} | {m['n_ventanas']} |")
    texto = "\n".join(L) + "\n"
    if a.salida:
        with open(a.salida, "w", encoding="utf-8") as f:
            f.write(texto)
    print(texto)


if __name__ == "__main__":
    main()
