#!/bin/sh
# Cada 3 días (cron de la tablet): baja precios de los ETF y los sube a la rama datos/mercado.
# Trabaja en un worktree aparte (~/Mis-cosas-mercado) para no tocar el árbol de main que usa la
# sincronización de Aula. Nunca hace push a main. Solo datos de mercado públicos.
set -u
REPO="${SYNC_REPO_DIR:-$HOME/Mis-cosas}"
WT="${MERCADO_WORKTREE:-$HOME/Mis-cosas-mercado}"
RAMA="datos/mercado"
LOG="${MERCADO_LOG:-/storage/emulated/0/Download/Universidad/Registro_Mercado.log}"
ts() { date '+%Y-%m-%d %H:%M:%S'; }

cd "$REPO" || { echo "[$(ts)] ERROR: no existe $REPO" >> "$LOG"; exit 1; }
git fetch -q origin || { echo "[$(ts)] ERROR: git fetch" >> "$LOG"; exit 1; }
if [ ! -d "$WT" ]; then
    if git ls-remote --exit-code --heads origin "$RAMA" >/dev/null 2>&1; then
        git worktree add -q -B "$RAMA" "$WT" "origin/$RAMA"
    else
        git worktree add -q -B "$RAMA" "$WT" origin/claude/mercado 2>/dev/null || git worktree add -q -B "$RAMA" "$WT" origin/main
    fi
fi
cd "$WT" || exit 1
git pull -q --rebase origin "$RAMA" 2>/dev/null || true
# trae siempre la versión vigente de los scripts de mercado desde main (si ya están ahí)
git checkout -q origin/main -- mercado/descargar.sh mercado/tickers.txt 2>/dev/null || true

salida=$(sh mercado/descargar.sh 2>&1)
echo "[$(ts)] $(echo "$salida" | grep -c '^OK') OK, $(echo "$salida" | grep -c '^ERROR') ERROR" >> "$LOG"
echo "$salida" | grep '^ERROR' >> "$LOG"

git add mercado/datos
if git diff --cached --quiet; then
    echo "[$(ts)] Sin datos nuevos." >> "$LOG"
    exit 0
fi
git commit -q -m "datos(mercado): $(date +%F)" && git push -q origin "$RAMA" \
    && echo "[$(ts)] Subido a $RAMA: $(git log --oneline -1)" >> "$LOG" \
    || { echo "[$(ts)] ERROR: commit/push de datos" >> "$LOG"; exit 1; }
