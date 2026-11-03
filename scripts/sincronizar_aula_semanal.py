#!/data/data/com.agycli/files/usr/bin/python3
"""
sincronizar_aula_semanal.py
Sincronización incremental determinística de Aula USM con Google Drive, GitHub y Google Calendar.
Utiliza el servicio Moodle Web Services (Mobile API) con token persistente y lista blanca estricta.
Cumple con los estándares de seguridad, enmascaramiento de tokens, e idempotencia.
"""

import urllib.request
import urllib.parse
import re
import json
import os
import subprocess
import hashlib
import shutil
import fcntl
import sys
import unicodedata
from datetime import datetime, timezone, timedelta

# Asegurar rutas de búsqueda para módulos locales
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)
_home_dir = "/data/data/com.agycli/files/home"
if _home_dir not in sys.path:
    sys.path.insert(0, _home_dir)

from aula_novedades import sincronizar_novedades  # noqa: E402

BASE_URL = os.environ.get("MOODLE_BASE_URL", "https://aula.usm.cl")
ROOT_DIR = os.environ.get("SYNC_ROOT_DIR", "/storage/emulated/0/Download/Universidad/2026-2")
DELTA_DIR = os.environ.get("SYNC_DELTA_DIR", "/storage/emulated/0/Download")
REPO_DIR = os.environ.get("SYNC_REPO_DIR", "/data/data/com.agycli/files/home/Mis-cosas")
LOG_FILE = os.environ.get("SYNC_LOG_FILE", "/storage/emulated/0/Download/Universidad/Registro_Sincronizaciones.log")
TOKEN_FILE = os.environ.get("MOODLE_TOKEN_FILE", os.path.expanduser("~/.moodle_token"))
META_FILE = os.environ.get("MOODLE_META_FILE", os.path.expanduser("~/.moodle_token.meta"))
MANIFEST_FILE = os.environ.get("SYNC_MANIFEST_FILE", "/storage/emulated/0/Download/Universidad/sync_manifest.json")
LOCK_FILE = os.environ.get("SYNC_LOCK_FILE", os.path.expanduser("~/.sync_aula.lock"))
# Mensajes privados: solo en la tablet (fuera del repo y fuera de la carpeta respaldada en Drive)
MENSAJES_FILE = os.environ.get("SYNC_MENSAJES_FILE", "/storage/emulated/0/Download/Universidad/mensajes_privados_aula.md")

# Verificación estricta de aislamiento en modo prueba
if os.environ.get("SYNC_TEST_MODE") == "1":
    _real_repo = os.path.realpath(os.path.expanduser("~/Mis-cosas"))
    for path_name, path_val in [
        ("SYNC_ROOT_DIR", ROOT_DIR),
        ("SYNC_DELTA_DIR", DELTA_DIR),
        ("SYNC_REPO_DIR", REPO_DIR),
        ("SYNC_LOG_FILE", LOG_FILE),
        ("SYNC_MANIFEST_FILE", MANIFEST_FILE),
        ("SYNC_MENSAJES_FILE", MENSAJES_FILE)
    ]:
        resolved = os.path.realpath(os.path.expanduser(path_val))
        if (
            resolved.startswith("/storage/emulated/0")
            or resolved == _real_repo
            or resolved.startswith(_real_repo + os.sep)
        ):
            raise AssertionError(f"ERROR DE AISLAMIENTO: {path_name} apunta a ruta protegida: {resolved}")

TZ = timezone(timedelta(hours=-3))

HASH_CACHE_FILE = os.environ.get("SYNC_HASH_CACHE", os.path.expanduser("~/.sync_hash_cache.json"))
_hash_cache = None
_hash_cache_sucio = False


def _cache_hashes():
    global _hash_cache
    if _hash_cache is None:
        _hash_cache = {}
        try:
            with open(HASH_CACHE_FILE, "r", encoding="utf-8") as f:
                _hash_cache = json.load(f)
        except Exception:
            _hash_cache = {}
    return _hash_cache


def compute_file_sha256(filepath):
    """SHA-256 de un archivo, reutilizando el valor guardado si tamaño y fecha no cambiaron.

    Evita recalcular cada corrida el hash de todo el material (cientos de MB en la tablet).
    La firma (tamaño, mtime en ns) cambia si el archivo se reescribe, y entonces se recalcula.
    """
    global _hash_cache_sucio
    try:
        st = os.stat(filepath)
    except OSError:
        return ""
    clave = os.path.realpath(filepath)
    firma = [st.st_size, st.st_mtime_ns]
    cache = _cache_hashes()
    previo = cache.get(clave)
    if previo and previo[:2] == firma:
        return previo[2]
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as fp:
            while chunk := fp.read(65536):
                h.update(chunk)
    except Exception:
        return ""
    cache[clave] = firma + [h.hexdigest()]
    _hash_cache_sucio = True
    return h.hexdigest()


def copiar_con_hash(origen, destino):
    """shutil.copy2 conserva la fecha del origen: si el destino ya estaba en el caché con el mismo
    tamaño y esa misma fecha, su hash anterior pasaría por vigente. Se registra el hash del origen."""
    global _hash_cache_sucio
    sha = compute_file_sha256(origen)
    shutil.copy2(origen, destino)
    st = os.stat(destino)
    if sha:
        _cache_hashes()[os.path.realpath(destino)] = [st.st_size, st.st_mtime_ns, sha]
        _hash_cache_sucio = True


def guardar_cache_hashes():
    """Guarda el caché de hashes (descarta rutas que ya no existen). Escritura atómica."""
    global _hash_cache_sucio
    cache = _cache_hashes()
    vivos = {k: v for k, v in cache.items() if os.path.exists(k)}
    if not _hash_cache_sucio and len(vivos) == len(cache):
        return
    try:
        os.makedirs(os.path.dirname(HASH_CACHE_FILE) or ".", exist_ok=True)
        tmp = HASH_CACHE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(vivos, f)
        os.replace(tmp, HASH_CACHE_FILE)
        _hash_cache_sucio = False
    except Exception as e:
        log(f"  AVISO: no se pudo guardar el caché de hashes: {e}")


RCLONE_SUBCOMANDOS_DESTRUCTIVOS = {"sync", "move", "moveto", "delete", "deletefile", "purge", "rmdir", "rmdirs", "cleanup", "dedupe"}


def construir_comando_respaldo_arbol(rclone_bin, origen, destino, dry_run=False):
    """Comando rclone para respaldar el árbol local en Drive.

    Usa `copy`: agrega y actualiza archivos en el destino, pero nunca borra allí lo que
    falte en origen. Así una carpeta local vacía o dañada no se replica en el respaldo.
    """
    cmd = [
        rclone_bin, "copy", origen, destino,
        "--fast-list",
        "--drive-chunk-size", "64M",
        "--transfers", "3",
        "--checkers", "6",
        "--update",
    ]
    if dry_run:
        cmd.append("--dry-run")
    if cmd[1] in RCLONE_SUBCOMANDOS_DESTRUCTIVOS or any(a.startswith("--delete") for a in cmd):
        raise AssertionError(f"Comando rclone destructivo no permitido: {cmd[1]}")
    return cmd


DRIVE_DESTINO = "gdrive:Universidad/2026-2"


def respaldar_en_drive(rclone_bin, archivos_nuevos, dry_run=False, run=subprocess.run):
    """Copia el árbol local a Drive con la misma estructura (ramo/subcarpeta/archivo) y verifica.

    - Corre en todas las corridas (no solo con archivos nuevos): si una semana falló la subida,
      la siguiente la completa. `copy --update` solo transfiere lo que falta o cambió.
    - Cada archivo nuevo se verifica en su ruta final de Drive con `rclone lsjson` (nombre y tamaño).
    - Sin paquetes ZIP ni carpeta Deltas.
    Devuelve la lista de errores (vacía si todo quedó en su lugar).
    """
    errores = []
    cmd = construir_comando_respaldo_arbol(rclone_bin, ROOT_DIR, DRIVE_DESTINO + "/", dry_run)
    log(f"Respaldando el espejo de Aula en Google Drive ({DRIVE_DESTINO}/<ramo>/<sección>)...")
    r = run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return [f"Fallo rclone copy árbol ({r.returncode}): {(r.stderr or '').strip()}"]
    if dry_run:
        return errores
    for local in archivos_nuevos:
        rel = os.path.relpath(local, ROOT_DIR).replace(os.sep, "/")
        destino = f"{DRIVE_DESTINO}/{rel}"
        chk = run([rclone_bin, "lsjson", destino], capture_output=True, text=True)
        ok = False
        if chk.returncode == 0:
            try:
                items = json.loads((chk.stdout or "").strip() or "[]")
                ok = len(items) == 1 and items[0].get("Size") == os.path.getsize(local)
            except ValueError:
                ok = False
        if ok:
            log(f"  [DRIVE] {rel}")
        else:
            errores.append(f"No verificado en Drive: {rel}")
    if archivos_nuevos and not errores:
        log(f"¡{len(archivos_nuevos)} archivo(s) nuevo(s) verificados en su carpeta de Drive!")
    return errores


def actualizar_manifest_sha256(root_dir):
    """Genera/actualiza manifest_sha256.json en la raíz del árbol para auditoría estricta e integridad en Drive."""
    try:
        manifest = {}
        for root, dirs, files in os.walk(root_dir):
            for f in sorted(files):
                if f == 'manifest_sha256.json':
                    continue
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, root_dir)
                sha = compute_file_sha256(full_path)
                if sha:
                    manifest[rel_path] = {
                        "sha256": sha,
                        "bytes": os.path.getsize(full_path)
                    }
        manifest_path = os.path.join(root_dir, "manifest_sha256.json")
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump(manifest, mf, indent=2, ensure_ascii=False)
        return manifest_path
    except Exception as me:
        log(f"  [ADVERTENCIA] Error al generar manifest_sha256: {me}")
        return None

def to_timestamp_safe(dt_val):
    """Convierte fecha ISO o timestamp a float de forma segura ante naive/aware."""
    if isinstance(dt_val, (int, float)):
        return float(dt_val)
    if isinstance(dt_val, str):
        try:
            dt = datetime.fromisoformat(dt_val)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=TZ)
            return dt.timestamp()
        except Exception:
            return None
    return None


def log(msg, token_to_mask=None):
    if token_to_mask:
        msg = msg.replace(token_to_mask, "[TOKEN_MASKED]")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted, flush=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def sanitizar(nombre):
    clean = re.sub(r'[/\\?%*:|"<>]', '_', nombre).strip()
    return unicodedata.normalize('NFC', clean)

def strip_html_tags(text):
    clean = re.sub(r'<[^>]+>', '', text)
    return unicodedata.normalize('NFC', clean).strip()

class InvalidTokenError(Exception):
    """Lanzada cuando la API Moodle reporta errorcode == 'invalidtoken'."""
    pass

class WhitelistViolationError(Exception):
    """Lanzada cuando se intenta invocar una función no autorizada en la lista blanca."""
    pass

class MoodleAPIClient:
    """Cliente para Moodle Web Services con lista blanca estricta y protección de credenciales."""
    ALLOWED_FUNCTIONS = {
        "core_webservice_get_site_info",
        "core_course_get_contents",
        "core_calendar_get_calendar_events",
        "mod_forum_get_forum_discussions",
        "mod_forum_get_forums_by_courses",
        "mod_forum_get_discussion_posts",
        "core_message_get_conversations",
        "core_message_get_conversation_messages",
        "mod_assign_get_assignments"  # solo lectura: enunciados adjuntos a las entregas
    }

    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.token = token.strip()
        self.endpoint = f"{self.base_url}/webservice/rest/server.php"

    def call(self, wsfunction, params=None):
        if wsfunction not in self.ALLOWED_FUNCTIONS:
            raise WhitelistViolationError(f"Función no permitida en lista blanca: {wsfunction}")

        payload = {
            'wstoken': self.token,
            'wsfunction': wsfunction,
            'moodlewsrestformat': 'json'
        }
        if params:
            payload.update(params)

        try:
            encoded_data = urllib.parse.urlencode(payload).encode('utf-8')
            req = urllib.request.Request(
                self.endpoint,
                data=encoded_data,
                headers={'User-Agent': 'Antigravity-Sync/1.0'}
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                raw = resp.read().decode('utf-8', errors='ignore')
                data = json.loads(raw)
        except Exception as e:
            clean_err = str(e).replace(self.token, "[TOKEN_MASKED]")
            raise RuntimeError(clean_err) from None

        if isinstance(data, dict) and "errorcode" in data:
            errcode = data["errorcode"]
            if errcode == "invalidtoken":
                raise InvalidTokenError("ERROR CRÍTICO: token de Aula expirado, Nicolás debe renovarlo")
            raise RuntimeError(f"Error Moodle API ({errcode}): {data.get('message', '')}")

        return data

    def download_file(self, fileurl, dest_path):
        """Descarga de archivos intentando POST con token en el cuerpo; si falla, usa GET."""
        clean_url = fileurl.replace(self.token, "[TOKEN_MASKED]")
        content = None
        
        # 1. Intentar POST con token en el cuerpo (evita token en URL)
        try:
            post_data = urllib.parse.urlencode({'token': self.token}).encode('utf-8')
            req = urllib.request.Request(
                fileurl,
                data=post_data,
                headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Xiaomi Pad 5)'}
            )
            with urllib.request.urlopen(req, timeout=40) as resp:
                content = resp.read()
        except Exception:
            # 2. Si POST falla (ej. 405 Method Not Allowed), fallback a GET con ?token=...
            try:
                sep = '&' if '?' in fileurl else '?'
                get_url = f"{fileurl}{sep}token={self.token}"
                req = urllib.request.Request(
                    get_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Xiaomi Pad 5)'}
                )
                with urllib.request.urlopen(req, timeout=40) as resp:
                    content = resp.read()
            except Exception as get_err:
                clean_msg = str(get_err).replace(self.token, "[TOKEN_MASKED]")
                raise RuntimeError(f"Error descargando {clean_url}: {clean_msg}") from None

        valido, mot = self._is_valid_document(content, os.path.basename(dest_path))
        if not valido:
            raise ValueError(f"Documento descargado inválido ({clean_url}): {mot}")

        return content

    @staticmethod
    def _is_valid_document(data, filename):
        if not data or len(data) < 10:
            return False, "Archivo vacío o truncado (<10 bytes)"
        if data[:4] == b"<!DO" or data[:5] == b"<html" or b"<html" in data[:120].lower():
            return False, "Respuesta es HTML (redirección a login o error de servidor)"
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf" and not data.startswith(b"%PDF"):
            return False, "Cabecera no coincide con formato PDF (%PDF ausente)"
        if ext in [".docx", ".xlsx", ".zip", ".pptx"] and not data.startswith(b"PK"):
            return False, "Cabecera no coincide con formato Office/Zip (PK ausente)"
        return True, "OK"

def agregar_enunciados_de_entregas(client, cid, sections):
    """Las entregas (mod_assign) traen su enunciado como 'introattachments', que
    core_course_get_contents no lista. Se agregan al módulo como archivos sintéticos para que
    el flujo normal (manifiesto, hash, Drive, commit) los trate igual. Devuelve cuántos agregó."""
    data = client.call("mod_assign_get_assignments", {"courseids[0]": cid})
    por_cmid = {}
    for crs in (data.get("courses", []) if isinstance(data, dict) else []):
        for a in crs.get("assignments", []):
            por_cmid[a.get("cmid")] = a
    agregados = 0
    for sec in sections:
        for mod in sec.get("modules", []):
            if mod.get("modname") != "assign":
                continue
            a = por_cmid.get(mod.get("id"))
            if not a:
                continue
            conts = mod.setdefault("contents", [])
            ya = {c.get("filename") for c in conts}
            for f in a.get("introattachments", []) or []:
                if f.get("filename") in ya or not f.get("fileurl"):
                    continue
                conts.append({"type": "file", "filename": f["filename"], "fileurl": f["fileurl"],
                              "filesize": f.get("filesize", 0), "timemodified": f.get("timemodified", 0)})
                agregados += 1
    return agregados

def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            t = f.read().strip()
            if t:
                return t
    return ""

def check_token_metadata(token_val):
    """Verifica si el token tiene >= 10 semanas de antigüedad para registrar aviso."""
    if os.path.exists(META_FILE):
        try:
            with open(META_FILE, "r", encoding="utf-8") as mf:
                meta = json.load(mf)
            captured_at = meta.get("captured_at")
            if captured_at:
                dt_cap = datetime.fromisoformat(captured_at)
                days_old = (datetime.now() - dt_cap).days
                if days_old >= 70:
                    log(f"AVISO: renovar token de Aula (capturado el {captured_at})", token_to_mask=token_val)
        except Exception as me:
            log(f"Advertencia: no se pudo leer {META_FILE}: {me}", token_to_mask=token_val)

def cargar_manifest():
    if os.path.exists(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"Advertencia: no se pudo leer manifest ({e}), iniciando nuevo.")
    return {}

def guardar_manifest(manifest):
    os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------------- espejo de Aula
# universidad/2026-2/<ramo>/ es igual a Aula: una carpeta por sección y, dentro, los archivos como los
# publica el docente. Lo que genera la automatización (contexto, avisos, foto de la página) va en
# <ramo>/_contexto/ y el espejo nunca lo toca.
CARPETA_CONTEXTO = "_contexto"
LIMITE_RETIROS = 20          # más archivos retirados de Aula en una corrida exige --permitir-masivo
LIMITE_GIT_MB = 95           # GitHub rechaza archivos sobre 100 MB; los mayores quedan en la tablet y en Drive


def nombre_seccion(sec, indice):
    """Carpeta de una sección: su número con dos dígitos (orden de Aula) y su nombre."""
    num = sec.get("section")
    if not isinstance(num, int):
        num = indice
    nombre = sanitizar(sec.get("name") or "").strip() or ("General" if num == 0 else f"Sección {num}")
    return f"{num:02d} {nombre}"


def ruta_espejo(sec, indice, mod, cont):
    """Ruta de un archivo relativa a la carpeta del ramo, como se ve en Aula.

    Un recurso de un solo archivo queda directo en la sección; carpetas, entregas y recursos con
    varios archivos quedan en una subcarpeta con el nombre del módulo (y sus subcarpetas internas).
    """
    partes = [nombre_seccion(sec, indice)]
    archivos = [c for c in mod.get("contents", []) if c.get("type") == "file"]
    if not (mod.get("modname") == "resource" and len(archivos) == 1):
        partes.append(sanitizar(mod.get("name") or "").strip() or f"Módulo {mod.get('id')}")
    partes += [sanitizar(x).strip() for x in (cont.get("filepath") or "/").split("/") if x.strip()]
    partes.append(sanitizar(cont.get("filename", "")).strip())
    return os.path.join(*partes)


def archivos_del_ramo(cdir):
    """Archivos del espejo en la carpeta de un ramo: todo menos _contexto/ y los ocultos."""
    if not os.path.isdir(cdir):
        return
    for root, dirs, files in os.walk(cdir):
        dirs[:] = [d for d in dirs if d != CARPETA_CONTEXTO and not d.startswith(".")]
        for f in files:
            if not f.startswith("."):
                yield os.path.join(root, f)


def borrar_carpetas_vacias(cdir):
    for root, dirs, files in os.walk(cdir, topdown=False):
        if root == cdir or CARPETA_CONTEXTO in os.path.relpath(root, cdir).split(os.sep):
            continue
        if not os.listdir(root):
            os.rmdir(root)


def reflejar_en_repo(courses, root_dir, repo_uni, limite_mb=LIMITE_GIT_MB):
    """Deja cada ramo del repo igual a su espejo en la tablet: copia lo nuevo o distinto y borra lo
    que ya no está en Aula. No toca _contexto/, los archivos ocultos ni lo que está fuera de los ramos.
    Devuelve (copiados, borrados, omitidos_por_tamaño)."""
    copiados = borrados = omitidos = 0
    tope = limite_mb * 1024 * 1024
    for c in courses:
        src = os.path.join(root_dir, c["folder"])
        dst = os.path.join(repo_uni, c["folder"])
        if not os.path.isdir(src):
            continue
        origen = {}
        for p in archivos_del_ramo(src):
            if os.path.getsize(p) > tope:
                omitidos += 1
                log(f"  [OMITIDO DE GIT > {limite_mb} MB] {os.path.relpath(p, root_dir)}")
                continue
            origen[os.path.relpath(p, src)] = p
        for rel, p in origen.items():
            d = os.path.join(dst, rel)
            if (not os.path.exists(d) or os.path.getsize(d) != os.path.getsize(p)
                    or compute_file_sha256(d) != compute_file_sha256(p)):
                os.makedirs(os.path.dirname(d), exist_ok=True)
                copiar_con_hash(p, d)
                copiados += 1
        for p in list(archivos_del_ramo(dst)):
            if os.path.relpath(p, dst) not in origen:
                os.remove(p)
                borrados += 1
        borrar_carpetas_vacias(dst)
    return copiados, borrados, omitidos

def sincronizar_evaluaciones(client, repo_dir):
    """Consulta eventos de calendario con la API y fusiona con evaluaciones_manual.json."""
    courses = [62177, 62178, 62182, 62192, 5623]
    course_map = {
        62177: ("FICA", "CIV222"),
        62178: ("FAE", "CIV233"),
        62182: ("Fluidos", "CIV244"),
        62192: ("Transporte", "CIV386"),
        5623: ("Prácticas", "POC")
    }

    now_ts = int(datetime.now().timestamp())
    params = [
        ('options[timestart]', str(now_ts - 15 * 86400)),
        ('options[timeend]', str(now_ts + 120 * 86400))
    ]
    for i, cid in enumerate(courses):
        params.append((f'events[courseids][{i}]', str(cid)))

    api_events = []
    try:
        res = client.call('core_calendar_get_calendar_events', params)
        for ev in res.get('events', []):
            cid = ev.get('courseid')
            ramo, codigo = course_map.get(cid, ("General", "USM"))
            st_ts = ev.get('timestart', 0)
            dur = ev.get('timeduration', 3600)
            dt_start = datetime.fromtimestamp(st_ts, tz=TZ).isoformat()
            dt_end = datetime.fromtimestamp(st_ts + dur, tz=TZ).isoformat()
            api_events.append({
                "uid": str(ev.get('id')),
                "ramo": ramo,
                "codigo": codigo,
                "evaluacion": sanitizar(ev.get('name', '')),
                "inicio": dt_start,
                "fin": dt_end,
                "lugar": "Aula USM",
                "fuente": "api:core_calendar_get_calendar_events"
            })
    except Exception as e:
        log(f"  [ERROR] Fallo al consultar eventos de calendario vía API: {e}", token_to_mask=client.token)

    # Cargar manuales
    manual_path = os.path.join(repo_dir, "universidad/2026-2/evaluaciones_manual.json")
    manual_events = []
    if os.path.exists(manual_path):
        try:
            with open(manual_path, "r", encoding="utf-8") as mf:
                manual_events = json.load(mf)
        except Exception as me:
            log(f"  [ERROR] No se pudo leer evaluaciones_manual.json: {me}")

    # Fusión determinística: lo manual prevalece sobre la API
    # Si un evento de la API tiene el mismo curso (ramo o código) y un inicio a ±1 h de una entrada manual
    # (o el mismo nombre), prevalece la manual y el de la API se descarta, con registro en el log.
    filtered_api_events = []
    for ev_api in api_events:
        ts_api = to_timestamp_safe(ev_api.get("inicio"))
        ramo_api = ev_api.get("ramo", "").strip().lower()
        cod_api = ev_api.get("codigo", "").strip().lower()
        eval_api_name = ev_api.get("evaluacion", "").strip().lower()
        
        coincide_manual = False
        matching_man = None
        for ev_man in manual_events:
            ramo_man = ev_man.get("ramo", "").strip().lower()
            cod_man = ev_man.get("codigo", "").strip().lower()
            eval_man_name = ev_man.get("evaluacion", "").strip().lower()

            mismo_curso = (
                (ramo_api and ramo_man and ramo_api == ramo_man) or
                (cod_api and cod_man and cod_api == cod_man) or
                (ramo_api and cod_man and ramo_api == cod_man) or
                (cod_api and ramo_man and cod_api == ramo_man)
            )

            if mismo_curso:
                ts_man = to_timestamp_safe(ev_man.get("inicio"))
                if ts_api is not None and ts_man is not None and abs(ts_api - ts_man) <= 3600:
                    coincide_manual = True
                    matching_man = ev_man
                    break
                if eval_api_name and eval_man_name and eval_api_name == eval_man_name:
                    coincide_manual = True
                    matching_man = ev_man
                    break

        if coincide_manual and matching_man:
            log(f"  [FUSIÓN EVALUACIONES] Evento API '{ev_api.get('evaluacion')}' descartado por coincidir con entrada manual '{matching_man.get('evaluacion')}' ({matching_man.get('ramo')} a las {matching_man.get('inicio')}).")
        else:
            filtered_api_events.append(ev_api)

    merged_list = list(manual_events) + filtered_api_events
    result_list = sorted(merged_list, key=lambda x: x.get("inicio", ""))
    
    out_eval = os.path.join(repo_dir, "universidad/2026-2/evaluaciones.json")
    os.makedirs(os.path.dirname(out_eval), exist_ok=True)
    with open(out_eval, "w", encoding="utf-8") as f:
        json.dump(result_list, f, indent=2, ensure_ascii=False)
    log(f"  [EVALUACIONES] Guardadas {len(result_list)} evaluaciones en {out_eval}")
    return out_eval

def escribir_estado_sincronizacion(repo_dir, nuevos, n_errores, novedades=None):
    """Escribe universidad/2026-2/ultima_sincronizacion.json en cada corrida que llega a esta etapa.

    Así cada sábado hay un commit chore(sync) aunque no haya archivos nuevos, y la tarea de
    contexto de Claude distingue "semana sin novedades" de "la sincronización no corrió".
    No incluye textos de error (podrían contener rutas o datos sensibles), solo conteos.
    """
    destino = os.path.join(repo_dir, "universidad", "2026-2", "ultima_sincronizacion.json")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    estado = {
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "estado": "OK" if n_errores == 0 else "CON ERRORES",
        "archivos_nuevos_o_modificados": nuevos,
        "errores": n_errores,
        "novedades": novedades or {},
    }
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return destino


def run_sync():
    lock_dir = os.path.dirname(LOCK_FILE)
    if lock_dir:
        os.makedirs(lock_dir, exist_ok=True)
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("[!] Otra instancia de sincronizar_aula_semanal.py ya se encuentra en ejecución.")
        return 0

    errores = []
    log("=======================================================")
    log("INICIANDO SINCRONIZACIÓN SEMANAL DETERMINÍSTICA (API)")
    log("=======================================================")
    
    token = get_token()
    if not token:
        log("  [ERROR CRÍTICO] Token de Aula no encontrado en ~/.moodle_token. Abortando.")
        log("FINALIZADO. Estado: CON ERRORES (1)")
        log("=======================================================")
        return 1

    check_token_metadata(token)

    client = MoodleAPIClient(BASE_URL, token)

    # 1. Verificación proactiva del token con get_site_info
    try:
        site_info = client.call("core_webservice_get_site_info")
        username = site_info.get("username", "desconocido")
        userid = site_info.get("userid")
        log(f"Sesión validada exitosamente vía API para usuario: {username}")
    except InvalidTokenError as ite:
        log(f"  [ERROR CRÍTICO] {ite}")
        log("FINALIZADO. Estado: CON ERRORES (1)")
        log("=======================================================")
        return 1
    except Exception as ce:
        log(f"  [ERROR CRÍTICO] Fallo de conexión o API: {ce}", token_to_mask=token)
        log("FINALIZADO. Estado: CON ERRORES (1)")
        log("=======================================================")
        return 1

    courses = [
        {"id": 62177, "short": "FICA", "folder": "CIV222_FUNDAMENTOS_DE_INGENIERÍA_DE_CONSTRUCCIÓN_Y_ADMINISTRACIÓN_"},
        {"id": 62178, "short": "FAE", "folder": "CIV233_FUNDAMENTOS_DE_ANÁLISIS_ESTRUCTURAL_"},
        {"id": 62182, "short": "Fluidos", "folder": "CIV244_MECÁNICA_DE_FLUIDOS_"},
        {"id": 62192, "short": "Transporte", "folder": "CIV386_INGENIERÍA_DE_TRANSPORTE_"},
        {"id": 5623, "short": "Prácticas", "folder": "POC_SJ_VV_Prácticas_Obras_Civiles"}
    ]

    manifest = cargar_manifest()
    archivos_descargados = []
    archivos_reubicados = []

    # Construir índice de hashes (sha256 -> ruta_en_disco) por curso
    # Se calcula una sola vez por corrida para detectar archivos existentes bajo otra estructura
    course_sha_indexes = {}
    for c in courses:
        cdir = os.path.join(ROOT_DIR, c["folder"])
        c_index = {}
        if os.path.exists(cdir):
            for root, _, files in os.walk(cdir):
                for f in files:
                    full_p = os.path.join(root, f)
                    if os.path.isfile(full_p):
                        h = compute_file_sha256(full_p)
                        if h:
                            c_index[h] = full_p
        course_sha_indexes[c["id"]] = c_index
    guardar_cache_hashes()

    # -------------------------------------------------------------
    # FASE 1: PLANIFICACIÓN (Detección previa sin escribir en disco)
    # Recorrer cursos y armar lista de archivos por descargar
    # -------------------------------------------------------------
    plan_descargas = []
    plan_copias = []            # (origen, destino, url): contenido ya en disco que va a su carpeta de Aula
    course_sections = {}
    esperados = {}              # cid -> rutas que Aula publica hoy
    urls_vistas = set()

    for c in courses:
        cid = c["id"]
        cshort = c["short"]
        cdir = os.path.join(ROOT_DIR, c["folder"])
        c_hashes = course_sha_indexes.get(cid, {})
        log(f"Revisando contenidos de: {cshort} (ID: {cid})...")

        try:
            sections = client.call("core_course_get_contents", {"courseid": cid})
            course_sections[cid] = sections
            try:
                n_ens = agregar_enunciados_de_entregas(client, cid, sections)
                if n_ens:
                    log(f"  {cshort}: {n_ens} adjunto(s) de enunciado de entregas detectados")
            except InvalidTokenError:
                raise
            except Exception as e_ens:
                log(f"  [AVISO] {cshort}: no se pudieron leer enunciados de entregas: {e_ens}", token_to_mask=token)
        except InvalidTokenError as ite:
            log(f"  [ERROR CRÍTICO] {ite}")
            return 1
        except Exception as e:
            err_msg = f"{cshort} error obteniendo contenidos: {e}"
            log(f"  [ERROR] {err_msg}", token_to_mask=token)
            errores.append(err_msg)
            continue

        esperados_c = esperados.setdefault(cid, set())
        dueno_ruta = {}
        for indice, sec in enumerate(sections):
            sec_name = sec.get("name") or "General"

            for mod in sec.get("modules", []):
                for cont in mod.get("contents", []):
                    if cont.get("type") != "file":
                        continue

                    fname = sanitizar(cont.get("filename", "")).strip()
                    fileurl = cont.get("fileurl", "")
                    filesize = int(cont.get("filesize", 0))
                    timemodified = int(cont.get("timemodified", 0))

                    if not fname or not fileurl:
                        continue

                    url_clean = fileurl.split("?")[0]
                    local_fpath = os.path.join(cdir, ruta_espejo(sec, indice, mod, cont))
                    if dueno_ruta.get(local_fpath, url_clean) != url_clean:
                        # Dos archivos de Aula con el mismo nombre en la misma carpeta: se distinguen por el módulo
                        base_n, ext_n = os.path.splitext(local_fpath)
                        local_fpath = f"{base_n} [{mod.get('id')}]{ext_n}"
                    dueno_ruta[local_fpath] = url_clean
                    esperados_c.add(local_fpath)
                    urls_vistas.add(url_clean)
                    target_dir = os.path.dirname(local_fpath)

                    item = {"tipo": "nuevo", "course": c, "sec_name": sec_name,
                            "sub_path": os.path.relpath(target_dir, cdir), "target_dir": target_dir,
                            "fname": fname, "fileurl": fileurl, "url_clean": url_clean,
                            "local_fpath": local_fpath, "filesize": filesize, "timemodified": timemodified}
                    manifest_entry = manifest.get(url_clean)

                    if manifest_entry and manifest_entry.get("timemodified") == timemodified \
                            and manifest_entry.get("filesize") == filesize:
                        manifest_entry["last_seen"] = datetime.now().isoformat()
                        if os.path.exists(local_fpath):
                            manifest_entry["local_path"] = local_fpath
                            continue
                        # Ya descargado en otra carpeta (estructura anterior o ruta obsoleta): se copia sin descargar
                        origen = manifest_entry.get("local_path")
                        if not (origen and os.path.exists(origen)):
                            origen = c_hashes.get(manifest_entry.get("sha256"))
                        if origen and os.path.exists(origen):
                            plan_copias.append((origen, local_fpath, url_clean))
                            continue
                        plan_descargas.append(item)
                    elif manifest_entry:
                        item["tipo"] = "modificado"
                        plan_descargas.append(item)
                    elif os.path.exists(local_fpath) and os.path.getsize(local_fpath) == filesize:
                        # Caso T9': archivo ya existe en disco con tamaño idéntico -> registrar sin descargar
                        sha = compute_file_sha256(local_fpath)
                        manifest[url_clean] = {
                            "timemodified": timemodified,
                            "filesize": filesize,
                            "local_path": local_fpath,
                            "sha256": sha,
                            "last_seen": datetime.now().isoformat()
                        }
                        c_hashes[sha] = local_fpath
                    else:
                        plan_descargas.append(item)

    # Guardia estricto de límite masivo (>20 archivos pendientes)
    # Se evalúa en la fase de plan ANTES de descargar o escribir ningún byte en disco
    if len(plan_descargas) > 20 and "--permitir-masivo" not in sys.argv:
        msg_masivo = f"ALERTA: Se detectaron {len(plan_descargas)} archivos pendientes de descarga (>20). Límite de seguridad activado: revisión requerida. No se descarga ni modifica ningún archivo en disco, manifest, repo ni Drive."
        log(f"  [ALERTA DE SEGURIDAD] {msg_masivo}")
        for item in plan_descargas[:10]:
            log(f"    - [{item['tipo']}] {item['course']['short']}: {item['fname']} ({item['filesize']} bytes)")
        if len(plan_descargas) > 10:
            log(f"    ... y {len(plan_descargas) - 10} archivos adicionales.")
        return 1

    # -------------------------------------------------------------
    # FASE 2: EJECUCIÓN
    # -------------------------------------------------------------
    # 2a. Contenido ya descargado que va a su carpeta de Aula: se copia (no se mueve, porque otra
    # entrada puede usar el mismo origen); lo que sobre en la carpeta anterior se retira en 2c.
    for origen, destino, url_clean in plan_copias:
        try:
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            copiar_con_hash(origen, destino)
            manifest[url_clean]["local_path"] = destino
            archivos_reubicados.append((origen, destino))
        except Exception as cp_err:
            errores.append(f"Error ubicando {os.path.basename(destino)}: {cp_err}")
            log(f"  [ERROR] {errores[-1]}")
    if plan_copias:
        log(f"  [ESTRUCTURA AULA] {len(plan_copias)} archivo(s) ubicados en su carpeta de Aula sin descargar.")

    # 2b. Descargas. Cada archivo de Aula queda en su propia ruta, aunque su contenido se repita en
    # otra sección; una versión modificada reemplaza a la anterior (la previa queda en el historial de git).
    for item in plan_descargas:
        c = item["course"]
        cid = c["id"]
        cshort = c["short"]
        c_hashes = course_sha_indexes.get(cid, {})
        fname = item["fname"]
        url_clean = item["url_clean"]
        local_fpath = item["local_fpath"]
        tipo = item["tipo"]

        try:
            data = client.download_file(item["fileurl"], local_fpath)
            data_sha = hashlib.sha256(data).hexdigest()
            os.makedirs(item["target_dir"], exist_ok=True)
            with open(local_fpath, "wb") as out_f:
                out_f.write(data)

            c_hashes[data_sha] = local_fpath
            manifest[url_clean] = {
                "timemodified": item["timemodified"],
                "filesize": item["filesize"],
                "local_path": local_fpath,
                "sha256": data_sha,
                "last_seen": datetime.now().isoformat()
            }
            archivos_descargados.append(local_fpath)
            tag_log = "[ARCHIVO MODIFICADO]" if tipo == "modificado" else "[NUEVO ARCHIVO]"
            log(f"  {tag_log} {cshort} -> {item['sub_path']}/{fname}")

        except Exception as dl_err:
            err_msg = f"Error procesando {fname}: {dl_err}"
            log(f"  [ERROR] {err_msg}", token_to_mask=token)
            errores.append(err_msg)

    # 2c. Retiro: lo que está en la carpeta de un ramo y Aula ya no publica. Solo en ramos cuyo
    # listado llegó completo, y con más de LIMITE_RETIROS archivos exige --permitir-masivo.
    retiros = []
    for c in courses:
        if c["id"] not in course_sections:
            continue
        cdir = os.path.join(ROOT_DIR, c["folder"])
        retiros += [p for p in archivos_del_ramo(cdir) if p not in esperados.get(c["id"], set())]
    espejo_completo = True
    if len(retiros) > LIMITE_RETIROS and "--permitir-masivo" not in sys.argv:
        espejo_completo = False
        msg_ret = (f"ALERTA: {len(retiros)} archivos ya no figuran en Aula (>{LIMITE_RETIROS}). No se retira nada "
                   f"ni se actualiza el repo hasta revisarlo; para aplicarlo, correr con --permitir-masivo.")
        log(f"  [ALERTA DE SEGURIDAD] {msg_ret}")
        for r in retiros[:10]:
            log(f"    - {os.path.relpath(r, ROOT_DIR)}")
        errores.append(msg_ret)
    else:
        for r in retiros:
            try:
                os.remove(r)
                log(f"  [RETIRADO DE AULA] {os.path.relpath(r, ROOT_DIR)}")
            except Exception as rm_err:
                errores.append(f"No se pudo retirar {os.path.relpath(r, ROOT_DIR)}: {rm_err}")
        for c in courses:
            if c["id"] in course_sections:
                borrar_carpetas_vacias(os.path.join(ROOT_DIR, c["folder"]))
        # El manifiesto olvida lo retirado: si vuelve a Aula, se descarga de nuevo
        carpetas_ok = tuple(os.path.join(ROOT_DIR, c["folder"]) + os.sep for c in courses if c["id"] in course_sections)
        for url in [u for u, e in manifest.items()
                    if u not in urls_vistas and str(e.get("local_path", "")).startswith(carpetas_ok)]:
            del manifest[url]

    guardar_manifest(manifest)
    log("-------------------------------------------------------")
    log(f"RESULTADO: {len(archivos_descargados)} archivo(s) nuevo(s) o modificado(s), {len(plan_copias)} reubicado(s), {len(retiros) if espejo_completo else 0} retirado(s). Errores: {len(errores)}")

    # 3. Novedades: foros (docentes), cambios en la página de cada ramo y mensajes privados
    novedades = {}
    try:
        novedades, err_nov = sincronizar_novedades(
            client, courses, REPO_DIR, userid, MENSAJES_FILE, lambda m: log(m, token_to_mask=token)
        )
        for e in err_nov:
            log(f"  [ERROR] {e}", token_to_mask=token)
            errores.append(e.replace(token, "[TOKEN_MASKED]"))
        if novedades.get("alertas_evaluacion"):
            log(f"  [ALERTA] {novedades['alertas_evaluacion']} publicación(es) o cambio(s) mencionan una posible modificación de evaluación. Revisar avisos.md, cambios_pagina.md y mensajes.")
    except Exception as fe:
        err_f = f"Excepción al sincronizar novedades: {fe}"
        log(f"  [ERROR] {err_f}", token_to_mask=token)
        errores.append(err_f)

    # 4. Sincronización de evaluaciones combinada con evaluaciones_manual.json
    try:
        sincronizar_evaluaciones(client, REPO_DIR)
    except Exception as ee:
        err_e = f"Excepción al sincronizar evaluaciones: {ee}"
        log(f"  [ERROR] {err_e}", token_to_mask=token)
        errores.append(err_e)

    # 5. Respaldo en Google Drive: cada archivo en su ramo y subcarpeta (mismo árbol que la tablet)
    if os.environ.get("SYNC_DISABLE_DRIVE") or os.environ.get("SYNC_TEST_MODE") == "1":
        log("Subida a Google Drive omitida (modo de prueba o SYNC_DISABLE_DRIVE activo).")
    else:
        rclone_bin = shutil.which("rclone")
        if not rclone_bin:
            errores.append("rclone no está disponible para el respaldo en Google Drive.")
            log(f"  [ERROR] {errores[-1]}")
        else:
            try:
                actualizar_manifest_sha256(ROOT_DIR)
                for e in respaldar_en_drive(rclone_bin, archivos_descargados, "--dry-run" in sys.argv):
                    log(f"  [ERROR] {e}")
                    errores.append(e)
            except Exception as ze:
                errores.append(f"Excepción en el respaldo de Google Drive: {ze}")
                log(f"  [ERROR] {errores[-1]}")

    # 6. Sincronización de calendario nativo (antes de git, para que el estado lo incluya)
    try:
        from sincronizar_calendario_android import sync_android_calendar
        res_cal = sync_android_calendar()
        if res_cal != 0:
            err_c = f"Sincronización de calendario reportó errores (código {res_cal})."
            log(f"  [ERROR] {err_c}")
            errores.append(err_c)
        else:
            log("Calendario nativo verificado y al día.")
    except Exception as ce:
        err_c = f"Excepción en sincronización de calendario: {ce}"
        log(f"  [ERROR] {err_c}")
        errores.append(err_c)

    # 6.5 Generación de contextos de asignaturas para Claude
    try:
        from generar_contexto_ramos import generar_contexto_para_ramo, generar_contexto_semestre, COURSES_META
        for cm in COURSES_META:
            generar_contexto_para_ramo(cm, client=client)
        generar_contexto_semestre()
        log("Contextos incrementales de asignaturas generados con éxito.")
    except Exception as gce:
        log(f"  [AVISO] No se pudieron generar contextos de asignaturas: {gce}")

    # 7. Latido de la corrida: deja constancia en el repo de que la sincronización corrió
    try:
        escribir_estado_sincronizacion(REPO_DIR, len(archivos_descargados), len(errores), novedades)
    except Exception as he:
        err_h = f"No se pudo escribir ultima_sincronizacion.json: {he}"
        log(f"  [ERROR] {err_h}")
        errores.append(err_h)

    # 8. Sincronización INCREMENTAL con GitHub AlboHack/Mis-cosas
    if os.path.exists(REPO_DIR) and os.path.isdir(os.path.join(REPO_DIR, ".git")) and not os.environ.get("SYNC_DISABLE_GIT"):
        try:
            log("Sincronizando con repositorio GitHub AlboHack/Mis-cosas...")
            p_pull = subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=REPO_DIR, capture_output=True, text=True)
            if p_pull.returncode != 0:
                subprocess.run(["git", "rebase", "--abort"], cwd=REPO_DIR, capture_output=True)
                err_g = f"Git rebase conflictivo, abortado: {p_pull.stderr.strip()}"
                log(f"  [ERROR] {err_g}")
                errores.append(err_g)
            else:
                target_repo_uni = os.path.join(REPO_DIR, "universidad/2026-2")
                if espejo_completo:
                    n_cp, n_bo, n_om = reflejar_en_repo(courses, ROOT_DIR, target_repo_uni)
                    log(f"  [REPO] Espejo de Aula: {n_cp} copiado(s), {n_bo} retirado(s), {n_om} sobre {LIMITE_GIT_MB} MB solo en tablet y Drive.")
                else:
                    log("  [REPO] Espejo no actualizado: retiro pendiente de revisión (--permitir-masivo).")

                subprocess.run(["git", "add", "-A", "universidad/2026-2/"], cwd=REPO_DIR, check=True)
                p_diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_DIR)
                if p_diff.returncode != 0:
                    fecha_c = datetime.now().strftime('%Y-%m-%d')
                    subprocess.run(["git", "commit", "-m", f"chore(sync): actualizacion semanal incremental ({fecha_c})"], cwd=REPO_DIR, check=True)
                    subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)
                    log(f"¡Repositorio GitHub actualizado con éxito ({fecha_c})!")
                else:
                    log("INCREMENTAL: Repositorio GitHub al día. Cero cambios que commitear.")
        except Exception as ge:
            err_g = f"Excepción en sincronización GitHub: {ge}"
            log(f"  [ERROR] {err_g}")
            errores.append(err_g)

    guardar_cache_hashes()
    log(f"FINALIZADO. Estado: {'OK' if len(errores) == 0 else 'CON ERRORES (' + str(len(errores)) + ')'}")
    log("=======================================================")
    return 0 if len(errores) == 0 else 1

if __name__ == "__main__":
    sys.exit(run_sync())
