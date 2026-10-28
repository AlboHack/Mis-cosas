#!/usr/bin/env python3
"""Escenarios de venta de una parte de un ETF: vender hoy, escalonado o al final del horizonte.

Monte Carlo con t de Student (df=4, colas gruesas) escalada a la volatilidad anual dada
(VIX/100 para el S&P 500, o la volatilidad realizada) y verificación con la fórmula lognormal.
Los montos se pasan por argumento: no se guardan en el repo.

Uso: python3 mercado/escenario.py --monto 200 --dias 20 --vol 0.175 [--deriva 0.07] [--tramos 2]
"""
import argparse
from math import erf, exp, log, sqrt

import numpy as np


def normal_cdf(z):
    return 0.5 * (1 + erf(z / sqrt(2)))


def simular(monto, dias, vol, deriva, tramos=1, n=400_000, df=4, semilla=7):
    """Valor final de vender `monto` repartido en `tramos` iguales a lo largo de `dias` (el primero hoy si tramos>1)."""
    rng = np.random.default_rng(semilla)
    sd = vol / sqrt(252)
    t = rng.standard_t(df, size=(n, dias)) * sd / sqrt(df / (df - 2))
    acum = np.cumsum(t + (deriva / 252 - 0.5 * sd ** 2), axis=1)
    if tramos == 1:
        return monto * np.exp(acum[:, -1])
    fechas = np.linspace(0, dias, tramos).round().astype(int)
    total = np.zeros(n)
    for d in fechas:
        total += (monto / tramos) * (1.0 if d == 0 else np.exp(acum[:, d - 1]))
    return total


def resumen(v, monto):
    q = np.percentile(v, [5, 50, 95])
    return {"media": v.mean(), "p5": q[0], "p50": q[1], "p95": q[2], "desv": v.std(),
            "p_perdida": float((v < monto).mean()), "p_m5": float((v < 0.95 * monto).mean()),
            "p_m10": float((v < 0.90 * monto).mean())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--monto", type=float, required=True)
    ap.add_argument("--dias", type=int, required=True, help="días hábiles hasta la última venta")
    ap.add_argument("--vol", type=float, required=True, help="volatilidad anual (VIX/100 para S&P 500)")
    ap.add_argument("--deriva", type=float, default=0.07, help="retorno anual esperado [supuesto]")
    ap.add_argument("--tramos", type=int, default=2)
    a = ap.parse_args()

    s = a.vol * sqrt(a.dias / 252)
    m = (a.deriva - 0.5 * a.vol ** 2) * a.dias / 252
    print(f"Monto {a.monto:.2f} | horizonte {a.dias} días hábiles | vol {a.vol:.1%} | deriva {a.deriva:.1%}")
    print("| Estrategia | Media | P5 | Mediana | P95 | Desv. | P(pérdida) | P(<−5%) | P(<−10%) |")
    print("|---|---|---|---|---|---|---|---|---|")
    print(f"| Todo hoy | {a.monto:.2f} | {a.monto:.2f} | {a.monto:.2f} | {a.monto:.2f} | 0.00 | 0% | 0% | 0% |")
    for nombre, tr in [(f"Escalonado en {a.tramos} tramos", a.tramos), ("Todo al final", 1)]:
        r = resumen(simular(a.monto, a.dias, a.vol, a.deriva, tr), a.monto)
        print(f"| {nombre} | {r['media']:.2f} | {r['p5']:.2f} | {r['p50']:.2f} | {r['p95']:.2f} | {r['desv']:.2f} | "
              f"{r['p_perdida']:.0%} | {r['p_m5']:.0%} | {r['p_m10']:.0%} |")
    print(f"Verificación lognormal (todo al final): P(pérdida) {normal_cdf(-m / s):.1%}, "
          f"P(<−5%) {normal_cdf((log(0.95) - m) / s):.1%}, P5 {a.monto * exp(m - 1.645 * s):.2f}, "
          f"P95 {a.monto * exp(m + 1.645 * s):.2f}")


if __name__ == "__main__":
    main()
