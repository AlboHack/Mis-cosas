import subprocess, json, re, os
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=-3))
ACCOUNT = "albornoz.pavez@gmail.com"

eventos = [
    {
        "ramo": "FICA",
        "titulo": "FICA - Control 2",
        "start": (2026, 10, 26, 16, 0),
        "end": (2026, 10, 26, 18, 0),
        "loc": "Aula USM / Sala Asignada",
        "desc": "Evaluacion Control 2 de Fundamentos de Ingenieria de Construccion y Administracion (FICA)."
    },
    {
        "ramo": "FAE",
        "titulo": "FAE - CERTAMEN 2 (Reprogramado)",
        "start": (2026, 10, 27, 17, 30),
        "end": (2026, 10, 27, 20, 0),
        "loc": "Campus San Joaquin (Salas B-103 / A012)",
        "desc": "Segundo certamen de Fundamentos de Analisis Estructural (FAE). Reprogramado por alerta meteorologica. Bloques 13-14-15-16."
    },
    {
        "ramo": "FAE",
        "titulo": "FAE - Cierre Entrega Tarea N 1 (SAP2000)",
        "start": (2026, 10, 27, 23, 59),
        "end": (2026, 10, 28, 0, 30),
        "loc": "Aula USM (Modulo Tarea 8325772)",
        "desc": "Plazo final extendido de entrega de Tarea 1 en software SAP2000 (Aviso Foro 497827)."
    },
    {
        "ramo": "FICA",
        "titulo": "FICA - Caso Practico 2",
        "start": (2026, 11, 2, 16, 0),
        "end": (2026, 11, 2, 18, 0),
        "loc": "Aula USM",
        "desc": "Resolucion y entrega de Caso Practico 2 de FICA."
    },
    {
        "ramo": "FICA",
        "titulo": "FICA - CERTAMEN 2",
        "start": (2026, 11, 9, 16, 0),
        "end": (2026, 11, 9, 18, 30),
        "loc": "Sala de Catedra FICA",
        "desc": "Segundo certamen semestral de FICA."
    },
    {
        "ramo": "FAE",
        "titulo": "FAE - CERTAMEN 3",
        "start": (2026, 11, 10, 17, 30),
        "end": (2026, 11, 10, 20, 0),
        "loc": "Sala B-103",
        "desc": "Tercer certamen de Fundamentos de Analisis Estructural. Bloques 13-14-15-16."
    },
    {
        "ramo": "Transporte",
        "titulo": "Transporte - CERTAMEN 3",
        "start": (2026, 11, 18, 14, 0),
        "end": (2026, 11, 18, 15, 30),
        "loc": "Sala de Catedra Transporte",
        "desc": "Tercer certamen de Ingenieria de Transporte."
    },
    {
        "ramo": "Fluidos",
        "titulo": "Fluidos - CERTAMEN 3",
        "start": (2026, 11, 23, 14, 0),
        "end": (2026, 11, 23, 16, 0),
        "loc": "Sala de Catedra CIV244",
        "desc": "Tercer certamen semestral de Mecanica de Fluidos."
    },
    {
        "ramo": "FICA",
        "titulo": "FICA - Presentacion 2 + Informe Final",
        "start": (2026, 11, 23, 16, 0),
        "end": (2026, 11, 23, 18, 30),
        "loc": "Sala de Catedra FICA",
        "desc": "Presentacion oral 2 y entrega final del informe de proyecto grupal de FICA."
    },
    {
        "ramo": "Fluidos",
        "titulo": "Fluidos - Entrega Notas Finales",
        "start": (2026, 11, 27, 18, 0),
        "end": (2026, 11, 27, 19, 0),
        "loc": "Aula USM",
        "desc": "Publicacion oficial de notas finales y promedios de Mecanica de Fluidos."
    },
    {
        "ramo": "Transporte",
        "titulo": "Transporte - Certamen Recuperativo",
        "start": (2026, 11, 30, 14, 0),
        "end": (2026, 11, 30, 15, 30),
        "loc": "Sala Asignada",
        "desc": "Certamen recuperativo y extraordinario de Ingenieria de Transporte."
    },
    {
        "ramo": "FAE",
        "titulo": "FAE - CERTAMEN 4 (Final)",
        "start": (2026, 12, 2, 17, 30),
        "end": (2026, 12, 2, 20, 0),
        "loc": "Sala A012",
        "desc": "Cuarto certamen semestral de Fundamentos de Analisis Estructural. Bloques 13-14-15-16."
    }
]

def adb_shell(cmd):
    p = subprocess.run(["adb", "shell", cmd], capture_output=True, text=True)
    return p.stdout.strip(), p.returncode

def get_google_calendar_id():
    """Busca dinamicamente el ID del calendario de Google perteneciente a ACCOUNT."""
    out, code = adb_shell("content query --uri content://com.android.calendar/calendars --projection _id:ownerAccount")
    if code != 0:
        return 7  # Fallback estándar
    for row in out.splitlines():
        if ACCOUNT in row:
            m = re.search(r'_id=(\d+)', row)
            if m:
                return int(m.group(1))
    return 7

def sync_android_calendar():
    cal_id = get_google_calendar_id()
    print(f"=== SINCRONIZANDO CON ANDROID GOOGLE CALENDAR (ID {cal_id}: {ACCOUNT}) ===", flush=True)
    
    # Consultar eventos existentes para este semestre
    out_ev, code = adb_shell(f"content query --uri content://com.android.calendar/events --projection _id:title:dtstart:dtend --where \"calendar_id={cal_id}\"")
    existentes = {}
    if code == 0:
        for row in out_ev.splitlines():
            m_id = re.search(r'_id=(\d+)', row)
            m_ti = re.search(r'title=([^,]+)', row)
            m_st = re.search(r'dtstart=(\d+)', row)
            if m_id and m_ti and m_st:
                existentes[m_ti.group(1).strip()] = {
                    "id": m_id.group(1),
                    "dtstart": int(m_st.group(1))
                }
                
    actualizados = 0
    insertados = 0
    
    for ev in eventos:
        y, m, d, H, M = ev["start"]
        ey, em, ed, eH, eM = ev["end"]
        dt_start = int(datetime(y, m, d, H, M, tzinfo=TZ).timestamp() * 1000)
        dt_end = int(datetime(ey, em, ed, eH, eM, tzinfo=TZ).timestamp() * 1000)
        titulo = ev["titulo"]
        
        if titulo in existentes:
            ev_id = existentes[titulo]["id"]
            ev_start = existentes[titulo]["dtstart"]
            # Si la fecha cambio (reprogramacion), actualizar
            if ev_start != dt_start:
                adb_shell(f"content update --uri content://com.android.calendar/events --bind dtstart:l:{dt_start} --bind dtend:l:{dt_end} --where \"_id={ev_id}\"")
                print(f" [ACTUALIZADO POR CAMBIO DE FECHA] {titulo} (ID {ev_id})", flush=True)
                actualizados += 1
            else:
                # Ya existe y con la misma fecha
                pass
        else:
            # Insertar nuevo
            insert_cmd = (
                f"content insert --uri content://com.android.calendar/events "
                f"--bind calendar_id:i:{cal_id} "
                f"--bind title:s:\"{titulo}\" "
                f"--bind description:s:\"{ev['desc']}\" "
                f"--bind eventLocation:s:\"{ev['loc']}\" "
                f"--bind dtstart:l:{dt_start} "
                f"--bind dtend:l:{dt_end} "
                f"--bind eventTimezone:s:\"America/Santiago\" "
                f"--bind hasAlarm:i:1"
            )
            adb_shell(insert_cmd)
            
            # Obtener ID recien insertado para añadir alarmas
            q_out, _ = adb_shell(f"content query --uri content://com.android.calendar/events --projection _id --where \"calendar_id={cal_id} AND title='{titulo}' AND dtstart={dt_start}\"")
            m_new = re.search(r'_id=(\d+)', q_out)
            if m_new:
                new_id = m_new.group(1)
                adb_shell(f"content insert --uri content://com.android.calendar/reminders --bind event_id:i:{new_id} --bind minutes:i:10080 --bind method:i:1")
                adb_shell(f"content insert --uri content://com.android.calendar/reminders --bind event_id:i:{new_id} --bind minutes:i:4320 --bind method:i:1")
                adb_shell(f"content insert --uri content://com.android.calendar/reminders --bind event_id:i:{new_id} --bind minutes:i:1440 --bind method:i:1")
                print(f" [INSERTADO] {titulo} (ID {new_id}) con 3 alarmas (7d, 3d, 1d)", flush=True)
                insertados += 1

    print(f"Sincronizacion de calendario finalizada: {insertados} insertados, {actualizados} actualizados.", flush=True)

if __name__ == "__main__":
    sync_android_calendar()
