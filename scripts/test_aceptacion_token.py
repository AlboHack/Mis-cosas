#!/data/data/com.agycli/files/usr/bin/python3
"""
scripts/test_aceptacion_token.py
Suite de pruebas de aceptación técnica para la arquitectura Moodle API con token:
T12, T3', T2', T9', T10, T11, Avisos Idempotencia y T13 (Aislamiento e Integridad Real).
Todos los tests corren en aislamiento estricto sobre directorios temporales,
sin tocar archivos reales, repositorios reales ni el calendario real de Android.
"""

import os
import sys
import shutil
import tempfile
import subprocess
import json
import hashlib
import time
import socket
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPTS_DIR)
SYNC_SCRIPT = os.path.join(SCRIPTS_DIR, "sincronizar_aula_semanal.py")
CAL_SCRIPT = os.path.join(SCRIPTS_DIR, "sincronizar_calendario_android.py")

REAL_ROOT_DIR = "/storage/emulated/0/Download/Universidad/2026-2"
REAL_LOG_FILE = "/storage/emulated/0/Download/Universidad/Registro_Sincronizaciones.log"

TS_V1 = int(datetime(2026, 10, 20, 10, 0).timestamp())
TS_V2 = int(datetime(2026, 10, 26, 10, 0).timestamp())
DATE_STR_V1 = datetime.fromtimestamp(TS_V1).strftime("%Y%m%d")

def get_file_content(v):
    prefix = f"%PDF-1.4 Version {v} content "
    pad_len = 100 - len(prefix)
    return (prefix + "X" * pad_len).encode("utf-8")

# Mock Moodle Server State
server_state = {
    "mode": "normal",
    "file_version": 1,
    "timemodified": TS_V1,
    "discussions": [
        {"discussion": 101, "name": "Aviso 1", "userfullname": "Profesor", "created": 1785000000, "message": "<p>Mensaje 1</p>"}
    ],
    "requests_received": []
}

class MockMoodleHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8', errors='ignore')
        params = dict(urllib.parse.parse_qsl(body))
        server_state["requests_received"].append({"path": self.path, "params": params})

        if server_state["mode"] == "network_error":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error with fake network trace")
            return

        if "/webservice/rest/server.php" in self.path:
            wsfunc = params.get("wsfunction", "")

            if server_state["mode"] == "invalidtoken":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "errorcode": "invalidtoken",
                    "message": "Token no válido o expirado"
                }).encode("utf-8"))
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            if wsfunc == "core_webservice_get_site_info":
                resp = {
                    "username": "nicolas.albornozp@usm.cl",
                    "fullname": "NICOLAS ALBORNOZ",
                    "siteurl": "https://aula.usm.cl",
                    "functions": []
                }
            elif wsfunc == "core_course_get_contents":
                cid = int(params.get("courseid", 0))
                if cid != 62177:
                    resp = []
                elif server_state["mode"] == "t15":
                    resp = [
                        {
                            "name": "General",
                            "modules": [
                                {
                                    "name": "Pauta Reubicada",
                                    "modname": "resource",
                                    "contents": [
                                        {
                                            "type": "file",
                                            "filename": "Pauta_Nueva_Seccion.pdf",
                                            "filesize": len(server_state.get("t15_data", b"")),
                                            "fileurl": f"http://127.0.0.1:{self.server.server_port}/webservice/pluginfile.php/t15/Pauta_Nueva_Seccion.pdf",
                                            "timemodified": TS_V1
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                elif server_state["mode"] == "t16":
                    modules_25 = []
                    for i in range(25):
                        fname = f"Doc_{i}.pdf"
                        prefix = f"%PDF-1.4 Unique {fname} content "
                        sz = len((prefix + "X" * (120 - len(prefix))).encode("utf-8"))
                        modules_25.append({
                            "name": f"Documento {i}",
                            "modname": "resource",
                            "contents": [
                                {
                                    "type": "file",
                                    "filename": fname,
                                    "filesize": sz,
                                    "fileurl": f"http://127.0.0.1:{self.server.server_port}/webservice/pluginfile.php/t16/{fname}",
                                    "timemodified": TS_V1 + i
                                }
                            ]
                        })
                    resp = [{"name": "General", "modules": modules_25}]
                elif server_state["mode"] == "t17":
                    contents_t17 = [
                        {
                            "type": "file",
                            "filename": "Pauta_Vigente.pdf",
                            "filesize": len(server_state.get("t17_pauta_v2", b"")),
                            "fileurl": f"http://127.0.0.1:{self.server.server_port}/webservice/pluginfile.php/t17/Pauta_Vigente.pdf",
                            "timemodified": TS_V2
                        }
                    ]
                    for i in range(21):
                        fname = f"Doc_Nuevo_{i}.pdf"
                        prefix = f"%PDF-1.4 T17 Doc {i} content "
                        sz = len((prefix + "X" * (120 - len(prefix))).encode("utf-8"))
                        contents_t17.append({
                            "type": "file",
                            "filename": fname,
                            "filesize": sz,
                            "fileurl": f"http://127.0.0.1:{self.server.server_port}/webservice/pluginfile.php/t17/{fname}",
                            "timemodified": TS_V1
                        })
                    resp = [{
                        "name": "General",
                        "modules": [
                            {
                                "name": "Contenidos T17",
                                "modname": "resource",
                                "contents": contents_t17
                            }
                        ]
                    }]
                else:
                    v = server_state["file_version"]
                    tmod = server_state["timemodified"]
                    resp = [
                        {
                            "name": "General",
                            "modules": [
                                {
                                    "name": "Pauta",
                                    "modname": "resource",
                                    "contents": [
                                        {
                                            "type": "file",
                                            "filename": "Pauta.pdf",
                                            "filesize": len(get_file_content(v)),
                                            "fileurl": f"http://127.0.0.1:{self.server.server_port}/webservice/pluginfile.php/123/mod_resource/content/1/Pauta.pdf",
                                            "timemodified": tmod
                                        }
                                    ]
                                },
                                {
                                    "name": "Noticias",
                                    "modname": "forum",
                                    "instance": 555
                                }
                            ]
                        }
                    ]
            elif wsfunc == "core_calendar_get_calendar_events":
                resp = {
                    "events": [
                        {
                            "id": 1124478,
                            "courseid": 62178,
                            "name": "Vencimiento de Tarea N°1",
                            "timestart": 1793156340,
                            "timeduration": 0
                        }
                    ]
                }
            elif wsfunc == "mod_forum_get_forum_discussions":
                resp = {"discussions": server_state["discussions"]}
            else:
                resp = {"errorcode": "unknownerror", "message": "Unknown function"}

            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        if "/webservice/pluginfile.php" in self.path:
            if server_state["mode"] == "t15":
                data = server_state.get("t15_data", b"")
            elif server_state["mode"] == "t16":
                fname = self.path.split("/")[-1].split("?")[0]
                prefix = f"%PDF-1.4 Unique {fname} content "
                data = (prefix + "X" * (120 - len(prefix))).encode("utf-8")
            elif server_state["mode"] == "t17":
                fname = self.path.split("/")[-1].split("?")[0]
                if fname == "Pauta_Vigente.pdf":
                    data = server_state.get("t17_pauta_v2", b"")
                else:
                    prefix = f"%PDF-1.4 T17 {fname} content "
                    data = (prefix + "X" * (120 - len(prefix))).encode("utf-8")
            else:
                v = server_state["file_version"]
                data = get_file_content(v)
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        if server_state["mode"] == "network_error":
            self.send_response(500)
            self.end_headers()
            return

        if "/webservice/pluginfile.php" in self.path:
            if server_state["mode"] == "t15":
                data = server_state.get("t15_data", b"")
            elif server_state["mode"] == "t16":
                fname = self.path.split("/")[-1].split("?")[0]
                prefix = f"%PDF-1.4 Unique {fname} content "
                data = (prefix + "X" * (120 - len(prefix))).encode("utf-8")
            elif server_state["mode"] == "t17":
                fname = self.path.split("/")[-1].split("?")[0]
                if fname == "Pauta_Vigente.pdf":
                    data = server_state.get("t17_pauta_v2", b"")
                else:
                    prefix = f"%PDF-1.4 T17 {fname} content "
                    data = (prefix + "X" * (120 - len(prefix))).encode("utf-8")
            else:
                v = server_state["file_version"]
                data = get_file_content(v)
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_response(404)
        self.end_headers()

def run_test_suite():
    print("======================================================================")
    print("BATERÍA DE PRUEBAS DE ACEPTACIÓN TÉCNICA (API TOKEN: T2', T3', T9', T10, T11, T12, T13, T14, T15, T16, T17)")
    print("======================================================================\n")

    # Registro de estado previo real para T13
    pre_git_status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
    pre_dir_mtime = os.path.getmtime(REAL_ROOT_DIR) if os.path.exists(REAL_ROOT_DIR) else 0
    pre_log_mtime = os.path.getmtime(REAL_LOG_FILE) if os.path.exists(REAL_LOG_FILE) else 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()

    mock_server = HTTPServer(('127.0.0.1', port), MockMoodleHandler)
    server_thread = threading.Thread(target=mock_server.serve_forever, daemon=True)
    server_thread.start()
    base_url = f"http://127.0.0.1:{port}"
    print(f"[INIT] Servidor Moodle simulado activo en {base_url}")

    # Creación de entorno temporal aislado
    test_env_dir = tempfile.mkdtemp(prefix="test_suite_api_")
    test_root_dir = os.path.join(test_env_dir, "Download/Universidad/2026-2")
    test_delta_dir = os.path.join(test_env_dir, "Download")
    test_repo_dir = os.path.join(test_env_dir, "Mis-cosas")
    test_log_file = os.path.join(test_env_dir, "Registro_Sincronizaciones.log")
    test_manifest_file = os.path.join(test_env_dir, "sync_manifest.json")
    test_lock_file = os.path.join(test_env_dir, "sync.lock")
    test_mapping_file = os.path.join(test_env_dir, "calendario_mapping.json")
    test_cal_sim_file = os.path.join(test_env_dir, "sim_calendar_state.json")
    token_file = os.path.join(test_env_dir, ".moodle_token")
    meta_file = os.path.join(test_env_dir, ".moodle_token.meta")

    os.makedirs(test_root_dir, exist_ok=True)
    os.makedirs(test_delta_dir, exist_ok=True)
    os.makedirs(os.path.join(test_repo_dir, "universidad/2026-2"), exist_ok=True)

    # Copiar evaluaciones_manual.json y evaluaciones.json al repo temporal para pruebas
    real_manual = os.path.join(REPO_ROOT, "universidad/2026-2/evaluaciones_manual.json")
    test_eval_file = os.path.join(test_repo_dir, "universidad/2026-2/evaluaciones.json")
    if os.path.exists(real_manual):
        shutil.copy2(real_manual, os.path.join(test_repo_dir, "universidad/2026-2/evaluaciones_manual.json"))
        shutil.copy2(real_manual, test_eval_file)

    test_token = "moodle_secret_token_1234567890abcdef"
    with open(token_file, "w") as tf:
        tf.write(test_token)

    with open(meta_file, "w") as mf:
        json.dump({"captured_at": "2026-10-26", "timestamp": int(time.time())}, mf)

    env_overrides = {
        "MOODLE_BASE_URL": base_url,
        "MOODLE_TOKEN_FILE": token_file,
        "MOODLE_META_FILE": meta_file,
        "SYNC_ROOT_DIR": test_root_dir,
        "SYNC_DELTA_DIR": test_delta_dir,
        "SYNC_REPO_DIR": test_repo_dir,
        "SYNC_LOG_FILE": test_log_file,
        "SYNC_MANIFEST_FILE": test_manifest_file,
        "SYNC_LOCK_FILE": test_lock_file,
        "SYNC_TEST_MODE": "1",
        "SYNC_DISABLE_GIT": "1",
        "SYNC_DISABLE_DRIVE": "1",
        "CALENDAR_TEST_MODE": "1",
        "CALENDAR_SIMULATE_ADB": "1",
        "CALENDAR_SIM_STATE_FILE": test_cal_sim_file,
        "CALENDAR_MAPPING_FILE": test_mapping_file,
        "CALENDAR_EVALUACIONES_FILE": test_eval_file
    }

    # Guardia de aislamiento estricto (Claude: Aborta si alguna ruta apunta a /storage/emulated/0 o ~/Mis-cosas)
    _real_repo = os.path.realpath(os.path.expanduser("~/Mis-cosas"))
    _real_mapping = os.path.realpath(os.path.expanduser("~/.calendario_mapping.json"))
    for k in ["SYNC_ROOT_DIR", "SYNC_DELTA_DIR", "SYNC_REPO_DIR", "SYNC_LOG_FILE", "SYNC_MANIFEST_FILE", "CALENDAR_MAPPING_FILE", "CALENDAR_EVALUACIONES_FILE"]:
        v = env_overrides[k]
        resolved = os.path.realpath(os.path.expanduser(v))
        if (
            resolved.startswith("/storage/emulated/0")
            or resolved == _real_repo
            or resolved.startswith(_real_repo + os.sep)
            or resolved == _real_mapping
        ):
            raise AssertionError(f"ERROR DE AISLAMIENTO: {k}={v} apunta a ruta protegida: {resolved}")

    print(f"[INIT] Aislamiento verificado: todas las rutas temporales validadas en {test_env_dir}\n")

    env_prod = os.environ.copy()
    env_prod.update(env_overrides)

    # ----------------------------------------------------------------------
    # T12: Whitelist estricta - Función fuera de lista blanca lanza excepción sin red
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T12: Validación Estricta de Lista Blanca (Sin llamada de red)] ---")
    sys.path.insert(0, SCRIPTS_DIR)
    from sincronizar_aula_semanal import MoodleAPIClient, WhitelistViolationError
    client_t12 = MoodleAPIClient(base_url, test_token)
    t12_pass = False
    reqs_before = len(server_state["requests_received"])
    try:
        client_t12.call("core_user_get_users_by_field")
        print("  [FAIL] La llamada a función no permitida no lanzó excepción.")
    except WhitelistViolationError as wve:
        reqs_after = len(server_state["requests_received"])
        if reqs_after == reqs_before:
            t12_pass = True
            print(f"  -> Verificado: WhitelistViolationError lanzada ('{wve}'). Cero peticiones de red realizadas.")
        else:
            print("  [FAIL] Se enviaron peticiones HTTP al servidor simulado.")
    print(f"Resultado T12: {'PASS' if t12_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T3': Detección de token inválido (código 1, ERROR CRÍTICO, manifest intacto)
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T3': Token Expirado/Inválido (Código 1, ERROR CRÍTICO, Manifest Intacto)] ---")
    server_state["mode"] = "invalidtoken"
    initial_manifest = {"https://fake.url": {"timemodified": 999, "filesize": 50}}
    with open(test_manifest_file, "w") as mf:
        json.dump(initial_manifest, mf)

    p_t3 = subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)
    manifest_after_t3 = json.load(open(test_manifest_file))
    
    t3_pass = (
        p_t3.returncode == 1 and
        "ERROR CRÍTICO: token de Aula expirado" in p_t3.stdout and
        manifest_after_t3 == initial_manifest
    )
    print(f"  Returncode: {p_t3.returncode}")
    print(f"  Mensaje detectado en stdout: {'ERROR CRÍTICO: token de Aula expirado' in p_t3.stdout}")
    print(f"  Manifest intacto: {manifest_after_t3 == initial_manifest}")
    print(f"Resultado T3': {'PASS' if t3_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T2': Modificación incremental (timemodified cambia -> versión nueva + respaldo YYYYMMDD)
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T2': Modificación Incremental y Respaldo por timemodified (Fecha YYYYMMDD)] ---")
    target_clean_dir = os.path.join(test_root_dir, "CIV222_FUNDAMENTOS_DE_INGENIERÍA_DE_CONSTRUCCIÓN_Y_ADMINISTRACIÓN_/Planificacion/General")
    os.makedirs(target_clean_dir, exist_ok=True)
    server_state["mode"] = "normal"
    server_state["file_version"] = 1
    server_state["timemodified"] = TS_V1

    # Corrida 1: Descarga versión 1
    subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)
    
    # Corrida 2: timemodified cambia a TS_V2, versión 2
    server_state["file_version"] = 2
    server_state["timemodified"] = TS_V2
    subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)

    vigente_f = os.path.join(target_clean_dir, "Pauta.pdf")
    respaldo_f = os.path.join(target_clean_dir, f"Pauta_v{DATE_STR_V1}.pdf")

    t2_pass = False
    if os.path.exists(vigente_f) and os.path.exists(respaldo_f):
        c_vig = open(vigente_f, "rb").read()
        c_res = open(respaldo_f, "rb").read()
        if b"Version 2" in c_vig and b"Version 1" in c_res:
            t2_pass = True
            print(f"  -> Verificado: Archivo vigente contiene 'Version 2', respaldo 'Pauta_v{DATE_STR_V1}.pdf' contiene 'Version 1'.")

    print(f"Resultado T2': {'PASS' if t2_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T9': Archivos ya en disco sin manifest -> 0 nuevos
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T9': Archivos Existentes en Disco sin Manifest (0 Nuevos)] ---")
    if os.path.exists(test_manifest_file):
        os.remove(test_manifest_file)

    p_t9 = subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)
    t9_pass = (
        p_t9.returncode == 0 and
        "RESULTADO: 0 archivo(s) nuevo(s)" in p_t9.stdout
    )
    print(f"  Salida: {[line for line in p_t9.stdout.splitlines() if 'RESULTADO:' in line]}")
    print(f"Resultado T9': {'PASS' if t9_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T10: Error de red forzado -> token ausente en logs, manifest y diff
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T10: Protección Estricta del Token ante Error Forzado de Red] ---")
    server_state["mode"] = "network_error"
    p_t10 = subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)
    
    raw_stdout = p_t10.stdout
    raw_stderr = p_t10.stderr
    raw_manifest = open(test_manifest_file).read() if os.path.exists(test_manifest_file) else ""
    log_content = open(test_log_file).read() if os.path.exists(test_log_file) else ""

    token_in_stdout = test_token in raw_stdout
    token_in_stderr = test_token in raw_stderr
    token_in_manifest = test_token in raw_manifest
    token_in_log = test_token in log_content

    t10_pass = (
        p_t10.returncode != 0 and
        not token_in_stdout and
        not token_in_stderr and
        not token_in_manifest and
        not token_in_log
    )
    print(f"  Token expuesto en stdout: {token_in_stdout}")
    print(f"  Token expuesto en stderr: {token_in_stderr}")
    print(f"  Token expuesto en manifest: {token_in_manifest}")
    print(f"  Token expuesto en log: {token_in_log}")
    print(f"Resultado T10: {'PASS' if t10_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T11: Sincronización de Calendario con Llave UID e Idempotencia (Simulada y Aislada)
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T11: Calendario con Llave UID e Idempotencia (Simulado y Aislado)] ---")
    t11_mapping_file = os.path.join(test_env_dir, "t11_mapping.json")
    if os.path.exists(t11_mapping_file):
        os.remove(t11_mapping_file)

    env_t11 = env_prod.copy()
    env_t11["CALENDAR_MAPPING_FILE"] = t11_mapping_file

    # Generar evaluaciones.json en test_repo_dir si aún no existe
    eval_json_test = os.path.join(test_repo_dir, "universidad/2026-2/evaluaciones.json")
    if not os.path.exists(eval_json_test):
        shutil.copy2(real_manual, eval_json_test)

    # Cargar las evaluaciones para inicializar el estado simulado del calendario Android
    evals = json.load(open(eval_json_test, "r", encoding="utf-8"))
    
    # Sembrar en el calendario simulado los 12 eventos con formato existente (con ':' en título y descripción)
    initial_sim_events = []
    for i, ev in enumerate(evals):
        dt_start_ms = int(datetime.fromisoformat(ev["inicio"]).timestamp() * 1000)
        dt_end_ms = int(datetime.fromisoformat(ev["fin"]).timestamp() * 1000)
        initial_sim_events.append({
            "_id": 500 + i,
            "title": f"{ev['ramo']}: {ev['evaluacion']}",
            "dtstart": dt_start_ms,
            "dtend": dt_end_ms,
            "eventLocation": ev.get("lugar", "Aula USM"),
            "description": f"Curso: {ev['ramo']} - Evaluacion: {ev['evaluacion']}"
        })
    with open(test_cal_sim_file, "w", encoding="utf-8") as csf:
        json.dump({"next_id": 600, "events": initial_sim_events}, csf, indent=2)

    # Corrida 1: Migración única (0 insertados, crea mapping)
    p_t11_1 = subprocess.run([sys.executable, CAL_SCRIPT], env=env_t11, capture_output=True, text=True)
    
    # Corrida 2: Idempotencia (0 insertados, 0 actualizados, 0 errores)
    p_t11_2 = subprocess.run([sys.executable, CAL_SCRIPT], env=env_t11, capture_output=True, text=True)

    # Corrida 3: Verificación de colon escaping estricto con ":" en descripción y título
    p_t11_3 = subprocess.run([sys.executable, CAL_SCRIPT], env=env_t11, capture_output=True, text=True)

    for line in p_t11_1.stdout.splitlines():
        if "Sincronizacion de calendario finalizada:" in line:
            print(f"  Corrida 1 (Migración): {line}")
    for line in p_t11_2.stdout.splitlines():
        if "Sincronizacion de calendario finalizada:" in line:
            print(f"  Corrida 2 (Idempotente): {line}")
    for line in p_t11_3.stdout.splitlines():
        if "Sincronizacion de calendario finalizada:" in line:
            print(f"  Corrida 3 (Idempotente con ':'): {line}")

    t11_pass = (
        p_t11_1.returncode == 0 and
        p_t11_2.returncode == 0 and
        p_t11_3.returncode == 0 and
        "0 insertados" in p_t11_1.stdout and
        "0 errores" in p_t11_1.stdout and
        "0 insertados" in p_t11_2.stdout and
        "0 actualizados" in p_t11_2.stdout and
        "0 errores" in p_t11_2.stdout and
        "0 insertados" in p_t11_3.stdout and
        "0 actualizados" in p_t11_3.stdout and
        "0 errores" in p_t11_3.stdout
    )
    print(f"Resultado T11: {'PASS' if t11_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T14: Re-emparejamiento ante _id obsoletos en mapping (Sin Duplicados)
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T14: Re-emparejamiento ante IDs Obsoletos en Mapping] ---")
    t14_mapping_file = os.path.join(test_env_dir, "t14_mapping.json")
    # Mapping con IDs obsoletos que ya no existen en Android
    obsolete_mapping = {ev["uid"]: str(99900 + i) for i, ev in enumerate(evals)}
    with open(t14_mapping_file, "w", encoding="utf-8") as t14mf:
        json.dump(obsolete_mapping, t14mf, indent=2)

    # Estado de calendario con otros IDs (700..711)
    t14_sim_events = []
    for i, ev in enumerate(evals):
        dt_start_ms = int(datetime.fromisoformat(ev["inicio"]).timestamp() * 1000)
        dt_end_ms = int(datetime.fromisoformat(ev["fin"]).timestamp() * 1000)
        t14_sim_events.append({
            "_id": 700 + i,
            "title": f"{ev['ramo']}: {ev['evaluacion']}",
            "dtstart": dt_start_ms,
            "dtend": dt_end_ms,
            "eventLocation": ev.get("lugar", "Aula USM"),
            "description": f"Curso: {ev['ramo']} - Evaluacion: {ev['evaluacion']}"
        })
    with open(test_cal_sim_file, "w", encoding="utf-8") as csf:
        json.dump({"next_id": 800, "events": t14_sim_events}, csf, indent=2)

    env_t14 = env_prod.copy()
    env_t14["CALENDAR_MAPPING_FILE"] = t14_mapping_file

    # Corrida 1: Detecta IDs obsoletos, purga mapping, re-empareja con 700..711 -> 0 insertados
    p_t14_1 = subprocess.run([sys.executable, CAL_SCRIPT], env=env_t14, capture_output=True, text=True)
    
    # Corrida 2: Idempotente -> 0 insertados, 0 actualizados, 0 errores
    p_t14_2 = subprocess.run([sys.executable, CAL_SCRIPT], env=env_t14, capture_output=True, text=True)

    for line in p_t14_1.stdout.splitlines():
        if "Sincronizacion de calendario finalizada:" in line:
            print(f"  Corrida 1 (Re-emparejamiento): {line}")
    for line in p_t14_2.stdout.splitlines():
        if "Sincronizacion de calendario finalizada:" in line:
            print(f"  Corrida 2 (Idempotente): {line}")

    t14_pass = (
        p_t14_1.returncode == 0 and
        p_t14_2.returncode == 0 and
        "0 insertados" in p_t14_1.stdout and
        "0 errores" in p_t14_1.stdout and
        "0 insertados" in p_t14_2.stdout and
        "0 actualizados" in p_t14_2.stdout and
        "0 errores" in p_t14_2.stdout
    )
    print(f"Resultado T14: {'PASS' if t14_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T15: Detección por Contenido contra lo Existente (Hash SHA-256 por Curso)
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T15: Deduplicación por Contenido con Estructura Diferente] ---")
    t15_content = b"%PDF-1.4 Contenido identico para prueba T15 de deduplicacion - Hash estricto 88888"
    course_folder = "CIV222_FUNDAMENTOS_DE_INGENIERÍA_DE_CONSTRUCCIÓN_Y_ADMINISTRACIÓN_"
    old_subfolder = os.path.join(test_root_dir, course_folder, "Carpeta_Antigua_Desordenada")
    os.makedirs(old_subfolder, exist_ok=True)
    old_file_path = os.path.join(old_subfolder, "Archivo_Antiguo.pdf")
    with open(old_file_path, "wb") as f:
        f.write(t15_content)

    if os.path.exists(test_manifest_file):
        os.remove(test_manifest_file)

    server_state["mode"] = "t15"
    server_state["t15_data"] = t15_content

    p_t15 = subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)

    new_dest = os.path.join(test_root_dir, course_folder, "Planificacion/General/Pauta_Nueva_Seccion.pdf")
    file_not_written = not os.path.exists(new_dest)
    zero_new_reported = "0 archivo(s) nuevo(s)" in p_t15.stdout
    dup_omitted = "[DUPLICADO OMITIDO]" in p_t15.stdout

    manifest_t15 = {}
    if os.path.exists(test_manifest_file):
        with open(test_manifest_file, "r", encoding="utf-8") as mf:
            manifest_t15 = json.load(mf)

    mapped_correctly = False
    for k, v in manifest_t15.items():
        if "Pauta_Nueva_Seccion.pdf" in k and v.get("local_path") == old_file_path:
            mapped_correctly = True
            break

    eval_json_p = os.path.join(test_repo_dir, "universidad/2026-2/evaluaciones.json")
    eval_dedup_pass = False
    if os.path.exists(eval_json_p):
        with open(eval_json_p, "r", encoding="utf-8") as ef:
            eval_data = json.load(ef)
        uids = [e["uid"] for e in eval_data]
        eval_dedup_pass = ("1124478" not in uids and "manual-FAE-Entrega Tarea 1 SAP2000" in uids and len(eval_data) == 12)

    t15_pass = (
        p_t15.returncode == 0 and
        file_not_written and
        zero_new_reported and
        dup_omitted and
        mapped_correctly and
        eval_dedup_pass
    )
    print(f"  Código de retorno 0: {p_t15.returncode == 0}")
    print(f"  Archivo NO duplicado en disco: {file_not_written}")
    print(f"  0 nuevos archivos reportados: {zero_new_reported}")
    print(f"  Log registró [DUPLICADO OMITIDO]: {dup_omitted}")
    print(f"  Manifest mapeado a archivo existente: {mapped_correctly}")
    print(f"  Deduplicación de evaluaciones (12 eventos sin duplicado API): {eval_dedup_pass}")
    print(f"Resultado T15: {'PASS' if t15_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T16: Límite Masivo Estricto (>20 archivos nuevos corta todo)
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T16: Límite Masivo (>20) Bloqueante] ---")
    server_state["mode"] = "t16"

    if os.path.exists(test_manifest_file):
        os.remove(test_manifest_file)

    p_t16_block = subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)
    manifest_saved_on_block = os.path.exists(test_manifest_file)
    git_status_repo = subprocess.run(["git", "status", "--porcelain"], cwd=test_repo_dir, capture_output=True, text=True).stdout.strip()
    msg_revision = "revisión requerida" in p_t16_block.stdout.lower() or "revision requerida" in p_t16_block.stdout.lower()

    p_t16_allow = subprocess.run([sys.executable, SYNC_SCRIPT, "--permitir-masivo"], env=env_prod, capture_output=True, text=True)
    manifest_saved_on_allow = os.path.exists(test_manifest_file)
    manifest_count = 0
    if manifest_saved_on_allow:
        with open(test_manifest_file, "r", encoding="utf-8") as mf:
            manifest_count = len(json.load(mf))

    t16_pass = (
        p_t16_block.returncode == 1 and
        not manifest_saved_on_block and
        msg_revision and
        git_status_repo == "" and
        p_t16_allow.returncode == 0 and
        manifest_saved_on_allow and
        manifest_count >= 25
    )
    print(f"  Bloqueo: código de retorno 1: {p_t16_block.returncode == 1}")
    print(f"  Bloqueo: manifest NO guardado: {not manifest_saved_on_block}")
    print(f"  Bloqueo: mensaje 'revisión requerida': {msg_revision}")
    print(f"  Bloqueo: repo git limpio: {git_status_repo == ''}")
    print(f"  Permitido: código de retorno 0: {p_t16_allow.returncode == 0}")
    print(f"  Permitido: manifest guardado ({manifest_count} entradas >= 25): {manifest_count >= 25}")
    print(f"Resultado T16: {'PASS' if t16_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T17: Límite Masivo Preventivo (1 Modificado + 21 Nuevos corta todo ANTES de escribir)
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T17: Límite Masivo Preventivo (1 Modificado + 21 Nuevos)] ---")
    course_folder = "CIV222_FUNDAMENTOS_DE_INGENIERÍA_DE_CONSTRUCCIÓN_Y_ADMINISTRACIÓN_"
    pauta_dir = os.path.join(test_root_dir, course_folder, "Planificacion/General")
    os.makedirs(pauta_dir, exist_ok=True)
    pauta_path = os.path.join(pauta_dir, "Pauta_Vigente.pdf")

    # 1. Sembrar archivo vigente y registrarlo en manifest (Versión 1)
    c_original = b"%PDF-1.4 Contenido original de Pauta Vigente - Version 1"
    with open(pauta_path, "wb") as f:
        f.write(c_original)
    sha_original = hashlib.sha256(c_original).hexdigest()

    url_vigente = f"http://127.0.0.1:{port}/webservice/pluginfile.php/t17/Pauta_Vigente.pdf"
    manifest_t17_init = {
        url_vigente: {
            "timemodified": TS_V1,
            "filesize": len(c_original),
            "local_path": pauta_path,
            "sha256": sha_original,
            "last_seen": datetime.now().isoformat()
        }
    }
    with open(test_manifest_file, "w", encoding="utf-8") as mf:
        json.dump(manifest_t17_init, mf, indent=2)

    server_state["mode"] = "t17"
    server_state["t17_pauta_v2"] = b"%PDF-1.4 Contenido MODIFICADO de Pauta Vigente - Version 2"

    # 2. Ejecutar SIN --permitir-masivo
    p_t17_block = subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)

    # Verificaciones T17:
    # - Código 1
    # - Archivo original intacto (mismo sha256 y contenido)
    # - Cero archivos de respaldo _v* creados
    # - Cero archivos nuevos en disco
    # - Manifest intacto sin cambios
    c_after = open(pauta_path, "rb").read() if os.path.exists(pauta_path) else b""
    sha_after = hashlib.sha256(c_after).hexdigest()
    file_intact = (c_after == c_original and sha_after == sha_original)

    backups_created = [f for f in os.listdir(pauta_dir) if f.startswith("Pauta_Vigente_v")]
    zero_backups = (len(backups_created) == 0)

    new_files_in_dir = [f for f in os.listdir(pauta_dir) if f.startswith("Doc_Nuevo")]
    zero_new_files = (len(new_files_in_dir) == 0)

    manifest_after = json.load(open(test_manifest_file, "r", encoding="utf-8")) if os.path.exists(test_manifest_file) else {}
    manifest_intact = (manifest_after.get(url_vigente, {}).get("timemodified") == TS_V1 and len(manifest_after) == 1)
    msg_revision = "revisión requerida" in p_t17_block.stdout.lower() or "revision requerida" in p_t17_block.stdout.lower()

    t17_pass = (
        p_t17_block.returncode == 1 and
        file_intact and
        zero_backups and
        zero_new_files and
        manifest_intact and
        msg_revision
    )
    print(f"  Bloqueo preventivo: código de retorno 1: {p_t17_block.returncode == 1}")
    print(f"  Archivo original 100% intacto: {file_intact} (sha={sha_after[:10]}...)")
    print(f"  Cero respaldos _v* espurios creados: {zero_backups} (encontrados: {backups_created})")
    print(f"  Cero archivos nuevos escritos en disco: {zero_new_files}")
    print(f"  Manifest intacto sin modificaciones: {manifest_intact}")
    print(f"  Mensaje 'revisión requerida' emitido: {msg_revision}")
    print(f"Resultado T17: {'PASS' if t17_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T20: Latido ultima_sincronizacion.json en cada corrida completa
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T20: Latido de sincronización] ---")
    server_state["mode"] = "normal"
    hb_path = os.path.join(test_repo_dir, "universidad/2026-2/ultima_sincronizacion.json")
    if os.path.exists(hb_path):
        os.remove(hb_path)
    p_t20 = subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)
    t20_pass = False
    if os.path.exists(hb_path):
        hb_txt = open(hb_path, encoding="utf-8").read()
        hb = json.loads(hb_txt)
        campos_ok = set(hb) == {"fecha", "estado", "archivos_nuevos_o_modificados", "errores"}
        estado_coherente = (hb["estado"] == "OK") == (p_t20.returncode == 0)
        sin_token = test_token not in hb_txt
        t20_pass = campos_ok and estado_coherente and sin_token
        print(f"  Archivo escrito: True | campos: {campos_ok} | estado coherente con código {p_t20.returncode}: {estado_coherente} | sin token: {sin_token}")
    else:
        print("  Archivo ultima_sincronizacion.json no escrito")
    print(f"Resultado T20: {'PASS' if t20_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T18: El respaldo en Drive nunca borra en destino lo que falte en origen
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T18: Respaldo rclone no destructivo] ---")
    from sincronizar_aula_semanal import construir_comando_respaldo_arbol
    cmd_t18 = construir_comando_respaldo_arbol("rclone", "/origen", "gdrive:Universidad/2026-2/", dry_run=True)
    usa_copy = (cmd_t18[1] == "copy" and "--dry-run" in cmd_t18)
    sin_flags_borrado = not any(a.startswith("--delete") or a in ("--max-delete",) for a in cmd_t18)
    print(f"  Subcomando 'copy' (no 'sync'): {usa_copy} -> {' '.join(cmd_t18[:4])}")
    print(f"  Sin flags --delete*: {sin_flags_borrado}")

    rclone_real = shutil.which("rclone")
    conserva_en_destino = True
    if rclone_real:
        t18_dir = tempfile.mkdtemp(prefix="t18_rclone_")
        src18, dst18 = os.path.join(t18_dir, "origen"), os.path.join(t18_dir, "destino")
        os.makedirs(src18)
        for n in ("a.pdf", "b.pdf"):
            with open(os.path.join(src18, n), "wb") as f:
                f.write(b"%PDF-1.4 " + n.encode())
        subprocess.run(construir_comando_respaldo_arbol(rclone_real, src18, dst18), capture_output=True, text=True)
        os.remove(os.path.join(src18, "b.pdf"))  # simula pérdida local
        r18 = subprocess.run(construir_comando_respaldo_arbol(rclone_real, src18, dst18), capture_output=True, text=True)
        conserva_en_destino = (r18.returncode == 0 and os.path.exists(os.path.join(dst18, "b.pdf")))
        print(f"  rclone real: archivo borrado en origen se conserva en destino: {conserva_en_destino}")
        shutil.rmtree(t18_dir, ignore_errors=True)
    else:
        print("  rclone no instalado: se omite la verificación con rclone real (solo se valida el comando).")

    t18_pass = usa_copy and sin_flags_borrado and conserva_en_destino
    print(f"Resultado T18: {'PASS' if t18_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # AVISOS: avisos.md solo se reescribe si hay novedades y sin *Última verificación*
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO AVISOS: Idempotencia y Formato en Foros] ---")
    server_state["mode"] = "normal"
    server_state["discussions"] = [
        {"discussion": 101, "name": "Aviso 1", "userfullname": "Profesor", "created": 1785000000, "message": "<p>Mensaje 1</p>"}
    ]
    subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)
    avisos_path = os.path.join(test_repo_dir, "universidad/2026-2/CIV222_FUNDAMENTOS_DE_INGENIERÍA_DE_CONSTRUCCIÓN_Y_ADMINISTRACIÓN_/avisos.md")
    
    avisos_pass = False
    if os.path.exists(avisos_path):
        c1 = open(avisos_path, "r", encoding="utf-8").read()
        no_verif_line = "*Última verificación:" not in c1
        mtime_1 = os.path.getmtime(avisos_path)
        
        time.sleep(1.2)
        subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)
        mtime_2 = os.path.getmtime(avisos_path)
        
        time.sleep(1.2)
        server_state["discussions"].append({
            "discussion": 102, "name": "Aviso Nuevo 2", "userfullname": "Ayudante", "created": 1785100000, "message": "<p>Clase recuperativa</p>"
        })
        subprocess.run([sys.executable, SYNC_SCRIPT], env=env_prod, capture_output=True, text=True)
        mtime_3 = os.path.getmtime(avisos_path)

        sin_cambios_estable = (mtime_1 == mtime_2)
        con_cambios_actualiza = (mtime_3 > mtime_2)
        avisos_pass = (no_verif_line and sin_cambios_estable and con_cambios_actualiza)
        print(f"  Sin línea de última verificación: {no_verif_line}")
        print(f"  Mtime sin cambios: {sin_cambios_estable} (mtime1={mtime_1}, mtime2={mtime_2})")
        print(f"  Mtime con nueva discusión: {con_cambios_actualiza} (mtime3={mtime_3})")

    print(f"Resultado Avisos Idempotencia: {'PASS' if avisos_pass else 'FAIL'}\n")

    # ----------------------------------------------------------------------
    # T13: Aislamiento Total e Integridad de Archivos Reales
    # ----------------------------------------------------------------------
    print("--- [EJECUTANDO T13: Aislamiento Total e Integridad de Datos Reales] ---")
    post_git_status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
    post_dir_mtime = os.path.getmtime(REAL_ROOT_DIR) if os.path.exists(REAL_ROOT_DIR) else 0
    post_log_mtime = os.path.getmtime(REAL_LOG_FILE) if os.path.exists(REAL_LOG_FILE) else 0

    git_clean = (post_git_status == "" and post_git_status == pre_git_status)
    dir_intact = (post_dir_mtime == pre_dir_mtime)
    log_intact = (post_log_mtime == pre_log_mtime)

    t13_pass = (git_clean and dir_intact and log_intact)
    print(f"  Git status del repo real limpio: {git_clean} (salida: '{post_git_status}')")
    print(f"  mtime carpeta real 2026-2 intacto: {dir_intact} (pre={pre_dir_mtime}, post={post_dir_mtime})")
    print(f"  mtime log real intacto: {log_intact} (pre={pre_log_mtime}, post={post_log_mtime})")
    print(f"Resultado T13: {'PASS' if t13_pass else 'FAIL'}\n")

    # Limpieza del entorno temporal
    shutil.rmtree(test_env_dir, ignore_errors=True)
    mock_server.shutdown()

    # ----------------------------------------------------------------------
    # RESUMEN GLOBAL
    # ----------------------------------------------------------------------
    print("======================================================================")
    global_pass = t2_pass and t3_pass and t9_pass and t10_pass and t11_pass and t12_pass and t14_pass and t15_pass and t16_pass and t17_pass and t18_pass and t20_pass and avisos_pass and t13_pass
    print(f"RESUMEN GLOBAL: {'TODAS LAS PRUEBAS PASARON (100% PASS)' if global_pass else 'FALLÓ ALGUNA PRUEBA'}")
    print("======================================================================")
    return 0 if global_pass else 1

if __name__ == "__main__":
    sys.exit(run_test_suite())
