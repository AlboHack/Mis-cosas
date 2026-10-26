#!/usr/bin/env python3
"""
scripts/sincronizar_calendario_android.py
Sincronización determinística e idempotente de evaluaciones con el calendario nativo de Android.
Utiliza 'uid' como llave primaria y gestiona migración automática para evitar duplicados.
Guarda el estado local de la tablet en ~/.calendario_mapping.json (fuera del repositorio).
"""
import subprocess
import json
import re
import os
import sys
import shlex
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=-3))
ACCOUNT = "albornoz.pavez@gmail.com"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.environ.get("SYNC_REPO_DIR", os.path.dirname(SCRIPT_DIR))
DEFAULT_EVALUACIONES = os.environ.get("CALENDAR_EVALUACIONES_FILE", os.path.join(REPO_ROOT, "universidad/2026-2/evaluaciones.json"))
DEFAULT_MAPPING = os.environ.get("CALENDAR_MAPPING_FILE", os.path.expanduser("~/.calendario_mapping.json"))

# Aislamiento en modo prueba
if os.environ.get("CALENDAR_TEST_MODE") == "1":
    _real_repo = os.path.realpath(os.path.expanduser("~/Mis-cosas"))
    _real_mapping = os.path.realpath(os.path.expanduser("~/.calendario_mapping.json"))
    resolved_m = os.path.realpath(os.path.expanduser(DEFAULT_MAPPING))
    resolved_e = os.path.realpath(os.path.expanduser(DEFAULT_EVALUACIONES))
    for p_name, p_val in [("CALENDAR_MAPPING_FILE", resolved_m), ("CALENDAR_EVALUACIONES_FILE", resolved_e)]:
        if (
            p_val.startswith("/storage/emulated/0")
            or p_val == _real_repo
            or p_val.startswith(_real_repo + os.sep)
            or p_val == _real_mapping
        ):
            raise AssertionError(f"ERROR DE AISLAMIENTO: {p_name} apunta a ruta protegida: {p_val}")

def simulate_adb_shell(cmd_str):
    sim_file = os.environ.get("CALENDAR_SIM_STATE_FILE", "/tmp/sim_cal_state.json")
    state = {"next_id": 100, "events": []}
    if os.path.exists(sim_file):
        try:
            with open(sim_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            pass

    if "content query --uri content://com.android.calendar/calendars" in cmd_str:
        return f"Row: 0 _id=1, ownerAccount={ACCOUNT}", 0

    if "content query --uri content://com.android.calendar/events" in cmd_str:
        if "--projection _id" in cmd_str and "dtstart=" in cmd_str:
            m = re.search(r'dtstart=(\d+)', cmd_str)
            target_dt = int(m.group(1)) if m else 0
            for ev in state["events"]:
                if ev.get("dtstart") == target_dt and not ev.get("deleted"):
                    return f"Row: 0 _id={ev['_id']}", 0
            return "", 0
        else:
            rows = []
            for i, ev in enumerate(state["events"]):
                if not ev.get("deleted"):
                    rows.append(
                        f"Row: {i} _id={ev['_id']}, title={ev.get('title','')}, "
                        f"dtstart={ev.get('dtstart',0)}, dtend={ev.get('dtend',0)}, "
                        f"eventLocation={ev.get('eventLocation','')}, description={ev.get('description','')}"
                    )
            return "\n".join(rows), 0

    def parse_binds(c):
        binds = {}
        tokens = shlex.split(c)
        i = 0
        while i < len(tokens):
            if tokens[i] == "--bind" and i + 1 < len(tokens):
                arg = tokens[i+1]
                parts = arg.split(":", 2)
                if len(parts) == 3:
                    col, t, val = parts
                    val = val.replace(r'\:', ':')
                    binds[col] = int(val) if t in ('l', 'i') else val
                i += 2
            else:
                i += 1
        return binds

    if "content insert --uri content://com.android.calendar/events" in cmd_str:
        binds = parse_binds(cmd_str)
        state["next_id"] += 1
        new_ev = dict(binds)
        new_ev["_id"] = state["next_id"]
        state["events"].append(new_ev)
        os.makedirs(os.path.dirname(sim_file), exist_ok=True)
        with open(sim_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return f"Inserted 1 row, result: content://com.android.calendar/events/{new_ev['_id']}", 0

    if "content update --uri content://com.android.calendar/events" in cmd_str:
        m_id = re.search(r'_id=(\d+)', cmd_str)
        if not m_id:
            return "No id", 1
        target_id = int(m_id.group(1))
        binds = parse_binds(cmd_str)
        for ev in state["events"]:
            if ev["_id"] == target_id:
                ev.update(binds)
                break
        os.makedirs(os.path.dirname(sim_file), exist_ok=True)
        with open(sim_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return "Updated 1 row", 0

    if "content insert --uri content://com.android.calendar/reminders" in cmd_str:
        return "Inserted 1 row", 0

    return "", 0

def adb_shell(cmd):
    if isinstance(cmd, list):
        cmd_str = " ".join(cmd)
    else:
        cmd_str = cmd
    if os.environ.get("CALENDAR_SIMULATE_ADB") == "1":
        return simulate_adb_shell(cmd_str)
    p = subprocess.run(["adb", "shell", cmd_str], capture_output=True, text=True)
    out = p.stdout.strip()
    if p.returncode != 0 or "[ERROR]" in out or "usage:" in out.lower():
        return out, 1
    return out, 0

def get_google_calendar_id():
    out, code = adb_shell(f"content query --uri content://com.android.calendar/calendars --projection _id:ownerAccount --where \"deleted=0 AND ownerAccount='{ACCOUNT}'\"")
    if code != 0 or not out:
        print(f"ERROR CRITICO: No se pudo consultar la cuenta {ACCOUNT} en com.android.calendar (código {code}).", file=sys.stderr)
        return None
    for row in out.splitlines():
        if ACCOUNT in row:
            m = re.search(r'_id=(\d+)', row)
            if m:
                return int(m.group(1))
    print(f"ERROR CRITICO: Cuenta {ACCOUNT} no encontrada en los calendarios activos de Android.", file=sys.stderr)
    return None

def escape_content_binding(val):
    """El comando 'content' de Android divide los argumentos --bind por ':'.
    Para preservar los dos puntos en el texto sin romper el parser, se escapan como '\\:'."""
    if val is None:
        return ""
    return str(val).replace(":", r"\:")

def sync_android_calendar(evaluaciones_path=DEFAULT_EVALUACIONES, mapping_path=DEFAULT_MAPPING):
    # Verificación estricta de archivo evaluaciones.json
    if not os.path.exists(evaluaciones_path):
        print(f"ERROR CRITICO: Archivo de evaluaciones ausente: {evaluaciones_path}", file=sys.stderr)
        return 1

    try:
        with open(evaluaciones_path, "r", encoding="utf-8") as f:
            evaluaciones = json.load(f)
    except Exception as e:
        print(f"ERROR CRITICO: Error leyendo {evaluaciones_path}: {e}", file=sys.stderr)
        return 1

    if not evaluaciones or len(evaluaciones) == 0:
        print(f"ERROR CRITICO: Archivo de evaluaciones vacío: {evaluaciones_path}", file=sys.stderr)
        return 1

    cal_id = get_google_calendar_id()
    if cal_id is None:
        return 1
        
    print(f"=== SINCRONIZANDO CON ANDROID GOOGLE CALENDAR (ID {cal_id}: {ACCOUNT}) ===", flush=True)
    
    # Consultar eventos activos (deleted=0)
    out_ev, code = adb_shell(f"content query --uri content://com.android.calendar/events --projection _id:title:dtstart:dtend:eventLocation:description --where \"calendar_id={cal_id} AND deleted=0\"")
    if code != 0:
        print("ERROR: Fallo al consultar eventos de calendario.", file=sys.stderr)
        return 1
        
    existing_by_id = {}
    existing_list = []
    for row in out_ev.splitlines():
        m_id = re.search(r'_id=(\d+)', row)
        m_ti = re.search(r'title=(.*?)(?:,\s*dtstart=)', row)
        m_st = re.search(r'dtstart=(\d+)', row)
        m_en = re.search(r'dtend=(\d+)', row)
        m_loc = re.search(r'eventLocation=(.*?)(?:,\s*description=)', row)
        m_desc = re.search(r'description=(.*)$', row)
        if m_id and m_ti and m_st:
            ev_id = m_id.group(1)
            item = {
                "id": ev_id,
                "title": m_ti.group(1).strip(),
                "dtstart": int(m_st.group(1)),
                "dtend": int(m_en.group(1)) if m_en else 0,
                "loc": m_loc.group(1).strip() if m_loc else "",
                "desc": m_desc.group(1).strip() if m_desc else ""
            }
            existing_by_id[ev_id] = item
            existing_list.append(item)

    # Cargar mapping uid -> _id
    mapping = {}
    mapping_modified = False
    if os.path.exists(mapping_path):
        try:
            with open(mapping_path, "r", encoding="utf-8") as mf:
                mapping = json.load(mf)
        except Exception as me:
            print(f"ADVERTENCIA: No se pudo leer {mapping_path}: {me}", file=sys.stderr)
            mapping = {}

    # 1. Purgar llaves obsoletas del mapping cuyos _id ya no existan en Android
    for uid in list(mapping.keys()):
        mapped_id = str(mapping[uid])
        if mapped_id not in existing_by_id:
            del mapping[uid]
            mapping_modified = True

    # 2. Migración y re-emparejamiento: si la llave no existe o fue purgada
    for ev in evaluaciones:
        uid = ev["uid"]
        if uid not in mapping:
            st_ms = int(datetime.fromisoformat(ev["inicio"]).timestamp() * 1000)
            ramo = ev.get("ramo", "").lower()
            evaluacion = ev.get("evaluacion", "").lower()
            
            # Buscar candidatos por hora de inicio (±1 h) y coincidencia de ramo
            candidates = []
            for ex in existing_list:
                if abs(ex["dtstart"] - st_ms) < 3600 * 1000 and (ramo in ex["title"].lower() or ramo in ex["desc"].lower()):
                    candidates.append(ex)
            
            if len(candidates) == 1:
                new_id = candidates[0]["id"]
                mapping[uid] = new_id
                mapping_modified = True
                print(f" AVISO: _id obsoleto para {uid}, re-emparejado con {new_id}")
            elif len(candidates) > 1:
                # Regla de seguridad ante ambigüedad
                c_titles = [c['title'] for c in candidates]
                print(f" [ERROR MIGRACIÓN AMBIGUA] Múltiples candidatos para {uid}: {c_titles}. No se asigna ninguno.", file=sys.stderr)
            else:
                # Fallback secundario: coincidencia exacta por título
                cand_title = [ex for ex in existing_list if ramo in ex["title"].lower() and any(w in ex["title"].lower() for w in evaluacion.split())]
                if len(cand_title) == 1:
                    new_id = cand_title[0]["id"]
                    mapping[uid] = new_id
                    mapping_modified = True
                    print(f" AVISO: _id obsoleto para {uid}, re-emparejado con {new_id}")

    if mapping_modified:
        os.makedirs(os.path.dirname(os.path.abspath(mapping_path)), exist_ok=True)
        with open(mapping_path, "w", encoding="utf-8") as mf:
            json.dump(mapping, mf, indent=2, ensure_ascii=False)
        os.chmod(mapping_path, 0o600)
        print(f" [MIGRACIÓN GUARDADA] Mapping UID -> _id guardado en {mapping_path} (chmod 600)")

    actualizados = 0
    insertados = 0
    errores = 0
    
    for ev in evaluaciones:
        uid = ev["uid"]
        ramo = ev.get("ramo", "")
        evaluacion = ev.get("evaluacion", "")
        
        # Título y descripción con dos puntos literales (sin sustituir por guión)
        titulo = f"{ramo}: {evaluacion}" if ":" not in evaluacion else f"{ramo} - {evaluacion}"
        loc = ev.get("lugar", "")
        fuente = ev.get("fuente", "Aula USM")
        desc = f"Evaluación {evaluacion} ({ramo}). Fuente: {fuente}."
        
        dt_start = int(datetime.fromisoformat(ev["inicio"]).timestamp() * 1000)
        dt_end = int(datetime.fromisoformat(ev["fin"]).timestamp() * 1000)
        
        target_id = mapping.get(uid)
        
        if target_id and str(target_id) in existing_by_id:
            cur = existing_by_id[str(target_id)]
            ev_id = str(target_id)
            
            # Comparación exacta: ambos lados usan el texto original sin sustituciones arbitrarias
            needs_update = (
                cur["dtstart"] != dt_start or
                cur["dtend"] != dt_end or
                cur["loc"] != loc or
                cur["desc"] != desc
            )
            
            if needs_update:
                update_cmd = (
                    f"content update --uri content://com.android.calendar/events "
                    f"--bind dtstart:l:{dt_start} "
                    f"--bind dtend:l:{dt_end} "
                    f"--bind eventLocation:s:\"{escape_content_binding(loc)}\" "
                    f"--bind description:s:\"{escape_content_binding(desc)}\" "
                    f"--where \"_id={ev_id}\""
                )
                _, u_code = adb_shell(update_cmd)
                if u_code == 0:
                    print(f" [ACTUALIZADO] {titulo} (UID {uid}, ID {ev_id}): horario/lugar/descripción alineados.", flush=True)
                    actualizados += 1
                else:
                    print(f" [ERROR AL ACTUALIZAR] {titulo} (UID {uid}, código {u_code})", file=sys.stderr)
                    errores += 1
        else:
            # Evento nuevo: insertar escapando los ':' para la invocación
            insert_cmd = (
                f"content insert --uri content://com.android.calendar/events "
                f"--bind calendar_id:i:{cal_id} "
                f"--bind title:s:\"{escape_content_binding(titulo)}\" "
                f"--bind description:s:\"{escape_content_binding(desc)}\" "
                f"--bind eventLocation:s:\"{escape_content_binding(loc)}\" "
                f"--bind dtstart:l:{dt_start} "
                f"--bind dtend:l:{dt_end} "
                f"--bind eventTimezone:s:\"America/Santiago\" "
                f"--bind hasAlarm:i:1"
            )
            _, i_code = adb_shell(insert_cmd)
            if i_code != 0:
                print(f" [ERROR AL INSERTAR] {titulo} (UID {uid}, código {i_code})", file=sys.stderr)
                errores += 1
                continue
                
            q_out, _ = adb_shell(f"content query --uri content://com.android.calendar/events --projection _id --where \"calendar_id={cal_id} AND dtstart={dt_start}\"")
            m_new = re.search(r'_id=(\d+)', q_out)
            if m_new:
                new_id = m_new.group(1)
                mapping[uid] = new_id
                mapping_modified = True
                for mins in [10080, 4320, 1440]:
                    adb_shell(f"content insert --uri content://com.android.calendar/reminders --bind event_id:i:{new_id} --bind minutes:i:{mins} --bind method:i:1")
                print(f" [INSERTADO] {titulo} (UID {uid}, ID {new_id}) con 3 alarmas (7d, 3d, 1d)", flush=True)
                insertados += 1
            else:
                print(f" [ERROR CRÍTICO] No se encontró _id tras insertar evento: {titulo} (UID {uid})", file=sys.stderr)
                errores += 1

    if mapping_modified:
        os.makedirs(os.path.dirname(os.path.abspath(mapping_path)), exist_ok=True)
        with open(mapping_path, "w", encoding="utf-8") as mf:
            json.dump(mapping, mf, indent=2, ensure_ascii=False)
        os.chmod(mapping_path, 0o600)

    print(f"Sincronizacion de calendario finalizada: {insertados} insertados, {actualizados} actualizados, {errores} errores.", flush=True)
    return 0 if errores == 0 else 1

if __name__ == "__main__":
    epath = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_EVALUACIONES
    mpath = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MAPPING
    sys.exit(sync_android_calendar(epath, mpath))
