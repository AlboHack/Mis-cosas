# T2 real: ejecuta run_sync() de produccion con API Moodle REST simulada.
# Uso: python3 scripts/pruebas/test_t2_real.py scripts/sincronizar_aula_semanal.py <dir_tmp> 1 ; luego ... <mismo dir_tmp> 2
# PASA si tras la corrida 2 el archivo vigente contiene "version 2" y existe Pauta_vYYYYMMDD.pdf con "version 1".
import importlib.util, os, sys, io, json, urllib.parse, time

# Aislamiento: generar_contexto_ramos, que run_sync() importa, toma sus rutas de estas variables;
# sin ellas escribía Contexto_Asignatura.md en el repo real.
os.environ["SYNC_REPO_DIR"] = os.path.join(sys.argv[2], "no_repo")
os.environ["SYNC_ROOT_DIR"] = os.path.join(sys.argv[2], "2026-2")

spec = importlib.util.spec_from_file_location("sync", sys.argv[1])
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

tmp = sys.argv[2]
v = sys.argv[3]
s.ROOT_DIR = os.path.join(tmp, "2026-2")
s.REPO_DIR = os.path.join(tmp, "no_repo")
s.LOG_FILE = os.path.join(tmp, "log.txt")
s.MANIFEST_FILE = os.path.join(tmp, "manifest.json")
s.LOCK_FILE = os.path.join(tmp, "lock")
s.get_token = lambda: "mock_token"

PURL = "https://aula.usm.cl/pluginfile.php/999/mod_folder/content/0/Pauta.pdf?forcedownload=1"
contenido = {"v": b"%PDF-1.4 version 1 de la pauta" if v == "1" else b"%PDF-1.4 version 2 CORREGIDA, otro largo"}
now_ts = int(time.time())

class R(io.BytesIO):
    def __init__(self, d, u):
        super().__init__(d)
        self.u = u
        self.headers = {}
    def geturl(self):
        return self.u

def fake(req, timeout=None):
    u = req.full_url if hasattr(req, "full_url") else req
    if "webservice/rest/server.php" in u:
        data = {}
        if hasattr(req, "data") and req.data:
            data = dict(urllib.parse.parse_qsl(req.data.decode("utf-8", errors="ignore")))
        fn = data.get("wsfunction", "")
        if fn == "core_webservice_get_site_info":
            res = {"username": "nicolas", "fullname": "Nicolas", "userissiteadmin": False}
        elif fn == "core_course_get_contents":
            cid = int(data.get("courseid", 0))
            if cid == 62182:
                res = [{
                    "name": "Certamenes",
                    "modules": [{
                        "id": 111,
                        "modname": "resource",
                        "name": "Pauta",
                        "contents": [{
                            "type": "file",
                            "filename": "Pauta.pdf",
                            "fileurl": PURL,
                            "filesize": len(contenido["v"]),
                            "timemodified": now_ts - 3600 if v == "1" else now_ts
                        }]
                    }]
                }]
            else:
                res = []
        elif fn == "mod_assign_get_assignments":
            res = {"courses": []}
        elif fn == "mod_forum_get_forums_by_courses":
            res = []
        elif fn == "core_calendar_get_calendar_events":
            res = {"events": []}
        elif fn == "core_message_get_conversations":
            res = {"conversations": []}
        else:
            res = {}
        return R(json.dumps(res).encode("utf-8"), u)

    if PURL in u:
        return R(contenido["v"], u)
    return R(b"<p>vacio</p>", u)

s.urllib.request.urlopen = fake
s.run_sync()
for root, _, fs in os.walk(s.ROOT_DIR):
    for f in fs:
        p = os.path.join(root, f)
        print("ARCHIVO:", os.path.relpath(p, s.ROOT_DIR), open(p, "rb").read())
