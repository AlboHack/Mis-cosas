"""Cerebro de cubicación y presupuesto: grafo de conocimiento tipado.

Nodos: Etapa, Sistema, Partida, Regla, Error, Chequeo, Herramienta, Fuente, Estudio.
Aristas: precede (Etapa->Etapa), aplica_a (Regla->Partida), cita (Regla|Error|Chequeo->Fuente),
         se_aplica_en (Regla->Etapa), ocurre_en (Error->Etapa), afecta (Error->Partida),
         previene (Chequeo->Error), se_hace_en (Chequeo->Etapa), usa (Etapa->Herramienta),
         estudia (Estudio->Fuente), exige (Sistema->Regla).
Uso:
  python cerebro.py validar            invariantes del grafo (código 1 si falla)
  python cerebro.py exportar           grafo.json + CEREBRO.md
  python cerebro.py partida albanileria   lista de control de una partida
"""
import json
import sys
from pathlib import Path
import networkx as nx

PV = "[Por verificar]"
N = []   # (id, tipo, texto, extra)
A = []   # (origen, destino, relacion)


def n(i, tipo, texto, **kw):
    N.append((i, tipo, texto, kw))


def a(o, d, r):
    A.append((o, d, r))


# ----------------------------------------------------------------- fuentes
# (texto, url, estado): "vista" = texto de la norma leído; "parcial" = copia incompleta; "secundaria" = resumen de terceros
F = {
    "F_NCh353": ("NCh353.Of2000 Construcción - Cubicación de obras de edificación - Requisitos (texto completo leído, copia escaneada)", "", "vista"),
    "F_NCh1156": ("NCh1156/1 a /3.Of1999 Especificaciones técnicas - Ordenación y designación de partidas (partes 1, 2 y 3 leídas)", "", "vista"),
    "F_NCh169": ("NCh169.Of2001 Ladrillos cerámicos - Clasificación y requisitos", "", "vista"),
    "F_NCh204": ("NCh204:2020 Barras laminadas en caliente para hormigón armado (tabla 4 masas nominales; 4.3.2 largos; 4.6 tolerancias)", "", "vista"),
    "F_NCh2123": ("NCh2123.Of1997 Mod. 2003 Albañilería confinada (copia parcial: solo cláusula 5 Materiales y Anexo B)", "", "parcial"),
    "F_NCh1928": ("NCh1928.Of1993 Mod. 2009 Albañilería armada (copia de 54 ppi leída página a página: cláusulas 6, 7 y Anexo A; la resistencia del hormigón de relleno en A.4 no se lee)", "", "vista"),
    "F_ACI318": ("ACI 318-19 Building Code Requirements for Structural Concrete (cap. 25: 25.3 ganchos, 25.4 desarrollo, 25.5 empalmes; copia en unidades inch-pound)", "", "vista"),
    "F_NCh2123_inacap": ("INACAP, apunte de albañilería confinada que resume NCh2123 (fuente secundaria; texto escaneado de baja calidad)", "", "secundaria"),
    "F_fichaEscalerilla": ("Ficha técnica de escalerilla de un fabricante (masa por metro y ancho según espesor de muro)", "", "falta"),
    "F_NCh430": ("NCh430-2007 Hormigón armado (solo las modificaciones nacionales al ACI 318-05; anclajes y empalmes se leyeron en ACI 318-19, no en la versión 318-05 que adopta)", "", "parcial"),
    "F_NCh170": ("NCh170:2016 Hormigón - Requisitos generales (grados G por resistencia cilíndrica; designación 5.2)", "", "vista"),
    "F_NCh2256": ("NCh2256/1.Of2001 Morteros - Requisitos generales (grados M; 7.1 mortero de junta)", "", "vista"),
    "F_NCh2257": ("NCh2257/3.Of1996 Morteros - Consistencia por asentamiento de cono (método de ensayo)", "", "vista"),
    "F_Solminihac": ("Solminihac y Thenoux, Procesos y Técnicas de Construcción, 5ª ed., Ediciones UC (cap. 5 presupuesto; cap. 10 albañilería; 14.3 techumbre)", "", "vista"),
    "F_cursoInsp": ("Curso 'Capacitación Inspectores Albañilería' (resume NCh1928 y NCh2123; fuente secundaria)", "", "secundaria"),
    "F_guiaMineduc": ("Mineduc, guía 'Cubicación de materiales e insumos' (resume NCh353; reemplazada por el texto de la norma)",
                      "https://www.curriculumnacional.cl/614/articles-228610_recurso_6.docx", "secundaria"),
    "F_CDT_tol": ("CDT, Manual de tolerancias para edificaciones", "https://cdt.cl/download/76541", "secundaria"),
    "F_MINVU_precios": ("MINVU, Tabla de precios referenciales DS27 por región (UF por partida)",
                        "https://www.minvu.gob.cl/wp-content/uploads/2026/09/TABLA-DE-PRECIOS-REFERENCIALES-DS27-REGION-DE-AYSEN-2026.pdf", "secundaria"),
    "F_tesisPerdidas": ("Hidalgo (2008), U. de Chile: pérdidas de materiales en edificación en extensión", "https://repositorio.uchile.cl/handle/2250/104976", "secundaria"),
    "F_UDD_brechas": ("Mancilla (2023), UDD: brechas presupuestarias en proyectos de construcción",
                      "https://repositorio.udd.cl/bitstreams/685a8b7e-a239-4bf3-bbee-9ae6817c5ca8/download", "secundaria"),
    "F_C3D_QTO": ("Mastering AutoCAD Civil 3D (Sybex), cap. Quantity Takeoff; Autodesk Help QTO",
                  "https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-Tutorials/files/GUID-E870AEEA-4E45-480B-9DA3-BE6846A41A8F.htm", "secundaria"),
    "F_ACAD_area": ("AutoCAD: MEASUREGEOM, AREA/LIST, hatch con campos, DATAEXTRACTION",
                    "https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-LT/files/GUID-5D5B0EE1-DD90-47AE-8A55-642FBFF5E4E4.htm", "secundaria"),
    "F_FSPR2019": ("Presupuestos FSPR 2019: escalerilla 1.03 a 1.13 kg/m² de muro",
                   "https://subinterior-2018.interior.gob.cl/media/2019/02/ANEXO-3.1-PRESUPUESTO-SEDE-SOCIAL.pdf", "secundaria"),
    "F_SedeC": ("Caso propio: Sede C FSPR 2023 (revisión en frío y conciliación)", "", "caso"),
}
for k, (t, u, est) in F.items():
    n(k, "Fuente", t, url=u, estado=est)

# ----------------------------------------------------------------- etapas
etapas = [
    ("E00", "Literatura y normas disponibles", "Por cada sistema constructivo del encargo, listar las normas y fuentes que citan sus reglas y su estado (python cerebro.py literatura <sistemas>); pedir a Nicolás lo que esté parcial, secundario o falte, y esperar su respuesta antes de ejecutar"),
    ("E01", "Alcance y encargo", "Qué se entrega, para quién, insumos, plazo y modalidad de contrato (suma alzada, serie de precios, administración); versión y fecha de cada documento"),
    ("E02", "Revisión de insumos", "Cotas, escalas, coherencia plano-EETT-itemizado; contradicciones a una lista de consultas"),
    ("E03", "Marco normativo y designaciones", "Sistema constructivo, normas que lo rigen, designación vigente de hormigón, acero, ladrillo y mortero"),
    ("E04", "Itemizado", "Partidas ordenadas según NCh1156, medibles, presupuestables y controlables, con unidad según EETT o NCh353"),
    ("E05", "Extracción de geometría", "PDF vectorial o DWG a DXF; calibrar escala con dos o más cotas por vista"),
    ("E06", "Datos de entrada", "Cada dato una sola vez, con unidad, base (M/E/I/S) y fuente"),
    ("E07", "Cubicación por partida", "Cantidades según NCh353, por ejes y sin agrupar; sin pérdidas"),
    ("E08", "Verificación independiente", "Segundo método por partida crítica; recubicación ciega; planilla contra script"),
    ("E09", "Análisis de precios unitarios", "Materiales puestos en obra con pérdidas, mano de obra con rendimientos y leyes sociales, equipos y otros"),
    ("E10", "Presupuesto", "Costo directo, gastos generales, imprevistos, utilidad, IVA; partidas faltantes u omitidas al final"),
    ("E11", "Conciliación con referencia", "Si existe un presupuesto previo: causa de cada diferencia, sin ajustar hacia la referencia"),
    ("E12", "Entregable y cierre", "Planilla con controles, informe, consultas al proyectista; boleta, cobro y registro de errores"),
]
for i, (k, t, d) in enumerate(etapas):
    n(k, "Etapa", t, detalle=d, orden=i + 1)
    if i:
        a(etapas[i - 1][0], k, "precede")

# ----------------------------------------------------------------- sistemas constructivos
sistemas = {"S_armada": "Albañilería armada", "S_confinada": "Albañilería confinada", "S_HA": "Hormigón armado",
            "S_techo": "Techumbre y cubierta", "S_termin": "Terminaciones", "S_tierra": "Movimiento de tierras"}
for k, t in sistemas.items():
    n(k, "Sistema", t)

# ----------------------------------------------------------------- partidas
partidas = {"P_excav": "Excavaciones y rellenos", "P_horm": "Hormigones (fundación, sobrecimiento, cadena)",
            "P_radier": "Radieres y emplantillados", "P_mold": "Moldajes", "P_fierro": "Enfierraduras, escalerillas y tensores",
            "P_alb": "Albañilería", "P_techo": "Techumbre y cubierta", "P_hoja": "Hojalatería (canales, bajadas, forros)",
            "P_ceram": "Cerámicos y revestimientos", "P_piso_cielo": "Pavimentos y cielos", "P_estuco": "Estucos y pinturas"}
for k, t in partidas.items():
    n(k, "Partida", t)

# ----------------------------------------------------------------- reglas: (id, texto, partidas, etapas, fuentes, sistemas)
reglas = [
    # Cubicación NCh353 (texto leído)
    ("R01", "NCh353 1.3: las pérdidas (despuntes, mortero caído, envases rotos, excesos) no van en la cubicación sino en el rendimiento del precio unitario",
     ["P_alb", "P_fierro", "P_horm"], ["E07", "E09"], ["F_NCh353"], []),
    ("R02", "NCh353 4.4: lo que pertenece a la vez a más de un elemento se mide una sola vez (esquinas, encuentros, cruces)",
     ["P_alb", "P_horm", "P_fierro"], ["E07"], ["F_NCh353"], []),
    ("R03", "NCh353 5.1.5 y Tabla 1: sobreancho de excavación solo si la fundación lleva moldaje (0.20 m por lado hasta 0.5 m de alto; 0.40 hasta 1.0; 0.50 hasta 1.5; 0.70 hasta 2.5; 0.80 sobre 2.5); con talud, 0.10 m por lado (5.1.6); zanja de cañería: diámetro exterior + 0.45 m (5.1.7)",
     ["P_excav"], ["E07"], ["F_NCh353"], ["S_tierra"]),
    ("R04", "NCh353 5.2 y Tabla 2: transporte de excedentes = volumen en banco + esponjamiento (10, 15, 25, 30 % o más según terreno); el asentamiento en el transporte no se descuenta",
     ["P_excav"], ["E07", "E09"], ["F_NCh353"], ["S_tierra"]),
    ("R05", "NCh353 5.3.1: rellenos por volumen neto rellenado; rellenos de excavaciones de fundación en partida separada de los rellenos de piso; compactación estimable con Tabla 3",
     ["P_excav"], ["E07"], ["F_NCh353"], ["S_tierra"]),
    ("R06", "NCh353 5.4.1: escarpes por superficie explanada",
     ["P_excav"], ["E07"], ["F_NCh353"], ["S_tierra"]),
    ("R07", "NCh353 6.1: hormigón por volumen sin descontar armaduras ni tuberías hasta 0.25 m; se descuentan aberturas mayores a 0.05 m²; partidas separadas por tipo de hormigón, elemento y moldaje",
     ["P_horm"], ["E07"], ["F_NCh353"], ["S_HA"]),
    ("R08", "NCh353 6.2.1 a 6.2.3: barras por masa nominal x largo total (resistentes, repartición, suples y estribos); por diámetro y largo comercial indicar número de barras y masa; barras de más de 12 m aparte",
     ["P_fierro"], ["E07"], ["F_NCh353", "F_NCh204"], ["S_HA", "S_armada", "S_confinada"]),
    ("R09", "NCh353 6.2.4 y 6.2.5: +5 % sobre la masa medida (4 % trabas, patas, guías, elementos de posición y despuntes; 1 % sobredimensión), salvo que el proyecto cuantifique trabas y patas",
     ["P_fierro"], ["E07"], ["F_NCh353"], ["S_HA", "S_armada", "S_confinada"]),
    ("R10", "NCh353 6.2.7 y 6.2.8: verticales de pilares y muros empalmadas 40 d en el piso superior; penetración en fundaciones no detallada = 40 d (la norma impresa dice 'quedando 10,1 m sobre el fondo', errata evidente: interpretar 0.1 m) [Por verificar la errata]",
     ["P_fierro"], ["E07"], ["F_NCh353"], ["S_armada", "S_confinada", "S_HA"]),
    ("R11", "NCh353 6.2.6 y 6.2.10: alambre de amarre en el precio unitario; enfierradura subcontratada a suma alzada: +1 % sobre cubicación de planos",
     ["P_fierro"], ["E09"], ["F_NCh353"], ["S_HA"]),
    ("R12", "NCh353 6.3: emplantillados por superficie o volumen indicando espesor; fundaciones por volumen real; radier por superficie con espesor",
     ["P_radier", "P_horm"], ["E07"], ["F_NCh353"], ["S_HA"]),
    ("R13", "NCh353 6.4 a 6.6 y 6.10.2: alturas de muros entre niveles superiores de losas o hasta el fondo de viga; vigas por luz libre; intersecciones en orden 1° pilares y muros, 2° vigas, 3° losas",
     ["P_horm"], ["E07"], ["F_NCh353"], ["S_HA"]),
    ("R14", "NCh353 7.1 a 7.3: cadenas por volumen real medido como vigas; pilares de refuerzo sin el hormigón entre endentados; apoyo de dintel no indicado = 0.30 m por extremo",
     ["P_horm"], ["E07"], ["F_NCh353"], ["S_armada", "S_confinada"]),
    ("R15", "NCh353 8.1.1 y Tabla 4.a: albañilería por superficie efectiva; vanos en ladrillo a máquina: <1.5 m² 0 % (50 % con pilar), 1.5 a 3.0 m² 50 % (75 %), >3.0 m² 100 %. Tabla 4.b para ladrillo a mano",
     ["P_alb"], ["E07"], ["F_NCh353"], ["S_armada", "S_confinada"]),
    ("R16", "NCh353 8.1.3: se descuentan de la albañilería los espacios de cadenas, dinteles, vigas y pilares embutidos; muros endentados desde el ladrillo más saliente",
     ["P_alb"], ["E07"], ["F_NCh353"], ["S_armada", "S_confinada"]),
    ("R17", "NCh353 8.1.6: refuerzos de acero en las juntas entre hiladas (escalerilla) se incluyen en la partida de albañilería, no en fierro",
     ["P_alb", "P_fierro"], ["E04", "E07"], ["F_NCh353"], ["S_armada", "S_confinada"]),
    ("R18", "NCh353 8.1.2 y 8.1.4: partidas separadas por naturaleza y espesor; la mano de obra de formar vanos de 2 m² o más va en el precio unitario del muro",
     ["P_alb"], ["E04", "E09"], ["F_NCh353"], ["S_armada", "S_confinada"]),
    ("R19", "NCh353 9.1.1: tabiques de madera por longitud con altura, sin descontar vanos menores a 3 m² si el dintel es del mismo material",
     ["P_alb"], ["E07"], ["F_NCh353"], ["S_termin"]),
    ("R20", "NCh353 9.5 y 9.6: estructura de techumbre por superficie proyectada horizontal (incluye canes de una pieza); aleros por ml con ancho; forros, canes a la vista y frontones aparte",
     ["P_techo"], ["E07"], ["F_NCh353", "F_Solminihac"], ["S_techo"]),
    ("R21", "NCh353 13: cubiertas por superficie de vertientes sin traslapos; incluye elementos intermedios entre cubierta y estructura (costaneras, entablado)",
     ["P_techo"], ["E07"], ["F_NCh353", "F_Solminihac"], ["S_techo"]),
    ("R22", "NCh353 12: caballetes, limatesas y forros por longitud sin traslapos y con ancho desarrollado; canales y bajadas por longitud incluyendo curvas, tes y ves; anclajes en el precio",
     ["P_hoja"], ["E07"], ["F_NCh353"], ["S_techo"]),
    ("R23", "NCh353 14: aislación e impermeabilización en láminas por superficie con retornos y sin traslapos; vanos <=1 m² no se descuentan, mayores se descuentan en el exceso",
     ["P_techo"], ["E07"], ["F_NCh353"], ["S_techo", "S_termin"]),
    ("R24", "NCh353 15 y 16: pavimentos y cielos por superficie efectiva entre paramentos terminados; cielo incluye sobre vanos sin dintel; radier en partida aparte del pavimento",
     ["P_piso_cielo"], ["E07"], ["F_NCh353"], ["S_termin"]),
    ("R25", "NCh353 18.2: cerámicos por superficie a la vista, sin descontar superficies no revestidas menores a 0.5 m²; biselado 0.5 ml por m² en el APU",
     ["P_ceram"], ["E07", "E09"], ["F_NCh353"], ["S_termin"]),
    ("R26", "NCh353 11: estucos por superficie proyectada; espesor supuesto 2.5 cm salvo EETT; descuento de vanos según 11.3",
     ["P_estuco"], ["E07"], ["F_NCh353"], ["S_termin"]),
    ("R27", "NCh353 24: pinturas por superficie recubierta, partida por clase de pintura",
     ["P_estuco"], ["E07"], ["F_NCh353"], ["S_termin"]),
    ("R28", "NCh353 Anexo A: el APU se desglosa en materiales, mano de obra (rendimiento y leyes sociales), herramientas o equipos menores y subcontratos",
     ["P_alb", "P_horm"], ["E09"], ["F_NCh353", "F_Solminihac"], []),
    ("R29", "Moldaje por superficie de contacto con el hormigón, en partida por elemento (NCh353 6.1.4); incluye fondos bajo dinteles y tapas de extremos; madera tradicional ~3 usos (hasta 5)",
     ["P_mold"], ["E07", "E09"], ["F_NCh353", "F_Solminihac", "F_SedeC"], ["S_HA", "S_armada"]),
    # Itemizado NCh1156
    ("R30", "NCh1156/1 a /3: secciones 0 informaciones generales, 1 gastos adicionales, obras provisionales y trabajos previos, 2 obras de construcción (2/1 obra gruesa, 2/2 terminaciones), 3 instalaciones, 4 obras complementarias; la medición de cada partida remite a NCh353 (7.8)",
     ["P_alb", "P_horm"], ["E04"], ["F_NCh1156", "F_Solminihac"], []),
    ("R31", "Partidas medibles, presupuestables y controlables, con código y unidad; una partida omitida es pérdida para el contratista",
     ["P_alb", "P_horm"], ["E04", "E10"], ["F_Solminihac"], []),
    # Materiales y designaciones
    ("R32", "NCh204:2020: masas nominales 6 mm 0.222, 8 mm 0.395, 10 mm 0.617, 12 mm 0.888, 16 mm 1.58 kg/m; largos normales 6 y 12 m; diámetros hasta 16 mm en rollo; tolerancia de masa ±3.5 %",
     ["P_fierro"], ["E03", "E07"], ["F_NCh204"], ["S_HA", "S_armada", "S_confinada"]),
    ("R33", "NCh170:2016: grados G05 a G60 por resistencia cilíndrica fc' (MPa); la designación incluye grado, fracción defectuosa, tamaño máximo de árido y asentamiento. EETT con 'H-xx' usan la designación antigua: pedir el grado G equivalente al proveedor [Por verificar la equivalencia]",
     ["P_horm"], ["E03", "E09"], ["F_NCh170"], ["S_HA"]),
    ("R34", "NCh169.Of2001: clases MqM, MqP, MqH y grados 1, 2, 3; tolerancias largo ±5 mm, ancho y alto ±3 mm. Armada exige grado 1 o 2 [Por verificar en NCh1928]; confinada exige MqM o MqP (NCh2123 5.2.1)",
     ["P_alb"], ["E03"], ["F_NCh169", "F_NCh2123", "F_cursoInsp"], ["S_armada", "S_confinada"]),
    ("R35", "NCh2256/1.Of2001: grados de mortero M0.5 a M30; mortero de junta con Dn de arena <= 1/3 de la junta, consistencia 180 a 220 mm, resistencia según NCh1928 o NCh2123",
     ["P_alb"], ["E03", "E09"], ["F_NCh2256"], ["S_armada", "S_confinada"]),
    ("R36", "Junta de albañilería de 10 a 15 mm (rango de validez de NCh2123 y NCh1928): fija el escantillón y el número de hiladas y de filas de escalerilla",
     ["P_alb", "P_fierro"], ["E03", "E07"], ["F_NCh2123", "F_cursoInsp", "F_Solminihac"], ["S_armada", "S_confinada"]),
    # Mínimos de diseño para detectar omisiones (no para rediseñar)
    ("R37", "NCh1928 6.4.1.1 y 6.4.3.2 a 6.4.3.5, 6.4.3.8: espesor >= máx(1/25 de la menor dimensión libre; 14 cm); cuantía >= 0.06 % por dirección y >= 0.15 % total, contando solo barras que recorren todo el ancho o alto; vertical >= 8 mm a <= 6e y <= 120 cm; en cada borde libre y encuentro al menos una barra de 12 mm; verticales fijadas cada <= 300 d y <= 3 m",
     ["P_fierro"], ["E02", "E07"], ["F_NCh1928", "F_cursoInsp"], ["S_armada"]),
    ("R38", "NCh1928 6.1.2 y 6.4.3.6: armadura de junta de diámetro <= mitad del espesor de la junta; refuerzo horizontal en el remate de cimientos, base y remate de vanos, nivel de piso, techo y parapetos; verticales >= 10 mm a cada lado de vano, prolongadas 60 cm más allá de las esquinas",
     ["P_fierro", "P_alb"], ["E02", "E07"], ["F_NCh1928", "F_cursoInsp"], ["S_armada"]),
    ("R39", "NCh1928 A.3.2 y A.4: mortero fm >= 10 MPa (fracción defectuosa 4 %), retentividad >= 70 %; sin ensayos, 1:0.22:4 en peso (cemento:cal:arena) con cono <= 18 cm; árido del hormigón de relleno <= 12.5 mm; resistencia del relleno 17.5 MPa [Por verificar: cifra del curso, ilegible en A.4]",
     ["P_alb"], ["E03", "E09"], ["F_NCh1928", "F_cursoInsp", "F_Solminihac"], ["S_armada"]),
    ("R40", "Anclajes y empalmes: NCh1928 6.1.5 traslapo >= 40 veces el menor diámetro; en huecos menores que 6 veces el diámetro mayor solo empalme soldado, mecánico o traslapo dentro de la cadena; 6.1.6 anclajes según hormigón armado. ACI 318-19 25.4.2.3: ld = fy ψt ψe ψg db / (2.1 λ √f'c) para barras <= 19 mm con espaciamiento y recubrimiento suficientes, >= 300 mm; 25.5.2.1 traslapo clase B = 1.3 ld; Tabla 25.3.1 ganchos de 90° y 180° con diámetro interior 6 db. A440-280H con G25: ld = 27 d y clase B = 35 d (40 d cubre); A630-420H con G25: ld = 40 d y clase B = 52 d (40 d no alcanza). NCh430 adopta ACI 318-05 [Por verificar que la ecuación coincide]",
     ["P_fierro"], ["E07"], ["F_NCh1928", "F_ACI318", "F_NCh430", "F_Solminihac"], ["S_HA", "S_armada", "S_confinada"]),
    # Presupuesto (Solminihac cap. 5)
    ("R41", "Presupuesto de venta = costo directo + gastos generales de obra + gastos generales indirectos (financiero, garantías, oficina central) + imprevistos + utilidad + IVA",
     ["P_alb", "P_horm"], ["E10"], ["F_Solminihac"], []),
    ("R42", "Costo de materiales puesto en obra, cotizado por proveedor; incluye pérdidas por robo, mal almacenamiento y transporte; P.U. = total de la partida / cantidad",
     ["P_alb", "P_horm"], ["E09"], ["F_Solminihac", "F_tesisPerdidas"], []),
    ("R43", "Mano de obra: rendimiento real (trabajo productivo, contributorio y no contributorio) y costo con leyes sociales",
     ["P_alb", "P_horm"], ["E09"], ["F_Solminihac"], []),
    ("R44", "Visita a terreno y lista de antecedentes (accesos, agua, energía, botaderos, suelo, napa, mano de obra local) antes de cerrar precios",
     ["P_excav"], ["E01", "E09"], ["F_Solminihac"], []),
    ("R45", "Incertidumbre: por partida relevante, valores optimista, más probable y pesimista; simular o usar PERT para el rango del costo",
     ["P_alb", "P_horm"], ["E10"], ["F_Solminihac", "F_UDD_brechas"], []),
    ("R46", "Precios de referencia: tabla MINVU DS27 de la región y cotizaciones; justificar cada P.U.",
     ["P_alb", "P_horm"], ["E09"], ["F_MINVU_precios", "F_Solminihac"], []),
    ("R47", "Las EETT fijan el alcance de cada partida (dónde va, qué incluye) y prevalecen sobre la costumbre",
     ["P_ceram", "P_excav"], ["E02", "E07"], ["F_SedeC", "F_NCh1156"], []),
    ("R48", "Plano sin cotas no se cubica: se consulta; trabajar por ejes y pisos sin agrupar",
     ["P_alb", "P_horm"], ["E02", "E05"], ["F_guiaMineduc"], []),
    ("R49", "NCh1928 7.1: todo hueco que aloja armadura se llena con hormigón de relleno, por etapas de altura limitada según el hueco (5 cm: 30 cm; 8 cm: 120 cm; >= 12 cm: 240 cm). Se cubica el volumen de huecos rellenos en m³, como partida propia o declarado dentro del APU de albañilería",
     ["P_alb", "P_horm"], ["E03", "E07", "E09"], ["F_NCh1928"], ["S_armada"]),
    ("R50", "Albañilería confinada (NCh2123 vía apunte INACAP) [Por verificar]: espesor >= 14 cm con ladrillo a máquina y 15 cm artesanal; paño <= 12.5 m² y <= 6 m entre pilares; pilares en bordes libres e intersecciones; cadenas a nivel de piso y techo de ancho >= espesor del muro; mortero 5 MPa artesanal y 10 MPa a máquina",
     ["P_alb", "P_horm", "P_fierro"], ["E02"], ["F_NCh2123_inacap", "F_NCh2123"], ["S_confinada"]),
    ("R51", "Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]",
     list(partidas), ["E00"], ["F_SedeC"], list(sistemas)),
]
for k, t, ps, es, fs, ss in reglas:
    n(k, "Regla", t)
    for p in ps:
        a(k, p, "aplica_a")
    for e in es:
        a(k, e, "se_aplica_en")
    for f in fs:
        a(k, f, "cita")
    for s_ in ss:
        a(s_, k, "exige")

# ----------------------------------------------------------------- errores típicos y su chequeo
errores = [
    ("X01", "Doble conteo en esquinas y encuentros en T", "E07", ["P_alb", "P_fierro"], "C01",
     "Muro pasante entero y el que llega cortado en la cara (NCh353 4.4); contraste con área de muros / espesor", ["F_NCh353", "F_SedeC"]),
    ("X02", "Vanos descontados al 100 % o no descontados, sin la Tabla 4 de NCh353", "E07", ["P_alb"], "C02",
     "Lista de vanos con área y si llevan pilar; aplicar NCh353 Tabla 4.a fila por fila", ["F_NCh353", "F_SedeC"]),
    ("X03", "Escala mal calibrada o asumida (vistas a escalas distintas en la misma lámina)", "E05", ["P_alb", "P_techo"], "C03",
     "Calibrar cada vista con dos cotas independientes y declarar el factor", ["F_SedeC"]),
    ("X04", "Unidad equivocada (m² con valor de m³) o magnitud incoherente", "E10", ["P_excav"], "C04",
     "Unidad contra magnitud: espesor implícito = volumen / área", ["F_SedeC"]),
    ("X05", "Cifra copiada entre partidas (canales = bajadas = forros)", "E10", ["P_hoja"], "C05",
     "Buscar valores repetidos en el itemizado y justificar cada uno", ["F_SedeC"]),
    ("X06", "Alcance de EETT ignorado (cerámica en todo el interior; relleno sobre la huella)", "E02", ["P_ceram", "P_excav"], "C06",
     "Leer la EETT de cada partida antes de cubicarla y anotar su alcance en Datos", ["F_SedeC"]),
    ("X07", "Pérdidas metidas en la cubicación, o criterio confundido con error", "E07", ["P_alb", "P_fierro"], "C07",
     "Cantidad neta en Cubicación (NCh353 1.3); pérdidas solo en APU; conciliación declara el criterio", ["F_NCh353", "F_tesisPerdidas"]),
    ("X08", "Masa por metro mal tomada (escalerilla al doble)", "E07", ["P_fierro"], "C08",
     "Masa = π/4 d² ρ por alambre; contrastar kg/m² de muro con referencias", ["F_FSPR2019", "F_SedeC"]),
    ("X09", "Armadura sin estribos, traslapos, patas ni penetración en fundación", "E07", ["P_fierro"], "C09",
     "kg/m teórico del elemento con NCh353 6.2.4 a 6.2.8 contra la cantidad", ["F_NCh353", "F_SedeC"]),
    ("X10", "Coincidencia artificial: calzar con la referencia", "E11", ["P_excav", "P_ceram"], "C10",
     "Recubicación ciega antes de mirar la referencia; coincidencias exactas se revisan igual", ["F_SedeC"]),
    ("X11", "Verificación circular: supuesto elegido porque coincide", "E08", ["P_horm"], "C11",
     "Un supuesto nunca se justifica por coincidir; marcarlo S o I y dar su sensibilidad", ["F_SedeC"]),
    ("X12", "Error de fórmula o de rango en la planilla", "E08", ["P_alb", "P_horm"], "C12",
     "Hoja Control planilla contra script de Python; recalc sin errores; auditor de estilo", ["F_SedeC"]),
    ("X13", "Rótulo del plano contradice el dibujo (pendiente 60 % rotulada, 40 % dibujada)", "E02", ["P_techo"], "C13",
     "Medir en corte y elevación; reportar la contradicción como consulta", ["F_SedeC"]),
    ("X14", "Elemento exigido por EETT o norma sin partida (armadura de sobrecimiento; refuerzo horizontal en base de vanos)", "E10", ["P_fierro", "P_horm"], "C14",
     "Recorrer EETT capítulo por capítulo y los mínimos de R37-R38 contra el itemizado; lo que falte va a partidas omitidas", ["F_NCh353", "F_cursoInsp", "F_SedeC"]),
    ("X15", "Plano o EETT en versión desactualizada", "E01", ["P_alb"], "C15",
     "Registrar versión y fecha de cada documento en Datos", ["F_Solminihac"]),
    ("X16", "Brecha presupuestaria por alcance mal definido", "E01", ["P_horm"], "C16",
     "Lista de supuestos y exclusiones aceptada por el cliente antes de cubicar", ["F_UDD_brechas"]),
    ("X17", "Designación de hormigón obsoleta (H-xx por cubo) usada para cotizar", "E03", ["P_horm"], "C17",
     "Traducir a grado G de NCh170:2016 con el proveedor antes del APU", ["F_NCh170"]),
    ("X18", "Fierro sin número de barras por diámetro y largo comercial", "E07", ["P_fierro"], "C18",
     "Tabla de corte: por diámetro, largo de 6 o 12 m, número de barras y masa (NCh353 6.2.2; NCh204 4.3.2)", ["F_NCh353", "F_NCh204"]),
    ("X19", "Diseño bajo mínimos normativos sin advertir al cliente (Sede C: 10 mm en encuentros; NCh1928 6.4.3.5 exige 12 mm)", "E02", ["P_fierro"], "C19",
     "Contrastar EETT con R37 a R40 y reportar como consulta, sin rediseñar", ["F_NCh1928", "F_SedeC"]),
    ("X20", "Escalerilla presupuestada como fierro aparte y además dentro del m² de albañilería", "E04", ["P_alb", "P_fierro"], "C20",
     "Ubicar la escalerilla en una sola partida (NCh353 8.1.6) y decirlo en el itemizado", ["F_NCh353"]),
    ("X21", "Hormigón de relleno de huecos sin partida ni APU en albañilería armada", "E10", ["P_alb", "P_horm"], "C21",
     "Volumen de huecos con armadura (NCh1928 7.1) en m³: partida propia o declarado en el APU de albañilería", ["F_NCh1928", "F_SedeC"]),
    ("X22", "Ejecutar con una norma parcial, secundaria o ausente sin advertirlo", "E00", ["P_alb", "P_fierro", "P_horm"], "C22",
     "Tabla de literatura por sistema (cerebro.py literatura) revisada; lo que no esté vista se pide a Nicolás antes de ejecutar", ["F_SedeC"]),
    ("X23", "EETT contradictorias entre cláusulas para un mismo elemento (Sede C: cadena 6φ10 en 3.4 y 12 mm en 3.5)", "E02", ["P_fierro"], "C23",
     "Cruzar cada elemento entre todas las cláusulas de EETT que lo nombran; la contradicción va a consultas con su efecto en kg", ["F_SedeC"]),
]
for k, t, et, ps, ck, ct, fs in errores:
    n(k, "Error", t)
    a(k, et, "ocurre_en")
    for p in ps:
        a(k, p, "afecta")
    for f in fs:
        a(k, f, "cita")
    n(ck, "Chequeo", ct)
    a(ck, k, "previene")
    a(ck, "E08" if et in ("E07", "E11") else et, "se_hace_en")

# ----------------------------------------------------------------- herramientas
herr = [("H01", "pdf_a_dxf.py y cubicar_dxf.py (kit): geometría vectorial y largos/áreas por capa", ["E05", "E07"]),
        ("H02", "AutoCAD: MEASUREGEOM, AREA/LIST, hatch con campos de área, QSELECT, DATAEXTRACTION a Excel", ["E05", "E07"]),
        ("H03", "Civil 3D Quantity Takeoff y Navisworks Quantification", ["E07"]),
        ("H04", "Planilla de la casa (skill planillas-ingenieria, auditor estilo.py)", ["E06", "E07", "E09", "E10", "E12"]),
        ("H05", "Skill verificacion-independiente y agentes en frío", ["E08", "E11"]),
        ("H06", "LaTeX utfsm (sinmarca) para el informe; compaginación OK", ["E12"]),
        ("H07", "SII: boleta de honorarios electrónica", ["E12"]),
        ("H10", "python cerebro.py literatura <sistemas>: fuentes por sistema con su estado y lista de lo que hay que pedir", ["E00"]),
        ("H08", "Copia de normas en la biblioteca USM o INN; registro de qué está leído y qué es secundario", ["E03"]),
        ("H09", "Plantilla de itemizado NCh1156 (secciones 0 a 4)", ["E04"])]
for k, t, es in herr:
    n(k, "Herramienta", t)
    for e in es:
        a(e, k, "usa")
a("H02", "F_ACAD_area", "cita")
a("H03", "F_C3D_QTO", "cita")
a("H09", "F_NCh1156", "cita")

# ----------------------------------------------------------------- pendientes de lectura
estudio = [("S01", "NCh1928 en copia de mejor resolución, solo para A.4 (resistencia del hormigón de relleno)", ["F_NCh1928", "F_cursoInsp"]),
           ("S02", "NCh2123 completa (requisitos de pilares y cadenas), no solo la modificación de materiales", ["F_NCh2123"]),
           ("S03", "ACI 318-05 o NCh430 completa para confirmar que ld y las clases de empalme coinciden con 318-19 (R40)", ["F_NCh430", "F_ACI318"]),
           ("S08", "Ficha técnica de escalerilla de fabricante para el kg/m² de muro (X08, X20)", ["F_fichaEscalerilla", "F_FSPR2019"]),
           ("S04", "Manual de tolerancias CDT para cotejar escantillón y alturas", ["F_CDT_tol"]),
           ("S05", "Tabla MINVU de la región del cliente para APU", ["F_MINVU_precios"]),
           ("S06", "Capítulo QTO de Civil 3D para movimiento de tierras", ["F_C3D_QTO"]),
           ("S07", "Ensayo de cono de morteros solo si un encargo pide control de calidad", ["F_NCh2257"])]
for k, t, fs in estudio:
    n(k, "Estudio", t)
    for f in fs:
        a(k, f, "estudia")


def grafo():
    G = nx.MultiDiGraph()
    for i, tipo, texto, kw in N:
        G.add_node(i, tipo=tipo, texto=texto, **kw)
    for o, d, r in A:
        assert o in G and d in G, (o, d, r)
        G.add_edge(o, d, rel=r)
    return G


def validar(G):
    prob = []
    tipo = nx.get_node_attributes(G, "tipo")
    E = nx.DiGraph([(o, d) for o, d, r in G.edges(data="rel") if r == "precede"])
    if not nx.is_directed_acyclic_graph(E) or nx.dag_longest_path_length(E) != len(etapas) - 1:
        prob.append("Las etapas no forman una ruta única sin ciclos")
    def sal(x, rel):
        return [d for _, d, r in G.out_edges(x, data="rel") if r == rel]
    def ent(x, rel):
        return [o for o, _, r in G.in_edges(x, data="rel") if r == rel]
    for x, t in tipo.items():
        if t == "Regla" and not sal(x, "cita"):
            prob.append(f"{x}: regla sin fuente")
        if t == "Regla" and not sal(x, "aplica_a"):
            prob.append(f"{x}: regla sin partida")
        if t == "Error" and not ent(x, "previene"):
            prob.append(f"{x}: error sin chequeo")
        if t == "Error" and not sal(x, "ocurre_en"):
            prob.append(f"{x}: error sin etapa")
        if t == "Chequeo" and not sal(x, "se_hace_en"):
            prob.append(f"{x}: chequeo sin etapa")
        if t == "Fuente" and G.in_degree(x) == 0:
            prob.append(f"{x}: fuente huérfana")
        if t == "Partida" and not ent(x, "aplica_a"):
            prob.append(f"{x}: partida sin reglas")
        if t == "Sistema" and not sal(x, "exige"):
            prob.append(f"{x}: sistema sin reglas")
        if t == "Etapa" and not (ent(x, "se_aplica_en") or ent(x, "se_hace_en") or sal(x, "usa")):
            prob.append(f"{x}: etapa vacía")
    return prob


def literatura(G, sel=None):
    """Fuentes que citan las reglas de cada sistema; devuelve filas y la lista de lo que hay que pedir."""
    sel = sel or list(sistemas)
    filas, pedir = [], {}
    for s_ in sel:
        fu = {}
        for _, rg, r in G.out_edges(s_, data="rel"):
            if r == "exige":
                for _, f, r2 in G.out_edges(rg, data="rel"):
                    if r2 == "cita":
                        fu.setdefault(f, []).append(rg)
        for f, rs in sorted(fu.items()):
            filas.append((sistemas[s_], f, G.nodes[f]["estado"], rs))
        # una regla queda cubierta si cita una fuente vista y no lleva [Por verificar]
        for rg in {r_ for rs in fu.values() for r_ in rs}:
            cit = [f for _, f, r2 in G.out_edges(rg, data="rel") if r2 == "cita"]
            ok = any(G.nodes[f]["estado"] == "vista" for f in cit) and "[Por verificar" not in G.nodes[rg]["texto"]
            if not ok:
                for f in cit:
                    if G.nodes[f]["estado"] in ("parcial", "secundaria", "falta"):
                        pedir.setdefault(f, set()).add(rg)
    return filas, pedir


def lista_partida(G, clave):
    p = [x for x, t in G.nodes(data="tipo") if t == "Partida" and clave.lower() in (x + G.nodes[x]["texto"]).lower()]
    out = []
    for x in p:
        out.append(f"## {G.nodes[x]['texto']}")
        for o, _, r in G.in_edges(x, data="rel"):
            if r == "aplica_a":
                out.append(f"- Regla {o}: {G.nodes[o]['texto']}")
        for o, _, r in G.in_edges(x, data="rel"):
            if r == "afecta":
                ch = [c for c, _, rr in G.in_edges(o, data="rel") if rr == "previene"]
                out.append(f"- Error {o}: {G.nodes[o]['texto']} -> chequeo: {G.nodes[ch[0]]['texto']}")
    return "\n".join(out)


def exportar(G, carpeta):
    carpeta = Path(carpeta)
    (carpeta / "grafo.json").write_text(json.dumps(nx.node_link_data(G, edges="edges"), ensure_ascii=False, indent=1))
    t = nx.get_node_attributes(G, "texto")
    L = ["# Cerebro de cubicación y presupuesto", "",
         "Generado desde `cerebro.py` (grafo tipado; no editar a mano). Las reglas citan la cláusula de la norma leída; "
         "las marcadas [Por verificar] vienen de fuentes secundarias o de copias incompletas. Estado de cada fuente al final: "
         "vista (texto leído), parcial (copia incompleta o ilegible), secundaria (resumen de terceros), caso (experiencia propia), falta (no se tiene).", "",
         f"Nodos: {G.number_of_nodes()} · aristas: {G.number_of_edges()} · validación: "
         f"{'OK' if not validar(G) else 'FALLA'}", "", "## Ruta de la tarea"]
    for k, tt, d in etapas:
        L.append(f"\n### {k} {tt}\n{d}")
        rs = [o for o, _, r in G.in_edges(k, data="rel") if r == "se_aplica_en"]
        xs = [o for o, _, r in G.in_edges(k, data="rel") if r == "ocurre_en"]
        cs = [o for o, _, r in G.in_edges(k, data="rel") if r == "se_hace_en"]
        hs = [d2 for _, d2, r in G.out_edges(k, data="rel") if r == "usa"]
        for o in rs:
            L.append(f"- Regla {o}: {t[o]}")
        for o in xs:
            L.append(f"- Error típico {o}: {t[o]}")
        for o in cs:
            L.append(f"- Chequeo {o}: {t[o]}")
        for o in hs:
            L.append(f"- Herramienta: {t[o]}")
    L.append("\n## E00: literatura por sistema (pedir antes de ejecutar)")
    filas, pedir = literatura(G)
    for st in sistemas.values():
        fs_ = [f"{f} [{e}]" for s2, f, e, _ in filas if s2 == st]
        L.append(f"- {st}: " + ", ".join(fs_))
    L.append("\nPedir o confirmar antes de ejecutar un encargo con esos sistemas:")
    for f, rs in sorted(pedir.items()):
        L.append(f"- {f} ({G.nodes[f]['estado']}): afecta {', '.join(sorted(rs))}")
    L.append("\n## Antes de presupuestar (E00 a E06)")
    for k, tt, d in etapas[:7]:
        L.append(f"\n**{k} {tt}.** {d}")
        for o, _, r in G.in_edges(k, data="rel"):
            if r in ("se_aplica_en", "se_hace_en"):
                L.append(f"- [ ] {t[o]}")
    L.append("\n## Reglas por sistema constructivo")
    for s_, ts in sistemas.items():
        L.append(f"\n### {ts}")
        for _, d2, r in G.out_edges(s_, data="rel"):
            if r == "exige":
                L.append(f"- {d2}: {t[d2]}")
    L.append("\n## Lista de control por partida")
    for p in partidas:
        L.append("\n" + lista_partida(G, p).replace("## ", "### "))
    L.append("\n## Lecturas pendientes")
    for k, tt, fs in estudio:
        L.append(f"- {tt} ({', '.join(fs)})")
    L.append("\n## Fuentes")
    for k, (tt, u, est) in F.items():
        L.append(f"- {k} [{est}]: {tt}" + (f" — {u}" if u else ""))
    (carpeta / "CEREBRO.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    G = grafo()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validar"
    if cmd == "validar":
        p = validar(G)
        print("\n".join(p) if p else f"GRAFO: OK ({G.number_of_nodes()} nodos, {G.number_of_edges()} aristas)")
        sys.exit(1 if p else 0)
    if cmd == "exportar":
        exportar(G, Path(__file__).parent)
        print("exportado")
    if cmd == "literatura":
        filas, pedir = literatura(G, sys.argv[2:] or None)
        for st, f, e, rs in filas:
            print(f"{st:28s} {f:20s} {e:11s} {', '.join(rs)}")
        print("\nPEDIR:" if pedir else "\nLITERATURA: OK")
        for f, rs in sorted(pedir.items()):
            print(f"- {f}: {G.nodes[f]['texto']} (afecta {', '.join(sorted(rs))})")
    if cmd == "partida":
        print(lista_partida(G, sys.argv[2]))
