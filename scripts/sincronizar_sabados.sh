#!/bin/sh
# Lanzador de la sincronización semanal de Aula USM (tablet, Antigravity/Termux).
# - Mantiene la CPU despierta durante la corrida (termux-wake-lock) y la libera siempre al salir.
# - Usa el código aprobado de main antes de correr (fast-forward; nunca reescribe historia).
# - Propaga el código de salida del script (0 = OK, 1 = con errores o corte de seguridad).
set -u
REPO="${SYNC_REPO_DIR:-$HOME/Mis-cosas}"
LOG="${SYNC_LOG_FILE:-/storage/emulated/0/Download/Universidad/Registro_Sincronizaciones.log}"

if command -v termux-wake-lock >/dev/null 2>&1; then
    termux-wake-lock
    trap 'termux-wake-unlock 2>/dev/null' EXIT INT TERM
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] AVISO: termux-wake-lock no disponible; la CPU podría dormirse a mitad de la corrida." >> "$LOG"
fi

cd "$REPO" || { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR CRÍTICO: no existe $REPO" >> "$LOG"; exit 1; }

if ! git pull --ff-only -q origin main; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] AVISO: no se pudo actualizar el código desde main; se usa la versión local." >> "$LOG"
fi

python3 scripts/sincronizar_aula_semanal.py "$@"
