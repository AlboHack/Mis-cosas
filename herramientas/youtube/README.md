# buscar_videos

Busca videos de YouTube sobre un tema, en inglés y en español. Lee la transcripción de cada video y los ordena según qué palabras clave cubren y en qué minuto. Entrega un JSON y un Markdown con enlaces `&t=` al minuto en que aparece cada clave.

**Corre en el PC de Nicolás, no en la nube.** YouTube bloquea las IP de servidores en la nube: responde 429, "Sign in to confirm you're not a bot" o `IpBlocked`. Desde una IP residencial funciona.

## Instalación (una vez)

```
pip install yt-dlp youtube-transcript-api
```

## Uso

```
python herramientas/youtube/buscar_videos.py "angular momentum control volume sprinkler" ^
  --terminos "control volume|volumen de control, angular momentum|momento angular, sprinkler|aspersor, torque|momento torsor, r cross|producto cruz" ^
  --tema-es "momento angular volumen de control aspersor" -n 15 --salida herramientas/youtube/resultados/CIV244/clase19
```

En PowerShell, la continuación de línea es `` ` `` en vez de `^`.

| Opción | Qué hace |
|---|---|
| `tema` | Consulta en inglés |
| `--terminos` | Términos del apunte separados por coma (`--claves` también sirve). Los alias van con `\|`. Por ejemplo, `r cross\|producto cruz`, porque en el audio nadie dice "r x V" |
| `--tema-es` | Consulta en español (obligatoria) |
| `--top` | Videos que pasan al extracto (8) |
| `--desde-json` | Repuntúa el JSON de una corrida anterior con otros términos, sin red. Este sí corre en la nube |
| `-n` | Resultados por idioma (15 por defecto) |
| `--pausa` | Segundos entre videos (1.0). Si aparece un 429, conviene subirla |

## Salida

- `<tema>.json`: todo, incluidas las transcripciones completas.
- `<tema>.md`: el ranking de similitud, con el minuto de cada término.
- `<tema>_extracto.md`: lo que se adjunta al chat de claude.ai para que Claude aplique la rúbrica de la skill `recomendar-videos`. Contiene los 8 videos que pasan el filtro, con los primeros 90 s y hasta 5 fragmentos de ±30 s alrededor de los términos más raros. Pesa unas 6 000 palabras (ejemplo: `ejemplos/clase19_CIV244/`).

## Filtro (antes de Claude)

- **Compuerta:** queda fuera todo video sin transcripción `en` o `es`, de menos de 3 min, short o en vivo, o que habla a menos de 60 palabras por minuto, porque en ese caso el contenido está en la imagen.
- **Puntaje de 0 a 3:** 1 punto por cobertura ≥ 0.5. Otro por evidencia institucional (código de ramo, o las palabras lecture, professor, clase o módulo N; "curso" no cuenta). Otro por vocabulario de derivación: 5 o más palabras como assume o despejamos, y 2.0 o más por cada 1000 palabras.
- **Evidencia:** los umbrales están en `investigacion/T2-senales.md`. Se ajustaron con 23 videos, así que son [Supuesto] hasta revisarlos en otros ramos.

## Cómo puntúa la similitud

Cada clave suma según dónde aparece:
- 1 punto si aparece en la transcripción o en un título de capítulo, con su minuto.
- 0.5 si aparece solo en el título o en la descripción, sin minuto.

El puntaje se divide por el número de términos: 1.00 significa que todos los términos aparecen con minuto. Los empates se ordenan por rareza: pesa más el término que pocos videos tratan, con el idf de la corrida. Después se ordena por menciones.

La búsqueda ignora mayúsculas y tildes, y no coincide dentro de otra palabra: `torque` no encuentra `torques`. Para cada clave usa la primera aparición. Los alias se escriben con `|`.

## Errores por video

El script no se cae cuando un video falla, ya sea porque es privado, está bloqueado o no tiene subtítulos. En el Markdown, el video queda como `sin transcripción`, y el motivo aparece como `Aviso:`. En ese caso el puntaje sale solo de los capítulos, el título y la descripción.

Si no hay transcripción, cualquier recomendación de ese video es un [Supuesto].

## Pruebas (sin red)

```
pytest herramientas/youtube/tests
```

## MCP de transcripciones (opcional, no activado)

Se revisó [jkawamoto/mcp-youtube-transcript](https://github.com/jkawamoto/mcp-youtube-transcript) en la versión v0.8.3, último commit `a0bfbbc` del 2026-11-04, con licencia MIT.
- **Qué hace:** expone 4 herramientas: `get_transcript`, `get_timed_transcript`, `get_video_info` y `get_available_languages`.
- **Código:** son 386 líneas. No usa `subprocess`, `eval` ni escritura de archivos.
- **Dependencias:** `youtube-transcript-api`, `yt-dlp`, `mcp`, `pydantic`, `requests`, `humanize` y `rich-click`.
- **A qué se conecta:** solo a YouTube, salvo que se configure un proxy. Puede usar Webshare, ScrapingAnt (`proxy.scrapingant.com`) o uno propio. Ese proxy solo se usa si se le pasan credenciales.

No encontré nada sospechoso. Aun así, **no hay `.mcp.json` en la raíz** del repo, por dos razones:
- Las sesiones de Claude Code en la nube lo cargarían y fallarían por el mismo bloqueo de IP.
- El README instala desde la rama principal sin fijar la versión: un cambio futuro en ese repo se ejecutaría solo.

Si se usa en el PC, por ejemplo desde Antigravity, conviene fijarlo al commit revisado:

```json
{
  "mcpServers": {
    "youtube-transcript": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/jkawamoto/mcp-youtube-transcript@a0bfbbc52e58ba05050936290bb7cfa4ef85a6bb", "mcp-youtube-transcript"]
    }
  }
}
```
