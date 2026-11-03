#!/usr/bin/env python3
"""T29: enunciados adjuntos a entregas (mod_assign) entran al flujo como archivos."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sincronizar_aula_semanal as s

class Fake:
    def call(self, fn, params=None):
        assert fn in s.MoodleAPIClient.ALLOWED_FUNCTIONS
        return {"courses": [{"id": 1, "assignments": [
            {"cmid": 10, "introattachments": [{"filename": "T2.pdf", "fileurl": "https://x/pluginfile.php/1/T2.pdf", "filesize": 5, "timemodified": 7}]},
            {"cmid": 11, "introattachments": []}]}]}

def main():
    secs = [{"name": "Info", "modules": [
        {"id": 10, "modname": "assign", "name": "Tarea 2", "contents": []},
        {"id": 11, "modname": "assign", "name": "Tarea 3"},
        {"id": 12, "modname": "resource", "name": "otro"}]}]
    n = s.agregar_enunciados_de_entregas(Fake(), 1, secs)
    n2 = s.agregar_enunciados_de_entregas(Fake(), 1, secs)  # idempotente
    m = secs[0]["modules"]
    casos = [("agrega 1", n == 1), ("idempotente", n2 == 0),
             ("archivo en Tarea 2", m[0]["contents"][0]["filename"] == "T2.pdf" and m[0]["contents"][0]["type"] == "file"),
             ("sin adjuntos no cambia", "contents" not in m[1] or m[1]["contents"] == [] ),
             ("recurso intacto", "contents" not in m[2]),
             ("en lista blanca", "mod_assign_get_assignments" in s.MoodleAPIClient.ALLOWED_FUNCTIONS)]
    for t, ok in casos: print(f"  {t}: {ok}")
    ok = all(v for _, v in casos); print(f"Resultado T29: {'PASS' if ok else 'FAIL'}"); return 0 if ok else 1

if __name__ == "__main__": sys.exit(main())
