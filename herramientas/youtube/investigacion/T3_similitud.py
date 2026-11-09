"""T3: compara dos formas de medir parecido entre el handout de la clase y cada video.

(a) cobertura: fracción de términos del handout que aparecen en la transcripción (como hoy).
(b) rareza: cada término pesa idf = ln(N/df) entre los videos de la corrida; el video suma
    idf * ln(1 + menciones) y se divide por la suma de idf. Premia los términos propios de la
    clase (no inercial, velocidad relativa) sobre los que dice cualquier video (control volume).

Uso: python T3_similitud.py ejemplo.json
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import buscar_videos as bv  # noqa: E402

# Términos del handout CIV244 Clase 19 (Soto, 2026-11-06), con alias hablados en inglés y español.
TERMINOS = bv.parsear_claves(
    "reynolds transport|transporte de reynolds|ttr|rtt,"
    "angular momentum|momento angular|momentum angular|cantidad de movimiento angular|moment of momentum,"
    "r cross|r times v|r times u|producto cruz|producto vectorial,"
    "control volume|volumen de control,"
    "control surface|superficie de control,"
    "sprinkler|aspersor|regador,"
    "nozzle|boquilla|tobera,"
    "relative velocity|velocidad relativa,"
    "angular velocity|velocidad angular|omega,"
    "torque|momento torsor|momento externo|applied moment,"
    "flow rate|caudal|mass flow|flujo masico,"
    "non inertial|noninertial|no inercial|rotating control volume|rotating frame,"
    "second law|segunda ley,"
    "vortex|vortice|torbellino|swirl"
)


def puntajes(videos):
    hall = {v["id"]: bv.buscar_en_transcripcion(v["transcripcion"], TERMINOS) if v["transcripcion"] else {}
            for v in videos}
    n = len(videos)
    df = {t[0]: sum(1 for h in hall.values() if t[0] in h) for t in TERMINOS}
    idf = {t: math.log(n / df[t]) if df[t] else 0.0 for t in df}
    filas = []
    for v in videos:
        h = hall[v["id"]]
        a = len(h) / len(TERMINOS)
        b = sum(idf[t] * math.log1p(h[t]["veces"]) for t in h) / (sum(idf.values()) or 1)
        filas.append((v, a, b, h))
    return filas, df


if __name__ == "__main__":
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    filas, df = puntajes(d["videos"])
    print("df por término:", df)
    for nombre, k in (("(a) cobertura", 1), ("(b) rareza", 2)):
        print(f"\n{nombre}")
        for v, a, b, h in sorted(filas, key=lambda f: -f[k])[:10]:
            print(f"  {a:.2f} {b:.2f}  {v['canal'][:22]:22} {v['titulo'][:55]}")
