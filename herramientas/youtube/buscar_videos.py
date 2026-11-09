#!/usr/bin/env python3
"""Recomienda videos de YouTube para estudiar un tema, según qué palabras clave
cubre cada video en su transcripción y en qué minuto aparecen.

Uso:
    python buscar_videos.py "angular momentum control volume sprinkler" \
        --claves "control volume, angular momentum, sprinkler, torque, r x V|r cross V, Euler turbomachine" \
        --tema-es "momento angular volumen de control aspersor" -n 15 --salida resultados/

Dependencias: pip install yt-dlp youtube-transcript-api
YouTube bloquea las IP de servidores en la nube (429 / "not a bot"): correr desde un PC con IP residencial.
"""
from __future__ import annotations

import argparse
import bisect
import json
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
    puntaje: float = 0.0

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.id}"


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
    """Puntaje; a igual puntaje, más menciones de las claves; luego vistas."""
    menciones = lambda v: sum(h["veces"] for h in v.en_transcripcion.values())  # noqa: E731
    return sorted(videos, key=lambda v: (-v.puntaje, -menciones(v), -(v.vistas or 0)))


def a_markdown(tema: str, claves: list[list[str]], videos: list[Video]) -> str:
    nombres = [a[0] for a in claves]
    lin = [f"# Videos para: {tema}", "", f"Claves: {', '.join(nombres)}", "",
           "| # | Video | Canal | Duración | Idioma | Cobertura |", "|---|---|---|---|---|---|"]
    for i, v in enumerate(videos, 1):
        dur = mmss(v.duracion) if v.duracion else "?"
        idioma = v.transcripcion_idioma or "sin transcripción"
        lin.append(f"| {i} | [{v.titulo.replace('|', '/')}]({v.url}) | {v.canal} | {dur} | {idioma} | {v.puntaje:.2f} |")
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
    p.add_argument("--claves", required=True, help="separadas por coma; alias con '|'")
    p.add_argument("--tema-es", help="consulta en español (por defecto: tema + ' en español')")
    p.add_argument("-n", type=int, default=15, help="resultados por idioma (15)")
    p.add_argument("--salida", default=".", help="carpeta de salida")
    p.add_argument("--pausa", type=float, default=1.0, help="segundos entre videos, para no gatillar 429")
    a = p.parse_args(argv)

    claves = parsear_claves(a.claves)
    from youtube_transcript_api import YouTubeTranscriptApi
    api = YouTubeTranscriptApi()

    vistos: dict[str, Video] = {}
    for consulta in (a.tema, a.tema_es or f"{a.tema} en español"):
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
        time.sleep(a.pausa)

    videos = ordenar(list(vistos.values()))
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    base = re.sub(r"[^a-z0-9]+", "_", normalizar(a.tema))[:60] or "videos"
    datos = {"tema": a.tema, "claves": claves, "videos": [asdict(v) | {"url": v.url} for v in videos]}
    (salida / f"{base}.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    (salida / f"{base}.md").write_text(a_markdown(a.tema, claves, videos), encoding="utf-8")
    print(f"Listo: {salida / base}.md ({len(videos)} videos)", file=sys.stderr)
    return 0 if videos else 1


if __name__ == "__main__":
    sys.exit(main())
