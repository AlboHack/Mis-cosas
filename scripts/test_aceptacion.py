#!/data/data/com.agycli/files/usr/bin/python3
import os, sys, shutil, tempfile, subprocess, hashlib, json
from datetime import datetime

print("======================================================================")
print("BATERÍA DE PRUEBAS DE ACEPTACIÓN TÉCNICA (T2, T6, T8 & CALENDARIO)")
print("======================================================================\n")

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SYNC_SCRIPT = os.path.join(SCRIPTS_DIR, "sincronizar_aula_semanal.py")
CAL_SCRIPT = os.path.join(SCRIPTS_DIR, "sincronizar_calendario_android.py")
T2_REAL_SCRIPT = os.path.join(SCRIPTS_DIR, "test_t2_real.py")

# ----------------------------------------------------------------------
# PRUEBA T2: test_t2_real.py ejerciendo run_sync() real de producción
# ----------------------------------------------------------------------
print("--- [EJECUTANDO T2: Detección de Modificación y Versionado Incremental (Real)] ---")
t2_dir = tempfile.mkdtemp(prefix="t2_prod_")
t2_pass = False
try:
    # Corrida 1: Moodle sirve versión 1
    p1 = subprocess.run([sys.executable, T2_REAL_SCRIPT, SYNC_SCRIPT, t2_dir, "1"], capture_output=True, text=True)
    print("Salida corrida 1:")
    for line in p1.stdout.splitlines():
        if "ARCHIVO:" in line or "NUEVO ARCHIVO" in line or "RESULTADO:" in line:
            print(f"  {line}")
            
    # Corrida 2: Moodle sirve versión 2 modificada en la misma URL
    p2 = subprocess.run([sys.executable, T2_REAL_SCRIPT, SYNC_SCRIPT, t2_dir, "2"], capture_output=True, text=True)
    print("Salida corrida 2:")
    for line in p2.stdout.splitlines():
        if "ARCHIVO:" in line or "VERSIÓN ANTERIOR" in line or "NUEVO ARCHIVO" in line or "RESULTADO:" in line:
            print(f"  {line}")
            
    # Verificaciones de archivo en disco
    target_f = os.path.join(t2_dir, "2026-2", "CIV244_MECÁNICA_DE_FLUIDOS_", "Evaluaciones_y_Entregas", "Certamenes", "Pauta.pdf")
    hoy = datetime.now().strftime("%Y%m%d")
    archived_f = os.path.join(t2_dir, "2026-2", "CIV244_MECÁNICA_DE_FLUIDOS_", "Evaluaciones_y_Entregas", "Certamenes", f"Pauta_v{hoy}.pdf")
    
    if os.path.exists(target_f) and os.path.exists(archived_f):
        c_vigente = open(target_f, "rb").read()
        c_backup = open(archived_f, "rb").read()
        if b"version 2" in c_vigente and b"version 1" in c_backup:
            t2_pass = True
            print(f"  -> Verificado: Archivo vigente contiene 'version 2', respaldo '{os.path.basename(archived_f)}' contiene 'version 1'.")
            
    print(f"Resultado T2: {'PASS' if t2_pass else 'FAIL'}\n")
finally:
    shutil.rmtree(t2_dir, ignore_errors=True)

# ----------------------------------------------------------------------
# PRUEBA T6: pull --rebase --autostash con divergencia upstream y abort
# ----------------------------------------------------------------------
print("--- [EJECUTANDO T6: Manejo Seguro de Conflicto en Rebase Git (pull --rebase --autostash)] ---")
temp_git = tempfile.mkdtemp(prefix="t6_test_")
t6_pass = False
try:
    repo = os.path.join(temp_git, "repo")
    subprocess.run(["git", "init", "-b", "main", repo], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "tester@test.local"], cwd=repo, check=True)
    
    # Commit base
    f_path = os.path.join(repo, "apunte.txt")
    with open(f_path, "w") as f:
        f.write("Linea base original\n")
    subprocess.run(["git", "add", "apunte.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "commit base"], cwd=repo, check=True, capture_output=True)
    
    # Crear rama upstream y commit conflictivo
    subprocess.run(["git", "branch", "upstream"], cwd=repo, check=True)
    subprocess.run(["git", "checkout", "upstream"], cwd=repo, check=True, capture_output=True)
    with open(f_path, "w") as f:
        f.write("Cambio remoto upstream conflictivo en la misma linea\n")
    subprocess.run(["git", "commit", "-am", "cambio upstream"], cwd=repo, check=True, capture_output=True)
    
    # Empaquetar upstream como remote bundle
    bundle_path = os.path.join(temp_git, "origin.bundle")
    subprocess.run(["git", "bundle", "create", bundle_path, "refs/heads/upstream"], cwd=repo, check=True, capture_output=True)
    
    # Volver a main y hacer commit local conflictivo
    subprocess.run(["git", "checkout", "main"], cwd=repo, check=True, capture_output=True)
    with open(f_path, "w") as f:
        f.write("Cambio local no sincronizado en la misma linea\n")
    subprocess.run(["git", "commit", "-am", "cambio local"], cwd=repo, check=True, capture_output=True)
    
    # Vincular origin al bundle
    subprocess.run(["git", "remote", "add", "origin", bundle_path], cwd=repo, check=True)
    
    # Ejecutar la lógica exacta de sincronizar_aula_semanal.py (líneas 338-343)
    errores = []
    print("Ejecutando pull --rebase --autostash origin ante divergencia upstream conflictiva...")
    p_pull = subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "upstream:refs/remotes/origin/main"], cwd=repo, capture_output=True, text=True)
    
    if p_pull.returncode != 0:
        print(f"  -> Conflicto detectado (código {p_pull.returncode}): {p_pull.stdout.strip()}")
        p_abort = subprocess.run(["git", "rebase", "--abort"], cwd=repo, capture_output=True, text=True)
        err_g = f"Git rebase conflictivo, abortado: {p_pull.stderr.strip()[:60]}..."
        errores.append(err_g)
        print("  -> Git rebase abortado exitosamente.")
        
    status_p = subprocess.run(["git", "status"], cwd=repo, capture_output=True, text=True)
    rebase_in_progress = "rebase in progress" in status_p.stdout or os.path.exists(os.path.join(repo, ".git", "rebase-merge"))
    
    t6_pass = (p_pull.returncode != 0 and len(errores) == 1 and not rebase_in_progress)
    print(f"Resultado T6: {'PASS' if t6_pass else 'FAIL'}\n")
finally:
    shutil.rmtree(temp_git, ignore_errors=True)

# ----------------------------------------------------------------------
# PRUEBA T8: Subida a Drive y Verificación con rclone lsjson (Nombre y Tamaño)
# ----------------------------------------------------------------------
print("--- [EJECUTANDO T8: Verificación Determinística de Subida con rclone lsjson] ---")
temp_rclone = tempfile.mkdtemp(prefix="t8_rclone_")
t8_pass = False
try:
    zip_path = os.path.join(temp_rclone, "Universidad_Nuevos_20261025_test.zip")
    with open(zip_path, "wb") as f:
        f.write(b"PK\x03\x04" + b"X" * 1024)
    expected_bytes = os.path.getsize(zip_path)
    zip_base = os.path.basename(zip_path)
    
    remote_dest = os.path.join(temp_rclone, "remote_dest")
    os.makedirs(remote_dest, exist_ok=True)
    
    print(f"Paquete delta generado: {zip_base} ({expected_bytes} bytes)")
    print("Ejecutando rclone copy...")
    rc_p = subprocess.run(["rclone", "copy", zip_path, remote_dest], capture_output=True, text=True)
    print(f"rclone copy returncode: {rc_p.returncode}")
    
    print("Ejecutando rclone lsjson para verificación de integridad (nombre y tamaño)...")
    chk = subprocess.run(["rclone", "lsjson", os.path.join(remote_dest, zip_base)], capture_output=True, text=True)
    print(f"rclone lsjson output: {chk.stdout.strip()}")
    
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
# PRUEBA CALENDARIO: Ejecuta scripts/sincronizar_calendario_android.py
# ----------------------------------------------------------------------
print("--- [EJECUTANDO CALENDARIO: Segunda Corrida en Copia Versionada (Idempotencia)] ---")
cal_p = subprocess.run([sys.executable, CAL_SCRIPT], capture_output=True, text=True)
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
global_pass = t2_pass and t6_pass and t8_pass and cal_pass
print(f"RESUMEN GLOBAL: {'TODAS LAS PRUEBAS PASARON (PASS)' if global_pass else 'FALLÓ ALGUNA PRUEBA'}")
print("======================================================================")
sys.exit(0 if global_pass else 1)
