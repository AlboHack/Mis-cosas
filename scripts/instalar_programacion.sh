#!/bin/sh
# Instala (o reinstala) la programación de la sincronización semanal en la tablet. Idempotente.
#   - cron (cronie) llama cada hora a scripts/programador_sync.py, que decide si corresponde correr.
#   - ~/.bashrc levanta crond si no está activo cada vez que se abre una sesión de Antigravity/Termux
#     (no hay arranque automático al encender la tablet: com.agycli no recibe BOOT_COMPLETED).
# Requisito previo: pkg install cronie
set -eu
REPO="${SYNC_REPO_DIR:-$HOME/Mis-cosas}"
MARCA="# sync-aula-usm"

command -v crond >/dev/null 2>&1 || { echo "Falta cronie: pkg install cronie"; exit 1; }
command -v crontab >/dev/null 2>&1 || { echo "Falta crontab (paquete cronie)"; exit 1; }

LINEA="7 * * * * python3 $REPO/scripts/programador_sync.py >/dev/null 2>&1 $MARCA"
{ crontab -l 2>/dev/null | grep -v "$MARCA" || true; echo "$LINEA"; } | crontab -

touch "$HOME/.bashrc"
if ! grep -q "$MARCA" "$HOME/.bashrc"; then
    printf '\n%s\npgrep -x crond >/dev/null 2>&1 || crond\n' "$MARCA" >> "$HOME/.bashrc"
fi

pgrep -x crond >/dev/null 2>&1 || crond
echo "crontab:"; crontab -l | grep "$MARCA"
echo "crond activo: $(pgrep -x crond >/dev/null 2>&1 && echo sí || echo NO)"
