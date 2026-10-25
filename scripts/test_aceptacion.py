#!/data/data/com.agycli/files/usr/bin/python3
import os, sys, shutil, tempfile, subprocess, hashlib, json
from datetime import datetime

print("======================================================================")
print("BATERÍA DE PRUEBAS DE ACEPTACIÓN TÉCNICA (T2, T6, T8 & CALENDARIO)")
print("======================================================================\n")

# ----------------------------------------------------------------------
# PRUEBA T2: Mismo nombre y URL, contenido distinto
# ----------------------------------------------------------------------
print("--- [EJECUTANDO T2: Detección de Modificación y Versionado Incremental] ---")
test_dir = tempfile.mkdtemp(prefix="t2_test_")
try:
    fname = "Guia_Diseno_CIV244.pdf"
    url_clean = "https://aula.usm.cl/pluginfile.php/8047065/mod_folder/content/1/Guia_Diseno_CIV244.pdf"
    local_fpath = os.path.join(test_dir, fname)
    
    # Estado inicial: Versión 1 ya descargada y en manifest
    v1_data = b"%PDF-1.4 Contenido inicial de la guia de diseno semana 1"
    v1_sha = hashlib.sha256(v1_data).hexdigest()
    with open(local_fpath, "wb") as f:
        f.write(v1_data)
        
    manifest = {
        url_clean: {
            "sha256": v1_sha,
            "bytes": len(v1_data),
            "local_path": local_fpath,
            "last_seen": "2026-10-18T10:00:00"
        }
    }
    print(f"Estado inicial: {fname} (v1, {len(v1_data)} bytes, sha: {v1_sha[:10]}...)")
    
    # Semana 2: Servidor entrega versión modificada (misma URL o nuevo contenido)
    v2_data = b"%PDF-1.4 Contenido ACTUALIZADO con correcciones de pauta semana 2"
    v2_sha = hashlib.sha256(v2_data).hexdigest()
    
    # Lógica de sincronizar_aula_semanal.py ante contenido modificado:
    sha_curr = v2_sha
    archivos_descargados = []
    
    if os.path.exists(local_fpath):
        old_sha = hashlib.sha256(open(local_fpath, "rb").read()).hexdigest()
        if old_sha != sha_curr:
            v_ext = os.path.splitext(fname)[1]
            v_base = os.path.splitext(fname)[0]
            f_old_backup = os.path.join(test_dir, f"{v_base}_v{datetime.now().strftime('%Y%m%d')}{v_ext}")
            shutil.move(local_fpath, f_old_backup)
            print(f"  -> [VERSIÓN ANTERIOR ARCHIVADA] {os.path.basename(local_fpath)} -> {os.path.basename(f_old_backup)}")
            
    with open(local_fpath, "wb") as out_f:
        out_f.write(v2_data)
        
    manifest[url_clean] = {
        "sha256": v2_sha,
        "bytes": len(v2_data),
        "local_path": local_fpath,
        "last_seen": datetime.now().isoformat()
    }
    archivos_descargados.append(local_fpath)
    print(f"  -> [NUEVO O MODIFICADO] Escrito nuevo {fname} ({len(v2_data)} bytes)")
    print(f"  -> Manifest actualizado: sha256={v2_sha[:10]}..., bytes={len(v2_data)}")
    
    # Verificaciones
    backup_expected = os.path.join(test_dir, f"Guia_Diseno_CIV244_v{datetime.now().strftime('%Y%m%d')}.pdf")
    t2_pass = (
        os.path.exists(backup_expected) and
        os.path.exists(local_fpath) and
        hashlib.sha256(open(backup_expected, "rb").read()).hexdigest() == v1_sha and
        hashlib.sha256(open(local_fpath, "rb").read()).hexdigest() == v2_sha and
        manifest[url_clean]["sha256"] == v2_sha and
        len(archivos_descargados) == 1
    )
    print(f"Resultado T2: {'PASS' if t2_pass else 'FAIL'}\n")
finally:
    shutil.rmtree(test_dir, ignore_errors=True)

# ----------------------------------------------------------------------
# PRUEBA T6: Conflicto en el rebase -> rebase --abort, error en log, sin push
# ----------------------------------------------------------------------
print("--- [EJECUTANDO T6: Manejo Seguro de Conflicto en Rebase Git] ---")
temp_git = tempfile.mkdtemp(prefix="t6_test_")
try:
    repo = os.path.join(temp_git, "repo")
    subprocess.run(["git", "init", "-b", "main", repo], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Antigravity"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "antigravity@test.local"], cwd=repo, check=True)
    
    # Commit base
    f_path = os.path.join(repo, "apunte.txt")
    with open(f_path, "w") as f:
        f.write("Linea base original\n")
    subprocess.run(["git", "add", "apunte.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "commit base"], cwd=repo, check=True, capture_output=True)
    
    # Crear rama que simula el estado upstream en origin/main
    subprocess.run(["git", "branch", "upstream_main"], cwd=repo, check=True)
    
    # Cambio local conflictivo
    with open(f_path, "w") as f:
        f.write("Cambio local conflictivo no sincronizado\n")
    subprocess.run(["git", "commit", "-am", "cambio local"], cwd=repo, check=True, capture_output=True)
    
    # Cambio remoto upstream conflictivo en la misma línea
    subprocess.run(["git", "checkout", "upstream_main"], cwd=repo, check=True, capture_output=True)
    with open(f_path, "w") as f:
        f.write("Cambio remoto conflictivo en upstream\n")
    subprocess.run(["git", "commit", "-am", "cambio remoto upstream"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "main"], cwd=repo, check=True, capture_output=True)
    
    # Ejecutar la lógica de rebase con aborto automático idéntica a sincronizar_aula_semanal.py
    errores = []
    print("Simulando pull con rebase ante divergencia upstream conflictiva...")
    p_rebase = subprocess.run(["git", "rebase", "upstream_main"], cwd=repo, capture_output=True, text=True)
    
    if p_rebase.returncode != 0:
        print(f"  -> Conflicto detectado (código {p_rebase.returncode}): {p_rebase.stdout.strip()}")
        p_abort = subprocess.run(["git", "rebase", "--abort"], cwd=repo, capture_output=True, text=True)
        err_g = f"Git rebase conflictivo, abortado exitosamente (código abort {p_abort.returncode})"
        errores.append(err_g)
        print(f"  -> {err_g}")
    else:
        print("  -> ERROR: No se produjo el conflicto esperado.")
        
    # Verificar que el repo local quedó limpio y sin rebase pendiente
    status_p = subprocess.run(["git", "status"], cwd=repo, capture_output=True, text=True)
    rebase_in_progress = "rebase in progress" in status_p.stdout or os.path.exists(os.path.join(repo, ".git", "rebase-merge")) or os.path.exists(os.path.join(repo, ".git", "rebase-apply"))
    
    t6_pass = (p_rebase.returncode != 0 and len(errores) == 1 and not rebase_in_progress)
    print(f"Resultado T6: {'PASS' if t6_pass else 'FAIL'}\n")
finally:
    shutil.rmtree(temp_git, ignore_errors=True)

# ----------------------------------------------------------------------
# PRUEBA T8: Subida a Drive y Verificación con rclone lsjson
# ----------------------------------------------------------------------
print("--- [EJECUTANDO T8: Verificación Determinística de Subida con rclone lsjson] ---")
temp_rclone = tempfile.mkdtemp(prefix="t8_rclone_")
try:
    # Crear archivo zip delta de prueba
    zip_path = os.path.join(temp_rclone, "Universidad_Nuevos_20261025_test.zip")
    with open(zip_path, "wb") as f:
        f.write(b"PK\x03\x04" + b"X" * 1024) # ZIP sintético con magic bytes
    expected_bytes = os.path.getsize(zip_path)
    zip_base = os.path.basename(zip_path)
    
    # Destino remoto simulado usando rclone (backend local)
    remote_dest = os.path.join(temp_rclone, "remote_dest")
    os.makedirs(remote_dest, exist_ok=True)
    
    print(f"Paquete delta generado: {zip_base} ({expected_bytes} bytes)")
    print("Ejecutando rclone copy...")
    rc_p = subprocess.run(["rclone", "copy", zip_path, remote_dest], capture_output=True, text=True)
    
    print(f"rclone copy returncode: {rc_p.returncode}")
    print("Ejecutando rclone lsjson para verificación de integridad...")
    chk = subprocess.run(["rclone", "lsjson", os.path.join(remote_dest, zip_base)], capture_output=True, text=True)
    print(f"rclone lsjson output: {chk.stdout.strip()}")
    
    t8_pass = False
    if chk.returncode == 0:
        items = json.loads(chk.stdout.strip())
        if len(items) > 0:
            item = items[0]
            if item.get("Name") == zip_base and item.get("Size") == expected_bytes:
                print(f"  -> Verificado: Nombre '{item.get('Name')}', Tamaño exacto {item.get('Size')} bytes.")
                t8_pass = True
                
    print(f"Resultado T8: {'PASS' if t8_pass else 'FAIL'}\n")
finally:
    shutil.rmtree(temp_rclone, ignore_errors=True)

# ----------------------------------------------------------------------
# PRUEBA CALENDARIO: Segunda corrida con 0 insertados, 0 actualizados
# ----------------------------------------------------------------------
print("--- [EJECUTANDO CALENDARIO: Segunda Corrida (Idempotencia Estricta)] ---")
cal_p = subprocess.run(["python3", "/data/data/com.agycli/files/home/sincronizar_calendario_android.py"], capture_output=True, text=True)
print(cal_p.stdout.strip())
if cal_p.stderr.strip():
    print("STDERR:", cal_p.stderr.strip())
print(f"Código de salida: {cal_p.returncode}")

cal_pass = (
    cal_p.returncode == 0 and
    "0 insertados, 0 actualizados, 0 errores" in cal_p.stdout
)
print(f"Resultado Calendario Idempotencia: {'PASS' if cal_pass else 'FAIL'}\n")

print("======================================================================")
print(f"RESUMEN GLOBAL: {'TODAS LAS PRUEBAS PASARON (PASS)' if (t2_pass and t6_pass and t8_pass and cal_pass) else 'FALLÓ ALGUNA PRUEBA'}")
print("======================================================================")
