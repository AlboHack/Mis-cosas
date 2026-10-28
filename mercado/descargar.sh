#!/bin/sh
# Descarga precios diarios de los ETF de tickers.txt (Yahoo → Nasdaq → Stooq). Ver descargar.py.
# Solo datos de mercado públicos: aquí NO va ninguna posición, saldo ni dato personal (repo público).
exec python3 "$(cd "$(dirname "$0")" && pwd)/descargar.py"
