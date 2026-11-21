# Freelance: cubicación y presupuestos de obra

Carpeta del trabajo de fin de semana de Nicolás: cubicación y presupuestos APU de edificación menor desde planos y EETT, con cada cantidad verificada por dos métodos.

| Carpeta | Contenido |
|---|---|
| `cerebro/` | Grafo de conocimiento: 13 etapas (E00 literatura a E12 cierre), reglas con cláusula de norma, errores típicos con su chequeo y fuentes con estado. `CEREBRO.md` se genera desde `cerebro.py`; no se edita a mano. |
| `kit/` | Herramientas: `cubicar_dxf.py` (largos y áreas por capa desde DXF, 7 pruebas), `pdf_a_dxf.py` (PDF vectorial a DXF), `estilo.py` (formato y auditor de planillas), plantilla de cubicación y APU. Instrucciones en `kit/LEEME.md`. |
| `casos/sede-c/` | Caso de portafolio: Sede Social Tipo C, FSPR 2023. Cubicación independiente, conciliación con el presupuesto oficial e informe. |
| `casos/muestra1/` | Vivienda de ejemplo usada para probar el kit. |
| `perfiles/` | Borradores de perfiles para plataformas. No publicados. |

## Uso
```
pip install ezdxf openpyxl networkx pytest
python cerebro/cerebro.py validar                       # GRAFO: OK
python cerebro/cerebro.py literatura S_armada S_HA      # E00: qué normas pedir antes de ejecutar
python cerebro/cerebro.py partida fierro                # lista de control de una partida
python cerebro/cerebro.py exportar                      # regenera CEREBRO.md
python -m pytest -q kit/test_cubicar_dxf.py
python casos/sede-c/armar_excel_v6.py                   # planilla con hoja Control contra Python
```

## Reglas de esta carpeta
- El repositorio es público: aquí no van precios cobrados, datos de clientes, ni texto o PDF de normas. Las reglas del cerebro parafrasean la norma y citan la cláusula.
- Cada encargo parte por E00: listar la literatura que exigen sus sistemas constructivos y pedir lo que falte antes de calcular.
- Los documentos de un cliente no se suben; un caso solo entra como portafolio si sus insumos son públicos.
