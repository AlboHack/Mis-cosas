# Decisiones de configuración

| Fecha | Decisión | Por qué | Evidencia |
|---|---|---|---|
| 2026-10-21 | Código recurrente en el paquete utfsm-calc, no pegado en las skills | Cargar una skill cargaba cientos de líneas de código y cada chat lo reescribía | 7 pruebas contra soluciones cerradas |
| 2026-10-21 | Pynite como juez independiente de pórticos | Coincide con el núcleo propio en la sexta cifra, incluida una rótula | Caso 01 |
| 2026-10-21 | anastruct descartado | Con una rótula interna se desvía 12 % | Caso 01 |
| 2026-10-21 | handcalcs para memorias de cálculo | El número del informe sale del código verificado | Compilado con pdflatex |
| 2026-10-21 | Punto decimal en todo | El preámbulo usa es-nodecimaldot | Falla de coma en caso 01 (v1) |
| 2026-10-21 | `friccion` lanza error en 2300 < Re < 4000 | Colebrook en transición sobrestima h_f hasta 93 % | Caso 02 |
| 2026-10-21 | profundizar-prompt y buscar-y-evaluar-skills solo a pedido | Cargaban unas 1 400 palabras en cada tarea | Reglas 4 y 5 de las instrucciones |
| 2026-10-21 | Fuentes externas registradas en `fuentes/` con revisión de cambios (`scripts/revisar_fuentes.py`) | Portar mejoras de los repos originales sin perder las adaptaciones | Base fijada en los commits de hoy |
| 2026-10-21 | Nueva skill interrogar-planteamiento, adaptada de grilling | Decisiones de modelo implícitas son la causa típica de diferencias con SAP2000 | Pendiente de caso de prueba |
| 2026-10-21 | writing-for-agents copiada sin cambios para editar skills en este repo | Principios de una sola fuente de verdad y divulgación progresiva | Licencia MIT incluida |
| 2026-10-21 | verification-before-completion (superpowers) no se adopta | verificacion-independiente ya la cubre con contenido de ingeniería | Solo registrada en fuentes para comparar |
| 2026-10-21 | pdf de Anthropic solo como referencia | Licencia propietaria: no se copia a un repo público | — |

