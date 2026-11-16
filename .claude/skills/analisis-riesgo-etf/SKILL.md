---
name: "analisis-riesgo-etf"
description: "Usar cuando Nicolás pida analizar ETFs, riesgo, probabilidades, tendencias o cuándo vender/comprar, con datos de mercado/ del repo Mis-cosas recolectados por la tablet."
---

# Análisis de riesgo de ETFs

## Principio
Estadística del pasado y distribuciones de retornos miden riesgo; no predicen el precio de un día. Nunca presentar una fecha "óptima" de venta basada en precio. Lo que sí tiene fecha: liquidación (T+1 en EE.UU.) y plazo de giro del bróker. No soy asesor financiero: dar información para que Nicolás decida.

## Flujo
1. Datos: la tablet (Antigravity) corre `sh mercado/descargar.sh` y llena `mercado/google_finance/AAAA-MM-DD.md` según `mercado/preguntas_google_finance.md`, y sube todo a una rama `datos/mercado-AAAAMMDD` (nunca a main). El contenedor de Claude no alcanza sitios financieros.
2. Leer la rama con git (clone parcial), correr `python3 mercado/analizar.py --datos <dir> --horizonte <días hábiles hasta la venta>`.
3. Para una posición concreta: Monte Carlo con t de Student (df=4) escalada a la volatilidad implícita (VIX/100 para S&P 500) y verificación con la fórmula lognormal cerrada. Reportar P5/P50/P95, P(pérdida), P(<−5%), P(<−10%), y comparar: vender hoy, escalonado, vender al final.
4. Noticias y agenda (FOMC, empleo, IPC/PCE, feriados): usarlas para explicar por qué la volatilidad puede cambiar, no para pronosticar dirección.

## Privacidad
Posiciones, saldos y montos de Nicolás nunca van al repo (público): se dan solo en el chat.

## Salida
Primero lo incómodo (riesgo real, límites del análisis). Luego tablas: rendimiento/riesgo, tendencia (0–4), distribución a horizonte con VaR/CVaR. Cerrar con las opciones y su trade-off, sin recomendar una con certeza.