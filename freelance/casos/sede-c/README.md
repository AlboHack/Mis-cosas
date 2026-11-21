# Caso Sede Social Tipo C (FSPR 2023)

Ejercicio de portafolio, no oficial: cubicación independiente de la sede tipo C en albañilería armada y conciliación con el presupuesto publicado por el Fondo Social Presidente de la República.

## Insumos públicos (no se copian aquí)
- Anexo 5.3, Planimetría sede tipo C: https://fspr.interior.gob.cl/media/2023/03/ANEXO-5.3-Planimetria-sede-tipo-C-albañileria-armada.pdf
- Anexo 3.3, Presupuesto: https://fspr.interior.gob.cl/media/2023/03/Ptto.-3.3.-Albañileria.pdf
- Anexo 4.3, Especificaciones técnicas (misma publicación del FSPR 2023).

## Archivos
| Archivo | Qué es |
|---|---|
| `sedeC_planta.dxf` | Planta extraída del PDF vectorial con `kit/pdf_a_dxf.py`, escalada con la cota de 12.85 m. |
| `cubicacion_sedeC.py` | Geometría y cantidades desde el DXF (genera `resultados.json`). |
| `correcciones.py` | Referencia en Python, independiente de la planilla (versiones v4 a v6 de los criterios). |
| `armar_excel_v6.py` | Arma `SedeC_cubicacion_v6.xlsx`: Resumen, Conciliacion, Datos, Cubicacion, Comparacion y Control (22 controles contra Python). |
| `informe/` | Fuente LaTeX del informe; `generar_v3.py` escribe las tablas desde Python. Compila con `utfsm.sty` (opción `sinmarca`) de `utfsm-calc`. |
| `SedeC_informe_v5.pdf` | Informe de 6 páginas. |

## Resultado
10 de 20 partidas quedan dentro de ±5 % del presupuesto oficial; cada diferencia mayor tiene causa asignada (criterio de medición o error del presupuesto). Pendientes: escalerilla de 4.2 mm según dato comercial (la planilla usa 4 mm), volumen del hormigón de relleno de huecos (NCh1928 7.1) y la contradicción de las EETT en la cadena (6φ10 en 3.4, φ12 en 3.5).
