"""Genera vivienda_ejemplo.dxf (dibujado en mm) con cantidades conocidas."""
import ezdxf
k = 1000.0
doc = ezdxf.new("R2010"); doc.header["$INSUNITS"] = 4
msp = doc.modelspace()
for capa, color in [("MUROS", 7), ("FUNDACIONES", 1), ("RADIER", 3), ("VANOS", 5), ("EJES", 8), ("TEXTOS", 2)]:
    doc.layers.add(capa, color=color)
def rect(capa, x1, y1, x2, y2):
    msp.add_lwpolyline([(x1*k, y1*k), (x2*k, y1*k), (x2*k, y2*k), (x1*k, y2*k)], close=True, dxfattribs={"layer": capa})
    return (x2 - x1) * (y2 - y1)
muros = [(0, 0, 9, .15), (0, 6.45, 9, 6.6), (0, .15, .15, 6.45), (8.85, .15, 9, 6.45), (4.5, .15, 4.65, 6.45), (4.65, 3.3, 8.85, 3.45)]
fund = [(-.175, -.175, 9.175, .325), (-.175, 6.275, 9.175, 6.775), (-.175, .325, .325, 6.275), (8.675, .325, 9.175, 6.275),
        (4.325, .325, 4.825, 6.275), (4.825, 3.125, 8.675, 3.625)]
radier = [(.15, .15, 4.5, 6.45), (4.65, .15, 8.85, 3.3), (4.65, 3.45, 8.85, 6.45)]
A = {c: sum(rect(c, *r) for r in rs) for c, rs in [("MUROS", muros), ("FUNDACIONES", fund), ("RADIER", radier)]}
p = doc.blocks.new("PUERTA_80"); p.add_line((0, 0), (800, 0)); p.add_arc((0, 0), 800, 0, 90)
v = doc.blocks.new("VENTANA_120"); v.add_lwpolyline([(0, 0), (1200, 0), (1200, 150), (0, 150)], close=True)
for x, y, r in [(2.0, 0.15, 0), (4.65, 1.0, 90), (4.65, 4.5, 90)]: msp.add_blockref("PUERTA_80", (x*k, y*k), dxfattribs={"layer": "VANOS", "rotation": r})
for x, y, r in [(1.5, 6.45, 0), (6.0, 6.45, 0), (6.0, 0, 0), (9.0, 1.0, 90)]: msp.add_blockref("VENTANA_120", (x*k, y*k), dxfattribs={"layer": "VANOS", "rotation": r})
for x in (0.075, 4.575, 8.925): msp.add_line((x*k, -1000), (x*k, 7600), dxfattribs={"layer": "EJES"})
for t, x, y in [("ESTAR-COMEDOR", 1.2, 3.2), ("DORMITORIO 1", 5.8, 1.6), ("DORMITORIO 2", 5.8, 4.8)]:
    msp.add_text(t, height=200, dxfattribs={"layer": "TEXTOS"}).set_placement((x*k, y*k))
doc.saveas("vivienda_ejemplo.dxf")
print({c: round(a, 4) for c, a in A.items()})
