# Spec: recomendador de videos v2

Esta especificación sale del [mapa](MAPA.md), donde está el porqué de cada decisión (T1 a T4). Estado: **aprobada por Nicolás el 2026-11-09 y construida**.

## Flujo

1. **Chat del proyecto en claude.ai.** Nicolás pide videos para una clase y entrega el PDF (apunte, handout o lámina). Claude, con la skill `recomendar-videos`:
   - extrae de 10 a 15 términos bilingües con alias hablados y se los muestra a Nicolás en una línea para que los corrija;
   - entrega un bloque de 3 líneas para pegar en Antigravity PC: `git pull`, el comando y `git push`.
2. **Antigravity PC** corre `buscar_videos.py`. YouTube bloquea las IP de la nube, así que no corre en otro lado. El script escribe `<tema>.json`, `<tema>.md` y `<tema>_extracto.md`.
3. **Nicolás** adjunta `<tema>_extracto.md` al chat.
4. **Claude** pone nota a los videos del extracto con la rúbrica y entrega la recomendación.

## Cambios en `buscar_videos.py`

- `--terminos "a|alias, b|alias"` reemplaza a `--claves`, que queda como alias. `--tema-es` pasa a ser obligatorio.
- **Compuerta (T2).** Se excluye todo video sin transcripción `en` o `es`, con una duración menor a 3 min, con `media_type` short, en vivo, o con menos de 60 palabras por minuto. El motivo se guarda en `compuerta`.
- **Señales (T2):**
  - `institucional`: código de curso o las palabras professor, lecture, lesson, lec N, university, clase o módulo N, en el canal, el título o la descripción, sin contar URL ni la palabra "curso". Se guarda el texto que coincidió.
  - `derivacion`: 5 o más palabras de derivación y 2.0 o más por cada 1000 palabras.
- **Filtro:** `filtro = (cobertura ≥ 0.5) + institucional + derivacion`, de 0 a 3. El resto de los campos que hoy se guardan siguen igual.
- **Orden de similitud (T3).** Se ordena por cobertura, luego por rareza (Σ idf · ln(1 + menciones) / Σ idf, con el idf entre los videos de la corrida) y luego por menciones.
- **Campos nuevos en el JSON:** `channel_id`, `channel_is_verified`, `channel_follower_count`, `like_count`, `comment_count`, `categories`, `tags`, `media_type`, `live_status`, `availability`, `palabras`, `ppm`, `deriv_n`, `deriv_por_mil`, `institucional`, `compuerta`, `rareza` y `filtro`. Seguidores, likes y verificación se guardan, pero no puntúan.
- **`<tema>_extracto.md`.** Incluye los 8 mejores por filtro (desempate por el orden de similitud) entre los que pasan la compuerta. Por video:
  - metadatos y señales;
  - los primeros 90 s de la transcripción, porque ahí suelen estar el contexto y quién es el autor;
  - hasta 5 fragmentos de ±30 s alrededor de la primera aparición de los términos más raros, sin repetir fragmentos que se traslapen.

  Tope estimado con los datos del ejemplo: unas 6 400 palabras, alrededor de 9 000 tokens y 38 KB.
- **Pruebas nuevas, sin red:** la compuerta, `institucional` (que "curso" no cuente), `derivacion`, la rareza contra un cálculo a mano y que el extracto respete el tope de 5 fragmentos y no traslape fragmentos.

## Rúbrica (T1), en la skill `recomendar-videos`

| Criterio | Peso clase | Peso ejemplo |
|---|---|---|
| Rigor del modelo (modelo correcto, supuestos, condiciones de borde, unidades y signos) | 30 % | 35.3 % |
| Paso a paso, desde el principio físico | 25 % | 29.4 % |
| Ejemplo resuelto e interpretado | 20 % | 23.5 % |
| Contexto y alcances | 15 % | — |
| Origen universitario | 10 % | 11.8 % |

- **Escala:** niveles de 0 a 3, como N/P/M/L en la rúbrica de los certámenes. La nota es Σ peso · nivel / 3.
- **Umbral:** se recomienda con 60/100.
- **Evidencia:** cada nivel se justifica con un minuto. Sin evidencia, el nivel es 0.
- **Error conceptual:** el rigor queda en 1 como máximo, y el error se informa con su minuto y su corrección.
- **Diagramas:** no se juzgan, porque la transcripción no los muestra.

## Salida de Claude en el chat

1. **Lo incómodo primero:** qué términos de la clase ningún video cubre y qué errores conceptuales se encontraron.
2. **Orden de visionado,** de 3 a 5 videos: primero una "clase", después un "ejemplo". Por video:
   - título enlazado, canal, rol y duración;
   - la nota y los 5 niveles;
   - el minuto de cada término, como enlace `&t=`;
   - qué tramo ver.
3. **Sin transcripción:** si un video la tiene incompleta, todo lo que se afirme de él va con [Supuesto].

## Fuera del alcance

Analizar la imagen del video, buscar en otras plataformas y que el chat llegue a YouTube directamente.
