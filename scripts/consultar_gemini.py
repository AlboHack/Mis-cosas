#!/usr/bin/env python3
"""
scripts/consultar_gemini.py
Cliente CLI autónomo en Python estándar para interactuar de forma bidireccional
y determinística con Google Gemini Web a través de Brave CDP (127.0.0.1:9222).

Cumple estrictamente con:
- Cero dependencias externas pip (Python 3 standard library).
- Cliente WebSocket nativo RFC 6455 con máscaras, framing 16/64 bits, ping/pong y reensamblado.
- Inyección confiable en editor Quill/Angular vía Input.insertText sin interferir portapapeles.
- Detección reactiva de streaming (desaparición de botón detener + estabilización de longitud).
- Extracción íntegra de Markdown desde el DOM.
- Persistencia dual en stdout y /storage/emulated/0/Download/Universidad/Consultas_Gemini/.
"""

import argparse
import base64
import datetime
import hashlib
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.parse
import urllib.request


# ==============================================================================
# SERIALIZADOR JAVASCRIPT DOM -> MARKDOWN
# ==============================================================================
DOM_MARKDOWN_SERIALIZER = r"""(() => {
    function domToMarkdown(element) {
        if (!element) return "";
        function serialize(node) {
            if (node.nodeType === Node.TEXT_NODE) return node.textContent;
            if (node.nodeType !== Node.ELEMENT_NODE) return "";
            const tag = node.tagName.toLowerCase();
            if (tag === "button" || tag === "gem-icon-button" || tag === "gem-icon" || tag === "mat-icon" ||
                node.classList.contains("buttons") || node.classList.contains("code-block-decoration") ||
                tag === "gem-popover" || node.classList.contains("circle-overlay")) {
                return "";
            }
            if (tag === "code-block") {
                const langSpan = node.querySelector(".code-block-decoration span");
                const lang = langSpan ? langSpan.innerText.trim().toLowerCase() : "";
                const codeEl = node.querySelector("pre code") || node.querySelector("pre") || node.querySelector("code");
                const codeText = codeEl ? codeEl.innerText : "";
                return "\n```" + lang + "\n" + codeText + "\n```\n";
            }
            if (tag === "pre") {
                const code = node.querySelector("code");
                return "\n```\n" + (code ? code.innerText : node.innerText) + "\n```\n";
            }
            if (tag === "code") return "`" + node.innerText + "`";
            if (tag === "h1") return "\n# " + serializeChildren(node).trim() + "\n\n";
            if (tag === "h2") return "\n## " + serializeChildren(node).trim() + "\n\n";
            if (tag === "h3") return "\n### " + serializeChildren(node).trim() + "\n\n";
            if (tag === "h4") return "\n#### " + serializeChildren(node).trim() + "\n\n";
            if (tag === "p") return "\n" + serializeChildren(node).trim() + "\n";
            if (tag === "b" || tag === "strong") return "**" + serializeChildren(node) + "**";
            if (tag === "i" || tag === "em") return "*" + serializeChildren(node) + "*";
            if (tag === "a") return "[" + serializeChildren(node) + "](" + (node.getAttribute("href") || "") + ")";
            if (tag === "ul") return "\n" + serializeChildren(node) + "\n";
            if (tag === "ol") {
                let idx = 1, res = "\n";
                for (const child of node.children) {
                    if (child.tagName.toLowerCase() === "li") {
                        res += idx + ". " + serializeChildren(child).trim() + "\n";
                        idx++;
                    }
                }
                return res + "\n";
            }
            if (tag === "li") return "- " + serializeChildren(node).trim() + "\n";
            if (tag === "table" || tag === "table-block") {
                const rows = Array.from(node.querySelectorAll("tr"));
                if (rows.length === 0) return "";
                let out = "\n";
                rows.forEach((row, rIdx) => {
                    const cells = Array.from(row.querySelectorAll("th, td"));
                    out += "| " + cells.map(c => serializeChildren(c).trim()).join(" | ") + " |\n";
                    if (rIdx === 0) out += "| " + cells.map(() => "---").join(" | ") + " |\n";
                });
                return out + "\n";
            }
            if (tag === "hr") return "\n---\n\n";
            if (tag === "br") return "\n";
            return serializeChildren(node);
        }
        function serializeChildren(node) {
            let res = "";
            for (let i = 0; i < node.childNodes.length; i++) res += serialize(node.childNodes[i]);
            return res;
        }
        return serialize(element).trim().replace(/\n{3,}/g, "\n\n");
    }

    const responses = Array.from(document.querySelectorAll(
        "model-response message-content, .model-response-text message-content, [id^='message-content-id-'], .response-container-content"
    ));
    if (responses.length === 0) return "";
    return domToMarkdown(responses[responses.length - 1]);
})()"""


# ==============================================================================
# CLIENTE WEBSOCKET RFC 6455 PURO ESTÁNDAR
# ==============================================================================
class PureWebSocketClient:
    """Cliente WebSocket RFC 6455 basado exclusivamente en la librería estándar."""

    def __init__(self, url: str, timeout: float = 30.0):
        self.url = url
        self.timeout = timeout
        parsed = urllib.parse.urlsplit(url)
        self.host = parsed.hostname or "127.0.0.1"
        self.port = parsed.port or (443 if parsed.scheme == "wss" else 80)
        self.path = (parsed.path or "/") + (("?" + parsed.query) if parsed.query else "")
        self._sock = None
        self._buf = bytearray()
        self._fragment_buf = bytearray()

    def connect(self):
        """Establece la conexión TCP y completa el handshake HTTP Upgrade."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self.timeout)
        self._sock.connect((self.host, self.port))

        sec_key = base64.b64encode(os.urandom(16)).decode("ascii")
        req = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {sec_key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"\r\n"
        )
        self._sock.sendall(req.encode("ascii"))

        # Lectura del handshake HTTP
        resp_bytes = bytearray()
        while b"\r\n\r\n" not in resp_bytes:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise ConnectionError("Conexión cerrada prematuramente durante handshake WebSocket.")
            resp_bytes.extend(chunk)

        header_part, _, leftover = resp_bytes.partition(b"\r\n\r\n")
        self._buf.extend(leftover)

        lines = header_part.decode("iso-8859-1").split("\r\n")
        status_line = lines[0]
        if "101" not in status_line:
            raise ConnectionError(f"Handshake WebSocket falló con estado: {status_line}")

        headers = {}
        for line in lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()

        guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        expected_accept = base64.b64encode(
            hashlib.sha1((sec_key + guid).encode("ascii")).digest()
        ).decode("ascii")

        if headers.get("sec-websocket-accept") != expected_accept:
            raise ConnectionError("Sec-WebSocket-Accept key inválida en respuesta del servidor.")

    def send_frame(self, opcode: int, payload: bytes):
        """Codifica y transmite una trama cliente enmascarada (RFC 6455 §5.2)."""
        length = len(payload)
        mask = os.urandom(4)
        b0 = 0x80 | (opcode & 0x0F)

        if length <= 125:
            header = bytes([b0, 0x80 | length]) + mask
        elif length <= 65535:
            header = bytes([b0, 0x80 | 126]) + struct.pack("!H", length) + mask
        else:
            header = bytes([b0, 0x80 | 127]) + struct.pack("!Q", length) + mask

        masked = bytearray(payload)
        for i in range(length):
            masked[i] ^= mask[i % 4]

        self._sock.sendall(header + masked)

    def send_text(self, text: str):
        """Envía un mensaje de texto UTF-8."""
        self.send_frame(0x1, text.encode("utf-8"))

    def _send_pong(self, data: bytes):
        """Responde a un Ping con Pong."""
        try:
            self.send_frame(0xA, data)
        except Exception:
            pass

    def _send_close(self, data: bytes):
        """Envía trama de cierre de conexión."""
        try:
            self.send_frame(0x8, data[:125])
        except Exception:
            pass

    def recv_text(self) -> str:
        """
        Recibe y decodifica el siguiente mensaje de texto completo,
        gestionando fragmentación, control frames y tramas de 16/64 bits.
        """
        while True:
            if len(self._buf) >= 2:
                b0 = self._buf[0]
                b1 = self._buf[1]
                fin = bool(b0 & 0x80)
                opcode = b0 & 0x0F
                has_mask = bool(b1 & 0x80)
                payload_len = b1 & 0x7F
                idx = 2

                if payload_len == 126:
                    if len(self._buf) < 4:
                        chunk = self._sock.recv(4096)
                        if not chunk:
                            raise ConnectionResetError("Socket cerrado esperando longitud extendida.")
                        self._buf.extend(chunk)
                        continue
                    payload_len = struct.unpack("!H", self._buf[2:4])[0]
                    idx = 4
                elif payload_len == 127:
                    if len(self._buf) < 10:
                        chunk = self._sock.recv(4096)
                        if not chunk:
                            raise ConnectionResetError("Socket cerrado esperando longitud extendida.")
                        self._buf.extend(chunk)
                        continue
                    payload_len = struct.unpack("!Q", self._buf[2:10])[0]
                    idx = 10

                mask_key = None
                if has_mask:
                    if len(self._buf) < idx + 4:
                        chunk = self._sock.recv(4096)
                        if not chunk:
                            raise ConnectionResetError("Socket cerrado esperando clave de máscara.")
                        self._buf.extend(chunk)
                        continue
                    mask_key = self._buf[idx : idx + 4]
                    idx += 4

                total_len = idx + payload_len
                if len(self._buf) >= total_len:
                    data = bytes(self._buf[idx:total_len])
                    self._buf = self._buf[total_len:]

                    if mask_key:
                        data = bytes(b ^ mask_key[i % 4] for i, b in enumerate(data))

                    if opcode == 0x9:  # Ping
                        self._send_pong(data)
                        continue
                    elif opcode == 0x8:  # Close
                        self._send_close(data)
                        self.close()
                        raise ConnectionResetError("WebSocket cerrado por el servidor.")
                    elif opcode == 0xA:  # Pong
                        continue
                    elif opcode in (0x1, 0x0):  # Text o Continuation
                        self._fragment_buf.extend(data)
                        if fin:
                            msg = self._fragment_buf.decode("utf-8")
                            self._fragment_buf = bytearray()
                            return msg
                        continue

            chunk = self._sock.recv(65536)
            if not chunk:
                raise ConnectionResetError("Conexión finalizada mientras se leía del socket.")
            self._buf.extend(chunk)

    def close(self):
        """Cierra el socket ordenadamente."""
        if self._sock:
            try:
                self.send_frame(0x8, struct.pack("!H", 1000))
            except Exception:
                pass
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None


# ==============================================================================
# CLIENTE CHROME DEVTOOLS PROTOCOL (CDP)
# ==============================================================================
class CDPClient:
    """Cliente para Chrome DevTools Protocol sobre conexión WebSocket."""

    def __init__(self, ws_url: str, timeout: float = 30.0):
        self.ws = PureWebSocketClient(ws_url, timeout=timeout)
        self._msg_id = 0

    def connect(self):
        self.ws.connect()

    def call(self, method: str, params: dict = None, timeout: float = None) -> dict:
        """Ejecuta un método CDP sincrónicamente y espera la respuesta correspondiente."""
        self._msg_id += 1
        call_id = self._msg_id
        req = {"id": call_id, "method": method}
        if params is not None:
            req["params"] = params

        self.ws.send_text(json.dumps(req))
        start_time = time.time()
        max_wait = timeout or self.ws.timeout

        while True:
            if time.time() - start_time > max_wait:
                raise TimeoutError(f"Tiempo agotado esperando respuesta CDP: {method} (id={call_id})")

            text = self.ws.recv_text()
            try:
                msg = json.loads(text)
            except Exception:
                continue

            # Descartar eventos asíncronos y respuestas de otros IDs
            if msg.get("id") == call_id:
                if "error" in msg:
                    err = msg["error"]
                    raise RuntimeError(f"Error CDP ({err.get('code')}): {err.get('message')}")
                return msg.get("result", {})

    def evaluate(self, expression: str, await_promise: bool = True, return_by_value: bool = True, user_gesture: bool = True) -> any:
        """Evalúa una expresión JavaScript en el contexto de la pestaña."""
        res = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "awaitPromise": await_promise,
                "returnByValue": return_by_value,
                "userGesture": user_gesture,
            },
        )
        if "exceptionDetails" in res:
            exc = res["exceptionDetails"]
            desc = exc.get("exception", {}).get("description") or exc.get("text")
            raise RuntimeError(f"Fallo de evaluación JavaScript: {desc}")
        return res.get("result", {}).get("value")

    def insert_text(self, text: str):
        """Inserta texto directamente en el elemento enfocado vía CDP Input."""
        return self.call("Input.insertText", {"text": text})

    def navigate(self, url: str) -> dict:
        """Navega la pestaña a la URL especificada."""
        return self.call("Page.navigate", {"url": url})

    def close(self):
        self.ws.close()


# ==============================================================================
# DESCUBRIMIENTO Y RECUPERACIÓN DE PESTAÑA GEMINI
# ==============================================================================
def discover_gemini_tab(port: int = 9222, auto_recover: bool = True, max_retries: int = 6) -> dict:
    """
    Localiza la pestaña activa de Gemini Web en Brave via CDP.
    Si el puerto no responde o Brave fue suspendido por LMK, activa recuperación automática vía ADB.
    """
    url = f"http://127.0.0.1:{port}/json"

    for attempt in range(max_retries):
        try:
            req = urllib.request.urlopen(url, timeout=3.0)
            tabs = json.loads(req.read().decode("utf-8"))

            for tab in tabs:
                if tab.get("type") == "page" and "gemini.google.com" in tab.get("url", ""):
                    if tab.get("webSocketDebuggerUrl"):
                        return tab

        except Exception:
            pass

        if not auto_recover:
            break

        # Intento de recuperación vía ADB
        try:
            subprocess.run(
                ["adb", "forward", f"tcp:{port}", "localabstract:chrome_devtools_remote"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            subprocess.run(
                [
                    "adb",
                    "shell",
                    "am",
                    "start",
                    "-n",
                    "com.brave.browser/com.google.android.apps.chrome.Main",
                    "-d",
                    "https://gemini.google.com",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass

        time.sleep(2.0)

    raise RuntimeError(
        f"No se pudo conectar a la pestaña de gemini.google.com en 127.0.0.1:{port}. "
        "Verifique que Brave esté iniciado y el reenvío ADB activo."
    )


# ==============================================================================
# AUTOMATIZACIÓN DE GEMINI WEB
# ==============================================================================
def reset_conversation(cdp: CDPClient, timeout: float = 20.0):
    """
    Inicia una nueva conversación (--nuevo) sin recargar la página completa.
    Espera a que el spinner desaparezca y el editor vuelva a montarse.
    """
    nav_script = """(() => {
        const btn = document.querySelector('[data-test-id="new-chat-button"] a, a[href="/app"], [aria-label*="Nueva conversación"], [aria-label*="New chat"]');
        if (btn) {
            btn.click();
            return "clicked";
        }
        window.location.href = "https://gemini.google.com/app";
        return "navigated";
    })()"""
    cdp.evaluate(nav_script)

    # Esperar a que el spinner desaparezca y el editor esté listo
    start_time = time.time()
    ready_check = """(() => {
        const isVisible = (el) => !!(el && (el.offsetWidth || el.offsetHeight || el.getClientRects().length));
        const activeSpinner = document.querySelector(".is-loading, mat-progress-spinner, [role='progressbar']");
        const editor = document.querySelector("rich-textarea .ql-editor");
        return (!isVisible(activeSpinner) && !!editor);
    })()"""

    while time.time() - start_time < timeout:
        try:
            if cdp.evaluate(ready_check):
                time.sleep(0.5)
                return True
        except Exception:
            pass
        time.sleep(0.5)

    raise TimeoutError("Tiempo agotado esperando reinicio de chat en Gemini Web.")


def inject_prompt_and_send(cdp: CDPClient, prompt: str, timeout: float = 15.0):
    """
    Inyecta el prompt en el editor Quill/Angular utilizando CDP Input.insertText
    y activa el botón de envío sin tocar el portapapeles ni robar foco.
    """
    # 1. Esperar a que el editor esté montado
    start_time = time.time()
    while time.time() - start_time < timeout:
        editor_exists = cdp.evaluate("!!document.querySelector('rich-textarea .ql-editor')")
        if editor_exists:
            break
        time.sleep(0.5)
    else:
        raise RuntimeError("No se encontró el editor 'rich-textarea .ql-editor' en la página.")

    # 2. Enfocar y seleccionar todo el contenido previo para reemplazo limpio
    focus_script = """(() => {
        const editor = document.querySelector("rich-textarea .ql-editor");
        if (!editor) return false;
        editor.focus();
        const sel = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(editor);
        sel.removeAllRanges();
        sel.addRange(range);
        document.execCommand("delete");
        return true;
    })()"""
    cdp.evaluate(focus_script)

    # 3. Inserción atómica nativa vía CDP
    cdp.insert_text(prompt)

    # 4. Esperar y hacer clic en el botón de envío
    send_script = """(() => {
        const btn = document.querySelector(".send-button button, button[aria-label*='Enviar'], button[aria-label*='Send']");
        if (!btn) return false;
        btn.click();
        return true;
    })()"""

    click_start = time.time()
    while time.time() - click_start < 5.0:
        if cdp.evaluate(send_script):
            return True
        time.sleep(0.2)

    raise RuntimeError("No fue posible disparar el botón de envío en Gemini Web.")


def wait_for_response(cdp: CDPClient, initial_count: int, timeout: float = 180.0, poll_interval: float = 0.5) -> str:
    """
    Supervisa la generación por streaming de Gemini hasta su finalización:
    - Espera a que comience la respuesta.
    - Espera a que el botón de detener desaparezca.
    - Exige que la longitud del texto se estabilice durante 3 ciclos sucesivos (1.5s).
    - Extrae el Markdown completo mediante el serializador DOM.
    """
    start_time = time.time()
    poll_state_js = """(() => {
        const stopBtn = document.querySelector(".send-button.stop, button[aria-label*='Detener'], button[aria-label*='Stop']");
        const responses = document.querySelectorAll(
            "model-response message-content, .model-response-text message-content, [id^='message-content-id-'], .response-container-content"
        );
        const last = responses.length > 0 ? responses[responses.length - 1] : null;
        const len = last ? (last.innerText || "").trim().length : 0;
        return {
            has_stop: !!stopBtn,
            count: responses.length,
            length: len
        };
    })()"""

    # 1. Esperar inicio de streaming o aparición del botón de stop
    time.sleep(0.5)
    while time.time() - start_time < 12.0:
        state = cdp.evaluate(poll_state_js)
        if state.get("has_stop") or state.get("count", 0) > initial_count or state.get("length", 0) > 0:
            break
        time.sleep(0.4)

    # 2. Bucle de monitoreo y estabilización
    consecutive_stable = 0
    last_length = -1

    while time.time() - start_time < timeout:
        state = cdp.evaluate(poll_state_js)
        has_stop = state.get("has_stop", False)
        current_len = state.get("length", 0)

        if not has_stop and current_len > 0:
            if current_len == last_length:
                consecutive_stable += 1
                if consecutive_stable >= 3:
                    # Estabilización confirmada
                    break
            else:
                consecutive_stable = 0
                last_length = current_len
        else:
            consecutive_stable = 0
            last_length = current_len

        time.sleep(poll_interval)
    else:
        raise TimeoutError(f"Tiempo agotado ({timeout}s) esperando estabilización de respuesta en Gemini.")

    # 3. Extracción de Markdown desde el DOM
    markdown = cdp.evaluate(DOM_MARKDOWN_SERIALIZER)
    return (markdown or "").strip()


# ==============================================================================
# PERSISTENCIA LOCAL
# ==============================================================================
def save_response(response_text: str, custom_output: str = None) -> str:
    """
    Guarda la respuesta en el almacenamiento local:
    - Siempre genera un respaldo con timestamp en /storage/emulated/0/Download/Universidad/Consultas_Gemini/
    - Si se especifica custom_output, guarda además en dicha ruta.
    """
    default_dir = "/storage/emulated/0/Download/Universidad/Consultas_Gemini"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"consulta_{timestamp}.md"
    default_file = os.path.join(default_dir, filename)

    try:
        os.makedirs(default_dir, exist_ok=True)
        with open(default_file, "w", encoding="utf-8") as f:
            f.write(response_text + "\n")
    except Exception as e:
        print(f"[WARN] No se pudo guardar en {default_file}: {e}", file=sys.stderr)

    if custom_output:
        try:
            custom_dir = os.path.dirname(os.path.abspath(custom_output))
            if custom_dir:
                os.makedirs(custom_dir, exist_ok=True)
            with open(custom_output, "w", encoding="utf-8") as f:
                f.write(response_text + "\n")
        except Exception as e:
            print(f"[ERROR] No se pudo guardar en archivo personalizado {custom_output}: {e}", file=sys.stderr)
            raise

    return default_file


# ==============================================================================
# FUNCIÓN PRINCIPAL API
# ==============================================================================
def consultar_gemini(
    prompt: str,
    nuevo: bool = False,
    output_file: str = None,
    port: int = 9222,
    timeout: float = 180.0,
    print_stdout: bool = True,
    no_save: bool = False,
) -> str:
    """
    Función de alto nivel para consultar Gemini Web vía CDP.
    Retorna la respuesta en formato Markdown original.
    """
    if not prompt or not prompt.strip():
        raise ValueError("El prompt no puede estar vacío.")

    tab = discover_gemini_tab(port=port, auto_recover=True)
    ws_url = tab["webSocketDebuggerUrl"]

    cdp = CDPClient(ws_url, timeout=timeout)
    cdp.connect()

    try:
        if nuevo:
            reset_conversation(cdp, timeout=20.0)

        # Contar respuestas previas para aislar el nuevo turno
        initial_count = cdp.evaluate(
            "document.querySelectorAll('model-response message-content, .response-container-content').length"
        ) or 0

        # Inyectar texto y enviar
        inject_prompt_and_send(cdp, prompt, timeout=15.0)

        # Monitorear respuesta y extraer Markdown
        response = wait_for_response(cdp, initial_count=initial_count, timeout=timeout)

        # Persistencia en archivo
        if not no_save:
            save_response(response, custom_output=output_file)
        elif output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(response + "\n")

        # Impresión en stdout
        if print_stdout:
            sys.stdout.write(response + "\n")
            sys.stdout.flush()

        return response

    finally:
        cdp.close()


# ==============================================================================
# PUNTO DE ENTRADA CLI
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Cliente CLI autónomo para Google Gemini Web vía Brave CDP (127.0.0.1:9222)."
    )
    parser.add_argument("prompt", nargs="?", default=None, help="Texto del prompt para Gemini.")
    parser.add_argument("-f", "--file", help="Ruta al archivo con el prompt de entrada.")
    parser.add_argument("-o", "--output", help="Ruta de archivo personalizada para guardar la respuesta en Markdown.")
    parser.add_argument("--nuevo", action="store_true", help="Iniciar una nueva conversación antes de consultar.")
    parser.add_argument("--port", type=int, default=9222, help="Puerto CDP de Brave (por defecto 9222).")
    parser.add_argument("--timeout", type=float, default=180.0, help="Tiempo máximo de espera para la respuesta en segundos.")
    parser.add_argument("--no-save", action="store_true", help="Desactivar guardado automático en el directorio predeterminado.")

    args = parser.parse_args()

    # Determinación del prompt
    prompt = None
    if args.file:
        if args.file == "-":
            prompt = sys.stdin.read()
        else:
            if not os.path.exists(args.file):
                parser.error(f"El archivo especificado no existe: {args.file}")
            with open(args.file, "r", encoding="utf-8") as f:
                prompt = f.read()
    elif args.prompt:
        if args.prompt == "-":
            prompt = sys.stdin.read()
        else:
            prompt = args.prompt
    else:
        if not sys.stdin.isatty():
            prompt = sys.stdin.read()
        else:
            parser.error("Debe proporcionar un prompt como argumento o mediante la opción -f / --file.")

    if not prompt or not prompt.strip():
        sys.stderr.write("Error: El prompt proporcionado está vacío.\n")
        sys.exit(1)

    try:
        consultar_gemini(
            prompt=prompt,
            nuevo=args.nuevo,
            output_file=args.output,
            port=args.port,
            timeout=args.timeout,
            print_stdout=True,
            no_save=args.no_save,
        )
    except Exception as e:
        sys.stderr.write(f"Error al consultar Gemini: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
