---
name: "interrogar-planteamiento"
description: "Usar cuando Nicolás quiera someter a interrogatorio un planteamiento antes de ejecutarlo: un modelo de SAP2000, el enfoque de un informe, la estrategia para un problema de certamen o un plan de estudio; también ante 'interrógame' o 'grill me'."
---

# Interrogar un planteamiento

Adaptado de `grilling` (mattpocock/skills, MIT). El objetivo es que ninguna decisión del planteamiento quede supuesta en silencio antes de modelar, redactar o resolver.

## Árbol de decisiones
Cada decisión abre las que dependen de ella. Ramas típicas:
- Modelo estructural: geometría y ejes, apoyos y liberaciones, rigideces (EA finita, corte, secciones), cargas y combinaciones, unidades y convención de signos, juez externo con que se validará.
- Informe: qué pide cada inciso, qué se compara contra qué, tolerancia aceptada, figuras y tablas necesarias.
- Problema de certamen: principio de partida (equilibrio, energía, continuidad), supuestos de validez y su rango adimensional, casos límite para controlar el resultado.
- Plan de estudio: fecha, temas, errores registrados en `aprendizaje/<tema>/ERRORES.md`.

## Rondas
La **frontera** son las decisiones cuyas dependencias ya están resueltas. En cada ronda se pregunta toda la frontera, numerada, con la respuesta recomendada:

```
❓ P1 - <título>: <pregunta, con opciones si sirven>
➡️ <respuesta recomendada y por qué, en una línea>
```

Cada pregunta se redacta para que "sí" acepte la recomendación. Una pregunta que depende de otra todavía abierta va en una ronda posterior.

## Hechos y decisiones
Los hechos los busca Claude, no Nicolás: el dato del enunciado, el valor de la norma (marcado [Por verificar] si no está el texto), un cálculo previo de orden de magnitud en Python. Las decisiones son de Nicolás: se le plantean y se espera su respuesta.

## Cierre
Termina cuando la frontera queda vacía. Entregar la lista de decisiones tomadas, en el orden del árbol, como especificación del trabajo. No ejecutar el modelo ni el informe hasta que Nicolás confirme esa lista.
