# T2. Señales automáticas para el filtro de calidad

Pregunta (MAPA.md, T2): ¿qué señales de yt-dlp y de la transcripción separan una clase universitaria rigurosa de un video flojo, sin gastar tokens, y con qué umbral?

Fecha: 2026-11-09. Fuentes primarias: código instalado de yt-dlp 2026.10.26 y youtube-transcript-api 1.2.5, y el JSON de ejemplo (23 videos). La nube no llega a YouTube, así que no se consultó ningún video en vivo.

## 1. Qué campos entrega yt-dlp para YouTube

El docstring de `InfoExtractor` (`yt_dlp/extractor/common.py`, líneas 303-417) define los campos. Qué llena YouTube y desde dónde se lee en `yt_dlp/extractor/youtube/_video.py` y `_tab.py`:

| Campo | Origen en el código | En búsqueda plana (`extract_flat`) | Confiabilidad |
|---|---|---|---|
| `title`, `duration`, `view_count`, `channel`, `channel_id`, `uploader_id` (handle @) | `_tab.py:_extract_video` (búsqueda); `_video.py:4174-4196` (página) | sí | alta |
| `description` | página completa (`_video.py:4182`); la búsqueda trae solo un fragmento (`descriptionSnippet`) | fragmento | alta en la página |
| `channel_is_verified` | insignia del dueño (`_video.py:4527-4529`; `_tab.py`) | sí | solo vale `True` o queda ausente, nunca `False` |
| `live_status`, `availability` | `_video.py:4198`; `_tab.py` | sí (`availability` sale de insignias) | alta |
| `media_type` (`video`, `short`, `livestream`) | `_video.py:4199-4202` | no | alta |
| `categories`, `tags` | microformato y `keywords` (`_video.py:4195-4196`) | no | alta, pero la categoría es una sola y casi siempre es "Education" o "Science & Technology", así que no discrimina [Supuesto] |
| `like_count` | `videoPrimaryInfoRenderer` de `initial_data` (`_video.py:4464-4468`) | no | `None` si el canal oculta los likes o si YouTube cambia la interfaz |
| `channel_follower_count` | `subscriberCountText` de `videoSecondaryInfoRenderer` (`_video.py:4489-4491`) | no | redondeado ("1.2K"), y `None` si el canal oculta los suscriptores |
| `comment_count` | `initial_data` (`_video.py:4390-4396`) | no | `None` si los comentarios están desactivados |
| `chapters`, `heatmap` | `initial_data` (`_video.py:4411-4419`) | no | los capítulos solo existen si el autor los creó; el `heatmap` solo en videos con suficientes vistas |
| `license` | fila de metadatos (`_video.py:4518-4519`) | no | casi siempre ausente |
| `average_rating`, `dislike_count` | `videoDetails` | no | YouTube ya no los publica; quedan en `None` |

`like_count`, `channel_follower_count`, `comment_count`, `chapters` y `heatmap` necesitan `initial_data`, que viene de la página del video o de la API `next` (`_download_initial_data`, `_video.py:3883-3897`). Se pierden si se pasa `player_skip=initial_data` o `webpage_skip`. `completar_metadatos()` ya hace la extracción completa, así que **guardarlos no cuesta otra petición**.

youtube-transcript-api 1.2.5 (`_transcripts.py`) solo entrega `is_generated`, `language_code` e `is_translatable`, más los segmentos `{text, start, duration}`. Ese `duration` es el tiempo en pantalla, no el tiempo hablado (línea 43). La transcripción no trae ninguna otra señal de calidad.

## 2. Prueba con los 23 videos del ejemplo

Script de prueba: `T2_senales.py`, en esta carpeta. Usa `normalizar()` de `buscar_videos.py`. Columnas:
- ppm: palabras por minuto, igual a palabras de la transcripción sobre la duración.
- término: aciertos por cada 1000 palabras de una lista bilingüe genérica de mecánica de fluidos, de unas 60 entradas (control volume, cantidad de movimiento, torque, velocidad relativa, flujo másico, incompresible, boquilla y otras).
- deriv: vocabulario de derivación por cada 1000 palabras, con el total de aciertos entre paréntesis. La lista en inglés: integrate, assume, boundary condition, derive, therefore, neglect, substitute, plug in, solve for, we get. La lista en español: integramos, suponemos, hipótesis, condición de borde, despreciamos, por lo tanto, reemplazamos, despejamos, nos queda, consideramos. Se sacaron "so" y "entonces" porque son muletillas: Hu dice "so" 203 veces e IngStark dice "entonces" 42 veces.
- ec: habla de ecuaciones por cada 1000 palabras (equals, is equal to, squared, divided by, minus, igual a, al cuadrado, dividido, menos, seno, coseno).
- inst: aparece un código de ramo (`[A-Z]{2,5} ?\d{3}`) o una palabra como professor, lecture, lesson, lec N, university, clase, curso o módulo N en el canal, el título o la descripción, sin contar las URL.
- cob: el `puntaje` actual de cobertura de claves.

| Canal | min | ppm | término | deriv (n) | ec | inst | cob |
|---|---|---|---|---|---|---|---|
| Joe Ranalli (EME 303, Penn State) | 8.1 | 162 | 68 | 2.3 (3) | 3.8 | sí | 0.67 |
| John Cimbala (Penn State) | 8.2 | 185 | 79 | 7.2 (11) | 5.9 | sí | 0.67 |
| Paul Ziade | 25.9 | 78 | 65 | 4.0 (8) | 8.4 | no | 0.67 |
| Jim Bugg (ME 215) | 38.2 | 160 | 45 | 5.2 (32) | 2.5 | sí | 0.67 |
| Marcus Romani | 58.0 | 162 | 24 | 0.3 (3) | 3.2 | no | 0.67 |
| David Hu, lec11 | 74.9 | 114 | 27 | 0.9 (8) | 5.2 | sí | 0.67 |
| Ibham Veza | 20.5 | 186 | 52 | 0.3 (1) | 2.4 | sí | 0.67 |
| Engineering with Yonas | 5.7 | 126 | 108 | 4.2 (3) | 8.4 | no | 0.58 |
| Joseph Feser (MEEG331) | 7.7 | 157 | 85 | 8.3 (10) | 11.6 | sí | 0.50 |
| Civil Engg Network | 12.8 | **29** | 51 | 0.0 (0) | 34.6 | no | 0.33 |
| Professor Ted Diehl (ME340) | 12.8 | 162 | 16 | 1.9 (4) | 4.4 | sí | 0.33 |
| Engineer Thileban Explains | 5.7 | 118 | 33 | 1.5 (1) | 4.5 | no | 0.25 |
| CLOVER (es) | 81.7 | 92 | 54 | 5.9 (44) | 4.7 | no | 0.17 |
| Fluid Mechanics, Tut. Q4 | 11.2 | 91 | 64 | 6.9 (7) | 6.9 | no | 0.17 |
| Miguel Jované, Módulo 8c (es) | 42.5 | 89 | 66 | 1.9 (7) | 13.5 | sí | 0.17 |
| Miguel Jované, Módulo 8 (es) | 30.5 | 85 | 63 | 1.9 (5) | 19.8 | sí | 0.17 |
| Ciência e brisa (pt) | 54.2 | sin transcripción | — | — | — | no | 0.08 |
| Raju's Tutorials | **1.4** | sin transcripción | — | — | — | no | 0.08 |
| IngStark (es) | 13.7 | 173 | 63 | 0.0 (0) | 9.3 | sí* | 0.00 |
| Hablemos de Hidráulica (es) | 4.8 | 134 | 64 | 6.2 (4) | 3.1 | no | 0.00 |
| Mecánica de Fluidos Jaén (es) | 17.5 | 147 | 69 | 10.1 (26) | 2.3 | no | 0.00 |
| Alfredo Abuchar Curi (es) | 10.1 | 113 | 74 | 4.4 (5) | 31.4 | no | 0.00 |
| Fluid Mechanics, Tut. Q5 | 9.0 | 93 | 33 | 16.6 (14) | 13.0 | no | 0.00 |

\* Falso positivo: IngStark dice "curso" porque vende un curso en su web.

Lectura de la tabla. Con n = 23 y sin una nota de referencia, nada de lo que sigue está probado [Supuesto]:
- **Todas las transcripciones son automáticas.** Las 21 que existen son automáticas, incluidas las de Cimbala y Ranalli. "Manual o automática" no separa nada en esta muestra.
- **Lo que sí sirve de compuerta, aunque cada regla excluye un solo video:** no tener transcripción (Raju, Ciência), durar menos de 3 min (Raju) y hablar menos de 60 ppm (Civil Engg Network, que es una solución escrita casi sin voz). Un video así no se puede evaluar por su transcripción, que es la única evidencia que el destino del mapa permite.
- **La densidad de términos no mide rigor.** Yonas, un canal con 8 vistas, tiene la densidad más alta (108), y Hu y Diehl, que son profesores, tienen las más bajas (16 a 27). Además, los videos en español de cantidad de movimiento lineal, que tienen 0 de cobertura, salen altos (63 a 74). Esta señal dice que el video es de mecánica de fluidos, no si es riguroso ni si trata el tema pedido. Lo segundo lo cubre la similitud de T3. Se descarta como señal de rigor.
- **El habla de ecuaciones mide cuántas cuentas se hacen en voz alta.** Los máximos son Civil Engg (34.6, con pocas palabras) y Abuchar (31.4, un ejercicio numérico). Un video de problemas resueltos sale alto y una clase conceptual sale baja. Se descarta.
- **El vocabulario de derivación separa en parte.** Cimbala, Bugg y Feser quedan altos (5 a 8 por 1000) y Veza, IngStark y Civil Engg cerca de 0. Pero Ranalli, que tiene solo 3 aciertos, y Hu, con 0.9, quedan bajos aunque son clases fuertes. Ranalli deriva el RTT con la pizarra, y eso no queda en el audio [Supuesto]. Por eso se usa para sumar, no para excluir, y exige un mínimo de 5 aciertos para que un video corto con 3 aciertos no gane solo por el cociente.
- **La evidencia institucional es la señal más limpia de la muestra.** Detecta 7 de los 7 videos con respaldo universitario visible (Ranalli, Cimbala, Bugg, Hu, Feser, Diehl y Veza; Jované cuenta por "Módulo 8"). Tiene un falso positivo (IngStark) y un falso negativo probable (Ziade) [Supuesto].
- **Ritmo:** los videos de profesores están entre 114 y 186 ppm. No se ve ninguna separación por encima de 60 ppm.

## 3. Qué dice la literatura

- Guo, Kim y Rubin (2014), *How video production affects student engagement*, ACM L@S, DOI 10.1145/2556325.2566239, con 6.9 millones de sesiones en edX ([PDF](https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf), [resumen UBC](https://blogs.ubc.ca/videolearninghub/?p=569)). Encontraron más compromiso con videos cortos (menos de 6 min) y con presentadores que hablan rápido; una fuente secundaria cita hasta 254 ppm [Por verificar: no se pudo abrir el PDF desde esta sesión]. El estudio mide compromiso, no rigor. Por eso no sirve para castigar las clases largas: Hu dura 75 min y Bugg 38 min.
- La revisión de 2022 *Beyond Viewing Counts, Likes & Co* ([SciTePress](https://www.scitepress.org/Papers/2022/110328/)) concluye que las vistas y los likes no explican la calidad instruccional evaluada por expertos.
- Leibniz-IPN, *Likes, views, comments: How is viewer engagement related to high- and low-quality explanatory videos?* ([ficha](https://www.leibniz-ipn.de/en/research/publications/likes-views-comments-how-is-viewer-engagement-related-to-high-and-low-quality-explanatory-videos), [Springer s11165-023-10148-z](https://link.springer.com/article/10.1007/s11165-023-10148-z)). Con 44 videos sobre la derivada, los de baja calidad recibieron más likes e interacción, y los de alta calidad más visionado de largo plazo [Por verificar: dato tomado del resumen del buscador].
- En los estudios de salud, el contenido subido por profesionales obtiene mejor nota en DISCERN y GQS, con vistas y likes parecidos a los de los no profesionales ([KU, kangaroo care](https://research.hub.ku.edu.tr/entities/publication/4b1270dd-8826-4d47-9797-21705e9a1986)). Eso respalda la señal institucional y no las de popularidad.

Las vistas, los likes y los seguidores **no deben pesar en el filtro de rigor**. En el ejemplo, IngStark tiene 42 368 vistas y Hu 360.

## 4. Recomendación

**Compuerta: si falla una regla, el video queda fuera y no se puntúa.**
1. Tiene transcripción en `en` o `es`.
2. Dura 3 min o más, `media_type` no es `short` y `live_status` no es `is_live` ni `is_upcoming`.
3. Habla 60 ppm o más. Por debajo de eso, el contenido está en la imagen y no se puede evaluar desde la transcripción.

**Puntos de rigor, de 0 a 2, cada uno explicable en una línea:**
- **+1 institucional.** Un código de ramo `(?<![A-Za-z0-9])[A-Z]{2,5} ?\d{3}[A-Z]?(?![A-Za-z0-9])` en el título o la descripción sin URL, o bien `professor|profesor|lecture|lesson|lec ?\d+|universi|college|cátedra|clase|módulo \d` en el canal, el título o la descripción. "Curso" se saca porque produce falsos positivos de venta. Se guarda el texto que gatilló el punto para que Claude lo vea.
- **+1 derivación.** 5 o más aciertos de la lista de derivación y 2.0 o más por cada 1000 palabras.

**Combinación.** Se ordena por `(cobertura ≥ 0.5) + institucional + derivación`, de 0 a 3, y a igual puntaje por la cobertura (después, por la similitud de T3). Pasan a la rúbrica de Claude los 8 primeros. En el ejemplo, eso deja dentro a Cimbala, Bugg y Feser (3), a Ranalli, Ziade, Hu y Veza (2) y a Romani (1, con cobertura 0.67). Quedan fuera Yonas, Diehl y todos los de cobertura baja. La compuerta saca a Raju, Ciência y Civil Engg. Los cuatro canales que se sabía fuertes quedan entre los 7 primeros. Es un resultado retrospectivo sobre la misma muestra que fijó los umbrales [Supuesto].

**Campos nuevos que `buscar_videos.py` debe guardar:**
- De `completar_metadatos`, sin peticiones extra: `channel_id`, `uploader_id`, `channel_is_verified`, `channel_follower_count`, `like_count`, `comment_count`, `categories`, `tags`, `media_type`, `live_status` y `availability`.
- Calculados: `palabras`, `ppm`, `deriv_n`, `deriv_por_mil`, `institucional` (el texto que gatilló el punto o `""`), `compuerta` (motivo de exclusión o `""`) y `rigor`.

Seguidores, likes, verificación y comentarios **se guardan pero no puntúan**. Hay que reunir 2 o 3 corridas evaluadas por Claude con la rúbrica de T1 antes de darles peso. Si después se usa la razón likes/vistas, la literatura sugiere que va al revés de lo que se esperaría.

**Riesgos:**
- Las listas son específicas de mecánica de fluidos y de un solo tema. Antes de usarlas en otros ramos, hay que revisar los aciertos de derivación en un tema de FAE.
- El sesgo hacia videos en inglés con código de ramo puede dejar fuera clases buenas en español. Los dos módulos de Jované entran solo por "Módulo N".
