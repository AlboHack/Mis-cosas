#!/bin/sh
# Descarga precios diarios (CSV de Stooq: Date,Open,High,Low,Close,Volume) de los ETF de tickers.txt.
# Solo datos de mercado públicos: aquí NO va ninguna posición, saldo ni dato personal (repo público).
# Uso (tablet): sh mercado/descargar.sh   -> mercado/datos/<TICKER>.csv
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DIR/datos"
grep -v '^#' "$DIR/tickers.txt" | awk 'NF{print $1}' | while read -r t; do
    s=$(echo "$t" | tr 'A-Z' 'a-z')
    out="$DIR/datos/$t.csv"
    if curl -sS -m 30 -o "$out.tmp" "https://stooq.com/q/d/l/?s=${s}.us&i=d" && head -1 "$out.tmp" | grep -q '^Date,Open,High,Low,Close'; then
        mv "$out.tmp" "$out"
        echo "OK $t $(($(wc -l < "$out") - 1)) días, último: $(tail -1 "$out" | cut -d, -f1,5)"
    else
        rm -f "$out.tmp"
        echo "ERROR $t (Stooq no devolvió CSV válido)"
    fi
done
