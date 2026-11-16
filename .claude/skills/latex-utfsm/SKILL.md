---
name: "latex-utfsm"
description: "Usar al generar o corregir LaTeX con formato UTFSM: informes, guías de ejercicios resueltos, material de clases particulares, tablas booktabs/siunitx, TikZ, pgfplots, memorias con handcalcs, errores de compilación, paso de PDF a LaTeX y la revisión de compaginación y de figuras antes de entregar un PDF."
---

# LaTeX con el formato de la casa (UTFSM, Obras Civiles)

El formato, las cajas, las macros de dibujo y el revisor están en el paquete utfsm-calc (regla 3 de las instrucciones). No se reescribe el preámbulo ni se copian scripts al chat: se instala el paquete y se ejecuta.

## 1. Partir un documento
```
python -m utfsm_calc.plantilla trabajo --tipo informe      # o: guia | particular
```
Deja en `trabajo/` el archivo `utfsm.sty`, `img/` con los logos y un `main.tex` de partida. Si LaTeX no encuentra `spanish.ldf`: `apt-get update && apt-get install -y texlive-lang-spanish`.

El preámbulo es `\usepackage{utfsm}` más los paquetes propios del trabajo. Opciones: `particular` (clases particulares: sin logos, coma decimal, marca de agua de texto), `coma`, `sinmarca`, `stanli`.

`utfsm.sty` ya trae, y no se repite: geometría carta, babel con punto decimal, siunitx, booktabs, tcolorbox, TikZ y pgfplots, encabezado con logos, marca de agua, colores `usmazul`, `usmrojo`, `usmverde`, `usmgris`, y `\EI`, `\EA`, `\GJ`, `\dd`, `\gC`, `\pend`, `\completar{}`.

Datos y portada: `\datos{titulo=..., subtitulo=..., ramo=..., profesor=..., autor=..., fecha=..., pie=...}` y luego `\portada`. Los logos tienen tamaño fijo; no se cambian.

## 2. Nada cortado por un salto de página
Se logra al escribir, no al final.
- Cajas indivisibles: `enunciado{fuente}`, `resultado`, `nota`, `cuidado`, `caja{título}`. Una caja nueva se define con `\newtcolorbox{nombre}{utfsm=color}`. `breakable` se agrega solo a la caja que el revisor informe como más alta que la página.
- `juntos`: bloque invisible que no se parte. Va ahí todo lo que debe compartir página: un texto con su figura, una tabla con su lectura.
- `pregunta` con `alternativas` adentro: cada pregunta de selección múltiple queda con sus alternativas.
- `\begin{figure}` y `\begin{table}` sin opción de posición: quedan fijas donde se escriben, dentro de su punto. Tabla más larga que una página: `longtable`.
- Un título por línea del `.tex`. Sin `\newpage`, `\clearpage` ni `\vspace` para acomodar páginas: eso lo hace el revisor con líneas `\Needspace{...}% anticorte`, que no se editan a mano.

## 3. Figuras TikZ
- Nombrar las coordenadas al inicio (`\coordinate (A) at (0,0);`) y construir todo desde ellas; dimensiones con `\pgfmathsetmacro`.
- Usar las macros de la casa. Ubican cada etiqueta donde no puede pisar una flecha ni otra etiqueta:

| Macro | Dibuja |
|---|---|
| estilos `barra`, `eje`, `carga`, `reaccion`, `interna`, `etq`, `nudo`, `rotula` | barras, ejes, flechas por tipo, etiquetas, nudos |
| `\pic[rotate=90] at (A) {apoyo fijo};` también `apoyo movil`, `empotrado` | apoyos; el origen del pic es el punto de apoyo |
| `\cota[desp]{A}{B}{$4$ m}` | cota paralela a AB, a la izquierda del sentido A→B; `desp` negativo: al otro lado |
| `\cargadist[alto]{A}{B}{$q$}` | carga distribuida sobre AB, mismo criterio de lado |
| `\fuerzasale[estilo]{O}{ángulo}{$N$}`, `\fuerzaentra[estilo]{O}{ángulo}{$P$}` | fuerzas de un DCL, etiqueta en el extremo libre; largo `\utfsmR` |
| `\tramobarra{O}{ángulo}` | tramo gris de la barra bajo la flecha de un DCL; va antes de las fuerzas |
| `\angulo[radio]{A}{O}{B}{$45^\circ$}` | arco antihorario de OA a OB, texto fuera del arco |
| `\momento[estilo]{O}{inicio}{fin}{$M$}` | momento como arco, en un sector sin flechas |

- Toda etiqueta suelta lleva `etq`. Una etiqueta que debe ir sobre una línea lleva `fill=white`; si no, va a un lado (`above`, `left`), nunca `midway` a secas.
- Las etiquetas de nudos y apoyos van fuera del achurado y de la línea de base del apoyo.
- Un DCL muestra todas las barras que llegan al nudo; si una fuerza es nula, se dice en la leyenda. Paneles que se comparan: misma escala y misma caja (`\path[use as bounding box]`).
- Curvas (diagramas $N, V, M$, elásticas, perfiles, curvas S): se calculan en Python y entran como `\addplot table [row sep=\\] {...};`. No se dibujan con funciones aproximadas.
- pgfplots con `\begin{axis}[utfsm, ...]`: deja la leyenda arriba, fuera del eje. Sin `title`: el título es el `\caption`.
- Ejemplo completo que pasa el revisor: `ejemplo.tex`, junto a `utfsm.sty` en el paquete (`python -c "import utfsm_calc.plantilla as p; print(p.TEX_DIR)"`).

## 4. Guías de ejercicios resueltos y apuntes
1. Enunciado copiado tal cual de la fuente, dentro de `enunciado` junto con su figura. Lo que se lea de la figura y no esté en el texto va fuera, como nota.
2. La figura del enunciado se redibuja con todas las longitudes acotadas, cargas con magnitud, $EI$/$EA$ y apoyos. Los dibujos de planteamiento muestran la coordenada $x_i$ de cada tramo, con origen y sentido.
3. $M(x)$ por corte: DCL de una parte con $M$ en su sentido positivo y $\sum M_{\text{corte}}=0$ con cada fuerza por su brazo y su sentido de giro. Sin $(\mathbf r\times\mathbf F)_z$.
4. Cada descomposición de ángulos (barra inclinada, tramo curvo, nudo) lleva su DCL o triángulo acotado.
5. Desarrollo completo, sin saltar pasos: ecuación general, cada término que se anula con su razón, álgebra e integrales.

## 5. Números y tablas desde Python
El número del informe es el número verificado: el LaTeX se genera desde el mismo código.
- `handcalc = latex.hc_setup()` y `@handcalc(jupyter_display=False, precision=4)` sobre una función que termina en `return locals()`; devuelve `(latex, valores)`. El código va en un archivo `.py` (falla con heredoc) y cada asignación con espacios alrededor del `=`.
- Límites de handcalcs: una precisión por función (con 4 decimales, un valor menor que $5\cdot10^{-5}$ sale 0: pasar $EI$ ya formado o usar cm$^4$), sin notación científica, una sentencia por línea, sin unidades. Solo para memorias e informes, no para el chat.
- `latex.tabla_comparacion([(nombre, teorico, software)], caption, label)` y `latex.pendientes('main.tex')`.
- Matrices y vectores en negrita recta (`\mathbf{K}\mathbf{u}=\mathbf{F}`). Tablas con booktabs, sin líneas verticales, columnas `S`.

## 6. De PDF, capturas o transcripciones a LaTeX
Separar la derivación de los pasos de software, reconstruir cada diagrama en TikZ con las macros de la sección 3 y marcar con `\completar{}` lo que no se lea con certeza.

## 7. Errores de compilación
Ir al primer error del log. Revisar en orden: paquete faltante, llave o entorno sin cerrar, shorthands de babel dentro de TikZ, separador decimal en siunitx o pgfplots.

## 8. Revisión antes de entregar (obligatoria)
```
python -m utfsm_calc.compaginacion main.tex
```
Compila, mueve a la página siguiente todo punto numerado que quedó partido y cabe en una página, y revisa páginas y figuras. Termina en `RESULTADO: OK` o lista los problemas.

1. Corregir cada `PROBLEMA` y volver a correr:

| Mensaje | Corrección |
|---|---|
| ETIQUETAS SUPERPUESTAS, TRAZO SOBRE ETIQUETA, ETIQUETA SOBRE ACHURADO | redibujar con las macros de la sección 3 o mover la etiqueta a un sector libre |
| CAJA OPACA TAPA CURVAS | leyenda fuera del eje: estilo `utfsm` |
| CAJA PARTIDA | quitar `breakable` o usar una caja de la sección 2 |
| CONTENIDO SE SALE POR ABAJO | achicar la figura o tabla, o dar `breakable` a esa caja |
| LEYENDA separada, PÁGINA VACÍA | la figura o tabla no va en `figure`/`table`, o no cabe: reducir `width` o partirla |
| OVERFULL, TEXTO FUERA DEL MARGEN | `multline` o `split` en la ecuación; `tabularx` en la tabla |
| REFERENCIA o CITA INDEFINIDA | falta el `\label` o va antes del `\caption` |

2. Leer con la herramienta de imágenes todas las hojas `main-figuras-N.png` (cada figura a tamaño legible) y `main-paginas-N.png`. El revisor no ve lo siguiente, y se mira ahí: geometría, cargas o cotas distintas de la fuente; un arco de ángulo que cruza una flecha; figuras insertadas como imagen; orden de las páginas, encabezado y portada.
3. Repetir hasta `RESULTADO: OK` y revisión visual sin observaciones. Los `aviso` se leen y se decide: una página a medio llenar suele ser el costo de no partir un punto.
4. Entregar el PDF compilado (las imágenes van incrustadas, no hace falta zip). El `.tex` y un `.zip` con `main.tex`, `utfsm.sty`, `img/` y los archivos incluidos son opcionales: solo si Nicolás los pide. Informar en una línea: páginas, figuras revisadas y `RESULTADO`
