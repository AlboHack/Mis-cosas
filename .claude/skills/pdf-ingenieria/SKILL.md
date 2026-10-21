---
name: "pdf-ingenieria"
description: "Usar cuando Nicolás trabaje con PDF de sus ramos: armar la entrega final de un informe con anexos escaneados, limpiar o comprimir escaneos de cálculos a mano, extraer tablas de normas, catálogos o salidas de SAP2000, o pasar enunciados y apuntes a texto."
---

# PDF para trabajo de ingeniería civil (UTFSM)

Complementa a la skill oficial `pdf` (pypdf, pdfplumber, reportlab, qpdf, pdftotext, OCR). Leer esa skill para la mecánica de cada operación; esta define los flujos de Nicolás y cómo comprobar que el resultado es correcto. Si el PDF debe pasar a LaTeX, usar además latex-utfsm.

## Reglas generales
- Trabajar sobre copias; nunca modificar el archivo subido.
- Antes de entregar, renderizar las páginas afectadas (pdftoppm a 60-80 dpi, hoja de contacto) y mirarlas.
- Informar siempre: número de páginas, tamaño en MB y cualquier página dudosa.

## 1. Entrega final de un informe
Caso típico: informe compilado en LaTeX + hojas de cálculo manual escaneadas + capturas de software.
- Preferir incluir los escaneos dentro del LaTeX (anexos con `\includegraphics`) para que la numeración y los encabezados sean continuos. Unir PDF por separado (qpdf `--empty --pages`) solo si el curso pide un archivo con partes independientes.
- Verificar: orden de anexos igual al índice, páginas en orientación correcta, sin páginas en blanco, enlaces internos funcionando, tamaño bajo el límite de la plataforma (Aula/Moodle). Si excede, comprimir imágenes (Ghostscript `-dPDFSETTINGS=/ebook` o reescalar los JPG a ~150-200 dpi) y volver a revisar legibilidad.
- Revisar fuentes incrustadas con `pdffonts` si el curso exige impresión.

## 2. Escaneos de cálculos a mano
- Limpieza: corrección de fondo por canal (dividir cada canal por su fondo suavizado, gamma ~1.8) para eliminar tintes rosados o azules y sombras; recortar bordes; enderezar si está inclinado.
- Mantener la tinta legible: comparar antes/después a 100% de zoom en una zona con subíndices y exponentes.
- No usar OCR sobre manuscritos para extraer resultados: el error en dígitos es alto. Si hay que transcribir números de una hoja, leerlos visualmente y verificarlos recalculándolos en Python.

## 3. Tablas de normas, catálogos y software
Ejemplos: tablas de perfiles (área, I, W), coeficientes de NCh433 o NCh1537, tablas exportadas de SAP2000 (Joint Displacements, Element Forces).
- Extraer con pdfplumber (`extract_tables`) o, si es imagen, recortar y leer visualmente; exportar a CSV o xlsx.
- Verificar contra un juez independiente antes de usar los datos: recomputar una propiedad (p. ej. I de un perfil desde b, h, tf, tw), comprobar sumas o equilibrio (reacciones vs. cargas), o contrastar 2-3 filas con la fuente a la vista.
- Respetar unidades y notación originales; indicar coma o punto decimal.

## 4. Enunciados, pautas y apuntes a texto
- PDF con texto: pdftotext `-layout`. PDF escaneado: OCR (pdf2image + pytesseract con `-l spa`) y revisión manual de fórmulas, que el OCR suele romper.
- Las ecuaciones se reescriben a mano en LaTeX (latex-utfsm), no se copian del OCR.

## 5. Otros
- Separar un PDF largo (p. ej. certamenes anteriores por pregunta) con pypdf o qpdf por rangos.
- Marca de agua o logos del departamento: usar los archivos del proyecto (`Logo_UTFSM.png`, `Logo depa.png`) y aplicarlos con pypdf `merge_page` solo si no se puede hacer desde LaTeX.

## Cierre
Entregar el PDF con SendUserFile y una línea con páginas, tamaño y verificaciones hechas.