# T3 real: ejecuta run_sync() con servidor simulado que redirige a portada/index.php?errorcode=4
# PASA si run_sync() retorna 1, se registra "ERROR CRÍTICO" en log y el manifest no cambia.
import importlib.util, os, sys, tempfile, io, json

spec = importlib.util.spec_from_file_location("sync", sys.argv[1])
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

tmp = sys.argv[2]
s.ROOT_DIR = os.path.join(tmp, "2026-2")
s.REPO_DIR = os.path.join(tmp, "no_repo")
s.LOG_FILE = os.path.join(tmp, "log.txt")
s.MANIFEST_FILE = os.path.join(tmp, "manifest.json")
s.LOCK_FILE = os.path.join(tmp, "lock")
s.get_cookie = lambda: "exp_cookie"

# Manifest preexistente que debe mantenerse inalterado
os.makedirs(tmp, exist_ok=True)
manifest_inicial = {
    "https://aula.usm.cl/pluginfile.php/999/mod_folder/content/0/Guia.pdf": {
        "sha256": "abcdef123456",
        "bytes": 500,
        "local_path": os.path.join(s.ROOT_DIR, "Guia.pdf")
    }
}
with open(s.MANIFEST_FILE, "w", encoding="utf-8") as f:
    json.dump(manifest_inicial, f)

class R(io.BytesIO):
    def __init__(self, d, u):
        super().__init__(d)
        self.u = u
        self.headers = {}
    def geturl(self):
        return self.u

def fake(req, timeout=None):
    # Simula la respuesta de Aula cuando la sesión MoodleSession expira
    return R(b"<html><head><title>Aula USM - Redireccion</title></head><body>Sesion expirada</body></html>",
             "https://aula.usm.cl/portada/index.php?errorcode=4")

s.urllib.request.urlopen = fake
ret = s.run_sync()

# Verificaciones
log_content = open(s.LOG_FILE, "r", encoding="utf-8").read() if os.path.exists(s.LOG_FILE) else ""
with open(s.MANIFEST_FILE, "r", encoding="utf-8") as f:
    manifest_final = json.load(f)

has_error_critico = "ERROR CRÍTICO" in log_content
manifest_intacto = (manifest_final == manifest_inicial)
t3_pass = (ret == 1 and has_error_critico and manifest_intacto)

print("Código de retorno:", ret)
print("ERROR CRÍTICO detectado en log:", has_error_critico)
print("Manifest inalterado:", manifest_intacto)
print(f"Resultado T3: {'PASS' if t3_pass else 'FAIL'}")

sys.exit(0 if t3_pass else 1)
