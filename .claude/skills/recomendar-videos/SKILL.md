---
name: "recomendar-videos"
description: "Usar solo cuando Nicolás pida videos de YouTube para estudiar o repasar un tema o una clase de un ramo, pida el prompt de búsqueda para Antigravity, o traiga un resultado de búsqueda para ordenar o evaluar."
---

# Recomendar videos

Un video se recomienda por lo que dice, no por el título. La evidencia es la transcripción, con el minuto en que aparece cada concepto. La obtiene el script `herramientas/youtube/buscar_videos.py`, que solo corre en el PC de Nicolás. YouTube bloquea las IP de la nube, así que desde este chat no se intenta: ni `curl` ni `pip`.

## Flujo
1. **Material.** Pedir el PDF de la clase (apunte, handout o lámina), o tomarlo de `universidad/2026-2/<ramo>/` si está en el conocimiento del proyecto. Si no hay material, preguntar qué se vio en clase, en vez de inventar el temario.
2. **Términos.** Sacar del material de 10 a 15 términos según "Elegir los términos". Mostrarlos en una sola línea y preguntar: "¿Falta algo que dijo el profesor en clase?". Se espera la respuesta antes del paso 3.
3. **Pedido.** Entregar el bloque de "Pedido para Antigravity PC" completo y listo para pegar, sin `<>` sin llenar.
4. **Resultado.** Nicolás adjunta al chat el `.md` de `herramientas/youtube/resultados/...`, desde GitHub o descargado. Con eso se presenta la recomendación. Si trae el JSON, se trabaja sobre el JSON.

## Pedido para Antigravity PC
Se rellenan los campos y se entrega dentro de un bloque de código:

```
Repo Mis-cosas: git fetch origin && git checkout <rama> && git pull
pip install -q yt-dlp youtube-transcript-api
python herramientas/youtube/buscar_videos.py "<tema en inglés>" --claves "<términos con alias>" --tema-es "<tema en español>" -n 15 --salida herramientas/youtube/resultados/<ramo>/<clase>
Si aparece 429 o "not a bot", repite con --pausa 3. No uses cookies ni proxies.
git add herramientas/youtube/resultados && git commit -m "Videos: <ramo> <clase>" && git push
Reporta: cuántos videos tuvieron transcripción, los avisos de error y la ruta del .md.
```

- **`<rama>`:** `main`. Mientras el PR del recomendador no se integre, `claude/eager-bohr-l1tnf2`.
- **`<ramo>`:** código corto, por ejemplo `CIV244`.
- **`<clase>`:** número y tema sin espacios, por ejemplo `clase19_momento_angular`.
- **Comillas:** los términos van entre comillas dobles, separados por coma, con los alias separados por `|`, sin comillas por dentro.

## Elegir los términos
1. Partir de lo que el material pide: el principio, la ecuación con nombre, cada caso que resuelve la clase y cada advertencia del profesor, como "este volumen de control es no inercial". Lo que la clase pide y casi ningún video trata es lo que más distingue al buen video.
2. Por ejemplo, para la Clase 19 de CIV244: `reynolds transport|transporte de reynolds|rtt|ttr, angular momentum|momento angular|cantidad de movimiento angular, r cross|r times v|producto cruz, control volume|volumen de control, sprinkler|aspersor, nozzle|boquilla|tobera, relative velocity|velocidad relativa, angular velocity|velocidad angular|omega, torque|momento torsor, non inertial|no inercial|rotating control volume`.
3. Escribir las claves como se dicen en voz alta, porque la transcripción es audio. El alias hablado debe ser un fragmento corto: `r cross`, no `r cross V`, porque se dice "r cross u" o "r cross the velocity". En la corrida del 2026-11-09, "r cross" aparecía en 10 transcripciones y `r cross V` coincidió solo en 2.
4. Toda clave lleva su alias en español. Sin ellos, los videos en español puntúan 0 aunque traten el tema.
5. Descartar los nombres de libro que nadie pronuncia. "Euler turbomachine" no apareció en ninguno de 21 videos.
6. El tema va en inglés y `--tema-es` en español. Casi todo el material de buena calidad está en inglés.

## Presentar la recomendación
- **Con el resultado actual (v1):** el `.md` trae la cobertura y los minutos, pero no el texto de la transcripción. La rúbrica de rigor (`herramientas/youtube/SPEC_v2.md` en el repo) se aplica cuando exista el extracto de la v2. Hasta entonces, el rigor de cada video va con [Supuesto].
- **Lo incómodo va primero:** si ningún video cubre una clave del ramo, decirlo, con la clave que falta.
- **Orden de visionado:** concepto, luego derivación, luego ejemplo resuelto. Este orden no es necesariamente el del puntaje. Se explica en una línea por qué cada video va en su lugar.
- **Por video:** título enlazado, canal, duración, idioma de la transcripción, y el minuto de cada clave como enlace `&t=`. Se dice qué parte ver si no conviene ver el video entero.
- **Sin transcripción:** si un video no tiene transcripción, cualquier afirmación sobre su contenido va con [Supuesto], porque se basa solo en el título, la descripción o los capítulos.
- **Cuántos:** de 3 a 5 videos. El resto queda en el archivo.
- Una mención de la clave no prueba que el video la explique bien. Si importa, se revisa el texto de la transcripción alrededor de ese minuto en el JSON.
