#!/usr/bin/env python3
"""
scripts/renovar_token_aula.py
Procedimiento automatizado para capturar y renovar el token móvil de Moodle Web Services.
Requiere sesión iniciada en Aula USM en Brave.
"""
import socket
import base64
import os
import json
import struct
import urllib.request
import urllib.parse
import hashlib
import random
import sys

def get_moodle_session_from_brave(cdp_port=9222):
    tabs = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{cdp_port}/json').read())
    aula_tabs = [t for t in tabs if 'aula.usm.cl' in t.get('url', '') or t.get('id') == '6253']
    if not aula_tabs:
        raise RuntimeError("No se encontró pestaña de Aula USM en Brave.")
    
    ws_url = aula_tabs[0]['webSocketDebuggerUrl']
    path = '/' + ws_url.split('/', 3)[3]
    
    s = socket.socket()
    s.connect(('127.0.0.1', cdp_port))
    sec_key = base64.b64encode(os.urandom(16)).decode()
    req = f'GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{cdp_port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {sec_key}\r\nSec-WebSocket-Version: 13\r\n\r\n'
    s.sendall(req.encode())
    s.recv(4096)
    
    msg_id = 0
    def cdp_call(method, params=None):
        nonlocal msg_id
        msg_id += 1
        payload = {'id': msg_id, 'method': method}
        if params: payload['params'] = params
        data = json.dumps(payload).encode('utf-8')
        mask = os.urandom(4)
        length = len(data)
        if length <= 125:
            header = bytes([0x81, 0x80 | length]) + mask
        elif length <= 65535:
            header = bytes([0x81, 0x80 | 126]) + struct.pack('!H', length) + mask
        else:
            header = bytes([0x81, 0x80 | 127]) + struct.pack('!Q', length) + mask
        masked = bytearray(length)
        for i in range(length): masked[i] = data[i] ^ mask[i % 4]
        s.sendall(header + masked)
        
        buf = b''
        while True:
            chunk = s.recv(65536)
            if not chunk: break
            buf += chunk
            while len(buf) >= 2:
                payload_len = buf[1] & 0x7F
                idx = 2
                if payload_len == 126:
                    if len(buf) < 4: break
                    payload_len = struct.unpack('!H', buf[2:4])[0]
                    idx = 4
                elif payload_len == 127:
                    if len(buf) < 10: break
                    payload_len = struct.unpack('!Q', buf[2:10])[0]
                    idx = 10
                if len(buf) >= idx + payload_len:
                    frame = buf[idx:idx+payload_len]
                    buf = buf[idx+payload_len:]
                    res = json.loads(frame.decode('utf-8', errors='ignore'))
                    if res.get('id') == msg_id:
                        return res
                else:
                    break
    
    cookies_res = cdp_call('Network.getCookies', {'urls': ['https://aula.usm.cl']})
    cookies = {c['name']: c['value'] for c in cookies_res.get('result', {}).get('cookies', [])}
    moodle_session = cookies.get('MoodleSession')
    s.close()
    if not moodle_session:
        raise RuntimeError("No se encontró la cookie MoodleSession en Brave.")
    return moodle_session

def renovar_token():
    print("[1/5] Obteniendo MoodleSession desde Brave...")
    moodle_session = get_moodle_session_from_brave()
    
    cookie_path = os.path.expanduser('~/.moodle_cookie')
    with open(cookie_path, 'w', encoding='utf-8') as cf:
        cf.write(moodle_session.strip())
    os.chmod(cookie_path, 0o600)
    print(f"[OK] Sesión MoodleSession actualizada en {cookie_path} (chmod 600)")
    
    print("[2/5] Solicitando launch.php con passport aleatorio...")
    passport = str(random.randint(100000, 999999))
    launch_url = f"https://aula.usm.cl/admin/tool/mobile/launch.php?service=moodle_mobile_app&passport={passport}&urlscheme=moodlemobile"
    
    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(NoRedirectHandler)
    req = urllib.request.Request(
        launch_url,
        headers={
            'Cookie': f'MoodleSession={moodle_session}',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; 21051182G) AppleWebKit/537.36'
        }
    )
    
    location_header = None
    body_text = None
    try:
        resp = opener.open(req)
        body_text = resp.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        location_header = e.headers.get('Location')
        if not location_header:
            body_text = e.read().decode('utf-8', errors='ignore')

    target_url = None
    if location_header and 'moodlemobile://' in location_header:
        target_url = location_header
    elif body_text and 'moodlemobile://' in body_text:
        import re
        m = re.search(r'moodlemobile://[^\s"\'<>]+', body_text)
        if m: target_url = m.group(0)

    if not target_url:
        raise RuntimeError("No se recibió redirección ni enlace moodlemobile:// desde Aula USM.")

    print("[3/5] Validando hash criptográfico...")
    token_data = target_url.split('token=', 1)[1] if 'token=' in target_url else target_url.split('://', 1)[1]
    token_b64 = token_data.split('&')[0]
    decoded = base64.b64decode(token_b64).decode('utf-8', errors='ignore')
    parts = decoded.split(':::')
    if len(parts) < 2:
        raise ValueError(f"Formato no reconocido en token decodificado: {parts}")
        
    received_hash = parts[0]
    token = parts[1]
    expected_hash = hashlib.md5(f"https://aula.usm.cl{passport}".encode('utf-8')).hexdigest()
    if received_hash.lower() != expected_hash.lower():
        raise ValueError("Error de seguridad: el hash recibido no coincide con md5(url+passport).")
        
    print("[4/5] Guardando token y metadatos...")
    token_path = os.path.expanduser('~/.moodle_token')
    with open(token_path, 'w', encoding='utf-8') as tf:
        tf.write(token.strip())
    os.chmod(token_path, 0o600)
    
    import datetime
    today_str = datetime.date.today().isoformat()
    meta = {
        'captured_at': today_str,
        'timestamp': int(datetime.datetime.now().timestamp())
    }
    meta_path = os.path.expanduser('~/.moodle_token.meta')
    with open(meta_path, 'w', encoding='utf-8') as mf:
        json.dump(meta, mf, indent=2)
    os.chmod(meta_path, 0o600)
    
    print("[5/5] Verificando token con core_webservice_get_site_info...")
    verify_url = "https://aula.usm.cl/webservice/rest/server.php"
    verify_data = urllib.parse.urlencode({
        'wstoken': token,
        'wsfunction': 'core_webservice_get_site_info',
        'moodlewsrestformat': 'json'
    }).encode('utf-8')
    vreq = urllib.request.Request(verify_url, data=verify_data, headers={'User-Agent': 'Antigravity-Sync/1.0'})
    vresp = urllib.request.urlopen(vreq)
    vinfo = json.loads(vresp.read().decode('utf-8'))
    if 'errorcode' in vinfo:
        raise RuntimeError(f"Error de API al verificar token: {vinfo.get('message')}")
        
    masked = token[:4] + "*" * (len(token) - 8) + token[-4:]
    print(f"[EXITO] Token renovado y validado: {masked} para usuario {vinfo.get('username')}")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(renovar_token())
    except Exception as e:
        print(f"[ERROR CRÍTICO] {e}", file=sys.stderr)
        sys.exit(1)
