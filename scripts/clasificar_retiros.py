"""Clasifica, sin borrar nada, lo que el espejo de Aula retiraría de la carpeta de la tablet.

Uso: python3 scripts/clasificar_retiros.py [carpeta_2026-2]
Cada archivo fuera de una carpeta de sección ("NN ...") y fuera de _contexto/ cae en una clase:
  COPIA     su contenido (sha256) ya está en una carpeta de sección del mismo ramo
  GENERADO  archivo viejo de la automatización (00_*.txt, respaldos <nombre>_vAAAAMMDD)
  SOLO_AQUI su contenido no está en el espejo: material que Aula ya no publica u otra cosa
Termina con VEREDICTO: OK si no hay SOLO_AQUI; si los hay, VEREDICTO: REVISAR y la lista completa.
"""
import hashlib
import os
import re
import sys

RAIZ = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "SYNC_ROOT_DIR", "/storage/emulated/0/Download/Universidad/2026-2")
SECCION = re.compile(r"^\d\d ")
GENERADO = re.compile(r"(^00_.*\.txt$)|(_v\d{8}\.[^.]+$)")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while bloque := f.read(1 << 16):
            h.update(bloque)
    return h.hexdigest()


def main():
    total = {"COPIA": 0, "GENERADO": 0, "SOLO_AQUI": 0}
    solo_aqui = []
    for ramo in sorted(os.listdir(RAIZ)):
        d = os.path.join(RAIZ, ramo)
        if not os.path.isdir(d):
            continue
        espejo, fuera = set(), []
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x != "_contexto" and not x.startswith(".")]
            primera = os.path.relpath(root, d).split(os.sep)[0]
            for f in files:
                if f.startswith("."):
                    continue
                p = os.path.join(root, f)
                if SECCION.match(primera):
                    espejo.add(sha256(p))
                else:
                    fuera.append(p)
        for p in fuera:
            if sha256(p) in espejo:
                clase = "COPIA"
            elif GENERADO.search(os.path.basename(p)):
                clase = "GENERADO"
            else:
                clase = "SOLO_AQUI"
                solo_aqui.append((os.path.relpath(p, RAIZ), os.path.getsize(p)))
            total[clase] += 1
    print(" | ".join(f"{k}: {v}" for k, v in total.items()))
    for rel, size in solo_aqui:
        print(f"SOLO_AQUI {size / 1048576:8.2f} MB  {rel}")
    print("VEREDICTO:", "OK" if not solo_aqui else "REVISAR")
    return 0


if __name__ == "__main__":
    sys.exit(main())
