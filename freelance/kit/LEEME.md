# Kit de cubicación v0

## Puesta en marcha (Windows)
1. Descomprimir el zip, por ejemplo en `C:\Users\<usuario>\Documents\kit_cubicacion`.
2. Abrir esa carpeta en el Explorador, escribir `cmd` en la barra de direcciones y presionar Enter.
   La consola debe mostrar la ruta de la carpeta, no `C:\WINDOWS\system32`.
3. Instalar: `python -m pip install ezdxf pytest`
4. Probar: `python -m pytest -q test_cubicar_dxf.py` (deben pasar 7 pruebas)
5. Medir el ejemplo: `python cubicar_dxf.py vivienda_ejemplo.dxf --salida cantidades.csv`

## Resultado esperado de vivienda_ejemplo.dxf (dibujado en mm)
| Capa | Área en planta [m2] | Cómo comprobarlo a mano |
|---|---|---|
| MUROS | 6.165 | 6 muros de 0.15 m de espesor: 9.0 + 9.0 + 6.3 + 6.3 + 6.3 + 4.2 = 41.1 m de largo |
| FUNDACIONES | 20.200 | 6 corridas de 0.50 m de ancho: 9.35 + 9.35 + 5.95 + 5.95 + 5.95 + 3.85 = 40.4 m |
| RADIER | 53.235 | 3 recintos: 4.35 x 6.30 + 4.20 x 3.15 + 4.20 x 3.00 |
Bloques en capa VANOS: 3 PUERTA_80 y 4 VENTANA_120.

## Con un plano propio
Exportar desde AutoCAD como DXF (DXFOUT) y correr:
`python cubicar_dxf.py plano.dxf --unidad mm --salida cantidades.csv`

Límites: mide líneas, arcos, círculos y polilíneas de forma exacta; elipses y splines por aproximación.
No mide sombreados ni la geometría dentro de bloques. No interpreta el plano: usted decide qué capa es qué partida.
