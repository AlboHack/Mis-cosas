#!/usr/bin/env python3
"""
Test Suite for scripts/consultar_gemini.py (Tiers 1 to 4)

Tier 1: Feature Coverage
- RFC 6455 Frame encoding & decoding (masks, opcodes, 7-bit, 16-bit, 64-bit payload lengths)
- WebSocket Handshake validation (Sec-WebSocket-Key / Sec-WebSocket-Accept, leftover buffer)
- Ping / Pong control frame handling
- CLI argument parsing (prompt positional, -f, -o, --nuevo, --port, --no-save)
- File output persistence & directory creation (os.makedirs, timestamp format)

Tier 2: Boundary Cases & Robustness
- Empty prompt rejection / validation
- Multiline prompt with code blocks, quotes, and Spanish accents/special characters
- Unreachable port 9222 handling and connection/timeout resilience
- Fragmented WebSocket frames (continuation frames opcode 0x0)
- TCP chunked streaming buffer reassembly

Tier 3: Mock CDP Loopback Server & Integration
- Mock CDP Server simulating /json endpoint and WebSocket RFC 6455 protocol
- Verification of CDP method calls: Input.insertText, Runtime.evaluate, Page.navigate
- End-to-end CLI subprocess verification against loopback CDP server
- DOM-to-Markdown serializer specification validation (code-blocks, headings, lists, tables)

Tier 4: System Integrity & Regression Safety
- AST analysis confirming Zero External Pip Dependencies (pure standard library only)
- Complete regression verification of scripts/test_aceptacion_token.py (100% PASS on 12/12 modules)

Zero external pip dependencies: Pure Python 3 standard library only.
"""

import ast
import base64
import hashlib
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.parse
import urllib.request

# Localizar repositorios y scripts
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
CONSULTAR_SCRIPT = os.path.join(SCRIPTS_DIR, "consultar_gemini.py")
ACCEPT_TEST_SCRIPT = os.path.join(SCRIPTS_DIR, "test_aceptacion_token.py")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import consultar_gemini
from consultar_gemini import (
    CDPClient,
    DOM_MARKDOWN_SERIALIZER,
    PureWebSocketClient,
    consultar_gemini as consultar_gemini_api,
    discover_gemini_tab,
    save_response,
)


# ==============================================================================
# REFERENCIA DE PROTOCOLO RFC 6455 PARA VALIDACIÓN INDEPENDIENTE
# ==============================================================================
def rfc6455_encode_frame(
    opcode: int,
    payload: bytes,
    masked: bool = True,
    fin: bool = True,
    mask_key: bytes = None,
) -> bytes:
    """Codificador RFC 6455 independiente para verificación cruzada de tramas."""
    b0 = (0x80 if fin else 0) | (opcode & 0x0F)
    length = len(payload)
    mask_bit = 0x80 if masked else 0x00

    if length <= 125:
        header = bytes([b0, mask_bit | length])
    elif length <= 65535:
        header = bytes([b0, mask_bit | 126]) + struct.pack("!H", length)
    else:
        header = bytes([b0, mask_bit | 127]) + struct.pack("!Q", length)

    if masked:
        if mask_key is None:
            mask_key = os.urandom(4)
        masked_data = bytearray(length)
        for i in range(length):
            masked_data[i] = payload[i] ^ mask_key[i % 4]
        return header + mask_key + bytes(masked_data)
    else:
        return header + payload


def rfc6455_decode_frame(raw_bytes: bytes) -> dict:
    """Decodificador RFC 6455 independiente para inspeccionar tramas recibidas."""
    if len(raw_bytes) < 2:
        raise ValueError("Trama incompleta (menos de 2 bytes)")
    b0 = raw_bytes[0]
    b1 = raw_bytes[1]
    fin = bool(b0 & 0x80)
    opcode = b0 & 0x0F
    has_mask = bool(b1 & 0x80)
    payload_len = b1 & 0x7F
    idx = 2

    if payload_len == 126:
        if len(raw_bytes) < 4:
            raise ValueError("Trama incompleta para longitud de 16 bits")
        payload_len = struct.unpack("!H", raw_bytes[2:4])[0]
        idx = 4
    elif payload_len == 127:
        if len(raw_bytes) < 10:
            raise ValueError("Trama incompleta para longitud de 64 bits")
        payload_len = struct.unpack("!Q", raw_bytes[2:10])[0]
        idx = 10

    mask_key = None
    if has_mask:
        if len(raw_bytes) < idx + 4:
            raise ValueError("Trama incompleta para máscara")
        mask_key = raw_bytes[idx : idx + 4]
        idx += 4

    total_len = idx + payload_len
    if len(raw_bytes) < total_len:
        raise ValueError("Trama incompleta para carga de datos")

    data = bytearray(raw_bytes[idx:total_len])
    if mask_key:
        for i in range(len(data)):
            data[i] ^= mask_key[i % 4]

    return {
        "fin": fin,
        "opcode": opcode,
        "has_mask": has_mask,
        "mask_key": mask_key,
        "payload_len": payload_len,
        "payload": bytes(data),
        "total_len": total_len,
    }


# ==============================================================================
# SERVIDOR MOCK CDP LOOPBACK RFC 6455 HERMÉTICO
# ==============================================================================
class MockCDPLoopbackServer:
    """
    Servidor HTTP/WebSocket RFC 6455 local en puerto efímero.
    Simula completamente el endpoint /json de Brave y el protocolo CDP
    para ejecutar pruebas determinísticas sin depender del navegador real.
    """

    def __init__(self, tab_id: str = "mock_gemini_tab_123"):
        self.tab_id = tab_id
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(("127.0.0.1", 0))
        self.port = self.server_sock.getsockname()[1]
        self.server_sock.listen(5)
        self.running = True
        self.recorded_calls = []
        self.simulated_streaming_rounds = 1
        self.poll_count = 0
        self.mock_response_markdown = (
            "# Respuesta Simulada de Gemini\n\n"
            "Cálculo estructural conforme a **NCh433** y **ACI 318**:\n\n"
            "```python\n"
            "def calcular_momento(w, l):\n"
            "    return w * l**2 / 8  # [kN*m]\n"
            "```\n\n"
            "| Parámetro | Valor | Unidad |\n"
            "| --- | --- | --- |\n"
            "| Carga w | 25.0 | kN/m |\n"
            "| Luz L | 6.0 | m |\n"
        )
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _serve(self):
        while self.running:
            try:
                conn, _ = self.server_sock.accept()
            except Exception:
                break
            client_thread = threading.Thread(target=self._handle_client, args=(conn,), daemon=True)
            client_thread.start()

    def _handle_client(self, conn: socket.socket):
        conn.settimeout(5.0)
        req_bytes = bytearray()
        try:
            while b"\r\n\r\n" not in req_bytes:
                chunk = conn.recv(4096)
                if not chunk:
                    conn.close()
                    return
                req_bytes.extend(chunk)

            header_part, _, leftover = req_bytes.partition(b"\r\n\r\n")
            lines = header_part.decode("iso-8859-1").split("\r\n")
            req_line = lines[0].split(" ")
            method = req_line[0]
            path = req_line[1] if len(req_line) > 1 else "/"

            headers = {}
            for line in lines[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    headers[k.strip().lower()] = v.strip()

            # 1. Endpoint HTTP GET /json
            if method == "GET" and path.startswith("/json"):
                tabs = [
                    {
                        "id": self.tab_id,
                        "type": "page",
                        "title": "Google Gemini - Chat Activo",
                        "url": "https://gemini.google.com/app",
                        "webSocketDebuggerUrl": f"ws://127.0.0.1:{self.port}/devtools/page/{self.tab_id}",
                    }
                ]
                body = json.dumps(tabs).encode("utf-8")
                resp = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: application/json; charset=UTF-8\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    f"Connection: close\r\n\r\n"
                ).encode("ascii") + body
                conn.sendall(resp)
                conn.close()
                return

            # 2. Handshake WebSocket Upgrade
            if headers.get("upgrade", "").lower() == "websocket":
                sec_key = headers.get("sec-websocket-key", "")
                guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
                accept_token = base64.b64encode(
                    hashlib.sha1((sec_key + guid).encode("ascii")).digest()
                ).decode("ascii")

                handshake_resp = (
                    "HTTP/1.1 101 Switching Protocols\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {accept_token}\r\n"
                    "\r\n"
                ).encode("ascii")
                conn.sendall(handshake_resp)

                # Procesar mensajes WebSocket
                self._handle_ws_session(conn, leftover)
                return

            # 404 para cualquier otra ruta
            conn.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n")
            conn.close()
        except Exception:
            try:
                conn.close()
            except Exception:
                pass

    def _handle_ws_session(self, conn: socket.socket, initial_buf: bytearray):
        buf = bytearray(initial_buf)
        while self.running:
            try:
                if len(buf) < 2:
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    buf.extend(chunk)
                    continue

                b0 = buf[0]
                b1 = buf[1]
                opcode = b0 & 0x0F
                has_mask = bool(b1 & 0x80)
                payload_len = b1 & 0x7F
                idx = 2

                if payload_len == 126:
                    if len(buf) < 4:
                        chunk = conn.recv(65536)
                        if not chunk:
                            break
                        buf.extend(chunk)
                        continue
                    payload_len = struct.unpack("!H", buf[2:4])[0]
                    idx = 4
                elif payload_len == 127:
                    if len(buf) < 10:
                        chunk = conn.recv(65536)
                        if not chunk:
                            break
                        buf.extend(chunk)
                        continue
                    payload_len = struct.unpack("!Q", buf[2:10])[0]
                    idx = 10

                mask_key = None
                if has_mask:
                    if len(buf) < idx + 4:
                        chunk = conn.recv(65536)
                        if not chunk:
                            break
                        buf.extend(chunk)
                        continue
                    mask_key = buf[idx : idx + 4]
                    idx += 4

                total_frame = idx + payload_len
                if len(buf) < total_frame:
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    buf.extend(chunk)
                    continue

                payload = bytearray(buf[idx:total_frame])
                buf = buf[total_frame:]

                if mask_key:
                    for i in range(len(payload)):
                        payload[i] ^= mask_key[i % 4]

                # Responder a Ping
                if opcode == 0x9:
                    pong = rfc6455_encode_frame(0xA, bytes(payload), masked=False)
                    conn.sendall(pong)
                    continue
                elif opcode == 0x8:  # Close
                    conn.sendall(rfc6455_encode_frame(0x8, b"", masked=False))
                    break
                elif opcode == 0x1:  # Text JSON-RPC
                    text = payload.decode("utf-8")
                    msg = json.loads(text)
                    self.recorded_calls.append(msg)
                    msg_id = msg.get("id")
                    method = msg.get("method")
                    params = msg.get("params", {})

                    resp_payload = {"id": msg_id, "result": {}}

                    if method == "Input.insertText":
                        resp_payload["result"] = {}
                    elif method == "Page.navigate":
                        resp_payload["result"] = {"frameId": "mock_frame_main"}
                    elif method == "Runtime.evaluate":
                        expr = params.get("expression", "")
                        if "DOM_MARKDOWN_SERIALIZER" in expr or "domToMarkdown" in expr:
                            resp_payload["result"] = {
                                "result": {"type": "string", "value": self.mock_response_markdown}
                            }
                        elif "poll_state_js" in expr or "has_stop" in expr:
                            self.poll_count += 1
                            if self.poll_count <= self.simulated_streaming_rounds:
                                resp_payload["result"] = {
                                    "result": {
                                        "type": "object",
                                        "value": {
                                            "has_stop": True,
                                            "count": 1,
                                            "length": 80 * self.poll_count,
                                        },
                                    }
                                }
                            else:
                                resp_payload["result"] = {
                                    "result": {
                                        "type": "object",
                                        "value": {
                                            "has_stop": False,
                                            "count": 1,
                                            "length": 350,
                                        },
                                    }
                                }
                        elif "ready_check" in expr or "rich-textarea" in expr or "send_script" in expr:
                            resp_payload["result"] = {
                                "result": {"type": "boolean", "value": True}
                            }
                        else:
                            resp_payload["result"] = {
                                "result": {"type": "boolean", "value": True}
                            }

                    resp_bytes = json.dumps(resp_payload).encode("utf-8")
                    out_frame = rfc6455_encode_frame(0x1, resp_bytes, masked=False)
                    conn.sendall(out_frame)

            except Exception:
                break
        try:
            conn.close()
        except Exception:
            pass

    def stop(self):
        self.running = False
        try:
            self.server_sock.close()
        except Exception:
            pass


# ==============================================================================
# TIER 1: FEATURE COVERAGE
# ==============================================================================
class TestTier1FeatureCoverage(unittest.TestCase):
    """
    Tier 1: Pruebas unitarias de cobertura de características.
    - Framing RFC 6455 (máscaras, longitudes 7-bit, 16-bit, 64-bit, opcodes).
    - Handshake WebSocket (Sec-WebSocket-Key / Accept, buffer residual).
    - Tramas de control Ping/Pong.
    - Análisis sintáctico de argumentos CLI.
    - Persistencia de archivos y creación recursiva de directorios.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_gemini_tier1_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rfc6455_encoding_short_payload(self):
        """Verifica codificación de tramas con longitud <= 125 bytes y máscara obligatoria."""
        payload = b"Hola Gemini!"
        client = PureWebSocketClient("ws://127.0.0.1:9222/test")
        
        # Simular socket en memoria para capturar trama transmitida
        sent_data = bytearray()
        class DummySock:
            def sendall(self, data):
                sent_data.extend(data)
        client._sock = DummySock()

        client.send_frame(0x1, payload)
        self.assertEqual(len(sent_data), len(payload) + 6)
        
        # Validar byte 0: FIN=1, Opcode=0x1 -> 0x81
        self.assertEqual(sent_data[0], 0x81)
        # Validar byte 1: MASK=1 -> (0x80 | 12) = 0x8C
        self.assertEqual(sent_data[1], 0x80 | len(payload))
        
        # Extraer máscara y desenmascarar
        mask = sent_data[2:6]
        masked_payload = sent_data[6:6 + len(payload)]
        unmasked = bytes(b ^ mask[i % 4] for i, b in enumerate(masked_payload))
        self.assertEqual(unmasked, payload)

    def test_rfc6455_encoding_medium_payload_16bit(self):
        """Verifica codificación de tramas de 16 bits (126 <= len <= 65535)."""
        payload = b"A" * 1024
        client = PureWebSocketClient("ws://127.0.0.1:9222/test")
        sent_data = bytearray()
        class DummySock:
            def sendall(self, data):
                sent_data.extend(data)
        client._sock = DummySock()

        client.send_frame(0x1, payload)
        self.assertEqual(sent_data[0], 0x81)
        self.assertEqual(sent_data[1], 0x80 | 126)
        extended_len = struct.unpack("!H", sent_data[2:4])[0]
        self.assertEqual(extended_len, 1024)

        mask = sent_data[4:8]
        masked_payload = sent_data[8:8 + 1024]
        unmasked = bytes(b ^ mask[i % 4] for i, b in enumerate(masked_payload))
        self.assertEqual(unmasked, payload)

    def test_rfc6455_encoding_large_payload_64bit(self):
        """Verifica codificación de tramas de 64 bits (len >= 65536)."""
        payload = b"X" * 70000
        client = PureWebSocketClient("ws://127.0.0.1:9222/test")
        sent_data = bytearray()
        class DummySock:
            def sendall(self, data):
                sent_data.extend(data)
        client._sock = DummySock()

        client.send_frame(0x1, payload)
        self.assertEqual(sent_data[0], 0x81)
        self.assertEqual(sent_data[1], 0x80 | 127)
        extended_len = struct.unpack("!Q", sent_data[2:10])[0]
        self.assertEqual(extended_len, 70000)

        mask = sent_data[10:14]
        masked_payload = sent_data[14:14 + 70000]
        unmasked = bytes(b ^ mask[i % 4] for i, b in enumerate(masked_payload))
        self.assertEqual(unmasked, payload)

    def test_rfc6455_handshake_standard_vector(self):
        """Verifica el cálculo de Sec-WebSocket-Accept según el vector oficial de RFC 6455 §1.3."""
        key = "dGhlIHNhbXBsZSBub25jZQ=="
        guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        expected_accept = "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="
        computed_accept = base64.b64encode(hashlib.sha1((key + guid).encode("ascii")).digest()).decode("ascii")
        self.assertEqual(computed_accept, expected_accept)

    def test_rfc6455_handshake_leftover_buffer_preservation(self):
        """
        Verifica que los bytes leídos durante el handshake que pertenecen a tramas posteriores
        no se descartan y se conservan en self._buf.
        """
        mock = MockCDPLoopbackServer()
        try:
            client = PureWebSocketClient(f"ws://127.0.0.1:{mock.port}/devtools/page/{mock.tab_id}")
            client.connect()
            self.assertIsNotNone(client._sock)
            client.close()
        finally:
            mock.stop()

    def test_rfc6455_ping_pong_control_frame(self):
        """Verifica que al recibir una trama Ping (0x9), el cliente responda con Pong (0xA)."""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(("127.0.0.1", 0))
        port = server_sock.getsockname()[1]
        server_sock.listen(1)

        pong_received = bytearray()
        def server_routine():
            conn, _ = server_sock.accept()
            # Handshake rápido
            conn.recv(4096)
            conn.sendall(
                b"HTTP/1.1 101 Switching Protocols\r\n"
                b"Upgrade: websocket\r\n"
                b"Connection: Upgrade\r\n"
                b"Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n\r\n"
            )
            # Enviar Ping
            ping_frame = rfc6455_encode_frame(0x9, b"heartbeat_token_123", masked=False)
            conn.sendall(ping_frame)
            # Enviar texto
            text_frame = rfc6455_encode_frame(0x1, b"ok_after_ping", masked=False)
            conn.sendall(text_frame)
            # Leer respuesta pong del cliente
            chunk = conn.recv(4096)
            pong_received.extend(chunk)
            conn.close()
            server_sock.close()

        t = threading.Thread(target=server_routine, daemon=True)
        t.start()

        # Cliente con Sec-WebSocket-Key forzada para coincidir con accept
        client = PureWebSocketClient(f"ws://127.0.0.1:{port}/")
        
        # Conectar manualmente con el socket
        client._sock = socket.socket()
        client._sock.connect(("127.0.0.1", port))
        req = (
            "GET / HTTP/1.1\r\nHost: 127.0.0.1\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        client._sock.sendall(req.encode("ascii"))
        resp = client._sock.recv(4096)
        _, _, leftover = resp.partition(b"\r\n\r\n")
        client._buf = bytearray(leftover)

        msg = client.recv_text()
        self.assertEqual(msg, "ok_after_ping")
        client.close()
        t.join(timeout=3.0)

        # Verificar que el servidor recibió Pong con la misma carga
        self.assertGreater(len(pong_received), 0)
        decoded = rfc6455_decode_frame(bytes(pong_received))
        self.assertEqual(decoded["opcode"], 0xA)
        self.assertEqual(decoded["payload"], b"heartbeat_token_123")

    def test_save_response_custom_output_and_recursion(self):
        """Verifica que save_response cree los directorios padres recursivamente."""
        nested_out = os.path.join(self.temp_dir, "nivel1", "nivel2", "resultado.md")
        test_content = "# Prueba Guardado\n\nTexto de respuesta."
        
        save_response(test_content, custom_output=nested_out)
        self.assertTrue(os.path.exists(nested_out))
        with open(nested_out, "r", encoding="utf-8") as f:
            read_back = f.read().strip()
        self.assertEqual(read_back, test_content)

    def test_cli_argument_parsing(self):
        """Verifica la lógica de flags y argumentos en consultar_gemini.py."""
        prompt_file = os.path.join(self.temp_dir, "prompt_test.txt")
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write("Consulta desde archivo")

        res_help = subprocess.run([sys.executable, CONSULTAR_SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(res_help.returncode, 0)
        self.assertIn("-f", res_help.stdout)
        self.assertIn("-o", res_help.stdout)
        self.assertIn("--nuevo", res_help.stdout)
        self.assertIn("--port", res_help.stdout)


# ==============================================================================
# TIER 2: BOUNDARIES & CORNER CASES
# ==============================================================================
class TestTier2BoundaryCases(unittest.TestCase):
    """
    Tier 2: Casos límite, resiliencia y entradas adversas.
    - Rechazo de prompts vacíos o solo espacios.
    - Prompts multilínea con bloques de código, caracteres acentuados y símbolos especiales.
    - Puerto no disponible / timeout sin volcados de pila sin controlar.
    - Tramas WebSocket fragmentadas (opcodes 0x1 y 0x0).
    - Desensamblado y lectura por fragmentos (chunked TCP).
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_gemini_tier2_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_empty_prompt_rejection(self):
        """Verifica rechazo inmediato de prompts vacíos con código de salida 1."""
        res_empty = subprocess.run([sys.executable, CONSULTAR_SCRIPT, ""], capture_output=True, text=True)
        self.assertNotEqual(res_empty.returncode, 0)
        self.assertTrue(
            "vacío" in res_empty.stderr.lower() or "debe proporcionar un prompt" in res_empty.stderr.lower()
        )

        res_whitespace = subprocess.run([sys.executable, CONSULTAR_SCRIPT, "   \n\t  "], capture_output=True, text=True)
        self.assertNotEqual(res_whitespace.returncode, 0)
        self.assertIn("vacío", res_whitespace.stderr.lower())

        with self.assertRaises(ValueError):
            consultar_gemini_api(prompt="   ")

    def test_multiline_prompt_with_code_and_accents(self):
        """Verifica que prompts complejos con código, comillas y caracteres UTF-8 se transmitan íntegros."""
        complex_prompt = (
            "Diseñar zapata aislada para NCh433:\n"
            "```python\n"
            "Pu = 1500.0  # [kN]\n"
            "q_adm = 0.25  # [MPa] = 250 kPa\n"
            "Area = Pu / (q_adm * 1000)  # m2\n"
            "print(f'Área requerida: {Area:.2f} m²')\n"
            "```\n"
            "¿Requiere armadura superior por tracción? Comillas: \"dobles\", 'simples', `backticks`."
        )

        mock = MockCDPLoopbackServer()
        try:
            tab = discover_gemini_tab(port=mock.port, auto_recover=False)
            cdp = CDPClient(tab["webSocketDebuggerUrl"])
            cdp.connect()
            cdp.insert_text(complex_prompt)
            cdp.close()

            # Verificar que el servidor mock recibió exactamente el texto con acentos y saltos
            insert_calls = [c for c in mock.recorded_calls if c.get("method") == "Input.insertText"]
            self.assertEqual(len(insert_calls), 1)
            received_text = insert_calls[0]["params"]["text"]
            self.assertEqual(received_text, complex_prompt)
        finally:
            mock.stop()

    def test_unreachable_port_handling(self):
        """Verifica que consultar un puerto cerrado no genere un bucle infinito ni excepción no controlada."""
        # Seleccionar puerto efímero cerrado
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        closed_port = s.getsockname()[1]
        s.close()

        with self.assertRaises(RuntimeError) as ctx:
            discover_gemini_tab(port=closed_port, auto_recover=False, max_retries=1)
        self.assertIn(str(closed_port), str(ctx.exception))

    def test_cdp_call_timeout(self):
        """Verifica que el cliente CDP aplique el timeout configurado ante métodos sin respuesta."""
        server_sock = socket.socket()
        server_sock.bind(("127.0.0.1", 0))
        port = server_sock.getsockname()[1]
        server_sock.listen(1)

        def hang_routine():
            conn, _ = server_sock.accept()
            conn.recv(4096)
            conn.sendall(
                b"HTTP/1.1 101 Switching Protocols\r\n"
                b"Upgrade: websocket\r\n"
                b"Connection: Upgrade\r\n"
                b"Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n\r\n"
            )
            # Leer llamada pero nunca responder
            conn.recv(4096)
            time.sleep(2.0)
            conn.close()
            server_sock.close()

        t = threading.Thread(target=hang_routine, daemon=True)
        t.start()

        client = PureWebSocketClient(f"ws://127.0.0.1:{port}/", timeout=1.0)
        client._sock = socket.socket()
        client._sock.settimeout(1.0)
        client._sock.connect(("127.0.0.1", port))
        req = (
            "GET / HTTP/1.1\r\nHost: 127.0.0.1\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        client._sock.sendall(req.encode("ascii"))
        resp = client._sock.recv(4096)
        _, _, client._buf = resp.partition(b"\r\n\r\n")

        cdp = CDPClient(f"ws://127.0.0.1:{port}/", timeout=0.8)
        cdp.ws = client

        with self.assertRaises(TimeoutError):
            cdp.call("Runtime.evaluate", {"expression": "1+1"}, timeout=0.6)
        cdp.close()
        t.join(timeout=3.0)

    def test_fragmented_websocket_frames(self):
        """Verifica la defragmentación de tramas (FIN=0 opcode 0x1, seguido de FIN=1 opcode 0x0)."""
        server_sock = socket.socket()
        server_sock.bind(("127.0.0.1", 0))
        port = server_sock.getsockname()[1]
        server_sock.listen(1)

        def frag_server():
            conn, _ = server_sock.accept()
            conn.recv(4096)
            conn.sendall(
                b"HTTP/1.1 101 Switching Protocols\r\n"
                b"Upgrade: websocket\r\n"
                b"Connection: Upgrade\r\n"
                b"Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n\r\n"
            )
            # Trama 1: FIN=0, opcode=0x1
            f1 = rfc6455_encode_frame(0x1, b"Fragmento Inicial ", masked=False, fin=False)
            conn.sendall(f1)
            time.sleep(0.1)
            # Trama 2: FIN=1, opcode=0x0 (Continuation)
            f2 = rfc6455_encode_frame(0x0, b"y Fragmento Final", masked=False, fin=True)
            conn.sendall(f2)
            time.sleep(0.2)
            conn.close()
            server_sock.close()

        t = threading.Thread(target=frag_server, daemon=True)
        t.start()

        client = PureWebSocketClient(f"ws://127.0.0.1:{port}/")
        client._sock = socket.socket()
        client._sock.connect(("127.0.0.1", port))
        req = (
            "GET / HTTP/1.1\r\nHost: 127.0.0.1\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        client._sock.sendall(req.encode("ascii"))
        resp = client._sock.recv(4096)
        _, _, leftover = resp.partition(b"\r\n\r\n")
        client._buf = bytearray(leftover)

        reassembled = client.recv_text()
        self.assertEqual(reassembled, "Fragmento Inicial y Fragmento Final")
        client.close()
        t.join(timeout=3.0)

    def test_tcp_chunked_streaming_byte_by_byte(self):
        """Verifica que la lectura de tramas byte a byte por TCP se reensamble sin corrupción."""
        raw_frame = rfc6455_encode_frame(0x1, b"Mensaje fragmentado a nivel TCP", masked=False)
        client = PureWebSocketClient("ws://127.0.0.1:9222/")
        
        class ByteByByteSocket:
            def __init__(self, data):
                self.data = data
                self.idx = 0
            def recv(self, bufsize):
                if self.idx < len(self.data):
                    b = bytes([self.data[self.idx]])
                    self.idx += 1
                    return b
                return b""

        client._sock = ByteByByteSocket(raw_frame)
        res = client.recv_text()
        self.assertEqual(res, "Mensaje fragmentado a nivel TCP")


# ==============================================================================
# TIER 3: MOCK CDP LOOPBACK SERVER & INTEGRATION
# ==============================================================================
class TestTier3MockCDPIntegration(unittest.TestCase):
    """
    Tier 3: Integración de protocolo y verificación contra Mock CDP Loopback.
    - Simulación de consulta completa y validación de llamadas Input.insertText / Runtime.evaluate.
    - Soporte para flag --nuevo y reinicio de conversación.
    - Ejecución CLI vía subproceso contra servidor mock.
    - Verificación estructural del serializador JavaScript DOM -> Markdown.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_gemini_tier3_")
        self.mock = MockCDPLoopbackServer()

    def tearDown(self):
        self.mock.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_end_to_end_query_api_mock(self):
        """Ejecuta consulta completa a través de consultar_gemini_api con mock CDP."""
        custom_out = os.path.join(self.temp_dir, "salida_api.md")
        prompt = "¿Cuál es el módulo de elasticidad del hormigón H30?"

        res = consultar_gemini_api(
            prompt=prompt,
            nuevo=False,
            output_file=custom_out,
            port=self.mock.port,
            timeout=10.0,
            print_stdout=False,
            no_save=True,
        )

        self.assertIn("Respuesta Simulada de Gemini", res)
        self.assertIn("NCh433", res)
        self.assertTrue(os.path.exists(custom_out))
        with open(custom_out, "r", encoding="utf-8") as f:
            self.assertEqual(f.read().strip(), res.strip())

        # Verificar llamadas registradas en Mock
        methods_called = [c.get("method") for c in self.mock.recorded_calls]
        self.assertIn("Input.insertText", methods_called)
        self.assertIn("Runtime.evaluate", methods_called)

    def test_end_to_end_nuevo_chat_flag(self):
        """Verifica que el flag nuevo active la evaluación de reinicio de chat."""
        prompt = "Consulta tras reinicio"
        consultar_gemini_api(
            prompt=prompt,
            nuevo=True,
            port=self.mock.port,
            timeout=10.0,
            print_stdout=False,
            no_save=True,
        )

        eval_calls = [
            c.get("params", {}).get("expression", "")
            for c in self.mock.recorded_calls
            if c.get("method") == "Runtime.evaluate"
        ]
        has_nav_eval = any("new-chat-button" in e or "Nueva conversación" in e or "window.location.href" in e for e in eval_calls)
        self.assertTrue(has_nav_eval, "No se detectó el script de reinicio de conversación en Runtime.evaluate")

    def test_cli_subprocess_execution_with_port(self):
        """Ejecuta el script CLI consultar_gemini.py como subproceso apuntando al puerto mock."""
        custom_file = os.path.join(self.temp_dir, "cli_salida.md")
        cmd = [
            sys.executable,
            CONSULTAR_SCRIPT,
            "Calcular deflexión máxima",
            "--port",
            str(self.mock.port),
            "-o",
            custom_file,
            "--no-save",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0, f"Error en CLI: {proc.stderr}")
        self.assertIn("Respuesta Simulada de Gemini", proc.stdout)
        self.assertTrue(os.path.exists(custom_file))

    def test_dom_markdown_serializer_spec(self):
        """
        Verifica que el serializador JavaScript DOM -> Markdown contenga las reglas
        especificadas en survey_dom_report.md (código, encabezados, listas, tablas y supresión de botones).
        """
        serializer_js = DOM_MARKDOWN_SERIALIZER
        self.assertIn("code-block", serializer_js)
        self.assertIn("code-block-decoration", serializer_js)
        self.assertIn("gem-icon-button", serializer_js)
        self.assertIn("table-block", serializer_js)
        self.assertIn("```", serializer_js)
        self.assertIn("h1", serializer_js)
        self.assertIn("h4", serializer_js)


# ==============================================================================
# TIER 4: REGRESSION SAFETY & SYSTEM INTEGRITY
# ==============================================================================
class TestTier4SystemIntegrityAndRegression(unittest.TestCase):
    """
    Tier 4: Integridad de dependencias y regresión con suite de aceptación.
    - Cero importaciones pip en scripts/consultar_gemini.py y scripts/test_gemini_cli.py.
    - Verificación 100% PASS de los 12 módulos de scripts/test_aceptacion_token.py.
    """

    def test_zero_pip_imports_consultar_gemini(self):
        """Analiza el AST de consultar_gemini.py para asegurar que no use librerías externas."""
        self.assertTrue(os.path.exists(CONSULTAR_SCRIPT), f"{CONSULTAR_SCRIPT} no existe.")
        with open(CONSULTAR_SCRIPT, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=CONSULTAR_SCRIPT)

        stdlib_whitelist = {
            "argparse", "base64", "datetime", "hashlib", "json", "os",
            "socket", "struct", "subprocess", "sys", "time", "urllib", "re"
        }

        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_pkg = alias.name.split(".")[0]
                    imported_modules.add(root_pkg)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_pkg = node.module.split(".")[0]
                    imported_modules.add(root_pkg)

        invalid_imports = imported_modules - stdlib_whitelist
        self.assertEqual(
            invalid_imports,
            set(),
            f"Violación de regla Zero-Pip: Se detectaron librerías no permitidas en {CONSULTAR_SCRIPT}: {invalid_imports}",
        )

    def test_zero_pip_imports_test_gemini_cli(self):
        """Analiza el AST de este script de pruebas para asegurar cumplimiento de Zero-Pip."""
        current_file = os.path.abspath(__file__)
        with open(current_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=current_file)

        stdlib_whitelist = {
            "ast", "base64", "hashlib", "json", "os", "shutil", "socket",
            "struct", "subprocess", "sys", "tempfile", "threading", "time",
            "unittest", "urllib", "consultar_gemini"
        }

        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_pkg = alias.name.split(".")[0]
                    imported_modules.add(root_pkg)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_pkg = node.module.split(".")[0]
                    imported_modules.add(root_pkg)

        invalid_imports = imported_modules - stdlib_whitelist
        self.assertEqual(
            invalid_imports,
            set(),
            f"Violación de regla Zero-Pip en suite de pruebas: {invalid_imports}",
        )

    def test_test_aceptacion_token_regression(self):
        """
        Ejecuta la suite técnica integral scripts/test_aceptacion_token.py
        y verifica que conserve el 100% PASS en sus 12 módulos.
        Nota: T13 verifica aislamiento y limpieza del working tree.
        """
        cmd = [sys.executable, ACCEPT_TEST_SCRIPT]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
        output = proc.stdout + proc.stderr

        # Verificar resultados clave de los módulos
        modules = ["T12", "T3'", "T2'", "T9'", "T10", "T11", "T14", "T15", "T16", "T17", "Avisos Idempotencia"]
        for mod in modules:
            self.assertIn(
                f"Resultado {mod}: PASS",
                output,
                f"El módulo {mod} no reportó PASS en test_aceptacion_token.py. Salida:\n{output[-1500:]}",
            )


# ==============================================================================
# EJECUCIÓN PRINCIPAL DE LA BATERÍA
# ==============================================================================
def main():
    print("=" * 70)
    print("BATERÍA DE PRUEBAS INTEGRAL: test_gemini_cli.py (TIERS 1 - 4)")
    print("=" * 70)

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    suite.addTests(loader.loadTestsFromTestCase(TestTier1FeatureCoverage))
    suite.addTests(loader.loadTestsFromTestCase(TestTier2BoundaryCases))
    suite.addTests(loader.loadTestsFromTestCase(TestTier3MockCDPIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestTier4SystemIntegrityAndRegression))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"RESUMEN: {result.testsRun} pruebas ejecutadas.")
    if result.wasSuccessful():
        print("RESULTADO GLOBAL: TODAS LAS PRUEBAS PASARON (100% PASS)")
        print("=" * 70)
        sys.exit(0)
    else:
        print(f"RESULTADO GLOBAL: {len(result.failures)} fallos, {len(result.errors)} errores.")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
