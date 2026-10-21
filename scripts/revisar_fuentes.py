"""Compara cada skill de origen externo con la versión registrada en fuentes/base.json.

Uso: python scripts/revisar_fuentes.py            -> informa qué fuentes cambiaron y muestra el diff
     python scripts/revisar_fuentes.py --registrar -> fija la versión actual como nueva base
Un cambio en la fuente no se copia solo: se revisa el diff y se porta lo que sirva, con su caso de prueba.
"""
import difflib, hashlib, json, subprocess, sys, tempfile, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTES = json.loads((RAIZ / "fuentes/fuentes.json").read_text(encoding="utf-8"))
BASE_P = RAIZ / "fuentes/base.json"
base = json.loads(BASE_P.read_text(encoding="utf-8")) if BASE_P.exists() else {}
registrar = "--registrar" in sys.argv

with tempfile.TemporaryDirectory() as tmp:
    clones = {}
    for f in FUENTES:
        r = f["repo"]
        if r not in clones:
            d = pathlib.Path(tmp) / r.replace("/", "_")
            subprocess.run(["git", "clone", "-q", "--depth", "1", f"https://github.com/{r}", str(d)], check=True)
            commit = subprocess.run(["git", "-C", str(d), "rev-parse", "--short", "HEAD"],
                                    capture_output=True, text=True).stdout.strip()
            clones[r] = (d, commit)
        d, commit = clones[r]
        p = d / f["ruta"]
        if not p.exists():
            print(f"[MOVIDA] {f['skill']}: {r}/{f['ruta']} ya no existe")
            continue
        texto = p.read_text(encoding="utf-8")
        h = hashlib.sha256(texto.encode()).hexdigest()[:12]
        clave = f"{r}/{f['ruta']}"
        prev = base.get(clave)
        if registrar or prev is None:
            base[clave] = {"commit": commit, "sha": h, "texto": texto}
            print(f"[BASE] {f['skill']}: {clave} @ {commit}")
        elif prev["sha"] == h:
            print(f"[SIN CAMBIOS] {f['skill']}: {clave}")
        else:
            print(f"[CAMBIÓ] {f['skill']}: {clave} {prev['commit']} -> {commit}")
            sys.stdout.writelines(difflib.unified_diff(prev["texto"].splitlines(True), texto.splitlines(True),
                                                       "base", "actual", n=1))

BASE_P.write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding="utf-8")
