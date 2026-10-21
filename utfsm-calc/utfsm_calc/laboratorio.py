"""Ajustes e incertidumbre para datos de ensayo."""
import numpy as np
from scipy import stats
import sympy as sp


def ajuste_lineal(x, y, conf=0.95):
    """y = m x + b. Devuelve dict con m, b, R2, errores estándar e IC de m y b."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    r = stats.linregress(x, y)
    t = stats.t.ppf((1 + conf) / 2, len(x) - 2)
    return dict(m=r.slope, b=r.intercept, R2=r.rvalue**2, se_m=r.stderr, se_b=r.intercept_stderr,
                IC_m=(r.slope - t * r.stderr, r.slope + t * r.stderr),
                IC_b=(r.intercept - t * r.intercept_stderr, r.intercept + t * r.intercept_stderr))


def propagar(expr, valores, incert):
    """Propagación lineal. expr: texto SymPy ('P/(b*h)'); valores e incert: dict por símbolo.
    Devuelve (valor, incertidumbre, contribuciones por variable)."""
    f = sp.sympify(expr)
    subs = {sp.Symbol(k): v for k, v in valores.items()}
    contrib = {k: float(sp.diff(f, sp.Symbol(k)).subs(subs)) * incert[k] for k in incert}
    return float(f.subs(subs)), float(np.sqrt(sum(c**2 for c in contrib.values()))), contrib
