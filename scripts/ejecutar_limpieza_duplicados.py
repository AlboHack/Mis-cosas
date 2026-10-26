#!/usr/bin/env python3
"""
scripts/ejecutar_limpieza_duplicados.py
Eliminación segura y determinística de archivos duplicados binarios.
Antes de borrar cualquier archivo:
1. Verifica que la ruta conservada exista en disco.
2. Verifica que el SHA-256 de la ruta conservada coincida con el esperado.
3. Verifica que la ruta a eliminar exista y tenga idéntico SHA-256.
Solo bajo estas 3 condiciones confirmadas se procede al borrado.
"""

import os
import sys
import json
import hashlib
import subprocess

REPO_DIR = os.environ.get("SYNC_REPO_DIR", "/data/data/com.agycli/files/home/Mis-cosas")
TABLET_DIR = os.environ.get("SYNC_ROOT_DIR", "/storage/emulated/0/Download/Universidad/2026-2")
REPORT_FILE = os.path.expanduser("/data/data/com.agycli/files/home/duplicados_report.json")

def ejecutar_limpieza():
    if not os.path.exists(REPORT_FILE):
        print(f"ERROR: No se encontró el reporte de duplicados en {REPORT_FILE}", file=sys.stderr)
        return 1

    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    dups = data.get("duplicates", [])
    print(f"Iniciando verificación y limpieza de {len(dups)} archivos duplicados...")

    borrados_repo = 0
    borrados_tablet = 0
    errores_repo = 0
    errores_tablet = 0

    for idx, item in enumerate(dups, 1):
        rel_conserve = item["conserve"]
        rel_delete = item["delete"]
        expected_sha = item["sha256"]

        # 1. Limpieza en repositorio Git
        p_conserve = os.path.join(REPO_DIR, rel_conserve)
        p_delete = os.path.join(REPO_DIR, rel_delete)

        if not os.path.exists(p_conserve):
            print(f"[ALERTA REPO] Archivo conservado ausente: {rel_conserve}. Omitiendo borrado de {rel_delete}.", file=sys.stderr)
            errores_repo += 1
            continue

        sha_c = hashlib.sha256(open(p_conserve, "rb").read()).hexdigest()
        if sha_c != expected_sha:
            print(f"[ALERTA REPO] SHA256 no coincide en conservado: {rel_conserve}. Omitiendo.", file=sys.stderr)
            errores_repo += 1
            continue

        if os.path.exists(p_delete):
            sha_d = hashlib.sha256(open(p_delete, "rb").read()).hexdigest()
            if sha_d == expected_sha:
                # Seguro para borrar
                subprocess.run(["git", "rm", "-f", rel_delete], cwd=REPO_DIR, check=True, stdout=subprocess.DEVNULL)
                borrados_repo += 1
            else:
                print(f"[ALERTA REPO] SHA256 difiere en duplicado: {rel_delete}. Omitiendo borrado.", file=sys.stderr)
                errores_repo += 1

        # 2. Limpieza en la tablet (almacenamiento compartido)
        rel_tab_conserve = rel_conserve.replace("universidad/2026-2/", "")
        rel_tab_delete = rel_delete.replace("universidad/2026-2/", "")
        t_conserve = os.path.join(TABLET_DIR, rel_tab_conserve)
        t_delete = os.path.join(TABLET_DIR, rel_tab_delete)

        if os.path.exists(t_conserve) and os.path.exists(t_delete):
            sha_tc = hashlib.sha256(open(t_conserve, "rb").read()).hexdigest()
            sha_td = hashlib.sha256(open(t_delete, "rb").read()).hexdigest()
            if sha_tc == expected_sha and sha_td == expected_sha:
                try:
                    os.remove(t_delete)
                    borrados_tablet += 1
                except Exception as e:
                    print(f"[ERROR TABLET] No se pudo borrar {t_delete}: {e}", file=sys.stderr)
                    errores_tablet += 1

    print("\n================ RESUMEN DE LIMPIEZA ================")
    print(f"Repositorio Git: {borrados_repo} archivos eliminados exitosamente (errores: {errores_repo}).")
    print(f"Tablet Android:  {borrados_tablet} archivos eliminados exitosamente (errores: {errores_tablet}).")
    print("======================================================")

    return 0 if errores_repo == 0 else 1

if __name__ == "__main__":
    sys.exit(ejecutar_limpieza())
