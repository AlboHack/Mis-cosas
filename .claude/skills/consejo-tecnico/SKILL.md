---
name: "consejo-tecnico"
description: "Usar solo cuando Nicolás pida un consejo (council), varias perspectivas o evaluar una decisión desde varios ángulos: elegir método, modelo o enfoque de un informe, un plan de estudio o de práctica, una decisión con trade-offs. La revisión de un entregable terminado es de revision-critica-y-certamenes; preguntarle a él por sus supuestos, de interrogar-planteamiento."
---

# Consejo técnico

Adaptado de `council` (tsenart/council-skill, MIT): rondas ciega y de contrainterrogatorio, pasada contrafactual e informe de minoría. De `Council` (danielmiessler/Personal_AI_Infrastructure, MIT) se toma que cada voz se redacta para el tema; de llm-council (karpathy) la revisión cruzada sobre posiciones anónimas. El consejo sirve si cambia la decisión; si las voces solo decoran la misma respuesta, sobra.

## 1. Hoja de hechos
Antes de convocar, reunir en una lista numerada los datos del enunciado, los números calculados en Python (con utfsm-calc si la función existe) y los valores de norma, marcados [Por verificar] si el texto no está a la vista. Todas las voces razonan sobre esta hoja: si una necesita un número nuevo, se calcula y se agrega a la hoja con su número.

## 2. Panel
Tres voces; cinco si Nicolás pide el panel completo o la decisión cruza áreas (estructura y costo, informe y plazo). Elegir voces que puedan discrepar de verdad en esta decisión y escribir para cada una un brief de tres líneas ajustado al tema: lente, la pregunta que no suelta, su punto ciego.

| Voz | Lente | Pregunta que no suelta |
|---|---|---|
| Modelador | primeros principios y validez del modelo (régimen, rango elástico, EA finita, hipótesis de LWR) | ¿Qué supuesto, si falla, invalida el método? |
| Verificador | juez externo, segundo método, orden de magnitud | ¿Con qué número independiente sabré que está bien? |
| Normativo | cláusula y año de NCh, ACI, AISC, MOP, REDEVU | ¿Qué exige la norma y en qué cláusula? |
| Constructor | constructibilidad, costo en UF o CLP, plazo, riesgo contractual | ¿Se puede ejecutar y cuánto cuesta equivocarse? |
| Corrector | la pauta: qué evalúa el profesor y cuánto pesa | ¿Qué descuenta puntaje aquí? |
| Abogado del diablo | modo de falla y alternativa más fuerte | ¿Qué haría fracasar la recomendación? |
| Estratega | tiempo de Nicolás, esfuerzo frente a beneficio | ¿Qué se deja de hacer para hacer esto? |

Las voces son roles técnicos, no personajes.

## 3. Ronda 1: análisis ciego
Cada voz recibe solo la pregunta, la hoja de hechos y su brief, y termina con veredicto, confianza (alta, media o baja) y dónde puede estar equivocada.
- Con subagentes (Claude Code): una llamada Agent por voz, todas en el mismo mensaje.
- Sin subagentes (claude.ai): escribir las voces una tras otra, cerrando cada una antes de empezar la siguiente, y declarar en una línea que el consejo corrió en un solo agente.

## 4. Ronda 2: contrainterrogatorio
Rotular las posiciones de la ronda 1 como A, B, C, sin el nombre de la voz, para que se juzgue el argumento y no el rol. Cada voz responde:
1. la posición con que más discrepa y por qué, con número si se puede;
2. la que fortaleció su análisis;
3. qué cambió en su posición;
4. la prueba que la haría cambiar de opinión: un cálculo, un ensayo, una cláusula.

Si en la ronda 1 todas coincidieron, correr una pasada contrafactual antes de cerrar: suponer que el consenso está equivocado, construir la alternativa más fuerte y nombrar el dato que la haría ganar.

## 5. Veredicto
Claude preside: decide el argumento con mejor evidencia, no la mayoría. Si la prueba decisiva es un cálculo corto, se ejecuta y el veredicto la incorpora. La respuesta sigue el orden de la regla 6 de las instrucciones y el consejo ocupa el lugar del desarrollo, en este formato:

```
Veredicto: <recomendación en una o dos líneas> (confianza)
Acuerdo: <lo que todas las voces sostienen>
Desacuerdo vivo: <punto> · prueba que lo decide: <cálculo, ensayo o cláusula>
Informe de minoría: <voz, posición y en qué caso tendría razón>
Decide Nicolás: <la decisión que es suya, con la opción recomendada>
```

Las rondas completas se muestran solo si Nicolás las pide.
