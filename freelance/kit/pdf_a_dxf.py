"""pdf_a_dxf.py - Extrae la planta 1:50 del plano tipo Sede Social C (PDF vectorial) a DXF en metros.

Escala: la cota total de 12.85 m mide 186.465 unidades PDF -> k = 12.85 / 186.465 m/unidad.
Capas por grosor de trazo del PDF:
  0.216 -> MUROS_CORTE   (muros cortados)
  0.062 -> ELEMENTOS     (ventanas, tabiques, artefactos)
  0.031 -> COTAS_AUX     (líneas de cota y auxiliares)
  trazo segmentado -> EJES_PROYECCION
  resto -> OTROS
Origen: esquina exterior inferior izquierda del muro (x = 246.53, y = 83.14 en el PDF). Eje Y hacia arriba.
"""
import sys
import pymupdf as fitz
import ezdxf

PDF = sys.argv[1] if len(sys.argv) > 1 else "in/plano.pdf"
SALIDA = sys.argv[2] if len(sys.argv) > 2 else "sedeC_planta.dxf"
K = 12.85 / 186.465
X0, Y0 = 246.53, 83.14
REGION = fitz.Rect(200, -135, 370, 170)          # planta de distribución, unidades PDF

def capa(d):
    if d.get("dashes") and d["dashes"] not in ("[] 0", "[] 0.0"):
        return "EJES_PROYECCION"
    w = round(d.get("width") or 0, 3)
    return {0.216: "MUROS_CORTE", 0.062: "ELEMENTOS", 0.031: "COTAS_AUX"}.get(w, "OTROS")

T = lambda p: ((p.x - X0) * K, -(p.y - Y0) * K)

def main():
    pag = fitz.open(PDF)[0]
    doc = ezdxf.new("R2010"); doc.header["$INSUNITS"] = 6
    for n, c in [("MUROS_CORTE", 7), ("ELEMENTOS", 4), ("COTAS_AUX", 8), ("EJES_PROYECCION", 1), ("OTROS", 9), ("TEXTOS", 2)]:
        doc.layers.add(n, color=c)
    msp = doc.modelspace(); n = 0
    for d in pag.get_drawings():
        if not REGION.contains(d["rect"]):
            continue
        ly = capa(d)
        for it in d["items"]:
            if it[0] == "l":
                msp.add_line(T(it[1]), T(it[2]), dxfattribs={"layer": ly}); n += 1
            elif it[0] == "c":                    # Bézier cúbica -> 8 cuerdas
                p0, p1, p2, p3 = it[1:5]
                pts = []
                for i in range(9):
                    t = i / 8; u = 1 - t
                    pts.append(fitz.Point(u**3*p0.x + 3*u*u*t*p1.x + 3*u*t*t*p2.x + t**3*p3.x,
                                          u**3*p0.y + 3*u*u*t*p1.y + 3*u*t*t*p2.y + t**3*p3.y))
                msp.add_lwpolyline([T(p) for p in pts], dxfattribs={"layer": ly}); n += 1
            elif it[0] == "re":
                r = it[1]
                msp.add_lwpolyline([T(r.tl), T(r.tr), T(r.br), T(r.bl)], close=True, dxfattribs={"layer": ly}); n += 1
            elif it[0] == "qu":
                q = it[1]
                msp.add_lwpolyline([T(q.ul), T(q.ur), T(q.lr), T(q.ll)], close=True, dxfattribs={"layer": ly}); n += 1
    for w in pag.get_text("words"):
        r = fitz.Rect(w[:4])
        if REGION.contains(r):
            msp.add_text(w[4], height=0.12, dxfattribs={"layer": "TEXTOS"}).set_placement(T(fitz.Point(r.x0, r.y1)))
    doc.saveas(SALIDA)
    print(f"{n} entidades -> {SALIDA} (k = {K:.6f} m por unidad PDF)")

if __name__ == "__main__":
    main()
