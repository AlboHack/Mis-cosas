#!/usr/bin/env python3
"""Recomienda videos de YouTube para estudiar un tema, según qué palabras clave
cubre cada video en su transcripción y en qué minuto aparecen.

Uso:
    python buscar_videos.py "angular momentum control volume sprinkler" \
        --terminos "control volume|volumen de control, angular momentum|momento angular, sprinkler|aspersor, r cross|producto cruz" \
        --tema-es "momento angular volumen de control aspersor" -n 15 --salida resultados/

Escribe <tema>.json (todo), <tema>.md (ranking) y <tema>_extracto.md (los 8 que pasan el filtro, con
fragmentos de transcripción, para que Claude aplique la rúbrica en el chat).

Dependencias: pip install yt-dlp youtube-transcript-api
YouTube bloquea las IP de servidores en la nube (429 / "not a bot"): correr desde un PC con IP residencial.
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
import re
import sys
import time
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path

IDIOMAS = ["en", "es"]


# ---------------------------------------------------------------- texto puro

def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, todo lo que no es letra o dígito pasa a un espacio."""
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def parsear_claves(texto: str) -> list[list[str]]:
    """'a, b|b2' -> [['a'], ['b', 'b2']]. Cada clave puede tener alias separados por '|'."""
    claves = []
    for parte in texto.split(","):
        alias = [a.strip() for a in parte.split("|") if a.strip()]
        if alias:
            claves.append(alias)
    return claves


def mmss(segundos: float) -> str:
    s = int(segundos)
    h, resto = divmod(s, 3600)
    m, s = divmod(resto, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _patron(alias: str) -> re.Pattern:
    return re.compile(r"(?<![a-z0-9])" + re.escape(normalizar(alias)) + r"(?![a-z0-9])")


def buscar_en_transcripcion(segmentos: list[dict], claves: list[list[str]]) -> dict:
    """segmentos: [{'start': s, 'text': ...}]. Devuelve {clave: {'t': s, 'veces': n}} de las
    claves halladas. Une los segmentos para encontrar claves partidas entre dos de ellos."""
    inicios, partes, pos = [], [], 0
    for seg in segmentos:
        txt = normalizar(seg.get("text", ""))
        inicios.append(pos)
        partes.append(txt)
        pos += len(txt) + 1
    unido = " ".join(partes)
    hallazgos = {}
    for alias in claves:
        primera, veces = None, 0
        for a in alias:
            ms = list(_patron(a).finditer(unido))
            veces += len(ms)
            if ms and (primera is None or ms[0].start() < primera):
                primera = ms[0].start()
        if primera is not None:
            i = bisect.bisect_right(inicios, primera) - 1
            hallazgos[alias[0]] = {"t": float(segmentos[i]["start"]), "veces": veces}
    return hallazgos


def buscar_en_texto(texto: str, claves: list[list[str]]) -> list[str]:
    t = normalizar(texto)
    return [alias[0] for alias in claves if any(_patron(a).search(t) for a in alias)]


def buscar_en_capitulos(capitulos: list[dict], claves: list[list[str]]) -> dict:
    hallazgos = {}
    for cap in capitulos or []:
        for c in buscar_en_texto(cap.get("title", ""), claves):
            hallazgos.setdefault(c, float(cap.get("start_time", 0)))
    return hallazgos


@dataclass
class Video:
    id: str
    titulo: str = ""
    canal: str = ""
    duracion: float | None = None
    vistas: int | None = None
    fecha: str = ""
    descripcion: str = ""
    capitulos: list = field(default_factory=list)
    busqueda: str = ""
    transcripcion_idioma: str = ""
    transcripcion_tipo: str = ""  # manual | automatica | sin_transcripcion
    transcripcion: list = field(default_factory=list)
    errores: list = field(default_factory=list)
    en_transcripcion: dict = field(default_factory=dict)
    en_capitulos: dict = field(default_factory=dict)
    en_descripcion: list = field(default_factory=list)
    puntaje: float = 0.0  # cobertura de los términos
    # metadatos de la página del video (se guardan; no puntúan)
    channel_id: str = ""
    uploader_id: str = ""
    channel_is_verified: bool | None = None
    channel_follower_count: int | None = None
    like_count: int | None = None
    comment_count: int | None = None
    categories: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    media_type: str = ""
    live_status: str = ""
    availability: str = ""
    # señales del filtro (T2) y similitud (T3)
    palabras: int = 0
    ppm: float = 0.0
    deriv_n: int = 0
    deriv_por_mil: float = 0.0
    institucional: str = ""
    compuerta: str = ""  # motivo de exclusión, "" si pasa
    rareza: float = 0.0
    filtro: int = 0

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.id}"

    @property
    def menciones(self) -> int:
        return sum(h["veces"] for h in self.en_transcripcion.values())


# --- Filtro (T2, herramientas/youtube/investigacion/T2-senales.md) ---------------------------
DERIVACION = [
    "integrate", "integral", "assume", "assumption", "boundary condition", "derive", "derivation", "therefore",
    "neglect", "approximate", "simplify", "substitute", "plug in", "solve for", "so that", "which gives",
    "integramos", "suponemos", "supongamos", "asumimos", "hipotesis", "condicion de borde",
    "condicion de contorno", "derivamos", "deducimos", "despreciamos", "por lo tanto", "reemplazamos",
    "sustituimos", "despejamos", "simplificamos", "nos queda"]
_PATRONES_DERIV = [_patron(p) for p in DERIVACION]
_CODIGO_RAMO = re.compile(r"(?<![A-Za-z0-9])[A-Z]{2,5} ?\d{3}[A-Z]?(?![A-Za-z0-9])")
_PALABRA_INST = re.compile(r"(?<![a-z0-9])(professor|profesor|lecture|lesson|lec ?\d+[a-z]?|universi\w*|college|catedra"
                           r"|clase|modulo \d+[a-z]?)(?![a-z0-9])")
_URL = re.compile(r"https?://\S+|www\.\S+")
MIN_DURACION, MIN_PPM, MIN_DERIV_N, MIN_DERIV_MIL = 180, 60, 5, 2.0


def evidencia_institucional(canal: str, titulo: str, descripcion: str) -> str:
    """Texto que delata respaldo universitario, o "". La palabra "curso" no cuenta: la usan los que venden cursos."""
    sin_url = _URL.sub(" ", titulo + "\n" + descripcion)
    m = _CODIGO_RAMO.search(sin_url)
    if m:
        return m.group(0)
    m = _PALABRA_INST.search(normalizar(canal + " " + sin_url))
    return m.group(0) if m else ""


def calcular_senales(v: Video) -> None:
    texto = " ".join(normalizar(s.get("text", "")) for s in v.transcripcion)
    v.palabras = len(texto.split())
    minutos = (v.duracion or 0) / 60
    v.ppm = round(v.palabras / minutos, 1) if minutos else 0.0
    v.deriv_n = sum(len(p.findall(texto)) for p in _PATRONES_DERIV)
    v.deriv_por_mil = round(1000 * v.deriv_n / v.palabras, 2) if v.palabras else 0.0
    v.institucional = evidencia_institucional(v.canal, v.titulo, v.descripcion)
    if not v.transcripcion or v.transcripcion_idioma[:2] not in ("en", "es"):
        v.compuerta = "sin transcripción en o es"
    elif v.duracion is not None and v.duracion < MIN_DURACION:
        v.compuerta = "dura menos de 3 min"
    elif v.media_type == "short" or v.live_status in ("is_live", "is_upcoming"):
        v.compuerta = "short o en vivo"
    elif v.ppm and v.ppm < MIN_PPM:
        v.compuerta = f"habla {v.ppm:.0f} ppm (< {MIN_PPM}): el contenido está en la imagen"
    else:
        v.compuerta = ""
    deriva = v.deriv_n >= MIN_DERIV_N and v.deriv_por_mil >= MIN_DERIV_MIL
    v.filtro = 0 if v.compuerta else int(v.puntaje >= 0.5) + int(bool(v.institucional)) + int(deriva)


# --- Similitud (T3) ------------------------------------------------------------------------
def idf_terminos(videos: list[Video], claves: list[list[str]]) -> dict:
    n = len(videos)
    df = {a[0]: sum(1 for v in videos if a[0] in v.en_transcripcion) for a in claves}
    return {t: math.log(n / k) if k else 0.0 for t, k in df.items()}


def aplicar_rareza(videos: list[Video], claves: list[list[str]]) -> dict:
    """rareza = Σ idf·ln(1+menciones) / Σ idf, con el idf entre los videos de esta corrida."""
    idf = idf_terminos(videos, claves)
    total = sum(idf.values()) or 1.0
    for v in videos:
        v.rareza = round(sum(idf[t] * math.log1p(h["veces"]) for t, h in v.en_transcripcion.items()) / total, 3)
    return idf


def puntuar(v: Video, claves: list[list[str]]) -> None:
    """1 punto por clave con minuto (transcripción o capítulo), 0.5 si solo está en título o
    descripción. Se normaliza por el número de claves: 1.0 = cobertura completa con minuto."""
    v.en_transcripcion = buscar_en_transcripcion(v.transcripcion, claves) if v.transcripcion else {}
    v.en_capitulos = buscar_en_capitulos(v.capitulos, claves)
    v.en_descripcion = buscar_en_texto(v.titulo + " " + v.descripcion, claves)
    puntos = 0.0
    for alias in claves:
        c = alias[0]
        if c in v.en_transcripcion or c in v.en_capitulos:
            puntos += 1
        elif c in v.en_descripcion:
            puntos += 0.5
    v.puntaje = round(puntos / len(claves), 3) if claves else 0.0


def ordenar(videos: list[Video]) -> list[Video]:
    """Similitud (T3): cobertura; a igual cobertura, rareza; luego menciones; luego vistas."""
    return sorted(videos, key=lambda v: (-v.puntaje, -v.rareza, -v.menciones, -(v.vistas or 0)))


def seleccionar(videos: list[Video], k: int = 8) -> list[Video]:
    """Los k mejores por filtro entre los que pasan la compuerta; desempata el orden de similitud."""
    pasan = [v for v in ordenar(videos) if not v.compuerta]
    return sorted(pasan, key=lambda v: -v.filtro)[:k]  # sorted es estable: conserva la similitud


INTRO_S, VENTANA_S, MAX_FRAGMENTOS = 90, 30, 5


def _texto_entre(v: Video, ini: float, fin: float) -> str:
    return " ".join(s["text"].replace("\n", " ") for s in v.transcripcion if ini <= s["start"] < fin).strip()


def fragmentos(v: Video, idf: dict) -> list[tuple[str, float, float]]:
    """Hasta MAX_FRAGMENTOS ventanas de ±VENTANA_S s en la primera aparición de los términos más
    raros, sin traslaparse entre sí ni con la intro [0, INTRO_S). Devuelve (término, ini, fin)."""
    elegidos: list[tuple[str, float, float]] = []
    ocupado = [(0.0, float(INTRO_S))]
    for t in sorted(v.en_transcripcion, key=lambda t: (-idf.get(t, 0), v.en_transcripcion[t]["t"])):
        c = v.en_transcripcion[t]["t"]
        ini, fin = max(0.0, c - VENTANA_S), c + VENTANA_S
        if any(ini < b and a < fin for a, b in ocupado):
            continue
        elegidos.append((t, ini, fin))
        ocupado.append((ini, fin))
        if len(elegidos) == MAX_FRAGMENTOS:
            break
    return sorted(elegidos, key=lambda e: e[1])


def a_extracto(tema: str, claves: list[list[str]], seleccion: list[Video], idf: dict, excluidos: list[Video]) -> str:
    """Lo que Claude lee en el chat para aplicar la rúbrica (spec v2): ~9 000 tokens para 8 videos."""
    nombres = [a[0] for a in claves]
    lin = [f"# Extracto para evaluar: {tema}", "",
           f"Términos: {', '.join(nombres)}", "",
           "Rúbrica: skill recomendar-videos. Cada nivel se justifica con un minuto de abajo; sin evidencia, 0.", ""]
    for i, v in enumerate(seleccion, 1):
        faltan = [c for c in nombres if c not in v.en_transcripcion]
        lin += [f"## {i}. {v.titulo}", "",
                f"- {v.url} · {v.canal} · {mmss(v.duracion) if v.duracion else '?'} · {v.fecha or '?'} · "
                f"transcripción {v.transcripcion_tipo} {v.transcripcion_idioma}",
                f"- Filtro {v.filtro}/3 · cobertura {v.puntaje:.2f} · rareza {v.rareza:.2f} · {v.ppm:.0f} ppm · "
                f"derivación {v.deriv_n} ({v.deriv_por_mil:.1f}/1000) · institucional: {v.institucional or 'no'}",
                f"- Términos: " + ", ".join(f"{t} {mmss(h['t'])}" for t, h in
                                             sorted(v.en_transcripcion.items(), key=lambda x: x[1]["t"])),
                f"- No aparecen: {', '.join(faltan) or 'ninguno'}", "",
                f"**[00:00–{mmss(INTRO_S)}] inicio:** {_texto_entre(v, 0, INTRO_S)}", ""]
        for t, ini, fin in fragmentos(v, idf):
            lin += [f"**[{mmss(ini)}–{mmss(fin)}] {t}** ({v.url}&t={int(ini)}s): {_texto_entre(v, ini, fin)}", ""]
    if excluidos:
        lin += ["## Excluidos por la compuerta", ""]
        lin += [f"- [{v.titulo}]({v.url}): {v.compuerta}" for v in excluidos]
    return "\n".join(lin) + "\n"


def a_markdown(tema: str, claves: list[list[str]], videos: list[Video]) -> str:
    nombres = [a[0] for a in claves]
    lin = [f"# Videos para: {tema}", "", f"Claves: {', '.join(nombres)}", "",
           "| # | Video | Canal | Duración | Idioma | Cobertura | Filtro |", "|---|---|---|---|---|---|---|"]
    for i, v in enumerate(videos, 1):
        dur = mmss(v.duracion) if v.duracion else "?"
        idioma = v.transcripcion_idioma or "sin transcripción"
        filtro = "fuera" if v.compuerta else f"{v.filtro}/3"
        lin.append(f"| {i} | [{v.titulo.replace('|', '/')}]({v.url}) | {v.canal} | {dur} | {idioma} | "
                   f"{v.puntaje:.2f} | {filtro} |")
    lin.append("")
    for i, v in enumerate(videos, 1):
        lin += [f"## {i}. {v.titulo}", "",
                f"{v.canal} · {mmss(v.duracion) if v.duracion else '?'} · {v.vistas or '?'} vistas · {v.fecha or '?'} · "
                f"transcripción: {v.transcripcion_tipo or 'sin_transcripcion'} {v.transcripcion_idioma}".rstrip(), ""]
        for c in nombres:
            if c in v.en_transcripcion:
                h = v.en_transcripcion[c]
                lin.append(f"- {c}: [{mmss(h['t'])}]({v.url}&t={int(h['t'])}s) ({h['veces']} veces)")
            elif c in v.en_capitulos:
                t = v.en_capitulos[c]
                lin.append(f"- {c}: [{mmss(t)}]({v.url}&t={int(t)}s) (capítulo)")
            elif c in v.en_descripcion:
                lin.append(f"- {c}: solo en título o descripción, sin minuto")
            else:
                lin.append(f"- {c}: no aparece")
        if v.compuerta:
            lin.append(f"- Fuera del filtro: {v.compuerta}")
        for e in v.errores:
            lin.append(f"- Aviso: {e}")
        lin.append("")
    return "\n".join(lin)


# ---------------------------------------------------------------- red

def buscar(consulta: str, n: int) -> list[dict]:
    import yt_dlp
    with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "skip_download": True}) as ydl:
        r = ydl.extract_info(f"ytsearch{n}:{consulta}", download=False)
    return [e for e in (r or {}).get("entries", []) if e and e.get("id")]


def completar_metadatos(v: Video) -> None:
    import yt_dlp
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as ydl:
            d = ydl.extract_info(v.url, download=False)
        v.titulo = d.get("title") or v.titulo
        v.canal = d.get("channel") or d.get("uploader") or v.canal
        v.duracion = d.get("duration") or v.duracion
        v.vistas = d.get("view_count") or v.vistas
        f = d.get("upload_date") or ""
        v.fecha = f"{f[:4]}-{f[4:6]}-{f[6:]}" if len(f) == 8 else f
        v.descripcion = d.get("description") or ""
        v.capitulos = [{"title": c.get("title", ""), "start_time": c.get("start_time", 0)}
                       for c in d.get("chapters") or []]
        for campo in ("channel_id", "uploader_id", "media_type", "live_status", "availability"):
            setattr(v, campo, d.get(campo) or "")
        for campo in ("channel_is_verified", "channel_follower_count", "like_count", "comment_count"):
            setattr(v, campo, d.get(campo))
        v.categories, v.tags = d.get("categories") or [], d.get("tags") or []
    except Exception as e:  # privado, bloqueado, eliminado, 429
        v.errores.append(f"metadatos: {type(e).__name__}: {str(e)[:150]}")


def descargar_transcripcion(v: Video, api) -> None:
    try:
        lista = api.list(v.id)
        try:
            t, tipo = lista.find_manually_created_transcript(IDIOMAS), "manual"
        except Exception:
            t, tipo = lista.find_generated_transcript(IDIOMAS), "automatica"
        v.transcripcion = [{"start": s.start, "text": s.text} for s in t.fetch()]
        v.transcripcion_idioma, v.transcripcion_tipo = t.language_code, tipo
    except Exception as e:  # sin subtítulos, desactivados, bloqueado
        v.transcripcion_tipo = "sin_transcripcion"
        v.errores.append(f"transcripción: {type(e).__name__}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("tema", help="consulta en inglés")
    p.add_argument("--terminos", "--claves", dest="claves", required=True,
                   help="términos del apunte separados por coma; alias hablados con '|'")
    p.add_argument("--tema-es", required=True, help="consulta en español")
    p.add_argument("--top", type=int, default=8, help="videos que pasan al extracto (8)")
    p.add_argument("-n", type=int, default=15, help="resultados por idioma (15)")
    p.add_argument("--salida", default=".", help="carpeta de salida")
    p.add_argument("--pausa", type=float, default=1.0, help="segundos entre videos, para no gatillar 429")
    p.add_argument("--desde-json", help="repuntúa un JSON de una corrida anterior, sin red (para probar términos)")
    a = p.parse_args(argv)

    claves = parsear_claves(a.claves)
    vistos: dict[str, Video] = {}
    if a.desde_json:
        campos = set(Video.__dataclass_fields__)
        for d in json.loads(Path(a.desde_json).read_text(encoding="utf-8"))["videos"]:
            vistos[d["id"]] = Video(**{k: val for k, val in d.items() if k in campos})
        for v in vistos.values():
            puntuar(v, claves)
            calcular_senales(v)
        return _escribir(a, claves, vistos)

    from youtube_transcript_api import YouTubeTranscriptApi
    api = YouTubeTranscriptApi()
    for consulta in (a.tema, a.tema_es):
        try:
            for e in buscar(consulta, a.n):
                if e["id"] not in vistos:
                    vistos[e["id"]] = Video(id=e["id"], titulo=e.get("title") or "", canal=e.get("channel") or "",
                                            duracion=e.get("duration"), vistas=e.get("view_count"), busqueda=consulta)
        except Exception as e:
            print(f"Búsqueda '{consulta}' falló: {type(e).__name__}: {e}", file=sys.stderr)

    for i, v in enumerate(vistos.values(), 1):
        print(f"[{i}/{len(vistos)}] {v.id} {v.titulo[:60]}", file=sys.stderr)
        completar_metadatos(v)
        descargar_transcripcion(v, api)
        puntuar(v, claves)
        calcular_senales(v)
        time.sleep(a.pausa)
    return _escribir(a, claves, vistos)


def _escribir(a, claves: list[list[str]], vistos: dict) -> int:
    idf = aplicar_rareza(list(vistos.values()), claves)
    videos = ordenar(list(vistos.values()))
    seleccion = seleccionar(videos, a.top)
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    base = re.sub(r"[^a-z0-9]+", "_", normalizar(a.tema))[:60] or "videos"
    datos = {"tema": a.tema, "claves": claves, "videos": [asdict(v) | {"url": v.url} for v in videos]}
    (salida / f"{base}.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    (salida / f"{base}.md").write_text(a_markdown(a.tema, claves, videos), encoding="utf-8")
    excluidos = [v for v in videos if v.compuerta]
    (salida / f"{base}_extracto.md").write_text(a_extracto(a.tema, claves, seleccion, idf, excluidos), encoding="utf-8")
    print(f"Listo: {salida / base}_extracto.md ({len(seleccion)} de {len(videos)} videos)", file=sys.stderr)
    return 0 if videos else 1


if __name__ == "__main__":
    sys.exit(main())
