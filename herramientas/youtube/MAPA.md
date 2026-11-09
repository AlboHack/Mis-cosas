# Mapa: recomendador de videos v2

Este mapa sigue el método wayfinder. Lleva la lista de decisiones y no guarda el detalle: cada decisión va en su ticket, más abajo. Se resuelve un ticket por sesión.

## Destino

Una especificación corta y aprobada por Nicolás para la versión 2 de `buscar_videos.py` y de la skill `recomendar-videos`. Con ella, dado el PDF de la clase, se recomiendan los videos más parecidos a esa materia y, entre ellos, los más rigurosos y profesionales. Cuando la spec está aprobada, se construye en el mismo PR ([AlboHack/Mis-cosas#1](https://github.com/AlboHack/Mis-cosas/pull/1)).

## Notas

- **Dominio:** ramos de Ingeniería Civil UTFSM. El material está en `universidad/2026-2/<ramo>/`. Los PDF tienen texto extraíble con `pdftotext`: el Apunte 12 de CIV244 y el certamen C2 de 2026 salen limpios.
- **Nodos:** el script corre en el PC con Antigravity, porque YouTube bloquea las IP de la nube. Claude lee el JSON que Antigravity sube al repo.
- **Economía:** Claude no lee 836 KB de transcripciones. Solo evalúa los 5 a 8 videos que pasan el filtro, y de cada uno solo fragmentos.
- **Skills a consultar:** `recomendar-videos`, y `ensenar-ingenieria` para el orden pedagógico.

## Decisiones hasta ahora

- **Juez de calidad:** primero un filtro automático en el script, y luego Claude evalúa con una rúbrica los 5 a 8 mejores (2026-11-09, Nicolás).
- **Referencia de similitud:** el apunte o la lámina de la clase en PDF, no claves escritas a mano (2026-11-09, Nicolás).
- **Destino:** primero la spec y después la construcción (2026-11-09, Nicolás).
- **Mapa:** este archivo, sin issues de GitHub (2026-11-09, Nicolás).
- **Prerrequisitos ya hechos:** alias hablados cortos y en español, y desempate por menciones (commit `35adc9d`).
- **[T1. Rúbrica](#t1-rúbrica-de-rigor-calidad-y-profesionalismo):** cinco criterios con niveles de 0 a 3, como N/P/M/L en los certámenes, y pesos 30/25/20/15/10. Un error conceptual limita el rigor y se informa con su minuto. Se recomienda con 60/100. Cada video lleva un rol, "clase" o "ejemplo".
- **[T2. Señales para el filtro](investigacion/T2-senales.md):** el filtro tiene dos pasos.
  - Una compuerta descarta al video que no tiene transcripción, que dura menos de 3 min o que habla a menos de 60 palabras por minuto.
  - Los que pasan reciben un puntaje de 0 a 3: 1 punto por cobertura ≥ 0.5, 1 por señales de institución y 1 por vocabulario de derivación. Los 8 mejores pasan a Claude.

  Vistas, likes y densidad de términos se descartaron como señales. Sin pauta de referencia, todo es [Supuesto].
- **[T3. Similitud](#t3-similitud-entre-el-apunte-en-español-y-la-transcripción-en-inglés):** Claude saca del PDF de la clase 10 a 15 términos bilingües y se los muestra a Nicolás antes de buscar. Se ordena por cobertura y, en caso de empate, por rareza (idf). Se probó con 23 videos y la Clase 19 de CIV244 ([script](investigacion/T3_similitud.py)).

## Tickets

| # | Ticket | Tipo | Bloqueado por | Estado |
|---|---|---|---|---|
| T1 | Rúbrica de rigor, calidad y profesionalismo | grilling (con Nicolás) | — | cerrado 2026-11-09 |
| T2 | Señales automáticas para el filtro | research | — | cerrado 2026-11-09 ([investigación](investigacion/T2-senales.md)) |
| T3 | Similitud entre el apunte en español y la transcripción en inglés | prototype (con Nicolás) | — | cerrado 2026-11-09 |
| T4 | Flujo de punta a punta y formato de salida | grilling (con Nicolás) | T1, T2, T3 | abierto |

### T1. Rúbrica de rigor, calidad y profesionalismo
**Pregunta:** ¿qué criterios y qué pesos usa Claude para poner nota a un video a partir de su transcripción? Los criterios candidatos son:
- deriva desde primeros principios, como el RTT, o solo aplica fórmulas;
- declara los supuestos y la validez (flujo permanente, incompresible, régimen);
- unidades y convención de signos;
- resuelve un ejemplo completo;
- errores conceptuales;
- autor con respaldo institucional;
- estructura y claridad.

¿Qué nota mínima hace falta para recomendar un video? ¿Cuenta como prueba de rigor que el video coincida con lo que piden las rúbricas de los certámenes?

**Resolución (2026-11-09, con Nicolás).** Nicolás valora cuatro cosas: que el video se parezca a sus clases, que dé contexto y alcances, que explique paso a paso y que ponga ejemplos. Sus profesores exigen mucho rigor, y una clase universitaria grabada vale más. La escala es la de la rúbrica del certamen C2 de CIV244, que pone nota a estos criterios: procedimiento paso a paso, parámetros, modelo correcto, condiciones de borde, interpretación y diagramas.

| Criterio | Peso | Qué mira Claude en la transcripción | Rúbrica C2 |
|---|---|---|---|
| Rigor del modelo | 30 % | Si el modelo es correcto para el caso, si declara los supuestos, las condiciones de borde, las unidades y la convención de signos | c, d, b |
| Paso a paso | 25 % | Si la derivación se puede seguir sin explicaciones adicionales, desde el principio físico (RTT, equilibrio) | a |
| Ejemplo resuelto e interpretado | 20 % | Si resuelve un problema completo y comenta el resultado | d, e |
| Contexto y alcances | 15 % | Si dice para qué sirve el modelo, cuándo vale y cuándo no (régimen, flujo permanente, incompresible) | c |
| Origen universitario | 10 % | 3: clase grabada de un curso universitario. 2: profesor universitario en canal propio. 1: ingeniero o tutor que se identifica. 0: no se sabe | — |

- **Niveles:** 0 = N, 1 = P, 2 = M, 3 = L, como en la rúbrica. La nota es Σ peso · nivel / 3, de 0 a 100.
- **Diagramas (criterio f):** no se juzgan, porque la transcripción no los muestra. Si el video dice "dibujamos el volumen de control", se anota como indicio [Supuesto].
- **Error conceptual:** baja la nota, no la veta. El rigor queda en 1 como máximo, y el error se informa siempre con su minuto y su corrección, aunque el video siga recomendado.
- **Umbral:** se recomienda con 60/100.
- **Rol:** cada video es "clase" (teoría y derivación) o "ejemplo" (resuelve un problema). A un "ejemplo" no se le exige contexto: se quita ese criterio y los pesos se reparten de nuevo de forma proporcional, quedando 35.3/29.4/23.5/11.8. La recomendación combina una clase seguida de un ejemplo.
- **Evidencia:** cada nivel se justifica con un minuto de la transcripción. Si no hay evidencia, el nivel es 0 y no se supone.

### T2. Señales automáticas para el filtro
**Pregunta:** ¿qué señales que entregan yt-dlp y la transcripción, sin gastar tokens, separan una clase rigurosa de un video flojo, y con qué umbral? Candidatas:
- seguidores del canal y si está verificado;
- razón entre likes y vistas;
- canal universitario o de profesor, según el nombre o la descripción;
- densidad de términos técnicos por minuto;
- presencia de palabras de derivación ("integrate", "assume", "boundary condition", "integramos", "suponemos");
- duración;
- transcripción manual o automática.

Hay que verificar qué campos devuelve yt-dlp en realidad y validar contra los 21 videos del ejemplo.

### T3. Similitud entre el apunte en español y la transcripción en inglés
**Pregunta:** ¿cómo se compara un apunte en español con un video en inglés? Opciones:
- (a) Claude extrae del PDF una lista bilingüe de 15 a 25 términos y ecuaciones con nombre, y el script la puntúa como hoy;
- (b) TF-IDF sobre esa lista bilingüe;
- (c) embeddings multilingües locales, más pesados de instalar en el PC.

El prototipo es probar (a) y (b) con el handout de la clase de momento angular de CIV244 y el JSON del ejemplo, y Nicolás juzga cuál ordena mejor.

**Resolución (2026-11-09, con Nicolás).** Se probó con el handout `CIV244_Clase_19_handout.pdf` (Soto, 2026-11-06), del que salieron 14 términos bilingües, y los 23 videos del ejemplo.
- **Efecto de los términos bilingües:** los videos en español pasan de 0 a 0.17 a 0.57 a 0.64 de cobertura.
- **Cobertura (a):** Cimbala baja al 10.° lugar, porque solo trata el volumen de control fijo y la clase pide además el volumen rotatorio y el no inercial.
- **Rareza (b):** premia lo propio de la clase. El "no inercial" solo aparece en Ziade (0:41) y en Bugg (7:49). Pero también favorece a los videos largos: Ranalli, 8 min y enfocado, cae del 2.° al 6.° lugar.
- **Decisión:** se ordena por (a) y, en caso de empate, por (b).
- **Términos:** Claude los saca del PDF, de 10 a 15 con alias hablados en inglés y español, y se los muestra a Nicolás en una línea antes de la búsqueda, por si el profesor vio en clase algo que el PDF no dice.
- **Descartado:** (c), embeddings multilingües. Exigen instalar un modelo en el PC, y (a)+(b) ya cruza los idiomas con la lista bilingüe.

### T4. Flujo de punta a punta y formato de salida
**Pregunta:** ¿quién corre cada paso y qué se entrega? Una propuesta de flujo:
1. Nicolás nombra la clase.
2. Claude extrae la lista de términos.
3. Antigravity corre el script con `--terminos` y sube el JSON.
4. Claude evalúa los mejores con la rúbrica y entrega el orden de visionado.

Hay que definir qué fragmentos de la transcripción lee Claude y con qué tope de tokens, y cómo se presenta la nota de cada video.

**Pregunta de Nicolás (2026-11-09):** ¿se puede lanzar la búsqueda desde un chat normal del proyecto en claude.ai? [Supuesto] Directamente no: el sandbox de claude.ai está en la nube, y YouTube bloquea esas IP. T4 debe definir:
- cómo pasa el pedido del chat a Antigravity PC: un texto que Nicolás copia, o un archivo en el canal;
- cómo vuelve el resultado al chat. El JSON pesa 836 KB, así que no conviene meterlo en el conocimiento del proyecto. Una opción es un extracto con solo los fragmentos de los 8 videos que pasan el filtro.

Antes, hay que verificarlo en el chat con `curl -sI https://www.youtube.com`.

## Sin especificar todavía

- Un registro de videos ya evaluados (id, nota, fecha), para no volver a evaluarlos en otra corrida ni en otro ramo.
- Canales de confianza que se repiten con buena nota (Cimbala, por ejemplo), y si se buscan dentro de ellos de forma directa.
- Qué pasa con los ramos sin material en PDF, o con láminas que son solo imágenes.

## Fuera del alcance

- Descargar el video o analizar la imagen (láminas, pizarra). La evidencia es la transcripción y los metadatos.
- Otras plataformas, como Coursera o MIT OCW. El destino es YouTube.
