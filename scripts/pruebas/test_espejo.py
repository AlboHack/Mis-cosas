"""T31: universidad/ como espejo de Aula: rutas por sección y módulo, y paso al repo con retiros sin tocar _contexto/."""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sincronizar_aula_semanal as s  # noqa: E402

fallas = []


def comprobar(nombre, cond):
    print(("OK    " if cond else "FALLA ") + nombre)
    if not cond:
        fallas.append(nombre)


# --- rutas
sec0 = {"section": 0, "name": ""}
sec3 = {"section": 3, "name": "Unidad 2: Hidrostática"}
f = lambda n, path="/": {"type": "file", "filename": n, "filepath": path}  # noqa: E731
recurso = {"id": 11, "modname": "resource", "name": "Programa", "contents": [f("Programa.pdf")]}
carpeta = {"id": 12, "modname": "folder", "name": "Ayudantía 3", "contents": [f("Guía.pdf"), f("P1.pdf", "/Pautas/")]}
entrega = {"id": 13, "modname": "assign", "name": "Tarea 2", "contents": [f("Enunciado.pdf")]}
recurso_multi = {"id": 14, "modname": "resource", "name": "Clase 5", "contents": [f("Clase5.pdf"), f("anexo.xlsx")]}

comprobar("sección 0 sin nombre -> '00 General'", s.ruta_espejo(sec0, 0, recurso, recurso["contents"][0]) == "00 General/Programa.pdf")
comprobar("':' del nombre de sección se sanea", s.ruta_espejo(sec3, 1, recurso, recurso["contents"][0]) == "03 Unidad 2_ Hidrostática/Programa.pdf")
comprobar("número de sección de Aula, no el índice", s.nombre_seccion({"section": 7, "name": "X"}, 2) == "07 X")
comprobar("sin número usa el índice", s.nombre_seccion({"name": "X"}, 4) == "04 X")
comprobar("carpeta de Aula -> subcarpeta con su nombre", s.ruta_espejo(sec0, 0, carpeta, carpeta["contents"][0]) == "00 General/Ayudantía 3/Guía.pdf")
comprobar("subcarpetas internas de una carpeta de Aula", s.ruta_espejo(sec0, 0, carpeta, carpeta["contents"][1]) == "00 General/Ayudantía 3/Pautas/P1.pdf")
comprobar("entrega -> subcarpeta con el nombre de la tarea", s.ruta_espejo(sec0, 0, entrega, entrega["contents"][0]) == "00 General/Tarea 2/Enunciado.pdf")
comprobar("recurso con varios archivos -> subcarpeta", s.ruta_espejo(sec0, 0, recurso_multi, recurso_multi["contents"][1]) == "00 General/Clase 5/anexo.xlsx")

# --- espejo en el repo
tmp = tempfile.mkdtemp(prefix="espejo_")
try:
    root, repo = os.path.join(tmp, "tablet"), os.path.join(tmp, "repo")
    curso = [{"folder": "CIV244"}]

    def escribir(p, contenido=b"x"):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(contenido)

    escribir(os.path.join(root, "CIV244/00 General/Programa.pdf"), b"programa")
    escribir(os.path.join(root, "CIV244/03 Unidad 2/Clase.pdf"), b"clase v2")
    escribir(os.path.join(root, "CIV244/03 Unidad 2/Grande.pdf"), b"g" * 2048)
    escribir(os.path.join(repo, "CIV244/03 Unidad 2/Clase.pdf"), b"clase v1")
    escribir(os.path.join(repo, "CIV244/Material_y_Apuntes/Viejo.pdf"), b"viejo")
    escribir(os.path.join(repo, "CIV244/_contexto/avisos.md"), b"avisos")
    escribir(os.path.join(repo, "CIV244/_contexto/.contexto_estado.json"), b"{}")
    escribir(os.path.join(repo, "evaluaciones.json"), b"[]")

    # Caso de la tablet: versión vieja en el repo ya en el caché de hashes, con el mismo tamaño y la misma
    # fecha que la nueva (copy2 conserva la fecha). La comparación no debe fiarse del hash viejo.
    clase_tab, clase_repo = os.path.join(root, "CIV244/03 Unidad 2/Clase.pdf"), os.path.join(repo, "CIV244/03 Unidad 2/Clase.pdf")
    s.compute_file_sha256(clase_repo)
    st_t = os.stat(clase_tab)
    os.utime(clase_repo, ns=(st_t.st_atime_ns, st_t.st_mtime_ns))
    s.compute_file_sha256(clase_repo)

    cp, bo, om = s.reflejar_en_repo(curso, root, repo, limite_mb=1 / 1024)  # tope de 1 KB para probar el límite
    en_repo = sorted(os.path.relpath(os.path.join(r, x), repo) for r, _, fs in os.walk(repo) for x in fs)
    comprobar("copia lo nuevo y lo modificado", cp == 2 and open(os.path.join(repo, "CIV244/03 Unidad 2/Clase.pdf"), "rb").read() == b"clase v2")
    comprobar("retira lo que no está en Aula y su carpeta vacía", bo == 1 and not os.path.exists(os.path.join(repo, "CIV244/Material_y_Apuntes")))
    comprobar("archivo sobre el límite no pasa al repo", om == 1 and not os.path.exists(os.path.join(repo, "CIV244/03 Unidad 2/Grande.pdf")))
    comprobar("_contexto/ y archivos fuera de los ramos intactos", en_repo == [
        "CIV244/00 General/Programa.pdf", "CIV244/03 Unidad 2/Clase.pdf",
        "CIV244/_contexto/.contexto_estado.json", "CIV244/_contexto/avisos.md", "evaluaciones.json"])
    comprobar("segunda pasada sin cambios", s.reflejar_en_repo(curso, root, repo, limite_mb=1 / 1024) == (0, 0, 1))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"Resultado T31: {'PASS' if not fallas else 'FAIL'}")
sys.exit(1 if fallas else 0)
