#!/usr/bin/env python3
"""Pruebas T21–T25 de aula_novedades.py con un cliente Moodle simulado (sin red, sin rutas reales)."""
import os
import shutil
import sys
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aula_novedades as an  # noqa: E402

AHORA = datetime(2026, 10, 31, 10, 0, tzinfo=an.TZ)
T = int(AHORA.timestamp())
DIA = 86400


class ClienteFalso:
    def __init__(self):
        self.foros = {}
        self.hilos = {}
        self.posts = {}
        self.secciones = {}
        self.convs = []
        self.mensajes = {}
        self.llamadas = []

    def call(self, fn, params=None):
        self.llamadas.append(fn)
        p = params or {}
        if fn == "mod_forum_get_forums_by_courses":
            return self.foros.get(int(p["courseids[0]"]), [])
        if fn == "mod_forum_get_forum_discussions":
            return {"discussions": self.hilos.get(p["forumid"], [])}
        if fn == "mod_forum_get_discussion_posts":
            return {"posts": self.posts.get(p["discussionid"], [])}
        if fn == "core_course_get_contents":
            return self.secciones.get(p["courseid"], [])
        if fn == "core_message_get_conversations":
            return {"conversations": self.convs}
        if fn == "core_message_get_conversation_messages":
            return self.mensajes.get(p["convid"], {})
        raise AssertionError(f"llamada inesperada {fn}")


def curso():
    return [{"id": 1, "short": "Fluidos", "folder": "CIV244"}]


def resultado(nombre, casos):
    for texto, ok in casos:
        print(f"  {texto}: {ok}")
    ok = all(v for _, v in casos)
    print(f"Resultado {nombre}: {'PASS' if ok else 'FAIL'}\n")
    return ok


def t21_foros(tmp):
    print("--- T21: Foros (solo docentes, incluye respuestas de docentes en hilos de estudiantes) ---")
    c = ClienteFalso()
    c.foros[1] = [{"id": 10, "course": 1, "type": "news", "name": "Avisos"},
                  {"id": 11, "course": 1, "type": "general", "name": "Consultas"}]
    c.hilos[10] = [{"discussion": 100, "name": "Bienvenida", "userfullname": "PROFESOR SOTO",
                    "created": T - 30 * DIA, "message": "<p>Hola curso</p>", "numreplies": 0}]
    c.hilos[11] = [{"discussion": 200, "name": "Duda C3", "userfullname": "ESTUDIANTE PEREZ",
                    "created": T - 2 * DIA, "message": "<p>¿Qué entra en el C3?</p>", "numreplies": 1}]
    c.posts[200] = [
        {"id": 2000, "parentid": 0, "author": {"fullname": "ESTUDIANTE PEREZ"}, "timecreated": T - 2 * DIA,
         "message": "<p>¿Qué entra en el C3?</p>", "subject": "Duda C3"},
        {"id": 2001, "parentid": 2000, "author": {"fullname": "PROFESOR SOTO"}, "timecreated": T - DIA,
         "message": "<p>Entran unidades 5 y 6. Además, el certamen 3 se posterga al lunes 23.</p>", "subject": "Re: Duda C3"},
    ]
    resumen, errores = an.sincronizar_novedades(c, curso(), tmp, None, None, lambda m: None, ahora=AHORA)
    avisos = open(os.path.join(tmp, "universidad/2026-2/CIV244/avisos.md"), encoding="utf-8").read()
    return resultado("T21", [
        ("sin errores", errores == []),
        ("aviso del docente en foro news incluido", "Bienvenida" in avisos),
        ("respuesta del docente en hilo de estudiante incluida", "se posterga al lunes 23" in avisos),
        ("texto y nombre del estudiante excluidos", "ESTUDIANTE PEREZ" not in avisos and "¿Qué entra" not in avisos),
        ("marca de posible cambio de evaluación", an.MARCA_ALERTA in avisos),
        ("alerta contada en el resumen (últimos 8 días)", resumen["alertas_evaluacion"] == 1),
    ])


def t22_pagina(tmp):
    print("--- T22: Cambios en la página del ramo ---")
    c = ClienteFalso()
    c.foros[1] = []
    base = [{"id": 1, "name": "Semana 12", "summary": "<p>Repaso C3</p>", "visible": 1, "modules": [
        {"id": 50, "modname": "label", "name": "Aviso", "description": "<p>Control 2 en sala A012</p>", "visible": 1},
        {"id": 51, "modname": "assign", "name": "Tarea 1", "visible": 1,
         "dates": [{"label": "Vencimiento:", "timestamp": T + 3 * DIA}]},
    ]}]
    c.secciones[1] = base
    dir_ramo = os.path.join(tmp, "universidad/2026-2/CIV244")
    an.sincronizar_novedades(c, curso(), tmp, None, None, lambda m: None, ahora=AHORA)
    linea_base_sin_bitacora = not os.path.exists(os.path.join(dir_ramo, "cambios_pagina.md"))

    import copy
    cambiada = copy.deepcopy(base)
    cambiada[0]["modules"][0]["description"] = "<p>El Control 2 se cambia a la sala B014</p>"
    cambiada[0]["modules"][1]["dates"][0]["timestamp"] = T + 5 * DIA
    cambiada[0]["modules"].append({"id": 52, "modname": "resource", "name": "Pauta C2", "visible": 1,
                                   "contents": [{"type": "file", "filename": "Pauta_C2.pdf"}]})
    c.secciones[1] = cambiada
    r2, _ = an.sincronizar_novedades(c, curso(), tmp, None, None, lambda m: None, ahora=AHORA)
    bitacora = open(os.path.join(dir_ramo, "cambios_pagina.md"), encoding="utf-8").read()
    mtime = os.path.getmtime(os.path.join(dir_ramo, "cambios_pagina.md"))

    r3, _ = an.sincronizar_novedades(c, curso(), tmp, None, None, lambda m: None, ahora=AHORA)
    sin_cambio_estable = os.path.getmtime(os.path.join(dir_ramo, "cambios_pagina.md")) == mtime
    return resultado("T22", [
        ("primera corrida solo fija la línea base", linea_base_sin_bitacora),
        ("detecta texto cambiado", "se cambia a la sala B014" in bitacora),
        ("detecta fecha cambiada", "Fecha cambiada en assign «Tarea 1»" in bitacora),
        ("detecta actividad nueva", "Nuevo: resource «Pauta C2»" in bitacora),
        ("marca de posible cambio de evaluación", an.MARCA_ALERTA in bitacora and r2["alertas_evaluacion"] >= 1),
        ("tercera corrida sin cambios no reescribe", sin_cambio_estable and r3["cambios_pagina"] == 0),
    ])


def t23_mensajes(tmp):
    print("--- T23: Mensajes privados solo en la tablet ---")
    c = ClienteFalso()
    c.foros[1] = []
    c.convs = [{"id": 7, "members": [{"id": 99, "fullname": "PROFESOR SOTO"}]}]
    c.mensajes[7] = {"members": [{"id": 99, "fullname": "PROFESOR SOTO"}], "messages": [
        {"useridfrom": 99, "timecreated": T - DIA, "text": "<p>Nicolás, tu prueba recuperativa se reprograma al martes.</p>"},
        {"useridfrom": 21469, "timecreated": T - DIA, "text": "<p>Gracias profe</p>"},
        {"useridfrom": 99, "timecreated": T - 30 * DIA, "text": "<p>Mensaje antiguo</p>"},
    ]}
    archivo = os.path.join(tmp, "fuera_del_repo", "mensajes_privados_aula.md")
    repo = os.path.join(tmp, "repo")
    r, errores = an.sincronizar_novedades(c, curso(), repo, 21469, archivo, lambda m: None, ahora=AHORA)
    local = open(archivo, encoding="utf-8").read()
    en_repo = []
    for raiz, _, archivos in os.walk(repo):
        for a in archivos:
            if "reprograma" in open(os.path.join(raiz, a), encoding="utf-8").read():
                en_repo.append(a)
    return resultado("T23", [
        ("sin errores", errores == []),
        ("mensaje reciente del docente guardado localmente", "se reprograma al martes" in local),
        ("excluye lo enviado por Nicolás y lo antiguo", "Gracias profe" not in local and "antiguo" not in local),
        ("marca de alerta y conteos", an.MARCA_ALERTA in local and r["mensajes_privados_recientes"] == 1 and r["alertas_evaluacion"] == 1),
        ("ningún texto de mensaje en el repo", en_repo == []),
    ])


def t24_lista_blanca():
    print("--- T24: Lista blanca solo de lectura ---")
    from sincronizar_aula_semanal import MoodleAPIClient, WhitelistViolationError
    permitidas = MoodleAPIClient.ALLOWED_FUNCTIONS
    escritura = ["core_message_send_instant_messages", "core_message_mark_message_read",
                 "mod_forum_add_discussion_post", "mod_assign_save_submission"]
    bloqueadas = []
    for fn in escritura:
        try:
            MoodleAPIClient("http://127.0.0.1:9", "x").call(fn)
        except WhitelistViolationError:
            bloqueadas.append(fn)
    nuevas = {"mod_forum_get_forums_by_courses", "mod_forum_get_discussion_posts",
              "core_message_get_conversations", "core_message_get_conversation_messages"}
    return resultado("T24", [
        ("funciones nuevas de lectura permitidas", nuevas <= permitidas),
        ("todas las permitidas son de lectura (get_*)", all("_get_" in f for f in permitidas)),
        ("funciones de escritura bloqueadas sin red", bloqueadas == escritura),
    ])


def t25_detector():
    print("--- T25: Detector de cambios de evaluación ---")
    positivos = ["El certamen 3 se posterga al lunes", "Se suspende el control de mañana",
                 "La entrega de la tarea se extiende hasta el viernes", "C2 queda para el 27 de octubre",
                 "Nueva sala para la prueba: B014"]
    negativos = ["Recuerden estudiar para el certamen", "Se cambia la sala de la ayudantía",
                 "Subí las diapositivas de la clase", ""]
    return resultado("T25", [
        ("detecta todos los positivos", all(an.es_alerta_evaluacion(t) for t in positivos)),
        ("no marca los negativos", not any(an.es_alerta_evaluacion(t) for t in negativos)),
    ])


def main():
    if os.environ.get("SYNC_TEST_MODE") != "1":
        os.environ["SYNC_TEST_MODE"] = "1"
    tmp = tempfile.mkdtemp(prefix="novedades_")
    for k, v in {"SYNC_ROOT_DIR": "r", "SYNC_DELTA_DIR": "d", "SYNC_REPO_DIR": "repo", "SYNC_LOG_FILE": "log.txt",
                 "SYNC_MANIFEST_FILE": "m.json", "SYNC_MENSAJES_FILE": "msj.md", "SYNC_LOCK_FILE": "lock"}.items():
        os.environ[k] = os.path.join(tmp, v)
    try:
        oks = [t21_foros(os.path.join(tmp, "a")), t22_pagina(os.path.join(tmp, "b")),
               t23_mensajes(os.path.join(tmp, "c")), t24_lista_blanca(), t25_detector()]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"RESUMEN NOVEDADES: {'TODAS PASARON' if all(oks) else 'FALLÓ ALGUNA'}")
    return 0 if all(oks) else 1


if __name__ == "__main__":
    sys.exit(main())
