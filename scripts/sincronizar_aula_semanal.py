#!/data/data/com.agycli/files/usr/bin/python3
"""
sincronizar_aula_semanal.py
Sincronización incremental determinística de Aula USM con Google Drive, GitHub y Google Calendar.
Cumple estrictamente con los estándares de seguridad, idempotencia y validación de contenido.
"""

import urllib.request, urllib.parse, re, json, os, subprocess, hashlib, shutil, fcntl, sys, unicodedata
from datetime import datetime
from html import unescape
import zipfile

BASE_URL = "https://aula.usm.cl"
ROOT_DIR = "/storage/emulated/0/Download/Universidad/2026-2"
REPO_DIR = "/data/data/com.agycli/files/home/Mis-cosas"
LOG_FILE = "/storage/emulated/0/Download/Universidad/Registro_Sincronizaciones.log"
COOKIE_FILE = "/data/data/com.agycli/files/home/.moodle_cookie"
MANIFEST_FILE = "/storage/emulated/0/Download/Universidad/sync_manifest.json"
LOCK_FILE = "/data/data/com.agycli/files/home/.sync_aula.lock"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted, flush=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def get_cookie():
    """Lee la cookie de Moodle guardada localmente con permisos 600."""
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r") as f:
            cookie = f.read().strip()
            if cookie:
                return cookie
    log("ERROR CRÍTICO: No se encontró .moodle_cookie o está vacía. Renovar credencial en el archivo.")
    return ""

def sanitizar(nombre):
    clean = re.sub(r'[/\\?%*:|"<>]', '_', nombre).strip()
    return unicodedata.normalize('NFC', clean)

def extraer_nombre_archivo(resp, fallback_title):
    cd_header = resp.headers.get("Content-Disposition", "")
    fname = ""
    # RFC 5987 filename*
    if "filename*=" in cd_header:
        m = re.search(r"filename\*=(?:UTF-8|utf-8)''([^;\s]+)", cd_header)
        if m:
            fname = urllib.parse.unquote(m.group(1))
    if not fname and "filename=" in cd_header:
        m = re.search(r'filename=[\"\']?([^\"\';]+)', cd_header)
        if m:
            fname = m.group(1)
            
    if not fname:
        final_url = resp.geturl().split("?")[0]
        fname = os.path.basename(final_url)
        
    if not fname or fname.endswith(".php"):
        fname = fallback_title + ".pdf"
        
    return sanitizar(fname)

def is_valid_document(data, filename):
    """Valida que la respuesta no sea HTML de error y coincida con el formato esperado."""
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

def determine_subfolder(cshort, ftitle):
    ft_clean = sanitizar(re.sub(r'\s*Carpeta\s*$', '', ftitle)).strip()
    ft_lower = ft_clean.lower()
    if any(k in ft_lower for k in ["planificaci", "programa", "calendario"]):
        return os.path.join("Planificacion", ft_clean)
    elif any(k in ft_lower for k in ["certam", "control", "tarea", "entrega"]):
        return os.path.join("Evaluaciones_y_Entregas", ft_clean)
    else:
        return os.path.join("Material_y_Apuntes", ft_clean)

def run_sync():
    # 1. Lockfile para evitar ejecuciones concurrentes
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("[!] Otra instancia de sincronizar_aula_semanal.py ya se encuentra en ejecución.")
        return 0

    errores = []
    log("=======================================================")
    log("INICIANDO SINCRONIZACIÓN SEMANAL INCREMENTAL DETERMINÍSTICA")
    log("=======================================================")
    
    cookie = get_cookie()
    if not cookie:
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
    
    for c in courses:
        cid = c["id"]
        cshort = c["short"]
        cdir = os.path.join(ROOT_DIR, c["folder"])
        log(f"Revisando novedades en: {cshort} (ID: {cid})...")
        
        try:
            req = urllib.request.Request(f"{BASE_URL}/course/view.php?id={cid}", headers={
                "Cookie": f"MoodleSession={cookie}",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; Xiaomi Pad 5) AppleWebKit/537.36"
            })
            chtml = urllib.request.urlopen(req, timeout=25).read().decode(errors="ignore")
        except Exception as e:
            err_msg = f"{cshort} vista de curso: {e}"
            log(f"  [ERROR] {err_msg}")
            errores.append(err_msg)
            continue
            
        # 1. Carpetas (mod/folder)
        folders = re.findall(r'href=[\"\'](https://aula\.usm\.cl/mod/folder/view\.php\?id=\d+)[\"\'][^>]*>(.*?)</a>', chtml)
        for furl, ftitle_raw in folders:
            ftitle = sanitizar(unescape(re.sub(r'<[^>]+>', '', ftitle_raw)))
            sub_path = determine_subfolder(cshort, ftitle)
            target_dir = os.path.join(cdir, sub_path)
            
            try:
                req_f = urllib.request.Request(furl, headers={
                    "Cookie": f"MoodleSession={cookie}",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Xiaomi Pad 5) AppleWebKit/537.36"
                })
                folder_html = urllib.request.urlopen(req_f, timeout=25).read().decode(errors="ignore")
                files_found = re.findall(r'href=[\"\'](https://aula\.usm\.cl/pluginfile\.php/[^\"]+)[\"\'][^>]*>(.*?)</a>', folder_html)
                for dl_url, fname_raw in files_found:
                    fname = sanitizar(unescape(re.sub(r'<[^>]+>', '', fname_raw))).strip()
                    if not fname or dl_url.endswith("/") or fname.endswith(".php"): continue
                    
                    url_clean = dl_url.split("?")[0]
                    local_fpath = os.path.join(target_dir, fname)
                    
                    # Verificación contra manifest
                    manifest_entry = manifest.get(url_clean)
                    if manifest_entry and os.path.exists(local_fpath):
                        if os.path.getsize(local_fpath) == manifest_entry.get("bytes"):
                            manifest[url_clean]["last_seen"] = datetime.now().isoformat()
                            continue
                            
                    # Descargar y validar
                    try:
                        req_dl = urllib.request.Request(dl_url, headers={
                            "Cookie": f"MoodleSession={cookie}",
                            "User-Agent": "Mozilla/5.0 (Linux; Android 13; Xiaomi Pad 5) AppleWebKit/537.36"
                        })
                        f_data = urllib.request.urlopen(req_dl, timeout=30).read()
                        valido, mot = is_valid_document(f_data, fname)
                        if not valido:
                            err_v = f"Documento inválido en {dl_url} ({fname}): {mot}"
                            log(f"  [ERROR VALIDACIÓN] {err_v}")
                            errores.append(err_v)
                            continue
                            
                        sha_curr = hashlib.sha256(f_data).hexdigest()
                        
                        # Si existía versión previa con diferente hash, archivar versión previa
                        if os.path.exists(local_fpath):
                            old_sha = hashlib.sha256(open(local_fpath, "rb").read()).hexdigest()
                            if old_sha != sha_curr:
                                v_ext = os.path.splitext(fname)[1]
                                v_base = os.path.splitext(fname)[0]
                                f_old_backup = os.path.join(target_dir, f"{v_base}_v{datetime.now().strftime('%Y%m%d')}{v_ext}")
                                shutil.move(local_fpath, f_old_backup)
                                log(f"  [VERSIÓN ANTERIOR ARCHIVADA] -> {os.path.basename(f_old_backup)}")
                            else:
                                manifest[url_clean] = {"sha256": sha_curr, "bytes": len(f_data), "local_path": local_fpath, "last_seen": datetime.now().isoformat()}
                                continue
                                
                        os.makedirs(target_dir, exist_ok=True)
                        with open(local_fpath, "wb") as out_f:
                            out_f.write(f_data)
                            
                        manifest[url_clean] = {"sha256": sha_curr, "bytes": len(f_data), "local_path": local_fpath, "last_seen": datetime.now().isoformat()}
                        archivos_descargados.append(local_fpath)
                        log(f"  [NUEVO ARCHIVO] {cshort} -> {sub_path}/{fname}")
                    except Exception as dl_err:
                        err_msg = f"Error descargando {fname} de {dl_url}: {dl_err}"
                        log(f"    [ERROR] {err_msg}")
                        errores.append(err_msg)
            except Exception as fe:
                err_msg = f"Error leyendo carpeta {furl}: {fe}"
                log(f"  [ERROR] {err_msg}")
                errores.append(err_msg)

        # 2. Recursos directos (mod/resource)
        resources = re.findall(r'href=[\"\'](https://aula\.usm\.cl/mod/resource/view\.php\?id=\d+)[\"\'][^>]*>(.*?)</a>', chtml)
        for rurl, rtitle_raw in resources:
            rtitle = sanitizar(unescape(re.sub(r'<[^>]+>', '', rtitle_raw)))
            rtitle = re.sub(r'\s*Archivo\s*$', '', rtitle).strip()
            
            try:
                req_r = urllib.request.Request(rurl, headers={
                    "Cookie": f"MoodleSession={cookie}",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Xiaomi Pad 5) AppleWebKit/537.36"
                })
                resp = urllib.request.urlopen(req_r, timeout=30)
                final_url = resp.geturl()
                url_clean = final_url.split("?")[0]
                
                fname = extraer_nombre_archivo(resp, rtitle)
                
                # Clasificar subcarpeta
                if any(k in rtitle.lower() for k in ["planificaci", "programa", "calendario"]):
                    dest_sub = os.path.join("Planificacion", rtitle)
                elif any(k in rtitle.lower() for k in ["certam", "control", "tarea"]):
                    dest_sub = os.path.join("Evaluaciones_y_Entregas", rtitle)
                else:
                    dest_sub = os.path.join("Material_y_Apuntes", rtitle)
                    
                target_dir = os.path.join(cdir, dest_sub)
                local_fpath = os.path.join(target_dir, fname)
                
                manifest_entry = manifest.get(url_clean)
                if manifest_entry and os.path.exists(local_fpath):
                    if os.path.getsize(local_fpath) == manifest_entry.get("bytes"):
                        manifest[url_clean]["last_seen"] = datetime.now().isoformat()
                        continue
                        
                data = resp.read()
                valido, mot = is_valid_document(data, fname)
                if not valido:
                    err_v = f"Documento inválido en {rurl} ({fname}): {mot}"
                    log(f"  [ERROR VALIDACIÓN] {err_v}")
                    errores.append(err_v)
                    continue
                    
                sha_curr = hashlib.sha256(data).hexdigest()
                if os.path.exists(local_fpath):
                    old_sha = hashlib.sha256(open(local_fpath, "rb").read()).hexdigest()
                    if old_sha != sha_curr:
                        v_ext = os.path.splitext(fname)[1]
                        v_base = os.path.splitext(fname)[0]
                        f_old = os.path.join(target_dir, f"{v_base}_v{datetime.now().strftime('%Y%m%d')}{v_ext}")
                        shutil.move(local_fpath, f_old)
                        log(f"  [VERSIÓN ANTERIOR ARCHIVADA] -> {os.path.basename(f_old)}")
                    else:
                        manifest[url_clean] = {"sha256": sha_curr, "bytes": len(data), "local_path": local_fpath, "last_seen": datetime.now().isoformat()}
                        continue
                        
                os.makedirs(target_dir, exist_ok=True)
                with open(local_fpath, "wb") as out_f:
                    out_f.write(data)
                    
                manifest[url_clean] = {"sha256": sha_curr, "bytes": len(data), "local_path": local_fpath, "last_seen": datetime.now().isoformat()}
                archivos_descargados.append(local_fpath)
                log(f"  [NUEVO RECURSO] {cshort} -> {dest_sub}/{fname}")
            except Exception as re_err:
                err_msg = f"Error en recurso {rurl}: {re_err}"
                log(f"  [ERROR] {err_msg}")
                errores.append(err_msg)

    guardar_manifest(manifest)
    log("-------------------------------------------------------")
    log(f"RESULTADO: {len(archivos_descargados)} archivo(s) nuevo(s) o modificado(s). Errores: {len(errores)}")
    
    # 3. Subida INCREMENTAL a Google Drive (SÓLO si hubo archivos nuevos)
    if len(archivos_descargados) > 0:
        fecha_str = datetime.now().strftime('%Y%m%d')
        zip_delta = f"/storage/emulated/0/Download/Universidad_Nuevos_{fecha_str}.zip"
        
        with zipfile.ZipFile(zip_delta, 'w', zipfile.ZIP_DEFLATED) as zf_new:
            for nf in archivos_descargados:
                rel = os.path.relpath(nf, ROOT_DIR)
                zf_new.write(nf, rel)
                
        sz_mb = os.path.getsize(zip_delta) / (1024 * 1024)
        log(f"Paquete Delta generado ({sz_mb:.2f} MB con {len(archivos_descargados)} archivos).")
        
        # Comprobar si rclone está disponible para subida determinística
        rclone_bin = shutil.which("rclone")
        if rclone_bin:
            log("Subiendo paquete delta vía rclone a Google Drive...")
            rc_p = subprocess.run(["rclone", "copy", zip_delta, "gdrive:Universidad/Deltas/"], capture_output=True, text=True)
            if rc_p.returncode == 0:
                zip_base = os.path.basename(zip_delta)
                chk = subprocess.run(["rclone", "lsjson", f"gdrive:Universidad/Deltas/{zip_base}"], capture_output=True, text=True)
                if chk.returncode == 0 and zip_base in chk.stdout:
                    log("¡Paquete delta subido y verificado exitosamente con rclone lsjson!")
                else:
                    err_rc = f"Fallo al verificar con rclone lsjson ({chk.returncode}): {chk.stderr.strip()}"
                    log(f"  [ERROR] {err_rc}")
                    errores.append(err_rc)
            else:
                err_rc = f"Fallo rclone copy ({rc_p.returncode}): {rc_p.stderr.strip()}"
                log(f"  [ERROR] {err_rc}")
                errores.append(err_rc)
        else:
            err_rc = "rclone no está instalado o no disponible en PATH para subida a Google Drive."
            log(f"  [ERROR] {err_rc}")
            errores.append(err_rc)
    else:
        log("INCREMENTAL: Sin archivos nuevos en Aula USM esta semana. No se genera ZIP ni subida a Drive.")
        
    # 4. Sincronización INCREMENTAL con GitHub AlboHack/Mis-cosas
    if os.path.exists(REPO_DIR):
        try:
            log("Sincronizando con repositorio GitHub AlboHack/Mis-cosas...")
            # 4.1 Pull seguro con autostash
            p_pull = subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=REPO_DIR, capture_output=True, text=True)
            if p_pull.returncode != 0:
                subprocess.run(["git", "rebase", "--abort"], cwd=REPO_DIR, capture_output=True)
                err_g = f"Git rebase conflictivo, abortado: {p_pull.stderr.strip()}"
                log(f"  [ERROR] {err_g}")
                errores.append(err_g)
            else:
                # 4.2 Si hubo archivos nuevos, copiarlos al repo respetando límite de 50 MB
                target_repo_uni = os.path.join(REPO_DIR, "universidad/2026-2")
                if len(archivos_descargados) > 0:
                    for src_f in archivos_descargados:
                        sz_mb = os.path.getsize(src_f) / (1024 * 1024)
                        if sz_mb >= 50:
                            log(f"  [OMITIDO DE GIT > 50 MB] {os.path.basename(src_f)} ({sz_mb:.1f} MB) - Mantenido local y en Drive")
                            continue
                        rel = os.path.relpath(src_f, ROOT_DIR)
                        dst_f = os.path.join(target_repo_uni, rel)
                        os.makedirs(os.path.dirname(dst_f), exist_ok=True)
                        shutil.copy2(src_f, dst_f)
                
                # 4.3 Git add y commit restringido exclusivamente a universidad/2026-2/
                subprocess.run(["git", "add", "universidad/2026-2/"], cwd=REPO_DIR, check=True)
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

    # 5. Sincronización de calendario nativo
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

    log(f"FINALIZADO. Estado: {'OK' if len(errores) == 0 else 'CON ERRORES (' + str(len(errores)) + ')'}")
    log("=======================================================")
    return 0 if len(errores) == 0 else 1

if __name__ == "__main__":
    sys.exit(run_sync())
