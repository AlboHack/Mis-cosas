"""cubicar_dxf.py - Extrae cantidades de un DXF por capa: longitudes, áreas y conteo de bloques.

Uso:
    python cubicar_dxf.py plano.dxf --unidad mm --salida cantidades.csv

--unidad es la unidad en que está DIBUJADO el plano (mm, cm o m). La salida siempre va en m y m2.
El script mide geometría; no interpreta el plano. Cada cantidad debe revisarse contra una medición
manual de control antes de entregarse (ver hoja Control de la plantilla).

Requiere: pip install ezdxf
"""
from __future__ import annotations
import argparse, csv, math, sys
from collections import defaultdict
import ezdxf
from ezdxf import path as ezpath

FACTOR = {"mm": 0.001, "cm": 0.01, "m": 1.0}
INSUNITS = {4: "mm", 5: "cm", 6: "m"}          # códigos $INSUNITS del DXF
LINEALES = {"LINE", "ARC", "CIRCLE", "LWPOLYLINE", "POLYLINE", "ELLIPSE", "SPLINE"}


def _puntos(entidad, flecha, segmentos=16):
    """Vértices de la entidad aproximada por cuerdas con flecha máxima `flecha` (unidades de dibujo)."""
    p = ezpath.make_path(entidad)
    return [(v.x, v.y) for v in p.flattening(flecha, segments=segmentos)]


def _largo(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def _area(pts):
    """Fórmula del polígono (shoelace); cierra el contorno si no viene cerrado."""
    if pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:]))) / 2


def _poli(vertices, cerrada):
    """Largo y área exactos de una polilínea con arcos (bulge). vertices = [(x, y, bulge)]."""
    n = len(vertices)
    tramos = n if cerrada else n - 1
    largo = area2 = 0.0
    for i in range(tramos):
        x1, y1, b = vertices[i]
        x2, y2, _ = vertices[(i + 1) % n]
        c = math.hypot(x2 - x1, y2 - y1)
        area2 += x1 * y2 - x2 * y1                       # shoelace sobre las cuerdas
        if b == 0 or c == 0:
            largo += c
        else:
            ang = 4 * math.atan(b)                        # ángulo central con signo
            r = c / (2 * math.sin(abs(ang) / 2))
            largo += r * abs(ang)
            area2 += math.copysign(r * r * (abs(ang) - math.sin(abs(ang))), b)   # segmento circular
    return largo, (abs(area2) / 2 if cerrada else 0.0)


def medir(e, flecha_rel=1e-6):
    """(largo, área, cerrada) en unidades de dibujo. Exacto para líneas, arcos, círculos y polilíneas;
    elipses y splines se aproximan por cuerdas."""
    t = e.dxftype()
    if t == "LINE":
        a, b = e.dxf.start, e.dxf.end
        return math.hypot(b.x - a.x, b.y - a.y), 0.0, False
    if t == "CIRCLE":
        r = e.dxf.radius
        return 2 * math.pi * r, math.pi * r * r, True
    if t == "ARC":
        ang = (e.dxf.end_angle - e.dxf.start_angle) % 360 or 360
        return e.dxf.radius * math.radians(ang), 0.0, False
    if t == "LWPOLYLINE":
        v = [(x, y, b) for x, y, b in e.get_points("xyb")]
        return (*_poli(v, bool(e.is_closed)), bool(e.is_closed))
    if t == "POLYLINE" and e.is_2d_polyline:
        v = [(p.dxf.location.x, p.dxf.location.y, p.dxf.get("bulge", 0.0)) for p in e.vertices]
        return (*_poli(v, bool(e.is_closed)), bool(e.is_closed))
    g = _puntos(e, 1e9)                                    # resto: aproximación por cuerdas
    diag = math.dist((min(p[0] for p in g), min(p[1] for p in g)), (max(p[0] for p in g), max(p[1] for p in g)))
    pts = _puntos(e, max(diag, 1e-12) * flecha_rel)
    cerrada = bool(getattr(e, "closed", False)) or (t == "ELLIPSE" and abs(e.dxf.end_param - e.dxf.start_param) >= 2 * math.pi - 1e-9)
    return _largo(pts), (_area(pts) if cerrada else 0.0), cerrada


def extraer(ruta, unidad=None):
    """Devuelve (capas, bloques, avisos).
    capas[capa] = {"largo_m", "area_m2", "n_lineales", "n_cerradas"}; bloques[(capa, nombre)] = cantidad."""
    doc = ezdxf.readfile(ruta)
    msp = doc.modelspace()
    avisos = []
    declarada = INSUNITS.get(doc.header.get("$INSUNITS", 0))
    if unidad is None:
        if declarada is None:
            raise ValueError("El DXF no declara unidades ($INSUNITS). Indique --unidad mm, cm o m.")
        unidad = declarada
    elif declarada and declarada != unidad:
        avisos.append(f"El DXF declara {declarada} y se pidió {unidad}: confirme la escala midiendo una cota conocida.")
    f = FACTOR[unidad]

    capas = defaultdict(lambda: dict(largo_m=0.0, area_m2=0.0, n_lineales=0, n_cerradas=0))
    bloques = defaultdict(int)
    otros = defaultdict(int)
    for e in msp:
        t, capa = e.dxftype(), e.dxf.layer
        if t == "INSERT":
            bloques[(capa, e.dxf.name)] += 1
            continue
        if t not in LINEALES:
            otros[t] += 1
            continue
        try:
            largo, area, cerrada = medir(e)
        except Exception as err:
            avisos.append(f"No se pudo medir {t} en capa {capa}: {err}")
            continue
        c = capas[capa]
        c["largo_m"] += largo * f
        c["n_lineales"] += 1
        if cerrada:
            c["area_m2"] += area * f * f
            c["n_cerradas"] += 1

    if bloques:
        avisos.append("Los bloques se cuentan, pero la geometría dentro de ellos NO se mide. "
                      "Si el plano viene dentro de bloques, descompóngalos (EXPLODE) antes de exportar.")
    for t, n in sorted(otros.items()):
        if t == "HATCH":
            avisos.append(f"{n} sombreados (HATCH) no medidos: el área se toma solo de polilíneas cerradas y círculos.")
    for capa, c in capas.items():
        abiertas = c["n_lineales"] - c["n_cerradas"]
        if c["n_cerradas"] and abiertas:
            avisos.append(f"Capa {capa}: {abiertas} elementos abiertos junto a {c['n_cerradas']} cerrados; "
                          "el área solo considera los cerrados.")
    return dict(capas), dict(bloques), avisos


def escribir_csv(ruta, capas, bloques):
    with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["tipo", "capa", "bloque", "largo_m", "area_m2", "cantidad", "elementos", "cerrados"])
        for capa in sorted(capas):
            c = capas[capa]
            w.writerow(["capa", capa, "", f"{c['largo_m']:.4f}", f"{c['area_m2']:.4f}", "", c["n_lineales"], c["n_cerradas"]])
        for (capa, nombre) in sorted(bloques):
            w.writerow(["bloque", capa, nombre, "", "", bloques[(capa, nombre)], "", ""])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Cantidades por capa desde un DXF.")
    ap.add_argument("dxf")
    ap.add_argument("--unidad", choices=list(FACTOR), help="unidad de dibujo; si se omite se lee del DXF")
    ap.add_argument("--salida", default="cantidades.csv")
    a = ap.parse_args(argv)
    capas, bloques, avisos = extraer(a.dxf, a.unidad)
    escribir_csv(a.salida, capas, bloques)
    print(f"{'capa':28s}{'largo [m]':>12s}{'área [m2]':>12s}{'elem.':>7s}{'cerr.':>7s}")
    for capa in sorted(capas):
        c = capas[capa]
        print(f"{capa:28s}{c['largo_m']:12.3f}{c['area_m2']:12.3f}{c['n_lineales']:7d}{c['n_cerradas']:7d}")
    for (capa, nombre), n in sorted(bloques.items()):
        print(f"bloque {nombre} en {capa}: {n}")
    for av in avisos:
        print("AVISO:", av)
    print("Salida:", a.salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
