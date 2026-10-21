import math, pytest
from utfsm_calc.estructuras import portico, portico_pynite, comparar_portico
from utfsm_calc.fluidos import colebrook, swamee_jain, friccion
from utfsm_calc.gestion import cpm, vpi
from utfsm_calc.laboratorio import ajuste_lineal, propagar
from utfsm_calc.latex import tabla_comparacion, pendientes

E, A, I = 2.1e7, 0.01, 1e-4

def test_voladizo_cerrado():
    U, R = portico({'A': (0, 0), 'B': (4, 0)}, [dict(i='A', j='B', E=E, A=A, I=I)],
                   {'A': [0, 1, 2]}, {'B': (0, -10, 0)})
    assert U['B'][1] == pytest.approx(-10 * 4**3 / (3 * E * I), rel=1e-12)
    assert R['A'][1] == pytest.approx(10)

def test_viga_q_cerrado():
    # biempotrada con q hacia abajo: w_centro = q L^4 / 384 EI
    n = {'A': (0, 0), 'C': (3, 0), 'B': (6, 0)}
    el = [dict(i='A', j='C', E=E, A=A, I=I, q=-2), dict(i='C', j='B', E=E, A=A, I=I, q=-2)]
    U, _ = portico(n, el, {'A': [0, 1, 2], 'B': [0, 1, 2]}, {})
    assert U['C'][1] == pytest.approx(-2 * 6**4 / (384 * E * I), rel=1e-10)
    U2, _ = portico_pynite(n, el, {'A': [0, 1, 2], 'B': [0, 1, 2]}, {})
    assert U2['C'][1] == pytest.approx(U['C'][1], rel=1e-6)

def test_portico_rotula_resorte():
    n = {'A': (0, 0), 'B': (0, 3), 'C': (5, 3), 'D': (5, 0)}
    el = [dict(i='A', j='B', E=2e7, A=0.02, I=2e-4),
          dict(i='B', j='C', E=2e7, A=0.02, I=2e-4, q=-2, hinge_end='j'),
          dict(i='D', j='C', E=2e7, A=0.02, I=2e-4)]
    assert comparar_portico(n, el, {'A': [0, 1, 2], 'D': [1]}, {'B': (4, 0, 0)}, {('D', 0): 500}) < 1e-4

def test_fluidos():
    assert colebrook(1e5, 1e-4) == pytest.approx(0.018514, rel=1e-4)
    assert swamee_jain(1e5, 1e-4) == pytest.approx(colebrook(1e5, 1e-4), rel=0.02)
    assert friccion(1000, 0.001) == pytest.approx(0.064)
    with pytest.raises(ValueError):
        friccion(2490, 0.001)

def test_cpm_vpi():
    t, ruta, T = cpm({'A': (3, []), 'B': (2, ['A']), 'C': (4, ['A']), 'D': (1, ['B', 'C'])})
    assert T == 8 and ruta == ['A', 'C', 'D'] and t['B']['H'] == 2
    assert vpi([100, 100], 0.1) == pytest.approx(100 / 1.1 + 100 / 1.21)

def test_laboratorio():
    r = ajuste_lineal([0, 1, 2, 3], [1, 3, 5, 7])
    assert r['m'] == pytest.approx(2) and r['R2'] == pytest.approx(1)
    v, u, _ = propagar('a*b', {'a': 2, 'b': 3}, {'a': 0.1, 'b': 0.1})
    assert v == 6 and u == pytest.approx(math.sqrt(0.3**2 + 0.2**2))

def test_latex(tmp_path):
    s = tabla_comparacion([('U3', 0.0, 1e-9), ('R', 3.0, 3.03)])
    assert '{---}' in s and '1.000' in s
    f = tmp_path / 'x.tex'; f.write_text('a \\pend b\n\\completar{falta R2}\n')
    assert pendientes(f) == [(1, 'pend', 'a \\pend b'), (2, 'completar', 'falta R2')]
