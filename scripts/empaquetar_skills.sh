#!/usr/bin/env bash
# Uso: scripts/empaquetar_skills.sh <carpeta-destino>
# Un .zip por skill, con la carpeta de la skill en la raíz del zip (formato que acepta claude.ai).
set -euo pipefail
destino=$(mkdir -p "$1" && cd "$1" && pwd)
cd "$(dirname "$0")/../.claude/skills"
for d in */; do
  n=${d%/}
  rm -f "$destino/$n.zip"
  zip -qr "$destino/$n.zip" "$n"
done
ls "$destino"
