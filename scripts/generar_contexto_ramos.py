#!/usr/bin/env python3
"""
generar_contexto_ramos.py
=========================
Generador incremental de archivos de contexto exhaustivos por asignatura (Semestre 2026-2).
Produce en cada ramo: universidad/2026-2/<ramo>/Contexto_Asignatura.md
Y un resumen global en: universidad/2026-2/Contexto_Semestre_2026-2.md

Diseñado para que Claude (y otros modelos / agentes) comprendan en 1 solo documento
el 100% del estado actual del ramo:
 - Metadatos, descripción y programa oficial.
 - Horarios, salas y equipo docente.
 - Calendario consolidado de evaluaciones (con cuenta regresiva y ponderaciones).
 - Módulos y secciones de Aula USM (recursos, carpetas, tareas con instrucciones y enunciados).
 - Inventario completo de archivos locales en disco y respaldo en Google Drive.
 - Avisos y alertas recientes de los foros docentes.
 - Historial incremental de cambios (Changelog de sincronizaciones).

Totalmente determinístico, estándar Python 3 (zero external dependencies).
"""

import os
import sys
import json
import html
import re
import hashlib
import unicodedata
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=-3))

REPO_DIR = os.environ.get("SYNC_REPO_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DIR = os.environ.get("SYNC_ROOT_DIR", os.path.join(REPO_DIR, "universidad", "2026-2"))

COURSES_META = [
    {
        "id": 62177,
        "sigla": "CIV222",
        "short": "FICA",
        "nombre": "Fundamentos de Ingeniería de Construcción y Administración",
        "folder": "CIV222_FUNDAMENTOS_DE_INGENIERÍA_DE_CONSTRUCCIÓN_Y_ADMINISTRACIÓN_",
        "depto": "Departamento de Obras Civiles",
        "sct": "140 hrs cronológicas (5 SCT)",
        "horarios": "Cátedra: Lunes | Bloques 11-12 (16:00 - 17:10) y 13-14 (17:30 - 18:40)",
        "profesor": "Equipo Docente Obras Civiles",
        "descripcion": (
            "El estudiante inicia el aprendizaje al concepto de proyecto en la industria de la construcción, "
            "etapas del ciclo de vida de un proyecto y sus participantes. Analiza la prefactibilidad de un proyecto "
            "a través de herramientas de ingeniería económica. Identifica los recursos involucrados en actividades de "
            "proyectos de construcción y métodos constructivos para ejecutar dichas actividades. Estima los costos "
            "involucrados en las actividades de un proyecto de construcción. Identifica las recientes herramientas "
            "tecnológicas y de gestión de la construcción."
        ),
    },
    {
        "id": 62178,
        "sigla": "CIV233",
        "short": "FAE",
        "nombre": "Fundamentos de Análisis Estructural",
        "folder": "CIV233_FUNDAMENTOS_DE_ANÁLISIS_ESTRUCTURAL_",
        "depto": "Departamento de Obras Civiles",
        "sct": "187 hrs cronológicas (6 SCT)",
        "horarios": (
            "Cátedra: Miércoles | Bloques 13-14 (17:30 - 18:40) y 15-16 (18:50 - 20:00) | Sala A012\n"
            "- Ayudantía: Viernes | Bloques 7-8 (12:30 - 13:40) | Sala K300"
        ),
        "profesor": "Equipo Docente Obras Civiles | Ayudantes: Gabriel Flores (gabriel.floresf@usm.cl), Matías Muñoz (mmunozr@usm.cl)",
        "descripcion": (
            "El estudiante determina las fuerzas internas y desplazamientos causados por solicitaciones estáticas en estructuras "
            "isostáticas e hiperestáticas constituidas por materiales de comportamiento lineal y no lineal. También identifica las "
            "deformadas, y analiza algunos casos especiales tales como cambios de temperatura, defectos de fabricación, asentamientos "
            "y resortes. El estudiante integra los fundamentos para el desarrollo de métodos de análisis estructural, que son "
            "aplicables tanto en el caso estático como dinámico."
        ),
    },
    {
        "id": 62182,
        "sigla": "CIV244",
        "short": "Fluidos",
        "nombre": "Mecánica de Fluidos",
        "folder": "CIV244_MECÁNICA_DE_FLUIDOS_",
        "depto": "Departamento de Obras Civiles",
        "sct": "203 hrs cronológicas (7 SCT)",
        "horarios": "Cátedra: Cátedras y Ayudantías según programación oficial | Campus San Joaquín",
        "profesor": "Profesor: Ricardo Quinteros (ricardo.quinteros@usm.cl) | Sala de consultas: KS-203",
        "descripcion": (
            "El estudiante desarrolla los fundamentos teóricos que le permiten modelar el comportamiento, tanto cinemático como dinámico, "
            "de los fluidos, principalmente aquellos considerados incompresibles. Con ello, el estudiante analiza, formula y resuelve problemas "
            "propios de la mecánica de fluidos, que finalmente describe conceptualmente, desde una perspectiva de tipo científica con desarrollos "
            "fenomenológicos rigurosos, que vincula con la comprensión de la física de los procesos hidrodinámicos."
        ),
    },
    {
        "id": 62192,
        "sigla": "CIV386",
        "short": "Transporte",
        "nombre": "Ingeniería de Transporte",
        "folder": "CIV386_INGENIERÍA_DE_TRANSPORTE_",
        "depto": "Departamento de Obras Civiles",
        "sct": "145 hrs cronológicas (5 SCT)",
        "horarios": "Cátedra: Miércoles | 14:00 - 16:30 | Salas B014 / B103",
        "profesor": "Profesor: Cristóbal Pineda A. (cristobal.pineda@usm.cl)",
        "descripcion": (
            "El estudiante distingue y analiza sistemas de transporte urbano, entendiendo los procesos de movilidad y su modelamiento "
            "matemático desde la necesidad por transporte hasta la operación de sistemas y redes, evaluando el impacto de diversos factores "
            "económicos, territoriales, sociales, culturales y tecnológicos."
        ),
    },
    {
        "id": 5623,
        "sigla": "POC",
        "short": "Prácticas",
        "nombre": "Prácticas Obras Civiles",
        "folder": "POC_SJ_VV_Prácticas_Obras_Civiles",
        "depto": "Coordinación de Obras Civiles USM (San Joaquín / Casa Central)",
        "sct": "Prácticas de Operario e Industriales / Profesionales",
        "horarios": "Modalidad continua y autónoma en empresas del sector de la construcción, minería y consultoría",
        "profesor": "Encargada de Prácticas: Camila Almonacid (practicas.oocc@usm.cl)",
        "descripcion": (
            "Prácticas de Operario (Industriales) y Profesionales, realizadas en empresas externas del sector de la construcción, minería y "
            "consultoría de ingeniería civil. Acreditación de horas laborales, desarrollo y entrega de informe final según pautas de convalidación."
        ),
    },
]

def format_bytes(n):
    if n < 1024:
        return f"{n} B"
    elif n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    else:
        return f"{n / (1024 * 1024):.2f} MB"

def clean_html(text):
    if not text:
        return ""
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", "", text)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|tr)>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t).replace("\xa0", " ")
    t = "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in t.splitlines())
    t = re.sub(r"\n{3,}", "\n\n", t)
    return unicodedata.normalize("NFC", t).strip()

def ts_to_str(ts):
    if not ts:
        return "Sin fecha especificada"
    dt = datetime.fromtimestamp(int(ts), tz=TZ)
    return dt.strftime("%Y-%m-%d %H:%M")

def get_countdown(ts, now_dt):
    if not ts:
        return "N/A"
    dt = datetime.fromtimestamp(int(ts), tz=TZ)
    diff = dt - now_dt
    days = diff.days
    secs = diff.seconds
    hours = secs // 3600
    if diff.total_seconds() < 0:
        return "Finalizada"
    if days == 0:
        return f"¡VENCE HOY! (en {hours} h)"
    elif days == 1:
        return "Vence mañana"
    else:
        return f"En {days} días ({dt.strftime('%d-%b')})"

def extraer_secciones_y_modulos(client, cid, dir_ramo):
    """Obtiene secciones y módulos desde la API de Moodle o desde el caché local pagina_curso.json."""
    sections = None
    if client:
        try:
            sections = client.call("core_course_get_contents", {"courseid": cid})
        except Exception:
            sections = None

    if sections is None:
        cache_p = os.path.join(dir_ramo, "pagina_curso.json")
        if os.path.exists(cache_p):
            try:
                with open(cache_p, "r", encoding="utf-8") as f:
                    foto = json.load(f)
                # Reconstruir secciones sintéticas a partir de foto
                secs_map = {}
                for sid, sdata in foto.get("secciones", {}).items():
                    secs_map[sid] = {"id": sid, "name": sdata.get("nombre"), "summary": sdata.get("resumen"), "modules": []}
                for mid, mdata in foto.get("modulos", {}).items():
                    s_name = mdata.get("seccion")
                    # buscar sección por nombre
                    target_sec = None
                    for s in secs_map.values():
                        if s["name"] == s_name:
                            target_sec = s
                            break
                    if not target_sec:
                        target_sec = {"id": f"sec_{s_name}", "name": s_name, "summary": "", "modules": []}
                        secs_map[target_sec["id"]] = target_sec
                    contents = [{"type": "file", "filename": f, "filesize": 0} for f in mdata.get("archivos", [])]
                    target_sec["modules"].append({
                        "id": mid,
                        "name": mdata.get("nombre"),
                        "modname": mdata.get("tipo"),
                        "description": mdata.get("descripcion"),
                        "contents": contents,
                        "dates": [{"label": k, "timestamp": v} for k, v in mdata.get("fechas", {}).items()]
                    })
                sections = list(secs_map.values())
            except Exception:
                sections = []
        else:
            sections = []
    return sections or []

def extraer_tareas_asignadas(client, cid):
    """Obtiene assignments con enunciados (intro) y adjuntos vía mod_assign_get_assignments."""
    if not client:
        return {}
    try:
        data = client.call("mod_assign_get_assignments", {"courseids[0]": cid})
        por_cmid = {}
        for crs in (data.get("courses", []) if isinstance(data, dict) else []):
            for a in crs.get("assignments", []):
                cmid = str(a.get("cmid") or a.get("id"))
                por_cmid[cmid] = a
                # También indexar por a['id']
                por_cmid[str(a.get("id"))] = a
        return por_cmid
    except Exception:
        return {}

def escanear_archivos_locales(dir_ramo):
    """Escanea los archivos descargados clasificados en el ramo."""
    archivos = {}
    for sub in ["Evaluaciones_y_Entregas", "Material_y_Apuntes", "Planificacion"]:
        sdir = os.path.join(dir_ramo, sub)
        if os.path.exists(sdir):
            for root, _, files in os.walk(sdir):
                for f in files:
                    if f.startswith(".") or f == "desktop.ini":
                        continue
                    full_p = os.path.join(root, f)
                    rel = os.path.relpath(full_p, dir_ramo).replace(os.sep, "/")
                    st = os.stat(full_p)
                    archivos[f] = {
                        "relpath": rel,
                        "subcarpeta": sub,
                        "size": st.st_size,
                        "mtime": int(st.st_mtime)
                    }
    return archivos

def cargar_evaluaciones_ramo(sigla, short_name):
    """Carga evaluaciones desde evaluaciones.json."""
    evals_path = os.path.join(BASE_DIR, "evaluaciones.json")
    if not os.path.exists(evals_path):
        evals_path = os.path.join(REPO_DIR, "universidad", "2026-2", "evaluaciones.json")
    if not os.path.exists(evals_path):
        return []
    try:
        with open(evals_path, "r", encoding="utf-8") as f:
            all_evals = json.load(f)
        ramo_evals = []
        for e in all_evals:
            r = (e.get("ramo") or "").strip().lower()
            c = (e.get("codigo") or "").strip().lower()
            if r == short_name.lower() or c == sigla.lower() or r == sigla.lower():
                ramo_evals.append(e)
        return ramo_evals
    except Exception:
        return []

def cargar_avisos_recientes(dir_ramo, max_avisos=5):
    """Lee avisos.md y extrae los últimos avisos docentes."""
    avisos_path = os.path.join(dir_ramo, "avisos.md")
    if not os.path.exists(avisos_path):
        return []
    try:
        with open(avisos_path, "r", encoding="utf-8") as f:
            content = f.read()
        secciones = re.split(r"\n##\s+", content)
        avisos = []
        for sec in secciones[1:]:
            lineas = sec.strip().splitlines()
            if not lineas:
                continue
            titulo = lineas[0].strip()
            alerta = any("POSIBLE CAMBIO DE EVALUACIÓN" in l for l in lineas[:4])
            fecha = ""
            autor = ""
            for l in lineas[1:6]:
                if l.startswith("- **Fecha:**"):
                    fecha = l.replace("- **Fecha:**", "").strip()
                elif l.startswith("- **Autor:**"):
                    autor = l.replace("- **Autor:**", "").strip()
            # Cuerpo
            cuerpo = "\n".join(l for l in lineas[4:] if not l.startswith("- **") and not l.startswith("---")).strip()
            avisos.append({
                "titulo": titulo,
                "fecha": fecha,
                "autor": autor,
                "alerta": alerta,
                "cuerpo": cuerpo[:400] + ("..." if len(cuerpo) > 400 else "")
            })
            if len(avisos) >= max_avisos:
                break
        return avisos
    except Exception:
        return []

def generar_contexto_para_ramo(cmeta, client=None, now_dt=None):
    if now_dt is None:
        now_dt = datetime.now(TZ)

    dir_ramo = os.path.join(BASE_DIR, cmeta["folder"])
    os.makedirs(dir_ramo, exist_ok=True)

    cid = cmeta["id"]
    sigla = cmeta["sigla"]
    short_name = cmeta["short"]

    # 1. Datos de Aula
    sections = extraer_secciones_y_modulos(client, cid, dir_ramo)
    assignments_api = extraer_tareas_asignadas(client, cid)
    evaluaciones = cargar_evaluaciones_ramo(sigla, short_name)
    avisos = cargar_avisos_recientes(dir_ramo, max_avisos=6)
    archivos_locales = escanear_archivos_locales(dir_ramo)

    # 2. Cargar estado previo para detección incremental
    estado_path = os.path.join(dir_ramo, ".contexto_estado.json")
    estado_previo = {}
    if os.path.exists(estado_path):
        try:
            with open(estado_path, "r", encoding="utf-8") as ef:
                estado_previo = json.load(ef)
        except Exception:
            estado_previo = {}

    # Construir estado actual
    archivos_keys = {f: d["size"] for f, d in archivos_locales.items()}
    assign_keys = {}
    for cmid, a in assignments_api.items():
        assign_keys[str(cmid)] = {
            "name": a.get("name"),
            "due": a.get("duedate"),
            "cutoff": a.get("cutoffdate"),
            "attachments": [x.get("filename") for x in a.get("introattachments", [])]
        }
    avisos_titulos = [a["titulo"] for a in avisos]

    estado_actual = {
        "timestamp": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "archivos": archivos_keys,
        "assignments": assign_keys,
        "avisos": avisos_titulos,
        "n_sections": len(sections),
        "n_modules": sum(len(s.get("modules", [])) for s in sections)
    }

    # Calcular diferencias incrementales
    cambios_detectados = []
    if estado_previo:
        # Nuevos archivos
        viejos_archivos = estado_previo.get("archivos", {})
        nuevos_f = [f for f in archivos_keys if f not in viejos_archivos]
        if nuevos_f:
            cambios_detectados.append(f"Nuevos archivos en disco y repo: {', '.join(nuevos_f)}")

        # Tareas modificadas o nuevas
        viejas_a = estado_previo.get("assignments", {})
        for cmid, a_data in assign_keys.items():
            if cmid not in viejas_a:
                cambios_detectados.append(f"Nueva tarea / entrega en Aula: «{a_data['name']}» (Vence: {ts_to_str(a_data['due'])})")
            else:
                old_due = viejas_a[cmid].get("due")
                if old_due != a_data["due"]:
                    cambios_detectados.append(f"Fecha modificada en «{a_data['name']}»: {ts_to_str(old_due)} → {ts_to_str(a_data['due'])}")

        # Nuevos avisos
        viejos_av = set(estado_previo.get("avisos", []))
        nuevos_av = [a for a in avisos_titulos if a not in viejos_av]
        if nuevos_av:
            cambios_detectados.append(f"Nuevos avisos docentes en foros: {', '.join(nuevos_av)}")

    # Guardar nuevo estado
    try:
        with open(estado_path, "w", encoding="utf-8") as ef:
            json.dump(estado_actual, ef, indent=2, ensure_ascii=False)
    except Exception:
        pass

    # 3. Leer historial previo de Contexto_Asignatura.md si existe
    contexto_md_path = os.path.join(dir_ramo, "Contexto_Asignatura.md")
    historial_previo = ""
    if os.path.exists(contexto_md_path):
        try:
            with open(contexto_md_path, "r", encoding="utf-8") as cf:
                md_text = cf.read()
            idx = md_text.find("## 📜 Historial Incremental de Cambios")
            if idx != -1:
                historial_previo = md_text[idx + len("## 📜 Historial Incremental de Cambios"):].strip()
        except Exception:
            historial_previo = ""

    # Preparar nuevo bloque de historial
    fecha_actual_str = now_dt.strftime("%Y-%m-%d %H:%M -03")
    nuevo_bloque_historial = ""
    if cambios_detectados:
        lineas_h = [f"### 🔄 Actualización: {fecha_actual_str}"]
        for c in cambios_detectados:
            lineas_h.append(f"- {c}")
        nuevo_bloque_historial = "\n".join(lineas_h)
    elif not historial_previo:
        nuevo_bloque_historial = (
            f"### 🚀 Línea Base de Contexto: {fecha_actual_str}\n"
            f"- Inicialización integral del archivo de contexto de la asignatura a partir de Aula USM.\n"
            f"- Total de {len(sections)} secciones y {sum(len(s.get('modules', [])) for s in sections)} módulos registrados.\n"
            f"- {len(archivos_locales)} archivos clasificados en disco, git y respaldo en Google Drive.\n"
            f"- {len(evaluaciones)} eventos de evaluación sincronizados con calendario oficial."
        )

    historial_completo = ""
    if nuevo_bloque_historial and historial_previo:
        historial_completo = f"{nuevo_bloque_historial}\n\n{historial_previo}"
    elif nuevo_bloque_historial:
        historial_completo = nuevo_bloque_historial
    else:
        historial_completo = historial_previo or "Sin cambios registrados desde la línea base."

    # 4. Construir Documento Markdown
    L = []
    L.append(f"# 📘 Contexto Integral de Asignatura: {cmeta['nombre']}")
    L.append(f"**Sigla:** `{sigla}` | **Aula ID:** `{cid}` | **Semestre:** 2026-2 (UTFSM)")
    L.append(f"**URL Aula USM:** https://aula.usm.cl/course/view.php?id={cid}")
    L.append(f"**Última Sincronización:** `{fecha_actual_str}`")
    L.append("")
    L.append("> [!NOTE]")
    L.append(f"> Este archivo es la **fuente única de verdad** para Claude y agentes de asistencia académica sobre `{sigla}`.")
    L.append("> Describe exhaustivamente todo el contenido publicado en Aula USM, fechas, entregas, pautas, archivos y estado actual.")
    L.append("")

    # Ficha Técnica
    L.append("## 📋 1. Ficha Técnica y Programa Oficial")
    L.append(f"- **Asignatura:** {cmeta['nombre']} ({sigla})")
    L.append(f"- **Departamento:** {cmeta['depto']}")
    L.append(f"- **Carga y Dedicación:** {cmeta['sct']}")
    L.append(f"- **Profesor / Coordinación:** {cmeta['profesor']}")
    L.append(f"- **Horarios y Salas:**\n  - {cmeta['horarios']}")
    L.append("")
    L.append("### 🎯 Descripción Oficial")
    L.append(cmeta['descripcion'])
    L.append("")

    # Calendario y Evaluaciones
    L.append("## 📅 2. Calendario Consolidado de Evaluaciones y Entregas")
    if evaluaciones:
        L.append("| # | Evaluación / Hito | Inicio | Cierre / Entrega | Cuenta Regresiva | Lugar | Fuente |")
        L.append("|---|-------------------|--------|------------------|------------------|-------|--------|")
        for i, ev in enumerate(evaluaciones, 1):
            nom = ev.get("evaluacion", "Evaluación")
            ini = ev.get("inicio", "")[:16].replace("T", " ")
            fin = ev.get("fin", "")[:16].replace("T", " ")
            lug = ev.get("lugar", "Aula USM")
            fte = "Manual" if "manual" in ev.get("fuente", "") else "Aula API"
            
            # Cuenta regresiva basada en fin o inicio
            ts_ev = None
            try:
                dt_fin = datetime.fromisoformat(ev.get("fin", ""))
                ts_ev = int(dt_fin.timestamp())
            except Exception:
                pass
            cd = get_countdown(ts_ev, now_dt)
            L.append(f"| {i} | **{nom}** | {ini} | {fin} | {cd} | {lug} | {fte} |")
    else:
        L.append("*No hay evaluaciones registradas en el calendario oficial.*")
    L.append("")

    # Tareas y Entregas con enunciados
    L.append("## 📝 3. Entregas, Tareas y Asignaciones en Aula (mod_assign)")
    asignaciones_mostradas = 0
    for sec in sections:
        for m in sec.get("modules", []):
            mtype = m.get("modname", "")
            if mtype == "assign":
                asignaciones_mostradas += 1
                mid = str(m.get("id"))
                m_name = m.get("name", "Entrega")
                m_url = m.get("url") or f"https://aula.usm.cl/mod/assign/view.php?id={mid}"
                
                # Datos de mod_assign_get_assignments
                a_data = assignments_api.get(mid) or {}
                due_ts = a_data.get("duedate")
                cutoff_ts = a_data.get("cutoffdate")
                allow_ts = a_data.get("allowsubmissionsfromdate")
                intro_html = a_data.get("intro") or m.get("description") or ""
                intro_txt = clean_html(intro_html)
                adjuntos = [x.get("filename") for x in a_data.get("introattachments", [])]
                
                L.append(f"### 📌 {m_name}")
                L.append(f"- **Enlace en Aula:** [{m_name}]({m_url})")
                L.append(f"- **Sección:** {sec.get('name')}")
                if allow_ts:
                    L.append(f"- **Habilitada desde:** {ts_to_str(allow_ts)}")
                L.append(f"- **Fecha Límite (Due Date):** {ts_to_str(due_ts)} ({get_countdown(due_ts, now_dt)})")
                if cutoff_ts:
                    L.append(f"- **Fecha de Corte Estricto:** {ts_to_str(cutoff_ts)}")
                
                if adjuntos:
                    L.append(f"- **Archivos de Enunciado Adjuntos:**")
                    for att in adjuntos:
                        loc = archivos_locales.get(att)
                        loc_str = f" (`{loc['relpath']}`)" if loc else " (Descarga gestionada)"
                        L.append(f"  - 📄 **{att}**{loc_str}")
                
                if intro_txt:
                    L.append(f"\n> **Instrucciones / Enunciado:**\n> " + intro_txt.replace("\n", "\n> ") + "\n")
                else:
                    L.append("- **Instrucciones:** *Sin texto adicional en la descripción; ver archivos adjuntos.*")
                L.append("")
    if asignaciones_mostradas == 0:
        L.append("*No se registran módulos de tipo entrega en este curso.*")
        L.append("")

    # Estructura Completa de Secciones y Módulos de Aula
    L.append("## 🗂️ 4. Estructura Detallada de Unidades y Módulos en Aula USM")
    for sec_idx, sec in enumerate(sections):
        s_name = sec.get("name") or f"Sección {sec_idx}"
        s_resumen = clean_html(sec.get("summary", ""))
        mods = sec.get("modules", [])
        
        L.append(f"### Sección: {s_name}")
        if s_resumen:
            L.append(f"> {s_resumen}")
            L.append("")
            
        if not mods:
            L.append("*Sin módulos publicados en esta sección.*")
            L.append("")
            continue
            
        for m in mods:
            m_type = m.get("modname", "")
            m_nom = m.get("name", "").strip()
            m_desc = clean_html(m.get("description", ""))
            contents = m.get("contents", [])
            files = [c for c in contents if c.get("type") == "file"]
            
            tipo_icon = {
                "folder": "📁 Carpeta",
                "resource": "📄 Documento/Recurso",
                "assign": "📝 Tarea/Entrega",
                "forum": "💬 Foro",
                "label": "🏷️ Etiqueta/Texto",
                "url": "🔗 Enlace Externo"
            }.get(m_type, f"📦 {m_type}")
            
            if m_type == "label":
                if m_desc:
                    L.append(f"- **{tipo_icon}:** {m_desc}")
                elif m_nom and not m_nom.lower().startswith("etiqueta"):
                    L.append(f"- **{tipo_icon}:** {m_nom}")
                continue
                
            L.append(f"- **[{tipo_icon}] {m_nom}**")
            if m_desc:
                L.append(f"  - *Descripción:* {m_desc}")
            if files:
                for f in files:
                    fname = f.get("filename", "")
                    fsize = format_bytes(int(f.get("filesize", 0)))
                    floc = archivos_locales.get(fname)
                    f_rel = f" -> `{floc['relpath']}`" if floc else ""
                    L.append(f"  - 📎 `{fname}` ({fsize}){f_rel}")
        L.append("")

    # Inventario Físico de Archivos
    L.append("## 💾 5. Inventario de Archivos Locales en Disco y Google Drive")
    L.append(f"Total de archivos sincronizados: **{len(archivos_locales)}**")
    L.append("")
    for sub in ["Evaluaciones_y_Entregas", "Material_y_Apuntes", "Planificacion"]:
        sub_files = [d for d in archivos_locales.values() if d["subcarpeta"] == sub]
        sub_files.sort(key=lambda x: x["relpath"].lower())
        L.append(f"### 📂 `{sub}/` ({len(sub_files)} archivos)")
        if sub_files:
            L.append("| Archivo | Tamaño | Modificado | Estado Google Drive |")
            L.append("|---------|--------|------------|---------------------|")
            for sf in sub_files:
                f_name = os.path.basename(sf["relpath"])
                sz = format_bytes(sf["size"])
                mt = ts_to_str(sf["mtime"])
                L.append(f"| `{f_name}` | {sz} | {mt} | Sincronizado |")
        else:
            L.append("*No hay archivos en esta carpeta.*")
        L.append("")

    # Avisos Recientes de Foros
    L.append("## 📢 6. Avisos y Novedades Docentes (Foros de Aula)")
    if avisos:
        for av in avisos:
            alerta_str = " ⚠️ **[POSIBLE CAMBIO DE EVALUACIÓN]**" if av["alerta"] else ""
            L.append(f"### 📣 {av['titulo']}{alerta_str}")
            L.append(f"- **Fecha:** {av['fecha']} | **Autor:** {av['autor']}")
            if av["cuerpo"]:
                L.append(f"> {av['cuerpo']}")
            L.append("")
    else:
        L.append("*No se registran avisos recientes en los foros.*")
        L.append("")

    # Historial Incremental
    L.append("## 📜 Historial Incremental de Cambios")
    L.append(historial_completo)
    L.append("")

    contenido_final = "\n".join(L)
    with open(contexto_md_path, "w", encoding="utf-8") as out_f:
        out_f.write(contenido_final)

    return contexto_md_path, len(cambios_detectados)

def generar_contexto_semestre(now_dt=None):
    """Genera el resumen global maestro en universidad/2026-2/Contexto_Semestre_2026-2.md."""
    if now_dt is None:
        now_dt = datetime.now(TZ)
    fecha_actual_str = now_dt.strftime("%Y-%m-%d %H:%M -03")
    
    evals_path = os.path.join(BASE_DIR, "evaluaciones.json")
    if not os.path.exists(evals_path):
        evals_path = os.path.join(REPO_DIR, "universidad", "2026-2", "evaluaciones.json")
    all_evals = []
    if os.path.exists(evals_path):
        try:
            with open(evals_path, "r", encoding="utf-8") as f:
                all_evals = json.load(f)
        except Exception:
            all_evals = []

    L = []
    L.append("# 🎓 Contexto Maestro del Semestre 2026-2 (UTFSM)")
    L.append(f"**Estudiante:** Nicolás Eduardo Albornoz Pavez (`nicolas.albornozp@usm.cl`)")
    L.append(f"**Carrera:** Ingeniería Civil — Universidad Técnica Federico Santa María")
    L.append(f"**Fecha de Corte:** `{fecha_actual_str}`")
    L.append("")
    L.append("> [!IMPORTANT]")
    L.append("> Este documento indexa y resume el estado actual del semestre 2026-2.")
    L.append("> Cada asignatura cuenta con su archivo de **contexto incremental detallado** (`Contexto_Asignatura.md`),")
    L.append("> donde se describen minuciosamente todas las actividades, pautas, enunciados de tareas, apuntes y foros.")
    L.append("")
    
    L.append("## 📚 1. Asignaturas Cursadas y Enlaces a Contextos Detallados")
    L.append("| Sigla | Ramo | Aula ID | SCT | Dedicación / Horarios | Contexto Detallado |")
    L.append("|-------|------|---------|-----|-----------------------|--------------------|")
    for cm in COURSES_META:
        rel_link = f"[{cm['folder'][:10]}... Contexto]({cm['folder']}/Contexto_Asignatura.md)"
        L.append(f"| **{cm['sigla']}** | {cm['nombre']} | `{cm['id']}` | {cm['sct'].split('(')[-1].replace(')', '') if '(' in cm['sct'] else '—'} | {cm['horarios'].split('|')[0].strip()} | {rel_link} |")
    L.append("")

    L.append("## 🚨 2. Cronograma Maestro de Evaluaciones Pendientes y Próximas")
    L.append("| Fecha | Asignatura | Evaluación / Hito | Cuenta Regresiva | Lugar |")
    L.append("|-------|------------|-------------------|------------------|-------|")
    for ev in all_evals:
        fin_str = ev.get("fin", "")[:16].replace("T", " ")
        ts_ev = None
        try:
            dt_fin = datetime.fromisoformat(ev.get("fin", ""))
            ts_ev = int(dt_fin.timestamp())
        except Exception:
            pass
        cd = get_countdown(ts_ev, now_dt)
        if cd != "Finalizada":
            L.append(f"| **{fin_str}** | `{ev.get('codigo')}` ({ev.get('ramo')}) | {ev.get('evaluacion')} | **{cd}** | {ev.get('lugar')} |")
    L.append("")

    master_path = os.path.join(BASE_DIR, "Contexto_Semestre_2026-2.md")
    with open(master_path, "w", encoding="utf-8") as mf:
        mf.write("\n".join(L))
    return master_path

def main():
    sys.path.insert(0, os.path.join(REPO_DIR, "scripts"))
    try:
        import sincronizar_aula_semanal as s
        tok = s.get_token()
        client = s.MoodleAPIClient(s.BASE_URL, tok) if tok else None
    except Exception:
        client = None

    now_dt = datetime.now(TZ)
    print(f"[{now_dt.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando generación de contextos de asignaturas...")
    for cm in COURSES_META:
        p, n_c = generar_contexto_para_ramo(cm, client=client, now_dt=now_dt)
        print(f"  ✓ {cm['sigla']} ({cm['short']}): generado en {os.path.basename(p)} ({n_c} cambios detectados)")

    m_path = generar_contexto_semestre(now_dt=now_dt)
    print(f"  ✓ Resumen maestro generado en: {os.path.basename(m_path)}")
    print("Completado exitosamente.")

if __name__ == "__main__":
    main()
