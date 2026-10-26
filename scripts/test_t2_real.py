# T2 real: ejecuta run_sync() de produccion con HTTP simulado. Uso: python3 test_t2_real.py scripts/sincronizar_aula_semanal.py <dir_tmp> 1 ; luego ... <mismo dir_tmp> 2
# PASA si tras la corrida 2 el archivo vigente contiene "version 2" y existe Pauta_vYYYYMMDD.pdf con "version 1".
import importlib.util, os, sys, tempfile, io, hashlib
spec = importlib.util.spec_from_file_location("sync", sys.argv[1]); s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
tmp = sys.argv[2]
s.ROOT_DIR = os.path.join(tmp, "2026-2"); s.REPO_DIR = os.path.join(tmp, "no_repo")
s.LOG_FILE = os.path.join(tmp, "log.txt"); s.MANIFEST_FILE = os.path.join(tmp, "manifest.json"); s.LOCK_FILE = os.path.join(tmp, "lock")
s.get_cookie = lambda: "x"
FURL = "https://aula.usm.cl/mod/folder/view.php?id=111"
PURL = "https://aula.usm.cl/pluginfile.php/999/mod_folder/content/0/Pauta.pdf?forcedownload=1"
contenido = {"v": b"%PDF-1.4 version 1 de la pauta" if sys.argv[3]=="1" else b"%PDF-1.4 version 2 CORREGIDA, otro largo"}
class R(io.BytesIO):
    def __init__(self, d, u): super().__init__(d); self.u = u; self.headers = {}
    def geturl(self): return self.u
def fake(req, timeout=None):
    u = req.full_url if hasattr(req, "full_url") else req
    if "course/view.php?id=62182" in u: return R(f'<a href="{FURL}">Certamenes Carpeta</a>'.encode(), u)
    if u == FURL: return R(f'<a href="{PURL}">Pauta.pdf</a>'.encode(), u)
    if u == PURL: return R(contenido["v"], u)
    return R(b"<p>vacio</p>", u)
s.urllib.request.urlopen = fake
s.run_sync()
for root, _, fs in os.walk(s.ROOT_DIR):
    for f in fs:
        p = os.path.join(root, f); print("ARCHIVO:", os.path.relpath(p, s.ROOT_DIR), open(p, "rb").read())
