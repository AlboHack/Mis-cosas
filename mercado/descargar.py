#!/usr/bin/env python3
"""Descarga precios diarios de los ETF de tickers.txt a mercado/datos/<TICKER>.csv (formato Stooq:
Date,Open,High,Low,Close,Volume). Close = cierre ajustado por dividendos y splits cuando la fuente lo da.

Fuentes, en orden (si una falla o bloquea, se prueba la siguiente):
  1. Yahoo Finance chart API (JSON, ~5 años, con cierre ajustado)
  2. Nasdaq API histórica (JSON, cierre sin ajustar)
  3. Stooq CSV (puede exigir verificación anti-bots)
Solo biblioteca estándar (sirve en Termux sin instalar nada). Solo datos públicos de mercado.
"""
import csv
import io
import json
import os
import sys
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone

UA = {"User-Agent": "Mozilla/5.0 (Linux; Android 13; Xiaomi Pad 5) AppleWebKit/537.36 Chrome/120 Safari/537.36",
      "Accept": "application/json,text/csv,*/*"}
DIR = os.path.dirname(os.path.abspath(__file__))


def _get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_yahoo(texto):
    d = json.loads(texto)["chart"]["result"][0]
    ts = d["timestamp"]
    q = d["indicators"]["quote"][0]
    adj = (d["indicators"].get("adjclose") or [{}])[0].get("adjclose")
    filas = []
    for i, t in enumerate(ts):
        c = (adj or q["close"])[i]
        if c is None:
            continue
        dia = datetime.fromtimestamp(t, tz=timezone.utc).date().isoformat()
        filas.append((dia, q["open"][i] or c, q["high"][i] or c, q["low"][i] or c, c, q["volume"][i] or 0))
    return filas


def parse_nasdaq(texto):
    filas = []
    for r in json.loads(texto)["data"]["tradesTable"]["rows"]:
        num = lambda s: float(str(s).replace("$", "").replace(",", "")) if s not in (None, "", "N/A") else None
        c = num(r["close"])
        if c is None:
            continue
        dia = datetime.strptime(r["date"], "%m/%d/%Y").date().isoformat()
        filas.append((dia, num(r.get("open")) or c, num(r.get("high")) or c, num(r.get("low")) or c, c,
                      int(num(r.get("volume")) or 0)))
    return filas


def parse_stooq(texto):
    if not texto.startswith("Date,Open,High,Low,Close"):
        raise ValueError("Stooq no devolvió CSV (posible verificación anti-bots)")
    return [(f["Date"], f["Open"], f["High"], f["Low"], f["Close"], f.get("Volume", 0))
            for f in csv.DictReader(io.StringIO(texto))]


def fuentes(t):
    hoy = date.today()
    return [
        ("yahoo", f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=5y&interval=1d&events=div%7Csplit", parse_yahoo),
        ("nasdaq", f"https://api.nasdaq.com/api/quote/{t}/historical?assetclass=etf&fromdate={hoy - timedelta(days=5 * 366)}"
                   f"&todate={hoy}&limit=9999", parse_nasdaq),
        ("stooq", f"https://stooq.com/q/d/l/?s={t.lower()}.us&i=d", parse_stooq),
    ]


def guardar(ruta, filas):
    filas = sorted({f[0]: f for f in filas}.values())
    tmp = ruta + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        w.writerows(filas)
    os.replace(tmp, ruta)
    return filas


def main():
    os.makedirs(os.path.join(DIR, "datos"), exist_ok=True)
    tickers = [l.split()[0] for l in open(os.path.join(DIR, "tickers.txt")) if l.strip() and not l.startswith("#")]
    errores = 0
    for t in tickers:
        motivos = []
        for nombre, url, parser in fuentes(t):
            try:
                filas = parser(_get(url))
                if len(filas) < 260:
                    raise ValueError(f"solo {len(filas)} días")
                filas = guardar(os.path.join(DIR, "datos", f"{t}.csv"), filas)
                print(f"OK {t} [{nombre}] {len(filas)} días, último: {filas[-1][0]},{float(filas[-1][4]):.2f}")
                break
            except Exception as e:
                motivos.append(f"{nombre}: {str(e)[:80]}")
        else:
            errores += 1
            print(f"ERROR {t} | " + " | ".join(motivos))
        time.sleep(1.5)  # no saturar las fuentes
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
