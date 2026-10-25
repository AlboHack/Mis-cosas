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
        "desc": "Segundo certamen de Fundamentos de Analisis Estructural (FAE). Reprogramado por alerta meteorologica (Aviso Foro 498536). Bloques 13-14-15-16."
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
        "end": (2026, 11, 18, 16, 30),
        "loc": "Salas B014 / B103",
        "desc": "Tercer certamen semestral de Ingenieria de Transporte (Modelacion Ortuzar, Guia N 3)."
    },
    {
        "ramo": "Fluidos",
        "titulo": "Fluidos - CERTAMEN 3",
        "start": (2026, 11, 20, 14, 0),
        "end": (2026, 11, 20, 16, 30),
        "loc": "Campus San Joaquin",
        "desc": "Tercer certamen de Mecanica de Fluidos: Unidades 5 y 6 (Navier-Stokes y Leyes de conservacion)."
    },
    {
        "ramo": "FICA",
        "titulo": "FICA - Presentacion 2 + Informe Final",
        "start": (2026, 11, 23, 16, 0),
        "end": (2026, 11, 23, 18, 30),
        "loc": "Sala de Catedra FICA / Aula USM",
        "desc": "Defensa final de proyecto de construccion y entrega de Informe 2 en Aula USM."
    },
    {
        "ramo": "Fluidos",
        "titulo": "Fluidos - Entrega Notas Finales",
        "start": (2026, 11, 27, 12, 0),
        "end": (2026, 11, 27, 13, 0),
        "loc": "Aula USM / SIGA",
        "desc": "Publicacion oficial de notas finales y actas de Mecanica de Fluidos."
    },
    {
        "ramo": "Transporte",
        "titulo": "Transporte - Certamen Recuperativo",
        "start": (2026, 12, 2, 14, 0),
        "end": (2026, 12, 2, 16, 30),
        "loc": "Salas B014 / B103",
        "desc": "Certamen recuperativo final de Ingenieria de Transporte."
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
    out, code = adb_shell("content query --uri content://com.android.calendar/calendars --projection _id:ownerAccount")
    if code != 0:
        return 7
    for row in out.splitlines():
        if ACCOUNT in row:
            m = re.search(r'_id=(\d+)', row)
            if m:
                return int(m.group(1))
    return 7

def sync_android_calendar():
    cal_id = get_google_calendar_id()
    print(f"=== SINCRONIZANDO CON ANDROID GOOGLE CALENDAR (ID {cal_id}: {ACCOUNT}) ===", flush=True)
    
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
            if ev_start != dt_start:
                adb_shell(f"content update --uri content://com.android.calendar/events --bind dtstart:l:{dt_start} --bind dtend:l:{dt_end} --where \"_id={ev_id}\"")
                print(f" [ACTUALIZADO POR CORRECCION DE FECHA] {titulo} (ID {ev_id})", flush=True)
                actualizados += 1
            else:
                pass
        else:
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
