#!/bin/sh
# Agrega (idempotente) la descarga de datos de mercado cada 3 días a las 09:13 (hora de la tablet).
set -eu
REPO="${SYNC_REPO_DIR:-$HOME/Mis-cosas}"
MARCA="# mercado-etf"
LINEA="13 9 */3 * * sh $REPO/mercado/actualizar_datos.sh >/dev/null 2>&1 $MARCA"
{ crontab -l 2>/dev/null | grep -v "$MARCA" || true; echo "$LINEA"; } | crontab -
crontab -l | grep "$MARCA"
