---
name: "recomendar-videos"
description: "Usar solo cuando Nicolás pida videos de YouTube para estudiar o repasar un tema de un ramo, o pida ordenar o evaluar videos que ya encontró."
---

# Recomendar videos

Un video se recomienda por lo que dice, no por el título. La evidencia es la transcripción, con el minuto en que aparece cada concepto. El script `herramientas/youtube/buscar_videos.py` la obtiene. Su README explica el uso.

## Dónde corre
- YouTube bloquea las IP de la nube. Desde un chat de claude.ai o Claude Code en la nube, la transcripción falla (`IpBlocked`, 429).
- Por eso no se corre el script aquí. Se entrega el comando para que Antigravity del PC lo corra y suba el `.md` o el `.json`, o para que Nicolás pegue el resultado.
- Si Nicolás ya trae el Markdown o el JSON, se trabaja sobre ese archivo.

## Elegir las palabras clave
1. Partir del material del ramo: láminas, apunte, pauta o enunciado (`universidad/<sección>/<módulo>/`). Si no hay material, preguntar qué cubre la clase, en vez de inventar el temario.
2. Elegir entre 5 y 8 claves que distingan el tema: el principio, la ecuación con nombre, el caso típico y el término que confunde. Por ejemplo, para momento angular en un volumen de control: `control volume, angular momentum, sprinkler, torque, r x V|r cross V, Euler turbomachine`.
3. Escribir las claves como se dicen en voz alta, porque la transcripción es audio. Los símbolos llevan su alias hablado (`r x V|r cross V`, `ΔP|pressure drop`). Si se busca en español, se agregan alias en ese idioma (`aspersor`, `momento angular`).
4. El tema va en inglés y `--tema-es` en español. Casi todo el material de buena calidad está en inglés.

## Presentar la recomendación
- **Lo incómodo va primero:** si ningún video cubre una clave del ramo, decirlo, con la clave que falta.
- **Orden de visionado:** concepto, luego derivación, luego ejemplo resuelto. Este orden no es necesariamente el del puntaje. Se explica en una línea por qué cada video va en su lugar.
- **Por video:** título enlazado, canal, duración, idioma de la transcripción, y el minuto de cada clave como enlace `&t=`. Se dice qué parte ver si no conviene ver el video entero.
- **Sin transcripción:** si un video no tiene transcripción, cualquier afirmación sobre su contenido va con [Supuesto], porque se basa solo en el título, la descripción o los capítulos.
- **Cuántos:** de 3 a 5 videos. El resto queda en el archivo.
- Una mención de la clave no prueba que el video la explique bien. Si importa, se revisa el texto de la transcripción alrededor de ese minuto en el JSON.
