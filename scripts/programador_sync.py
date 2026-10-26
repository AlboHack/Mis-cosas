#!/usr/bin/env python3
"""Decide cada hora si corresponde correr la sincronización semanal y, si corresponde, la lanza.

Lo invoca cron (cronie) cada hora. Corre scripts/sincronizar_sabados.sh cuando:
  - nunca hubo una corrida exitosa, o
  - la última exitosa tiene 7 días o más, o
  - es sábado desde las 10:00 y la última exitosa no fue hoy.
Así, si la tablet estuvo apagada o HyperOS mató crond el sábado, la corrida se recupera en
cuanto crond vuelve a estar activo.

Tras un intento fallido (sin token, sin WiFi, corte de seguridad) espera REINTENTO_H horas
antes de volver a intentar, para no golpear Aula ni llenar el log cada hora.

Estado en ~/.sync_programador.json (fuera del repo): {"ultimo_ok": iso, "ultimo_intento": iso}.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

ESTADO = os.environ.get("SYNC_PROGRAMADOR_ESTADO", os.path.expanduser("~/.sync_programador.json"))
LANZADOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sincronizar_sabados.sh")
REINTENTO_H = 6
DIA_SEMANA = 5   # sábado (lunes = 0)
HORA = 10


def _leer(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            d = json.load(f)
        return {k: datetime.fromisoformat(v) for k, v in d.items() if v}
    except Exception:
        return {}


def _escribir(ruta, estado):
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({k: v.isoformat(timespec="seconds") for k, v in estado.items()}, f)
    os.replace(tmp, ruta)


def corresponde(ahora, ultimo_ok, ultimo_intento):
    """True si hay que lanzar la sincronización ahora."""
    if ultimo_intento and not (ultimo_ok and ultimo_ok >= ultimo_intento):
        if ahora - ultimo_intento < timedelta(hours=REINTENTO_H):
            return False
    if ultimo_ok is None:
        return True
    if ahora - ultimo_ok >= timedelta(days=7):
        return True
    return ahora.weekday() == DIA_SEMANA and ahora.hour >= HORA and ultimo_ok.date() < ahora.date()


def main(ahora=None, lanzar=None):
    ahora = ahora or datetime.now()
    estado = _leer(ESTADO)
    if not corresponde(ahora, estado.get("ultimo_ok"), estado.get("ultimo_intento")):
        return 0
    estado["ultimo_intento"] = ahora
    _escribir(ESTADO, estado)
    rc = (lanzar or (lambda: subprocess.run(["sh", LANZADOR]).returncode))()
    if rc == 0:
        estado["ultimo_ok"] = ahora
        _escribir(ESTADO, estado)
    return rc


if __name__ == "__main__":
    sys.exit(main())
