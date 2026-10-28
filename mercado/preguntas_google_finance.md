# Recolección en Google Finance (Antigravity, navegador de la tablet)

Objetivo: datos blandos y de contexto que no vienen en los CSV de precios. Copiar valores **tal cual
aparecen**; si un dato no está visible escribir `N/D`. No interpretar, no resumir con opinión, no inventar.
Nada personal (posiciones, saldos, cuentas) en este archivo: el repo es público.

Archivo de salida: `mercado/google_finance/AAAA-MM-DD.md` con exactamente estas secciones.

## 1. Mercado (página principal de Google Finance y búsquedas directas)
| Indicador | Valor | Cambio día | Hora del dato |
|---|---|---|---|
| S&P 500 | | | |
| Nasdaq Composite | | | |
| Dow Jones | | | |
| VIX | | | |
| Rendimiento bono EE.UU. 10 años | | | |
| Índice dólar (DXY) | | | |
| USD/CLP | | | |
| Petróleo WTI | | | |
| Oro (spot) | | | |
| Bitcoin (USD) | | | |

## 2. Ficha por ETF (una fila por ticker de `mercado/tickers.txt`, página `google.com/finance/quote/<TICKER>:<BOLSA>`)
| ETF | Precio | Cierre anterior | Rango día | Rango 52 sem | Activos netos (AUM) | Ratio de gastos | Rendimiento dividendo | Volumen promedio |
|---|---|---|---|---|---|---|---|---|

## 3. Noticias por ETF y de mercado (últimos 7 días)
Para cada ETF y para "Mercado", hasta 5 titulares, del más reciente al más antiguo:
`- [AAAA-MM-DD] Fuente | Titular exacto | URL`

## 4. Agenda (búsqueda en Google Finance / noticias)
Fechas y hora (Chile) de los próximos eventos hasta el 15 de diciembre, con la fuente:
- Reuniones de la Fed (FOMC) y publicación de minutas
- Informe de empleo de EE.UU. (nóminas no agrícolas)
- IPC (CPI) y PCE de EE.UU.
- Feriados y medias jornadas de la bolsa de EE.UU. (Acción de Gracias)
- Resultados trimestrales de las 5 mayores empresas del S&P 500, si caen en el período
