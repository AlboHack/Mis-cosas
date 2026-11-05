#!/usr/bin/env bash
# Grafo del código del repo con graphify (https://github.com/Graphify-Labs/graphify, Apache-2.0).
# Solo código: se extrae con tree-sitter, sin LLM ni claves, y nada sale del equipo después de instalar.
# Copia scripts/, utfsm-calc/ y antigravity-pc/ a una carpeta temporal: nunca lee universidad/ (580 MB de PDF).
#
# Uso:  scripts/grafo_codigo.sh explain "reflejar_en_repo"     # qué es, quién lo llama y a quién llama
#       scripts/grafo_codigo.sh path "run_sync" "compute_file_sha256"
#       scripts/grafo_codigo.sh query "dónde se calcula el hash de un archivo"
#       scripts/grafo_codigo.sh build                          # reconstruye el grafo
set -euo pipefail

VERSION="0.9.102"   # el nombre del paquete es graphifyy, con doble y (pyproject.toml del repo oficial)
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
BASE="${GRAFO_DIR:-${TMPDIR:-/tmp}/grafo_codigo}"
VENV="$BASE/venv"
CORPUS="$BASE/corpus"
GRAFO="$CORPUS/graphify-out/graph.json"

instalar() {
    [ -x "$VENV/bin/graphify" ] && return
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install -q "graphifyy==$VERSION"
}

construir() {
    instalar
    rm -rf "$CORPUS"; mkdir -p "$CORPUS"
    for d in scripts utfsm-calc antigravity-pc; do cp -r "$RAIZ/$d" "$CORPUS/$d"; done
    find "$CORPUS" \( -name __pycache__ -o -name '*.egg-info' \) -prune -exec rm -rf {} +
    (cd "$CORPUS" && "$VENV/bin/graphify" extract . --code-only)
}

# Reconstruye si falta el grafo o si algún archivo del código es más nuevo que él
necesita_construir() {
    [ -f "$GRAFO" ] || return 0
    [ -n "$(find "$RAIZ/scripts" "$RAIZ/utfsm-calc" "$RAIZ/antigravity-pc" -type f -newer "$GRAFO" -print -quit)" ]
}

orden="${1:-}"
case "$orden" in
    build) construir ;;
    explain|path|query)
        necesita_construir && construir
        "$VENV/bin/graphify" "$orden" "${@:2}" --graph "$GRAFO" ;;
    *) sed -n '2,12p' "$0"; exit 2 ;;
esac
