#!/usr/bin/env python3
"""Prueba T28: lógica del programador horario (sin lanzar la sincronización real)."""
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    tmp = tempfile.mkdtemp(prefix="t28_")
    os.environ["SYNC_PROGRAMADOR_ESTADO"] = os.path.join(tmp, "estado.json")
    import programador_sync as p
    p.ESTADO = os.environ["SYNC_PROGRAMADOR_ESTADO"]
    sab = datetime(2026, 10, 31, 10, 5)          # sábado 10:05
    vie = datetime(2026, 10, 30, 22, 0)          # viernes
    c = p.corresponde
    casos = [
        ("sin historial: corre", c(vie, None, None)),
        ("sábado 10:05, último ok el sábado anterior: corre", c(sab, sab - timedelta(days=7), sab - timedelta(days=7))),
        ("sábado 09:30: no corre aún", not c(sab.replace(hour=9, minute=30), sab - timedelta(days=7), sab - timedelta(days=7))),
        ("sábado, ya corrió hoy: no corre", not c(sab + timedelta(hours=3), sab, sab)),
        ("tablet apagada el sábado, lunes 8 días después: corre", c(sab + timedelta(days=2), sab - timedelta(days=7), sab - timedelta(days=7))),
        ("miércoles a 4 días del último ok: no corre", not c(sab + timedelta(days=4), sab, sab)),
        ("falló hace 2 h: espera", not c(sab + timedelta(hours=2), sab - timedelta(days=7), sab)),
        ("falló hace 7 h: reintenta", c(sab + timedelta(hours=7), sab - timedelta(days=7), sab)),
    ]
    llamadas = []
    rc1 = p.main(ahora=sab, lanzar=lambda: llamadas.append(1) or 1)          # falla
    rc2 = p.main(ahora=sab + timedelta(hours=1), lanzar=lambda: llamadas.append(2) or 0)   # dentro de la espera: no lanza
    rc3 = p.main(ahora=sab + timedelta(hours=7), lanzar=lambda: llamadas.append(3) or 0)   # reintento ok
    rc4 = p.main(ahora=sab + timedelta(hours=8), lanzar=lambda: llamadas.append(4) or 0)   # ya ok hoy
    casos.append(("secuencia falla→espera→reintento ok→no repite", llamadas == [1, 3] and (rc1, rc2, rc3, rc4) == (1, 0, 0, 0)))
    shutil.rmtree(tmp, ignore_errors=True)
    for t, ok in casos:
        print(f"  {t}: {ok}")
    ok = all(v for _, v in casos)
    print(f"Resultado T28: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
