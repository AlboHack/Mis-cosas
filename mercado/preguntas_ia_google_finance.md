# Preguntas para la IA de Google Finance (Antigravity, navegador de la tablet)

Reglas para quien pregunta:
- Hacer las preguntas **una por una**, en este orden, y pegar la respuesta **textual** (sin resumir).
- A cada pregunta agregar al final: *"Indica la fuente y la fecha de cada número."*
- Si la respuesta no trae fuente o fecha, anotar `[SIN FUENTE]` al lado. Claude la tratará como no verificada.
- No pedir recomendaciones de compra/venta: solo hechos, cifras y escenarios con fuente.
- Nada personal en las preguntas ni en el archivo (repo público).

Salida: `mercado/google_finance/AAAA-MM-DD_ia.md`, con el formato `### P<n>. <pregunta>` + respuesta textual.

## A. Macro y Fed
1. ¿Qué decidió la Reserva Federal en su última reunión (tasa, votación, guía futura) y cuál es la fecha de la próxima?
2. ¿Qué probabilidad asigna el mercado (FedWatch u otra) a recortes o alzas de tasa en las próximas dos reuniones?
3. ¿Cuál fue el último dato de inflación de EE.UU. (IPC y PCE, general y subyacente) y cuándo sale el próximo?
4. ¿Cuál fue el último informe de empleo (nóminas, desempleo, salarios) y cuándo sale el próximo?
5. ¿Cuál fue el último PIB trimestral de EE.UU. y qué esperan los economistas para el próximo trimestre?
6. ¿Cómo está la curva de rendimientos (2 y 10 años) y qué ha cambiado en el último mes?

## B. Valorización y salud del S&P 500
7. ¿Cuál es el P/E actual (trailing y forward) del S&P 500 y cómo se compara con su promedio de 10 y 25 años?
8. ¿Cuál es el CAPE (Shiller P/E) actual?
9. ¿Qué crecimiento de utilidades se espera para el S&P 500 este trimestre y el próximo año?
10. ¿Qué porcentaje de empresas del S&P 500 ha superado las estimaciones de utilidades esta temporada?
11. ¿Qué porcentaje de acciones del S&P 500 está sobre su media móvil de 200 días (amplitud del mercado)?
12. ¿Cuánto pesan las 10 mayores empresas en el S&P 500 y cómo ha cambiado esa concentración?

## C. Sentimiento y flujos
13. ¿Cuál es el nivel actual del VIX y su promedio de los últimos 12 meses?
14. ¿Qué muestra el índice Fear & Greed de CNN u otro indicador de sentimiento?
15. ¿Cuáles han sido los flujos netos (entradas/salidas) de los ETF de renta variable de EE.UU. en el último mes?
16. ¿Qué dice la última encuesta de sentimiento de inversionistas (AAII u otra)?

## D. Sectores y temas con tendencia
17. ¿Cuáles han sido los 3 mejores y los 3 peores sectores del S&P 500 en el último mes y en lo que va del año?
18. ¿Qué está impulsando a los semiconductores y a la inteligencia artificial en las últimas semanas?
19. ¿Cómo les va a las empresas pequeñas (Russell 2000) frente a las grandes y por qué?
20. ¿Cómo está el oro y qué explica su movimiento reciente?
21. ¿Cómo están los mercados emergentes y Chile (IPSA, cobre, peso chileno)?
22. ¿Cómo está el petróleo y qué esperan la OPEP y la EIA?

## E. Por ETF (repetir para cada ticker de mercado/tickers.txt)
23. ¿Cuál es el ratio de gastos, los activos netos, el rendimiento por dividendo y la fecha del próximo dividendo de <TICKER>?
24. ¿Cuáles son sus 5 mayores posiciones y qué porcentaje del fondo representan?
25. ¿Qué noticias de la última semana afectan a <TICKER> o a su sector?

## F. Riesgos y calendario
26. ¿Cuáles son los principales riesgos que mencionan los analistas para el mercado de EE.UU. en las próximas 6 semanas?
27. ¿Qué eventos con fecha (Fed, datos, resultados de grandes empresas, vencimientos de opciones, feriados) hay hasta el 31 de diciembre?
28. ¿Cómo se ha comportado históricamente el S&P 500 en noviembre y diciembre (promedio y frecuencia de meses positivos)?
29. ¿Cuál fue la mayor caída del S&P 500 en un mes en los últimos 5 años y qué la causó?
30. ¿Cuál es el tipo de cambio USD/CLP hoy y su rango del último mes?
