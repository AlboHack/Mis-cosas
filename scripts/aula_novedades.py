"""Novedades de Aula USM: foros, cambios en la página de cada ramo y mensajes privados.

Todo se lee con funciones de solo lectura del Web Service de Moodle (lista blanca en
MoodleAPIClient). Qué va a cada lugar:

- Repo público (universidad/2026-2/<ramo>/):
    avisos.md          publicaciones de docentes y ayudantes en todos los foros del ramo,
                       incluidas sus respuestas dentro de hilos abiertos por estudiantes.
    pagina_curso.json  foto de la página del ramo (secciones, textos, actividades, fechas).
    cambios_pagina.md  bitácora de lo que cambió en la página entre corridas.
- Solo en la tablet (nunca en el repo ni en Drive): mensajes privados recientes, porque
  son conversaciones personales. Al repo llega solo el conteo en ultima_sincronizacion.json.

Cada texto se revisa con es_alerta_evaluacion(); los que hablan de una evaluación y de un
cambio (reprogramación, suspensión, nueva fecha...) se marcan con "⚠ POSIBLE CAMBIO DE
EVALUACIÓN" y se cuentan en el latido para que la tarea semanal de Claude los destaque.
"""
import html
import json
import os
import re
import unicodedata
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=-3))
MARCA_ALERTA = "⚠ POSIBLE CAMBIO DE EVALUACIÓN"
DIAS_MENSAJES = 14

_EVAL = re.compile(
    r"\b(certamen|certámenes|certamenes|control|prueba|evaluaci[oó]n|examen|entrega|tarea|quiz|"
    r"interrogaci[oó]n|laboratorio|informe|presentaci[oó]n|c\d)\b",
    re.IGNORECASE,
)
_CAMBIO = re.compile(
    r"(cambi|reprogram|posterg|aplaz|adelant|suspend|se corre|correr[aá]|se mueve|mover[aá]|"
    r"traslad|nueva fecha|nuevo horario|nueva sala|se modific|queda para|pasa al|pasa a ser|extend|extien|prorrog|ampl[ií]a)",
    re.IGNORECASE,
)


def texto_plano(contenido_html):
    """HTML de Moodle a texto legible (bloques en líneas separadas, entidades decodificadas)."""
    if not contenido_html:
        return ""
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", "", contenido_html)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|tr)>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t).replace("\xa0", " ")
    t = "\n".join(re.sub(r"[ \t]+", " ", linea).strip() for linea in t.splitlines())
    t = re.sub(r"\n{3,}", "\n\n", t)
    return unicodedata.normalize("NFC", t).strip()


def es_alerta_evaluacion(texto):
    """True si el texto menciona una evaluación y además un cambio de fecha, hora o sala."""
    return bool(texto) and bool(_EVAL.search(texto)) and bool(_CAMBIO.search(texto))


def _fecha(ts):
    return datetime.fromtimestamp(int(ts or 0), tz=TZ).strftime("%Y-%m-%d %H:%M")


def _escribir_si_cambia(ruta, contenido):
    previo = ""
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            previo = f.read()
    if previo == contenido:
        return False
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return True


# --------------------------------------------------------------------------- foros
def recolectar_foros(client, course_id):
    """Publicaciones de docentes en todos los foros del ramo.

    Docentes = autores que publican en el foro de tipo 'news' (en Moodle solo docentes y
    ayudantes con permiso escriben ahí). Si no se identifica ninguno, se usan todos los
    iniciadores de hilos del foro 'news' (vacío) y se devuelven todos los hilos, como antes.
    """
    foros = client.call("mod_forum_get_forums_by_courses", {"courseids[0]": course_id}) or []
    foros = [f for f in foros if int(f.get("course", course_id)) == int(course_id)]

    hilos_por_foro = {}
    for foro in foros:
        res = client.call("mod_forum_get_forum_discussions", {"forumid": foro["id"]}) or {}
        hilos_por_foro[foro["id"]] = res.get("discussions", [])

    docentes = set()
    for foro in foros:
        if foro.get("type") == "news":
            docentes.update(h.get("userfullname", "") for h in hilos_por_foro[foro["id"]])
    docentes.discard("")

    publicaciones = []
    for foro in foros:
        for h in hilos_por_foro[foro["id"]]:
            autor = h.get("userfullname", "")
            if not docentes or autor in docentes:
                publicaciones.append({
                    "id": f"d{h.get('discussion')}",
                    "foro": foro.get("name", ""),
                    "asunto": h.get("name") or h.get("subject") or "Sin asunto",
                    "autor": autor or "Docente",
                    "fecha": int(h.get("created") or h.get("timemodified") or 0),
                    "texto": texto_plano(h.get("message", "")),
                    "respuesta_a": None,
                })
            if docentes and int(h.get("numreplies") or 0) > 0:
                posts = (client.call("mod_forum_get_discussion_posts",
                                     {"discussionid": h.get("discussion")}) or {}).get("posts", [])
                for p in posts:
                    p_autor = (p.get("author") or {}).get("fullname", "")
                    if p.get("parentid") and p_autor in docentes:
                        publicaciones.append({
                            "id": f"p{p.get('id')}",
                            "foro": foro.get("name", ""),
                            "asunto": p.get("subject") or h.get("name") or "Respuesta",
                            "autor": p_autor,
                            "fecha": int(p.get("timecreated") or 0),
                            "texto": texto_plano(p.get("message", "")),
                            "respuesta_a": h.get("name", ""),
                        })
    publicaciones.sort(key=lambda x: (x["fecha"], x["id"]), reverse=True)
    return publicaciones, sorted(docentes)


def render_avisos(nombre_ramo, publicaciones):
    lineas = [f"# Avisos y Novedades - {nombre_ramo}", ""]
    for p in publicaciones:
        alerta = es_alerta_evaluacion(f"{p['asunto']}\n{p['texto']}")
        lineas.append(f"## {p['asunto']}")
        if alerta:
            lineas.append(f"**{MARCA_ALERTA}**")
        lineas.append(f"- **Fecha:** {_fecha(p['fecha'])}")
        lineas.append(f"- **Autor:** {p['autor']}")
        lineas.append(f"- **Foro:** {p['foro']}")
        if p["respuesta_a"]:
            lineas.append(f"- **Respuesta en el hilo:** {p['respuesta_a']}")
        lineas.append(f"- **ID:** {p['id']}")
        lineas += ["", p["texto"], "", "---", ""]
    return "\n".join(lineas).rstrip() + "\n"


# --------------------------------------------------------------------------- página del curso
def foto_pagina(secciones):
    """Foto comparable de la página del ramo a partir de core_course_get_contents."""
    foto = {"secciones": {}, "modulos": {}}
    for s in secciones or []:
        sid = str(s.get("id", s.get("section", s.get("name", ""))))
        foto["secciones"][sid] = {
            "nombre": s.get("name", ""),
            "resumen": texto_plano(s.get("summary", "")),
            "visible": int(s.get("visible", 1)),
        }
        for m in s.get("modules", []):
            mid = str(m.get("id", f"{sid}:{m.get('name', '')}"))
            foto["modulos"][mid] = {
                "seccion": s.get("name", ""),
                "tipo": m.get("modname", ""),
                "nombre": m.get("name", ""),
                "descripcion": texto_plano(m.get("description", "")),
                "visible": int(m.get("visible", 1)),
                "fechas": {d.get("label", ""): int(d.get("timestamp") or 0) for d in m.get("dates", []) or []},
                "archivos": sorted(c.get("filename", "") for c in m.get("contents", []) or [] if c.get("type") == "file"),
            }
    return foto


def _corto(t, n=400):
    t = " ".join(t.split())
    return t if len(t) <= n else t[: n - 1] + "…"


def diferencias_pagina(antes, ahora):
    """Lista de cambios legibles entre dos fotos. Vacía si son equivalentes."""
    cambios = []
    sa, sn = antes.get("secciones", {}), ahora.get("secciones", {})
    for sid in sn:
        if sid not in sa:
            cambios.append(f"Sección nueva: «{sn[sid]['nombre']}»" + (f". {_corto(sn[sid]['resumen'])}" if sn[sid]["resumen"] else ""))
            continue
        a, n = sa[sid], sn[sid]
        if a["nombre"] != n["nombre"]:
            cambios.append(f"Sección renombrada: «{a['nombre']}» → «{n['nombre']}»")
        if a["resumen"] != n["resumen"]:
            cambios.append(f"Texto de la sección «{n['nombre']}» cambió. Ahora dice: {_corto(n['resumen']) or '(vacío)'}")
        if a["visible"] != n["visible"]:
            cambios.append(f"Sección «{n['nombre']}» {'visible' if n['visible'] else 'oculta'}")
    for sid in sa:
        if sid not in sn:
            cambios.append(f"Sección eliminada: «{sa[sid]['nombre']}»")

    ma, mn = antes.get("modulos", {}), ahora.get("modulos", {})
    for mid in mn:
        n = mn[mid]
        etiqueta = f"{n['tipo']} «{n['nombre']}» ({n['seccion']})"
        if mid not in ma:
            extra = f". {_corto(n['descripcion'])}" if n["descripcion"] else ""
            fechas = "; ".join(f"{k}: {_fecha(v)}" for k, v in n["fechas"].items())
            cambios.append(f"Nuevo: {etiqueta}{extra}" + (f" [{fechas}]" if fechas else ""))
            continue
        a = ma[mid]
        if a["nombre"] != n["nombre"]:
            cambios.append(f"Renombrado: «{a['nombre']}» → «{n['nombre']}» ({n['seccion']})")
        if a["descripcion"] != n["descripcion"]:
            cambios.append(f"Descripción de {etiqueta} cambió. Ahora dice: {_corto(n['descripcion']) or '(vacío)'}")
        for k in sorted(set(a["fechas"]) | set(n["fechas"])):
            va, vn = a["fechas"].get(k), n["fechas"].get(k)
            if va != vn:
                cambios.append(f"Fecha cambiada en {etiqueta}: {k} {_fecha(va) if va else '—'} → {_fecha(vn) if vn else '—'}")
        if a["visible"] != n["visible"]:
            cambios.append(f"{etiqueta} {'visible' if n['visible'] else 'oculto'}")
        nuevos = sorted(set(n["archivos"]) - set(a["archivos"]))
        quitados = sorted(set(a["archivos"]) - set(n["archivos"]))
        if nuevos:
            cambios.append(f"Archivos agregados en {etiqueta}: {', '.join(nuevos)}")
        if quitados:
            cambios.append(f"Archivos retirados de {etiqueta}: {', '.join(quitados)}")
    for mid in ma:
        if mid not in mn:
            cambios.append(f"Retirado: {ma[mid]['tipo']} «{ma[mid]['nombre']}» ({ma[mid]['seccion']})")
    return cambios


def registrar_cambios_pagina(dir_ramo, secciones, ahora=None):
    """Compara con la foto anterior, agrega los cambios a cambios_pagina.md y guarda la foto.

    Devuelve (n_cambios, n_alertas). La primera corrida solo fija la línea base.
    """
    ruta_foto = os.path.join(dir_ramo, "pagina_curso.json")
    ruta_bitacora = os.path.join(dir_ramo, "cambios_pagina.md")
    nueva = foto_pagina(secciones)
    previa = None
    if os.path.exists(ruta_foto):
        with open(ruta_foto, "r", encoding="utf-8") as f:
            previa = json.load(f)

    n_cambios = n_alertas = 0
    if previa is not None:
        cambios = diferencias_pagina(previa, nueva)
        if cambios:
            n_cambios = len(cambios)
            fecha = (ahora or datetime.now(TZ)).strftime("%Y-%m-%d")
            bloque = [f"## {fecha}", ""]
            for c in cambios:
                alerta = es_alerta_evaluacion(c)
                n_alertas += int(alerta)
                bloque.append(f"- {'**' + MARCA_ALERTA + '** ' if alerta else ''}{c}")
            bloque.append("")
            cabecera = "# Cambios en la página del ramo\n\n"
            anterior = ""
            if os.path.exists(ruta_bitacora):
                with open(ruta_bitacora, "r", encoding="utf-8") as f:
                    anterior = f.read()
                if anterior.startswith(cabecera):
                    anterior = anterior[len(cabecera):]
            _escribir_si_cambia(ruta_bitacora, cabecera + "\n".join(bloque) + "\n" + anterior)

    _escribir_si_cambia(ruta_foto, json.dumps(nueva, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    return n_cambios, n_alertas


# --------------------------------------------------------------------------- mensajes privados
def recolectar_mensajes(client, userid, desde_ts):
    """Mensajes privados recibidos desde desde_ts (no los enviados por Nicolás)."""
    res = client.call("core_message_get_conversations", {"userid": userid, "limitnum": 30}) or {}
    mensajes = []
    for conv in res.get("conversations", []):
        miembros = {m.get("id"): m.get("fullname", "") for m in conv.get("members", [])}
        detalle = client.call("core_message_get_conversation_messages", {
            "currentuserid": userid, "convid": conv.get("id"), "newest": 1, "limitnum": 20,
        }) or {}
        miembros.update({m.get("id"): m.get("fullname", "") for m in detalle.get("members", [])})
        for msg in detalle.get("messages", []):
            if int(msg.get("timecreated") or 0) < desde_ts or msg.get("useridfrom") == userid:
                continue
            mensajes.append({
                "de": miembros.get(msg.get("useridfrom"), str(msg.get("useridfrom"))),
                "fecha": int(msg.get("timecreated") or 0),
                "texto": texto_plano(msg.get("text", "")),
            })
    mensajes.sort(key=lambda m: m["fecha"], reverse=True)
    return mensajes


def render_mensajes(mensajes):
    lineas = ["# Mensajes privados recientes de Aula (solo en la tablet, no se publica)", ""]
    for m in mensajes:
        alerta = es_alerta_evaluacion(m["texto"])
        lineas.append(f"## {_fecha(m['fecha'])} · {m['de']}")
        if alerta:
            lineas.append(f"**{MARCA_ALERTA}**")
        lineas += ["", m["texto"], "", "---", ""]
    return "\n".join(lineas).rstrip() + "\n"


# --------------------------------------------------------------------------- orquestación
def sincronizar_novedades(client, courses, repo_dir, userid, archivo_mensajes, log, ahora=None):
    """Ejecuta foros, página y mensajes. Devuelve (resumen, errores) sin lanzar excepciones."""
    resumen = {"avisos_actualizados": 0, "cambios_pagina": 0, "mensajes_privados_recientes": 0, "alertas_evaluacion": 0}
    errores = []
    base = os.path.join(repo_dir, "universidad", "2026-2")

    for c in courses:
        dir_ramo = os.path.join(base, c["folder"])
        try:
            publicaciones, docentes = recolectar_foros(client, c["id"])
            if publicaciones:
                contenido = render_avisos(c["short"], publicaciones)
                if _escribir_si_cambia(os.path.join(dir_ramo, "avisos.md"), contenido):
                    resumen["avisos_actualizados"] += 1
                    log(f"  [AVISOS ACTUALIZADOS] {c['short']}: {len(publicaciones)} publicaciones de {len(docentes)} docente(s)")
                resumen["alertas_evaluacion"] += sum(
                    es_alerta_evaluacion(f"{p['asunto']}\n{p['texto']}") for p in publicaciones
                    if (ahora or datetime.now(TZ)).timestamp() - p["fecha"] <= 8 * 86400
                )
        except Exception as e:
            errores.append(f"Foros de {c['short']}: {e}")

        try:
            secciones = client.call("core_course_get_contents", {"courseid": c["id"]})
            n_cambios, n_alertas = registrar_cambios_pagina(dir_ramo, secciones, ahora)
            resumen["cambios_pagina"] += n_cambios
            resumen["alertas_evaluacion"] += n_alertas
            if n_cambios:
                log(f"  [PÁGINA DEL RAMO] {c['short']}: {n_cambios} cambio(s), {n_alertas} posible(s) cambio(s) de evaluación")
        except Exception as e:
            errores.append(f"Página de {c['short']}: {e}")

    if userid and archivo_mensajes:
        try:
            desde = (ahora or datetime.now(TZ)) - timedelta(days=DIAS_MENSAJES)
            mensajes = recolectar_mensajes(client, userid, desde.timestamp())
            resumen["mensajes_privados_recientes"] = len(mensajes)
            resumen["alertas_evaluacion"] += sum(es_alerta_evaluacion(m["texto"]) for m in mensajes)
            _escribir_si_cambia(archivo_mensajes, render_mensajes(mensajes))
            if mensajes:
                log(f"  [MENSAJES] {len(mensajes)} mensaje(s) privado(s) en los últimos {DIAS_MENSAJES} días (ver {archivo_mensajes})")
        except Exception as e:
            errores.append(f"Mensajes privados: {e}")

    return resumen, errores
