"""Pruebas de cubicar_dxf.py contra valores analíticos (segundo método independiente).
Ejecutar: python -m pytest -q"""
import math
import ezdxf
import pytest
from cubicar_dxf import extraer, main

TOL = 1e-9   # tolerancia relativa: la geometría de líneas, arcos y polilíneas es exacta


def plano(ruta, k=1.0, insunits=6):
    """Plano de prueba con geometría de resultado conocido. k escala las coordenadas (k=1000 -> mm)."""
    doc = ezdxf.new("R2010"); doc.header["$INSUNITS"] = insunits
    msp = doc.modelspace()
    P = lambda *pts: [(x * k, y * k) for x, y in pts]
    # losa rectangular 6 x 4 m: perímetro 20, área 24
    msp.add_lwpolyline(P((0, 0), (6, 0), (6, 4), (0, 4)), close=True, dxfattribs={"layer": "LOSA"})
    # pilar circular r = 0.5 m: perímetro pi, área pi/4
    msp.add_circle((10 * k, 0), 0.5 * k, dxfattribs={"layer": "PILAR_CIRC"})
    # línea 3-4-5: largo 5
    msp.add_line((0, 10 * k), (3 * k, 14 * k), dxfattribs={"layer": "EJES"})
    # arco r = 2 m, 90 grados: largo pi
    msp.add_arc((20 * k, 0), 2 * k, 0, 90, dxfattribs={"layer": "ARCOS"})
    # semicírculo cerrado de diámetro 2 m (bulge = 1): perímetro pi + 2, área pi/2
    msp.add_lwpolyline([(30 * k, 0, 0, 0, 1), (32 * k, 0, 0, 0, 0)], format="xyseb", close=True,
                       dxfattribs={"layer": "SEMI"})
    # polilínea abierta en L de 2 + 3 m: largo 5, sin área
    msp.add_lwpolyline(P((40, 0), (42, 0), (42, 3)), dxfattribs={"layer": "ABIERTA"})
    # 4 bloques
    doc.blocks.new("PILAR").add_circle((0, 0), 0.2 * k)
    for i in range(4):
        msp.add_blockref("PILAR", (50 * k + i * k, 0), dxfattribs={"layer": "PILARES"})
    doc.saveas(ruta)
    return ruta


ESPERADO = {  # capa: (largo m, área m2)
    "LOSA": (20.0, 24.0),
    "PILAR_CIRC": (math.pi, math.pi / 4),
    "EJES": (5.0, 0.0),
    "ARCOS": (math.pi, 0.0),
    "SEMI": (math.pi + 2, math.pi / 2),
    "ABIERTA": (5.0, 0.0),
}


@pytest.mark.parametrize("k,unidad,ins", [(1.0, "m", 6), (1000.0, "mm", 4), (100.0, "cm", 5)])
def test_cantidades_contra_analitico(tmp_path, k, unidad, ins):
    capas, bloques, _ = extraer(plano(tmp_path / "p.dxf", k, ins), unidad)
    for capa, (largo, area) in ESPERADO.items():
        assert capas[capa]["largo_m"] == pytest.approx(largo, rel=TOL), capa
        assert capas[capa]["area_m2"] == pytest.approx(area, rel=TOL, abs=1e-9), capa
    assert bloques[("PILARES", "PILAR")] == 4


def test_unidad_se_lee_del_dxf(tmp_path):
    capas, _, _ = extraer(plano(tmp_path / "p.dxf", 1000.0, 4))
    assert capas["LOSA"]["area_m2"] == pytest.approx(24.0, rel=TOL)


def test_error_de_escala_se_avisa(tmp_path):
    """Plano en mm leído como m: el script debe avisar; el área sale 1e6 veces mayor."""
    capas, _, avisos = extraer(plano(tmp_path / "p.dxf", 1000.0, 4), "m")
    assert any("declara mm" in a for a in avisos)
    assert capas["LOSA"]["area_m2"] == pytest.approx(24.0e6, rel=TOL)


def test_sin_unidades_exige_declararlas(tmp_path):
    with pytest.raises(ValueError):
        extraer(plano(tmp_path / "p.dxf", 1.0, 0))


def test_aviso_de_bloques_y_csv(tmp_path):
    ruta = plano(tmp_path / "p.dxf")
    _, _, avisos = extraer(ruta, "m")
    assert any("bloques" in a.lower() for a in avisos)
    salida = tmp_path / "c.csv"
    assert main([str(ruta), "--unidad", "m", "--salida", str(salida)]) == 0
    texto = salida.read_text(encoding="utf-8-sig")
    assert "LOSA" in texto and "PILAR" in texto
