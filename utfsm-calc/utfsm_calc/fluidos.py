"""Fricción en tuberías. Colebrook por brentq y Swamee-Jain como contraste."""
import math
from scipy.optimize import brentq


def colebrook(Re, rel_rug):
    """Factor de Darcy f. Re > 4000. rel_rug = epsilon/D."""
    g = lambda f: 1 / math.sqrt(f) + 2 * math.log10(rel_rug / 3.7 + 2.51 / (Re * math.sqrt(f)))
    return brentq(g, 1e-4, 1.0)


def swamee_jain(Re, rel_rug):
    return 0.25 / math.log10(rel_rug / 3.7 + 5.74 / Re**0.9) ** 2


def friccion(Re, rel_rug):
    """Laminar (64/Re) o Colebrook; avisa en transición 2300 < Re < 4000."""
    if Re < 2300:
        return 64 / Re
    if Re < 4000:
        raise ValueError(f"Re = {Re:.0f} en transición: no hay f único. Cotas: laminar "
                         f"{64 / Re:.4f}, Colebrook {colebrook(Re, rel_rug):.4f}. Elegir y justificar.")
    return colebrook(Re, rel_rug)
