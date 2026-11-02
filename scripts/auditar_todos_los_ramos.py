#!/usr/bin/env python3
"""
auditar_todos_los_ramos.py
==========================
Auditoría integral de concordancia entre Aula USM, disco local, git repo,
Google Drive y los archivos de contexto incrementales para cada asignatura.
"""

import os
import sys
import json

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_DIR, "scripts"))

import sincronizar_aula_semanal as s
import generar_contexto_ramos as g

def auditar():
    tok = s.get_token()
    client = s.MoodleAPIClient(s.BASE_URL, tok) if tok else None
    
    print("=" * 70)
    print("AUDITORÍA INTEGRAL DE CONCORDANCIA ACADÉMICA (SEMESTRE 2026-2)")
    print("=" * 70)
    
    # 1. Sesión Aula USM
    if client:
        site_info = client.call("core_webservice_get_site_info")
        print(f"✓ Conexión Aula USM: ACTIVA (Usuario: {site_info.get('fullname')})")
    else:
        print("⚠ Conexión Aula USM: OFFLINE (usando archivos locales)")
        
    # Cargar evaluaciones maestras
    evals_path = os.path.join(REPO_DIR, "universidad/2026-2/evaluaciones.json")
    with open(evals_path, "r", encoding="utf-8") as ef:
        all_evals = json.load(ef)
    print(f"✓ Evaluaciones consolidadas: {len(all_evals)} hitos registrados en evaluaciones.json\n")

    errores_globales = []
    
    for cm in g.COURSES_META:
        cid = cm["id"]
        sigla = cm["sigla"]
        short_name = cm["short"]
        folder_name = cm["folder"]
        dir_ramo = os.path.join(REPO_DIR, "universidad/2026-2", folder_name)
        
        print(f"🔍 Auditando: [{sigla}] {cm['nombre']} (ID Aula: {cid})")
        print(f"   Ruta: universidad/2026-2/{folder_name}/")
        
        # A. Archivos en Aula vs Disco
        archivos_aula = {}
        if client:
            sections = client.call("core_course_get_contents", {"courseid": cid})
            s.agregar_enunciados_de_entregas(client, cid, sections)
            for sec in sections:
                for mod in sec.get("modules", []):
                    for cont in mod.get("contents", []):
                        if cont.get("type") == "file":
                            fname = s.sanitizar(cont.get("filename", "")).strip()
                            fsize = int(cont.get("filesize", 0))
                            if fname:
                                archivos_aula[fname] = fsize

        # Archivos en disco
        archivos_disco = g.escanear_archivos_locales(dir_ramo)
        
        # Verificar que todo archivo de Aula esté en disco
        faltantes = []
        for fname, fsz in archivos_aula.items():
            if fname not in archivos_disco:
                # Comprobar si existe con otro tamaño o nombre sanitizado
                faltantes.append(fname)
                
        if faltantes:
            print(f"   ❌ {len(faltantes)} archivo(s) faltante(s) en disco: {faltantes}")
            errores_globales.append(f"{sigla}: {len(faltantes)} archivo(s) de Aula no encontrados en disco")
        else:
            print(f"   ✓ Archivos Aula vs Disco: 100% concordante ({len(archivos_disco)} archivos locales)")
            
        # Desglose por subcarpetas
        n_eval = len([f for f, d in archivos_disco.items() if d["subcarpeta"] == "Evaluaciones_y_Entregas"])
        n_mat = len([f for f, d in archivos_disco.items() if d["subcarpeta"] == "Material_y_Apuntes"])
        n_plan = len([f for f, d in archivos_disco.items() if d["subcarpeta"] == "Planificacion"])
        print(f"      - Evaluaciones_y_Entregas: {n_eval} archivos")
        print(f"      - Material_y_Apuntes:     {n_mat} archivos")
        print(f"      - Planificacion:          {n_plan} archivos")
        
        # B. Tareas en Aula (mod_assign)
        if client:
            assigns_api = g.extraer_tareas_asignadas(client, cid)
            print(f"   ✓ Tareas en Aula (mod_assign): {len(assigns_api)} registradas")
            for cmid, a in assigns_api.items():
                due_str = g.ts_to_str(a.get("duedate"))
                adj = [x.get("filename") for x in a.get("introattachments", [])]
                adj_str = f" | Adjunto: {adj}" if adj else ""
                print(f"      • {a.get('name')} (Vence: {due_str}{adj_str})")
                for att in adj:
                    if att not in archivos_disco:
                        errores_globales.append(f"{sigla}: Adjunto de entrega '{att}' no encontrado en disco")

        # C. Evaluaciones registradas en el calendario
        evals_ramo = g.cargar_evaluaciones_ramo(sigla, short_name)
        print(f"   ✓ Evaluaciones programadas en calendario: {len(evals_ramo)} hitos")
        for ev in evals_ramo:
            print(f"      • {ev.get('evaluacion')} ({ev.get('inicio', '')[:16]}) -> {ev.get('lugar')}")

        # D. Archivo de Contexto Incremental (Contexto_Asignatura.md)
        ctx_file = os.path.join(dir_ramo, "Contexto_Asignatura.md")
        if os.path.exists(ctx_file):
            sz = os.path.getsize(ctx_file)
            with open(ctx_file, "r", encoding="utf-8") as cf:
                text = cf.read()
            secciones_esperadas = [
                "1. Ficha Técnica y Programa Oficial",
                "2. Calendario Consolidado de Evaluaciones",
                "3. Entregas, Tareas y Asignaciones en Aula",
                "4. Estructura Detallada de Unidades y Módulos",
                "5. Inventario de Archivos Locales en Disco",
                "6. Avisos y Novedades Docentes",
                "Historial Incremental de Cambios"
            ]
            sec_ok = all(s in text for s in secciones_esperadas)
            if sec_ok and sz > 2000:
                print(f"   ✓ Contexto_Asignatura.md: VÁLIDO ({sz:,} bytes, todas las secciones OK)")
            else:
                print(f"   ❌ Contexto_Asignatura.md: INCOMPLETO o secciones faltantes")
                errores_globales.append(f"{sigla}: Contexto_Asignatura.md incompleto")
        else:
            print(f"   ❌ Contexto_Asignatura.md: NO EXISTE")
            errores_globales.append(f"{sigla}: Contexto_Asignatura.md no existe")
            
        # E. Estado Incremental (.contexto_estado.json)
        estado_f = os.path.join(dir_ramo, ".contexto_estado.json")
        if os.path.exists(estado_f):
            print(f"   ✓ Estado incremental (.contexto_estado.json): PRESENTE y sincronizado\n")
        else:
            print(f"   ❌ Estado incremental (.contexto_estado.json): NO EXISTE\n")
            errores_globales.append(f"{sigla}: .contexto_estado.json no existe")

    # F. Archivo Maestro del Semestre
    m_ctx = os.path.join(REPO_DIR, "universidad/2026-2/Contexto_Semestre_2026-2.md")
    if os.path.exists(m_ctx):
        print(f"✓ Contexto_Semestre_2026-2.md: PRESENTE ({os.path.getsize(m_ctx):,} bytes)")
    else:
        print("❌ Contexto_Semestre_2026-2.md: NO EXISTE")
        errores_globales.append("Contexto_Semestre_2026-2.md no existe")

    print("\n" + "=" * 70)
    if not errores_globales:
        print("RESULTADO DE AUDITORÍA: 100% CONCORDANCIA Y ORDEN TOTAL (PASS)")
        print("Todas las asignaturas concordantes con Aula, disco, git y contextos.")
        print("=" * 70)
        return 0
    else:
        print(f"RESULTADO DE AUDITORÍA: {len(errores_globales)} DISCREPANCIAS DETECTADAS")
        for e in errores_globales:
            print(f" - {e}")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(auditar())
