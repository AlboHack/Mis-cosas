# Cerebro de cubicación y presupuesto

Generado desde `cerebro.py` (grafo tipado; no editar a mano). Las reglas citan la cláusula de la norma leída; las marcadas [Por verificar] vienen de fuentes secundarias o de copias incompletas. Estado de cada fuente al final: vista (texto leído), parcial (copia incompleta o ilegible), secundaria (resumen de terceros), caso (experiencia propia), falta (no se tiene).

Nodos: 169 · aristas: 468 · validación: OK

## Ruta de la tarea

### E00 Literatura y normas disponibles
Por cada sistema constructivo del encargo, listar las normas y fuentes que citan sus reglas y su estado (python cerebro.py literatura <sistemas>); pedir a Nicolás lo que esté parcial, secundario o falte, y esperar su respuesta antes de ejecutar
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]
- Error típico X22: Ejecutar con una norma parcial, secundaria o ausente sin advertirlo
- Chequeo C22: Tabla de literatura por sistema (cerebro.py literatura) revisada; lo que no esté vista se pide a Nicolás antes de ejecutar
- Herramienta: python cerebro.py literatura <sistemas>: fuentes por sistema con su estado y lista de lo que hay que pedir

### E01 Alcance y encargo
Qué se entrega, para quién, insumos, plazo y modalidad de contrato (suma alzada, serie de precios, administración); versión y fecha de cada documento
- Regla R44: Visita a terreno y lista de antecedentes (accesos, agua, energía, botaderos, suelo, napa, mano de obra local) antes de cerrar precios
- Error típico X15: Plano o EETT en versión desactualizada
- Error típico X16: Brecha presupuestaria por alcance mal definido
- Chequeo C15: Registrar versión y fecha de cada documento en Datos
- Chequeo C16: Lista de supuestos y exclusiones aceptada por el cliente antes de cubicar

### E02 Revisión de insumos
Cotas, escalas, coherencia plano-EETT-itemizado; contradicciones a una lista de consultas
- Regla R37: NCh1928 6.4.1.1 y 6.4.3.2 a 6.4.3.5, 6.4.3.8: espesor >= máx(1/25 de la menor dimensión libre; 14 cm); cuantía >= 0.06 % por dirección y >= 0.15 % total, contando solo barras que recorren todo el ancho o alto; vertical >= 8 mm a <= 6e y <= 120 cm; en cada borde libre y encuentro al menos una barra de 12 mm; verticales fijadas cada <= 300 d y <= 3 m
- Regla R38: NCh1928 6.1.2 y 6.4.3.6: armadura de junta de diámetro <= mitad del espesor de la junta; refuerzo horizontal en el remate de cimientos, base y remate de vanos, nivel de piso, techo y parapetos; verticales >= 10 mm a cada lado de vano, prolongadas 60 cm más allá de las esquinas
- Regla R47: Las EETT fijan el alcance de cada partida (dónde va, qué incluye) y prevalecen sobre la costumbre
- Regla R48: Plano sin cotas no se cubica: se consulta; trabajar por ejes y pisos sin agrupar
- Regla R50: Albañilería confinada (NCh2123 vía apunte INACAP) [Por verificar]: espesor >= 14 cm con ladrillo a máquina y 15 cm artesanal; paño <= 12.5 m² y <= 6 m entre pilares; pilares en bordes libres e intersecciones; cadenas a nivel de piso y techo de ancho >= espesor del muro; mortero 5 MPa artesanal y 10 MPa a máquina
- Error típico X06: Alcance de EETT ignorado (cerámica en todo el interior; relleno sobre la huella)
- Error típico X13: Rótulo del plano contradice el dibujo (pendiente 60 % rotulada, 40 % dibujada)
- Error típico X19: Diseño bajo mínimos normativos sin advertir al cliente (Sede C: 10 mm en encuentros; NCh1928 6.4.3.5 exige 12 mm)
- Error típico X23: EETT contradictorias entre cláusulas para un mismo elemento (Sede C: cadena 6φ10 en 3.4 y 12 mm en 3.5)
- Chequeo C06: Leer la EETT de cada partida antes de cubicarla y anotar su alcance en Datos
- Chequeo C13: Medir en corte y elevación; reportar la contradicción como consulta
- Chequeo C19: Contrastar EETT con R37 a R40 y reportar como consulta, sin rediseñar
- Chequeo C23: Cruzar cada elemento entre todas las cláusulas de EETT que lo nombran; la contradicción va a consultas con su efecto en kg

### E03 Marco normativo y designaciones
Sistema constructivo, normas que lo rigen, designación vigente de hormigón, acero, ladrillo y mortero
- Regla R32: NCh204:2020: masas nominales 6 mm 0.222, 8 mm 0.395, 10 mm 0.617, 12 mm 0.888, 16 mm 1.58 kg/m; largos normales 6 y 12 m; diámetros hasta 16 mm en rollo; tolerancia de masa ±3.5 %
- Regla R33: NCh170:2016: grados G05 a G60 por resistencia cilíndrica fc' (MPa); la designación incluye grado, fracción defectuosa, tamaño máximo de árido y asentamiento. EETT con 'H-xx' usan la designación antigua: pedir el grado G equivalente al proveedor [Por verificar la equivalencia]
- Regla R34: NCh169.Of2001: clases MqM, MqP, MqH y grados 1, 2, 3; tolerancias largo ±5 mm, ancho y alto ±3 mm. Armada exige grado 1 o 2 [Por verificar en NCh1928]; confinada exige MqM o MqP (NCh2123 5.2.1)
- Regla R35: NCh2256/1.Of2001: grados de mortero M0.5 a M30; mortero de junta con Dn de arena <= 1/3 de la junta, consistencia 180 a 220 mm, resistencia según NCh1928 o NCh2123
- Regla R36: Junta de albañilería de 10 a 15 mm (rango de validez de NCh2123 y NCh1928): fija el escantillón y el número de hiladas y de filas de escalerilla
- Regla R39: NCh1928 A.3.2 y A.4: mortero fm >= 10 MPa (fracción defectuosa 4 %), retentividad >= 70 %; sin ensayos, 1:0.22:4 en peso (cemento:cal:arena) con cono <= 18 cm; árido del hormigón de relleno <= 12.5 mm; resistencia del relleno 17.5 MPa [Por verificar: cifra del curso, ilegible en A.4]
- Regla R49: NCh1928 7.1: todo hueco que aloja armadura se llena con hormigón de relleno, por etapas de altura limitada según el hueco (5 cm: 30 cm; 8 cm: 120 cm; >= 12 cm: 240 cm). Se cubica el volumen de huecos rellenos en m³, como partida propia o declarado dentro del APU de albañilería
- Error típico X17: Designación de hormigón obsoleta (H-xx por cubo) usada para cotizar
- Chequeo C17: Traducir a grado G de NCh170:2016 con el proveedor antes del APU
- Herramienta: Copia de normas en la biblioteca USM o INN; registro de qué está leído y qué es secundario

### E04 Itemizado
Partidas ordenadas según NCh1156, medibles, presupuestables y controlables, con unidad según EETT o NCh353
- Regla R17: NCh353 8.1.6: refuerzos de acero en las juntas entre hiladas (escalerilla) se incluyen en la partida de albañilería, no en fierro
- Regla R18: NCh353 8.1.2 y 8.1.4: partidas separadas por naturaleza y espesor; la mano de obra de formar vanos de 2 m² o más va en el precio unitario del muro
- Regla R30: NCh1156/1 a /3: secciones 0 informaciones generales, 1 gastos adicionales, obras provisionales y trabajos previos, 2 obras de construcción (2/1 obra gruesa, 2/2 terminaciones), 3 instalaciones, 4 obras complementarias; la medición de cada partida remite a NCh353 (7.8)
- Regla R31: Partidas medibles, presupuestables y controlables, con código y unidad; una partida omitida es pérdida para el contratista
- Error típico X20: Escalerilla presupuestada como fierro aparte y además dentro del m² de albañilería
- Chequeo C20: Ubicar la escalerilla en una sola partida (NCh353 8.1.6) y decirlo en el itemizado
- Herramienta: Plantilla de itemizado NCh1156 (secciones 0 a 4)

### E05 Extracción de geometría
PDF vectorial o DWG a DXF; calibrar escala con dos o más cotas por vista
- Regla R48: Plano sin cotas no se cubica: se consulta; trabajar por ejes y pisos sin agrupar
- Error típico X03: Escala mal calibrada o asumida (vistas a escalas distintas en la misma lámina)
- Chequeo C03: Calibrar cada vista con dos cotas independientes y declarar el factor
- Herramienta: pdf_a_dxf.py y cubicar_dxf.py (kit): geometría vectorial y largos/áreas por capa
- Herramienta: AutoCAD: MEASUREGEOM, AREA/LIST, hatch con campos de área, QSELECT, DATAEXTRACTION a Excel

### E06 Datos de entrada
Cada dato una sola vez, con unidad, base (M/E/I/S) y fuente
- Herramienta: Planilla de la casa (skill planillas-ingenieria, auditor estilo.py)

### E07 Cubicación por partida
Cantidades según NCh353, por ejes y sin agrupar; sin pérdidas
- Regla R01: NCh353 1.3: las pérdidas (despuntes, mortero caído, envases rotos, excesos) no van en la cubicación sino en el rendimiento del precio unitario
- Regla R02: NCh353 4.4: lo que pertenece a la vez a más de un elemento se mide una sola vez (esquinas, encuentros, cruces)
- Regla R03: NCh353 5.1.5 y Tabla 1: sobreancho de excavación solo si la fundación lleva moldaje (0.20 m por lado hasta 0.5 m de alto; 0.40 hasta 1.0; 0.50 hasta 1.5; 0.70 hasta 2.5; 0.80 sobre 2.5); con talud, 0.10 m por lado (5.1.6); zanja de cañería: diámetro exterior + 0.45 m (5.1.7)
- Regla R04: NCh353 5.2 y Tabla 2: transporte de excedentes = volumen en banco + esponjamiento (10, 15, 25, 30 % o más según terreno); el asentamiento en el transporte no se descuenta
- Regla R05: NCh353 5.3.1: rellenos por volumen neto rellenado; rellenos de excavaciones de fundación en partida separada de los rellenos de piso; compactación estimable con Tabla 3
- Regla R06: NCh353 5.4.1: escarpes por superficie explanada
- Regla R07: NCh353 6.1: hormigón por volumen sin descontar armaduras ni tuberías hasta 0.25 m; se descuentan aberturas mayores a 0.05 m²; partidas separadas por tipo de hormigón, elemento y moldaje
- Regla R08: NCh353 6.2.1 a 6.2.3: barras por masa nominal x largo total (resistentes, repartición, suples y estribos); por diámetro y largo comercial indicar número de barras y masa; barras de más de 12 m aparte
- Regla R09: NCh353 6.2.4 y 6.2.5: +5 % sobre la masa medida (4 % trabas, patas, guías, elementos de posición y despuntes; 1 % sobredimensión), salvo que el proyecto cuantifique trabas y patas
- Regla R10: NCh353 6.2.7 y 6.2.8: verticales de pilares y muros empalmadas 40 d en el piso superior; penetración en fundaciones no detallada = 40 d (la norma impresa dice 'quedando 10,1 m sobre el fondo', errata evidente: interpretar 0.1 m) [Por verificar la errata]
- Regla R12: NCh353 6.3: emplantillados por superficie o volumen indicando espesor; fundaciones por volumen real; radier por superficie con espesor
- Regla R13: NCh353 6.4 a 6.6 y 6.10.2: alturas de muros entre niveles superiores de losas o hasta el fondo de viga; vigas por luz libre; intersecciones en orden 1° pilares y muros, 2° vigas, 3° losas
- Regla R14: NCh353 7.1 a 7.3: cadenas por volumen real medido como vigas; pilares de refuerzo sin el hormigón entre endentados; apoyo de dintel no indicado = 0.30 m por extremo
- Regla R15: NCh353 8.1.1 y Tabla 4.a: albañilería por superficie efectiva; vanos en ladrillo a máquina: <1.5 m² 0 % (50 % con pilar), 1.5 a 3.0 m² 50 % (75 %), >3.0 m² 100 %. Tabla 4.b para ladrillo a mano
- Regla R16: NCh353 8.1.3: se descuentan de la albañilería los espacios de cadenas, dinteles, vigas y pilares embutidos; muros endentados desde el ladrillo más saliente
- Regla R17: NCh353 8.1.6: refuerzos de acero en las juntas entre hiladas (escalerilla) se incluyen en la partida de albañilería, no en fierro
- Regla R19: NCh353 9.1.1: tabiques de madera por longitud con altura, sin descontar vanos menores a 3 m² si el dintel es del mismo material
- Regla R20: NCh353 9.5 y 9.6: estructura de techumbre por superficie proyectada horizontal (incluye canes de una pieza); aleros por ml con ancho; forros, canes a la vista y frontones aparte
- Regla R21: NCh353 13: cubiertas por superficie de vertientes sin traslapos; incluye elementos intermedios entre cubierta y estructura (costaneras, entablado)
- Regla R22: NCh353 12: caballetes, limatesas y forros por longitud sin traslapos y con ancho desarrollado; canales y bajadas por longitud incluyendo curvas, tes y ves; anclajes en el precio
- Regla R23: NCh353 14: aislación e impermeabilización en láminas por superficie con retornos y sin traslapos; vanos <=1 m² no se descuentan, mayores se descuentan en el exceso
- Regla R24: NCh353 15 y 16: pavimentos y cielos por superficie efectiva entre paramentos terminados; cielo incluye sobre vanos sin dintel; radier en partida aparte del pavimento
- Regla R25: NCh353 18.2: cerámicos por superficie a la vista, sin descontar superficies no revestidas menores a 0.5 m²; biselado 0.5 ml por m² en el APU
- Regla R26: NCh353 11: estucos por superficie proyectada; espesor supuesto 2.5 cm salvo EETT; descuento de vanos según 11.3
- Regla R27: NCh353 24: pinturas por superficie recubierta, partida por clase de pintura
- Regla R29: Moldaje por superficie de contacto con el hormigón, en partida por elemento (NCh353 6.1.4); incluye fondos bajo dinteles y tapas de extremos; madera tradicional ~3 usos (hasta 5)
- Regla R32: NCh204:2020: masas nominales 6 mm 0.222, 8 mm 0.395, 10 mm 0.617, 12 mm 0.888, 16 mm 1.58 kg/m; largos normales 6 y 12 m; diámetros hasta 16 mm en rollo; tolerancia de masa ±3.5 %
- Regla R36: Junta de albañilería de 10 a 15 mm (rango de validez de NCh2123 y NCh1928): fija el escantillón y el número de hiladas y de filas de escalerilla
- Regla R37: NCh1928 6.4.1.1 y 6.4.3.2 a 6.4.3.5, 6.4.3.8: espesor >= máx(1/25 de la menor dimensión libre; 14 cm); cuantía >= 0.06 % por dirección y >= 0.15 % total, contando solo barras que recorren todo el ancho o alto; vertical >= 8 mm a <= 6e y <= 120 cm; en cada borde libre y encuentro al menos una barra de 12 mm; verticales fijadas cada <= 300 d y <= 3 m
- Regla R38: NCh1928 6.1.2 y 6.4.3.6: armadura de junta de diámetro <= mitad del espesor de la junta; refuerzo horizontal en el remate de cimientos, base y remate de vanos, nivel de piso, techo y parapetos; verticales >= 10 mm a cada lado de vano, prolongadas 60 cm más allá de las esquinas
- Regla R40: Anclajes y empalmes: NCh1928 6.1.5 traslapo >= 40 veces el menor diámetro; en huecos menores que 6 veces el diámetro mayor solo empalme soldado, mecánico o traslapo dentro de la cadena; 6.1.6 anclajes según hormigón armado. ACI 318-19 25.4.2.3: ld = fy ψt ψe ψg db / (2.1 λ √f'c) para barras <= 19 mm con espaciamiento y recubrimiento suficientes, >= 300 mm; 25.5.2.1 traslapo clase B = 1.3 ld; Tabla 25.3.1 ganchos de 90° y 180° con diámetro interior 6 db. A440-280H con G25: ld = 27 d y clase B = 35 d (40 d cubre); A630-420H con G25: ld = 40 d y clase B = 52 d (40 d no alcanza). NCh430 adopta ACI 318-05 [Por verificar que la ecuación coincide]
- Regla R47: Las EETT fijan el alcance de cada partida (dónde va, qué incluye) y prevalecen sobre la costumbre
- Regla R49: NCh1928 7.1: todo hueco que aloja armadura se llena con hormigón de relleno, por etapas de altura limitada según el hueco (5 cm: 30 cm; 8 cm: 120 cm; >= 12 cm: 240 cm). Se cubica el volumen de huecos rellenos en m³, como partida propia o declarado dentro del APU de albañilería
- Error típico X01: Doble conteo en esquinas y encuentros en T
- Error típico X02: Vanos descontados al 100 % o no descontados, sin la Tabla 4 de NCh353
- Error típico X07: Pérdidas metidas en la cubicación, o criterio confundido con error
- Error típico X08: Masa por metro mal tomada (escalerilla al doble)
- Error típico X09: Armadura sin estribos, traslapos, patas ni penetración en fundación
- Error típico X18: Fierro sin número de barras por diámetro y largo comercial
- Herramienta: pdf_a_dxf.py y cubicar_dxf.py (kit): geometría vectorial y largos/áreas por capa
- Herramienta: AutoCAD: MEASUREGEOM, AREA/LIST, hatch con campos de área, QSELECT, DATAEXTRACTION a Excel
- Herramienta: Civil 3D Quantity Takeoff y Navisworks Quantification
- Herramienta: Planilla de la casa (skill planillas-ingenieria, auditor estilo.py)

### E08 Verificación independiente
Segundo método por partida crítica; recubicación ciega; planilla contra script
- Error típico X11: Verificación circular: supuesto elegido porque coincide
- Error típico X12: Error de fórmula o de rango en la planilla
- Chequeo C01: Muro pasante entero y el que llega cortado en la cara (NCh353 4.4); contraste con área de muros / espesor
- Chequeo C02: Lista de vanos con área y si llevan pilar; aplicar NCh353 Tabla 4.a fila por fila
- Chequeo C07: Cantidad neta en Cubicación (NCh353 1.3); pérdidas solo en APU; conciliación declara el criterio
- Chequeo C08: Masa = π/4 d² ρ por alambre; contrastar kg/m² de muro con referencias
- Chequeo C09: kg/m teórico del elemento con NCh353 6.2.4 a 6.2.8 contra la cantidad
- Chequeo C10: Recubicación ciega antes de mirar la referencia; coincidencias exactas se revisan igual
- Chequeo C11: Un supuesto nunca se justifica por coincidir; marcarlo S o I y dar su sensibilidad
- Chequeo C12: Hoja Control planilla contra script de Python; recalc sin errores; auditor de estilo
- Chequeo C18: Tabla de corte: por diámetro, largo de 6 o 12 m, número de barras y masa (NCh353 6.2.2; NCh204 4.3.2)
- Herramienta: Skill verificacion-independiente y agentes en frío

### E09 Análisis de precios unitarios
Materiales puestos en obra con pérdidas, mano de obra con rendimientos y leyes sociales, equipos y otros
- Regla R01: NCh353 1.3: las pérdidas (despuntes, mortero caído, envases rotos, excesos) no van en la cubicación sino en el rendimiento del precio unitario
- Regla R04: NCh353 5.2 y Tabla 2: transporte de excedentes = volumen en banco + esponjamiento (10, 15, 25, 30 % o más según terreno); el asentamiento en el transporte no se descuenta
- Regla R11: NCh353 6.2.6 y 6.2.10: alambre de amarre en el precio unitario; enfierradura subcontratada a suma alzada: +1 % sobre cubicación de planos
- Regla R18: NCh353 8.1.2 y 8.1.4: partidas separadas por naturaleza y espesor; la mano de obra de formar vanos de 2 m² o más va en el precio unitario del muro
- Regla R25: NCh353 18.2: cerámicos por superficie a la vista, sin descontar superficies no revestidas menores a 0.5 m²; biselado 0.5 ml por m² en el APU
- Regla R28: NCh353 Anexo A: el APU se desglosa en materiales, mano de obra (rendimiento y leyes sociales), herramientas o equipos menores y subcontratos
- Regla R29: Moldaje por superficie de contacto con el hormigón, en partida por elemento (NCh353 6.1.4); incluye fondos bajo dinteles y tapas de extremos; madera tradicional ~3 usos (hasta 5)
- Regla R33: NCh170:2016: grados G05 a G60 por resistencia cilíndrica fc' (MPa); la designación incluye grado, fracción defectuosa, tamaño máximo de árido y asentamiento. EETT con 'H-xx' usan la designación antigua: pedir el grado G equivalente al proveedor [Por verificar la equivalencia]
- Regla R35: NCh2256/1.Of2001: grados de mortero M0.5 a M30; mortero de junta con Dn de arena <= 1/3 de la junta, consistencia 180 a 220 mm, resistencia según NCh1928 o NCh2123
- Regla R39: NCh1928 A.3.2 y A.4: mortero fm >= 10 MPa (fracción defectuosa 4 %), retentividad >= 70 %; sin ensayos, 1:0.22:4 en peso (cemento:cal:arena) con cono <= 18 cm; árido del hormigón de relleno <= 12.5 mm; resistencia del relleno 17.5 MPa [Por verificar: cifra del curso, ilegible en A.4]
- Regla R42: Costo de materiales puesto en obra, cotizado por proveedor; incluye pérdidas por robo, mal almacenamiento y transporte; P.U. = total de la partida / cantidad
- Regla R43: Mano de obra: rendimiento real (trabajo productivo, contributorio y no contributorio) y costo con leyes sociales
- Regla R44: Visita a terreno y lista de antecedentes (accesos, agua, energía, botaderos, suelo, napa, mano de obra local) antes de cerrar precios
- Regla R46: Precios de referencia: tabla MINVU DS27 de la región y cotizaciones; justificar cada P.U.
- Regla R49: NCh1928 7.1: todo hueco que aloja armadura se llena con hormigón de relleno, por etapas de altura limitada según el hueco (5 cm: 30 cm; 8 cm: 120 cm; >= 12 cm: 240 cm). Se cubica el volumen de huecos rellenos en m³, como partida propia o declarado dentro del APU de albañilería
- Herramienta: Planilla de la casa (skill planillas-ingenieria, auditor estilo.py)

### E10 Presupuesto
Costo directo, gastos generales, imprevistos, utilidad, IVA; partidas faltantes u omitidas al final
- Regla R31: Partidas medibles, presupuestables y controlables, con código y unidad; una partida omitida es pérdida para el contratista
- Regla R41: Presupuesto de venta = costo directo + gastos generales de obra + gastos generales indirectos (financiero, garantías, oficina central) + imprevistos + utilidad + IVA
- Regla R45: Incertidumbre: por partida relevante, valores optimista, más probable y pesimista; simular o usar PERT para el rango del costo
- Error típico X04: Unidad equivocada (m² con valor de m³) o magnitud incoherente
- Error típico X05: Cifra copiada entre partidas (canales = bajadas = forros)
- Error típico X14: Elemento exigido por EETT o norma sin partida (armadura de sobrecimiento; refuerzo horizontal en base de vanos)
- Error típico X21: Hormigón de relleno de huecos sin partida ni APU en albañilería armada
- Chequeo C04: Unidad contra magnitud: espesor implícito = volumen / área
- Chequeo C05: Buscar valores repetidos en el itemizado y justificar cada uno
- Chequeo C14: Recorrer EETT capítulo por capítulo y los mínimos de R37-R38 contra el itemizado; lo que falte va a partidas omitidas
- Chequeo C21: Volumen de huecos con armadura (NCh1928 7.1) en m³: partida propia o declarado en el APU de albañilería
- Herramienta: Planilla de la casa (skill planillas-ingenieria, auditor estilo.py)

### E11 Conciliación con referencia
Si existe un presupuesto previo: causa de cada diferencia, sin ajustar hacia la referencia
- Error típico X10: Coincidencia artificial: calzar con la referencia
- Herramienta: Skill verificacion-independiente y agentes en frío

### E12 Entregable y cierre
Planilla con controles, informe, consultas al proyectista; boleta, cobro y registro de errores
- Herramienta: Planilla de la casa (skill planillas-ingenieria, auditor estilo.py)
- Herramienta: LaTeX utfsm (sinmarca) para el informe; compaginación OK
- Herramienta: SII: boleta de honorarios electrónica

## E00: literatura por sistema (pedir antes de ejecutar)
- Albañilería armada: F_ACI318 [vista], F_NCh169 [vista], F_NCh1928 [vista], F_NCh204 [vista], F_NCh2123 [parcial], F_NCh2256 [vista], F_NCh353 [vista], F_NCh430 [parcial], F_SedeC [caso], F_Solminihac [vista], F_cursoInsp [secundaria]
- Albañilería confinada: F_ACI318 [vista], F_NCh169 [vista], F_NCh1928 [vista], F_NCh204 [vista], F_NCh2123 [parcial], F_NCh2123_inacap [secundaria], F_NCh2256 [vista], F_NCh353 [vista], F_NCh430 [parcial], F_SedeC [caso], F_Solminihac [vista], F_cursoInsp [secundaria]
- Hormigón armado: F_ACI318 [vista], F_NCh170 [vista], F_NCh1928 [vista], F_NCh204 [vista], F_NCh353 [vista], F_NCh430 [parcial], F_SedeC [caso], F_Solminihac [vista]
- Techumbre y cubierta: F_NCh353 [vista], F_SedeC [caso], F_Solminihac [vista]
- Terminaciones: F_NCh353 [vista], F_SedeC [caso]
- Movimiento de tierras: F_NCh353 [vista], F_SedeC [caso]

Pedir o confirmar antes de ejecutar un encargo con esos sistemas:
- F_NCh2123 (parcial): afecta R34, R50
- F_NCh2123_inacap (secundaria): afecta R50
- F_NCh430 (parcial): afecta R40
- F_cursoInsp (secundaria): afecta R34, R39

## Antes de presupuestar (E00 a E06)

**E00 Literatura y normas disponibles.** Por cada sistema constructivo del encargo, listar las normas y fuentes que citan sus reglas y su estado (python cerebro.py literatura <sistemas>); pedir a Nicolás lo que esté parcial, secundario o falte, y esperar su respuesta antes de ejecutar
- [ ] Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]
- [ ] Tabla de literatura por sistema (cerebro.py literatura) revisada; lo que no esté vista se pide a Nicolás antes de ejecutar

**E01 Alcance y encargo.** Qué se entrega, para quién, insumos, plazo y modalidad de contrato (suma alzada, serie de precios, administración); versión y fecha de cada documento
- [ ] Visita a terreno y lista de antecedentes (accesos, agua, energía, botaderos, suelo, napa, mano de obra local) antes de cerrar precios
- [ ] Registrar versión y fecha de cada documento en Datos
- [ ] Lista de supuestos y exclusiones aceptada por el cliente antes de cubicar

**E02 Revisión de insumos.** Cotas, escalas, coherencia plano-EETT-itemizado; contradicciones a una lista de consultas
- [ ] NCh1928 6.4.1.1 y 6.4.3.2 a 6.4.3.5, 6.4.3.8: espesor >= máx(1/25 de la menor dimensión libre; 14 cm); cuantía >= 0.06 % por dirección y >= 0.15 % total, contando solo barras que recorren todo el ancho o alto; vertical >= 8 mm a <= 6e y <= 120 cm; en cada borde libre y encuentro al menos una barra de 12 mm; verticales fijadas cada <= 300 d y <= 3 m
- [ ] NCh1928 6.1.2 y 6.4.3.6: armadura de junta de diámetro <= mitad del espesor de la junta; refuerzo horizontal en el remate de cimientos, base y remate de vanos, nivel de piso, techo y parapetos; verticales >= 10 mm a cada lado de vano, prolongadas 60 cm más allá de las esquinas
- [ ] Las EETT fijan el alcance de cada partida (dónde va, qué incluye) y prevalecen sobre la costumbre
- [ ] Plano sin cotas no se cubica: se consulta; trabajar por ejes y pisos sin agrupar
- [ ] Albañilería confinada (NCh2123 vía apunte INACAP) [Por verificar]: espesor >= 14 cm con ladrillo a máquina y 15 cm artesanal; paño <= 12.5 m² y <= 6 m entre pilares; pilares en bordes libres e intersecciones; cadenas a nivel de piso y techo de ancho >= espesor del muro; mortero 5 MPa artesanal y 10 MPa a máquina
- [ ] Leer la EETT de cada partida antes de cubicarla y anotar su alcance en Datos
- [ ] Medir en corte y elevación; reportar la contradicción como consulta
- [ ] Contrastar EETT con R37 a R40 y reportar como consulta, sin rediseñar
- [ ] Cruzar cada elemento entre todas las cláusulas de EETT que lo nombran; la contradicción va a consultas con su efecto en kg

**E03 Marco normativo y designaciones.** Sistema constructivo, normas que lo rigen, designación vigente de hormigón, acero, ladrillo y mortero
- [ ] NCh204:2020: masas nominales 6 mm 0.222, 8 mm 0.395, 10 mm 0.617, 12 mm 0.888, 16 mm 1.58 kg/m; largos normales 6 y 12 m; diámetros hasta 16 mm en rollo; tolerancia de masa ±3.5 %
- [ ] NCh170:2016: grados G05 a G60 por resistencia cilíndrica fc' (MPa); la designación incluye grado, fracción defectuosa, tamaño máximo de árido y asentamiento. EETT con 'H-xx' usan la designación antigua: pedir el grado G equivalente al proveedor [Por verificar la equivalencia]
- [ ] NCh169.Of2001: clases MqM, MqP, MqH y grados 1, 2, 3; tolerancias largo ±5 mm, ancho y alto ±3 mm. Armada exige grado 1 o 2 [Por verificar en NCh1928]; confinada exige MqM o MqP (NCh2123 5.2.1)
- [ ] NCh2256/1.Of2001: grados de mortero M0.5 a M30; mortero de junta con Dn de arena <= 1/3 de la junta, consistencia 180 a 220 mm, resistencia según NCh1928 o NCh2123
- [ ] Junta de albañilería de 10 a 15 mm (rango de validez de NCh2123 y NCh1928): fija el escantillón y el número de hiladas y de filas de escalerilla
- [ ] NCh1928 A.3.2 y A.4: mortero fm >= 10 MPa (fracción defectuosa 4 %), retentividad >= 70 %; sin ensayos, 1:0.22:4 en peso (cemento:cal:arena) con cono <= 18 cm; árido del hormigón de relleno <= 12.5 mm; resistencia del relleno 17.5 MPa [Por verificar: cifra del curso, ilegible en A.4]
- [ ] NCh1928 7.1: todo hueco que aloja armadura se llena con hormigón de relleno, por etapas de altura limitada según el hueco (5 cm: 30 cm; 8 cm: 120 cm; >= 12 cm: 240 cm). Se cubica el volumen de huecos rellenos en m³, como partida propia o declarado dentro del APU de albañilería
- [ ] Traducir a grado G de NCh170:2016 con el proveedor antes del APU

**E04 Itemizado.** Partidas ordenadas según NCh1156, medibles, presupuestables y controlables, con unidad según EETT o NCh353
- [ ] NCh353 8.1.6: refuerzos de acero en las juntas entre hiladas (escalerilla) se incluyen en la partida de albañilería, no en fierro
- [ ] NCh353 8.1.2 y 8.1.4: partidas separadas por naturaleza y espesor; la mano de obra de formar vanos de 2 m² o más va en el precio unitario del muro
- [ ] NCh1156/1 a /3: secciones 0 informaciones generales, 1 gastos adicionales, obras provisionales y trabajos previos, 2 obras de construcción (2/1 obra gruesa, 2/2 terminaciones), 3 instalaciones, 4 obras complementarias; la medición de cada partida remite a NCh353 (7.8)
- [ ] Partidas medibles, presupuestables y controlables, con código y unidad; una partida omitida es pérdida para el contratista
- [ ] Ubicar la escalerilla en una sola partida (NCh353 8.1.6) y decirlo en el itemizado

**E05 Extracción de geometría.** PDF vectorial o DWG a DXF; calibrar escala con dos o más cotas por vista
- [ ] Plano sin cotas no se cubica: se consulta; trabajar por ejes y pisos sin agrupar
- [ ] Calibrar cada vista con dos cotas independientes y declarar el factor

**E06 Datos de entrada.** Cada dato una sola vez, con unidad, base (M/E/I/S) y fuente

## Reglas por sistema constructivo

### Albañilería armada
- R08: NCh353 6.2.1 a 6.2.3: barras por masa nominal x largo total (resistentes, repartición, suples y estribos); por diámetro y largo comercial indicar número de barras y masa; barras de más de 12 m aparte
- R09: NCh353 6.2.4 y 6.2.5: +5 % sobre la masa medida (4 % trabas, patas, guías, elementos de posición y despuntes; 1 % sobredimensión), salvo que el proyecto cuantifique trabas y patas
- R10: NCh353 6.2.7 y 6.2.8: verticales de pilares y muros empalmadas 40 d en el piso superior; penetración en fundaciones no detallada = 40 d (la norma impresa dice 'quedando 10,1 m sobre el fondo', errata evidente: interpretar 0.1 m) [Por verificar la errata]
- R14: NCh353 7.1 a 7.3: cadenas por volumen real medido como vigas; pilares de refuerzo sin el hormigón entre endentados; apoyo de dintel no indicado = 0.30 m por extremo
- R15: NCh353 8.1.1 y Tabla 4.a: albañilería por superficie efectiva; vanos en ladrillo a máquina: <1.5 m² 0 % (50 % con pilar), 1.5 a 3.0 m² 50 % (75 %), >3.0 m² 100 %. Tabla 4.b para ladrillo a mano
- R16: NCh353 8.1.3: se descuentan de la albañilería los espacios de cadenas, dinteles, vigas y pilares embutidos; muros endentados desde el ladrillo más saliente
- R17: NCh353 8.1.6: refuerzos de acero en las juntas entre hiladas (escalerilla) se incluyen en la partida de albañilería, no en fierro
- R18: NCh353 8.1.2 y 8.1.4: partidas separadas por naturaleza y espesor; la mano de obra de formar vanos de 2 m² o más va en el precio unitario del muro
- R29: Moldaje por superficie de contacto con el hormigón, en partida por elemento (NCh353 6.1.4); incluye fondos bajo dinteles y tapas de extremos; madera tradicional ~3 usos (hasta 5)
- R32: NCh204:2020: masas nominales 6 mm 0.222, 8 mm 0.395, 10 mm 0.617, 12 mm 0.888, 16 mm 1.58 kg/m; largos normales 6 y 12 m; diámetros hasta 16 mm en rollo; tolerancia de masa ±3.5 %
- R34: NCh169.Of2001: clases MqM, MqP, MqH y grados 1, 2, 3; tolerancias largo ±5 mm, ancho y alto ±3 mm. Armada exige grado 1 o 2 [Por verificar en NCh1928]; confinada exige MqM o MqP (NCh2123 5.2.1)
- R35: NCh2256/1.Of2001: grados de mortero M0.5 a M30; mortero de junta con Dn de arena <= 1/3 de la junta, consistencia 180 a 220 mm, resistencia según NCh1928 o NCh2123
- R36: Junta de albañilería de 10 a 15 mm (rango de validez de NCh2123 y NCh1928): fija el escantillón y el número de hiladas y de filas de escalerilla
- R37: NCh1928 6.4.1.1 y 6.4.3.2 a 6.4.3.5, 6.4.3.8: espesor >= máx(1/25 de la menor dimensión libre; 14 cm); cuantía >= 0.06 % por dirección y >= 0.15 % total, contando solo barras que recorren todo el ancho o alto; vertical >= 8 mm a <= 6e y <= 120 cm; en cada borde libre y encuentro al menos una barra de 12 mm; verticales fijadas cada <= 300 d y <= 3 m
- R38: NCh1928 6.1.2 y 6.4.3.6: armadura de junta de diámetro <= mitad del espesor de la junta; refuerzo horizontal en el remate de cimientos, base y remate de vanos, nivel de piso, techo y parapetos; verticales >= 10 mm a cada lado de vano, prolongadas 60 cm más allá de las esquinas
- R39: NCh1928 A.3.2 y A.4: mortero fm >= 10 MPa (fracción defectuosa 4 %), retentividad >= 70 %; sin ensayos, 1:0.22:4 en peso (cemento:cal:arena) con cono <= 18 cm; árido del hormigón de relleno <= 12.5 mm; resistencia del relleno 17.5 MPa [Por verificar: cifra del curso, ilegible en A.4]
- R40: Anclajes y empalmes: NCh1928 6.1.5 traslapo >= 40 veces el menor diámetro; en huecos menores que 6 veces el diámetro mayor solo empalme soldado, mecánico o traslapo dentro de la cadena; 6.1.6 anclajes según hormigón armado. ACI 318-19 25.4.2.3: ld = fy ψt ψe ψg db / (2.1 λ √f'c) para barras <= 19 mm con espaciamiento y recubrimiento suficientes, >= 300 mm; 25.5.2.1 traslapo clase B = 1.3 ld; Tabla 25.3.1 ganchos de 90° y 180° con diámetro interior 6 db. A440-280H con G25: ld = 27 d y clase B = 35 d (40 d cubre); A630-420H con G25: ld = 40 d y clase B = 52 d (40 d no alcanza). NCh430 adopta ACI 318-05 [Por verificar que la ecuación coincide]
- R49: NCh1928 7.1: todo hueco que aloja armadura se llena con hormigón de relleno, por etapas de altura limitada según el hueco (5 cm: 30 cm; 8 cm: 120 cm; >= 12 cm: 240 cm). Se cubica el volumen de huecos rellenos en m³, como partida propia o declarado dentro del APU de albañilería
- R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]

### Albañilería confinada
- R08: NCh353 6.2.1 a 6.2.3: barras por masa nominal x largo total (resistentes, repartición, suples y estribos); por diámetro y largo comercial indicar número de barras y masa; barras de más de 12 m aparte
- R09: NCh353 6.2.4 y 6.2.5: +5 % sobre la masa medida (4 % trabas, patas, guías, elementos de posición y despuntes; 1 % sobredimensión), salvo que el proyecto cuantifique trabas y patas
- R10: NCh353 6.2.7 y 6.2.8: verticales de pilares y muros empalmadas 40 d en el piso superior; penetración en fundaciones no detallada = 40 d (la norma impresa dice 'quedando 10,1 m sobre el fondo', errata evidente: interpretar 0.1 m) [Por verificar la errata]
- R14: NCh353 7.1 a 7.3: cadenas por volumen real medido como vigas; pilares de refuerzo sin el hormigón entre endentados; apoyo de dintel no indicado = 0.30 m por extremo
- R15: NCh353 8.1.1 y Tabla 4.a: albañilería por superficie efectiva; vanos en ladrillo a máquina: <1.5 m² 0 % (50 % con pilar), 1.5 a 3.0 m² 50 % (75 %), >3.0 m² 100 %. Tabla 4.b para ladrillo a mano
- R16: NCh353 8.1.3: se descuentan de la albañilería los espacios de cadenas, dinteles, vigas y pilares embutidos; muros endentados desde el ladrillo más saliente
- R17: NCh353 8.1.6: refuerzos de acero en las juntas entre hiladas (escalerilla) se incluyen en la partida de albañilería, no en fierro
- R18: NCh353 8.1.2 y 8.1.4: partidas separadas por naturaleza y espesor; la mano de obra de formar vanos de 2 m² o más va en el precio unitario del muro
- R32: NCh204:2020: masas nominales 6 mm 0.222, 8 mm 0.395, 10 mm 0.617, 12 mm 0.888, 16 mm 1.58 kg/m; largos normales 6 y 12 m; diámetros hasta 16 mm en rollo; tolerancia de masa ±3.5 %
- R34: NCh169.Of2001: clases MqM, MqP, MqH y grados 1, 2, 3; tolerancias largo ±5 mm, ancho y alto ±3 mm. Armada exige grado 1 o 2 [Por verificar en NCh1928]; confinada exige MqM o MqP (NCh2123 5.2.1)
- R35: NCh2256/1.Of2001: grados de mortero M0.5 a M30; mortero de junta con Dn de arena <= 1/3 de la junta, consistencia 180 a 220 mm, resistencia según NCh1928 o NCh2123
- R36: Junta de albañilería de 10 a 15 mm (rango de validez de NCh2123 y NCh1928): fija el escantillón y el número de hiladas y de filas de escalerilla
- R40: Anclajes y empalmes: NCh1928 6.1.5 traslapo >= 40 veces el menor diámetro; en huecos menores que 6 veces el diámetro mayor solo empalme soldado, mecánico o traslapo dentro de la cadena; 6.1.6 anclajes según hormigón armado. ACI 318-19 25.4.2.3: ld = fy ψt ψe ψg db / (2.1 λ √f'c) para barras <= 19 mm con espaciamiento y recubrimiento suficientes, >= 300 mm; 25.5.2.1 traslapo clase B = 1.3 ld; Tabla 25.3.1 ganchos de 90° y 180° con diámetro interior 6 db. A440-280H con G25: ld = 27 d y clase B = 35 d (40 d cubre); A630-420H con G25: ld = 40 d y clase B = 52 d (40 d no alcanza). NCh430 adopta ACI 318-05 [Por verificar que la ecuación coincide]
- R50: Albañilería confinada (NCh2123 vía apunte INACAP) [Por verificar]: espesor >= 14 cm con ladrillo a máquina y 15 cm artesanal; paño <= 12.5 m² y <= 6 m entre pilares; pilares en bordes libres e intersecciones; cadenas a nivel de piso y techo de ancho >= espesor del muro; mortero 5 MPa artesanal y 10 MPa a máquina
- R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]

### Hormigón armado
- R07: NCh353 6.1: hormigón por volumen sin descontar armaduras ni tuberías hasta 0.25 m; se descuentan aberturas mayores a 0.05 m²; partidas separadas por tipo de hormigón, elemento y moldaje
- R08: NCh353 6.2.1 a 6.2.3: barras por masa nominal x largo total (resistentes, repartición, suples y estribos); por diámetro y largo comercial indicar número de barras y masa; barras de más de 12 m aparte
- R09: NCh353 6.2.4 y 6.2.5: +5 % sobre la masa medida (4 % trabas, patas, guías, elementos de posición y despuntes; 1 % sobredimensión), salvo que el proyecto cuantifique trabas y patas
- R10: NCh353 6.2.7 y 6.2.8: verticales de pilares y muros empalmadas 40 d en el piso superior; penetración en fundaciones no detallada = 40 d (la norma impresa dice 'quedando 10,1 m sobre el fondo', errata evidente: interpretar 0.1 m) [Por verificar la errata]
- R11: NCh353 6.2.6 y 6.2.10: alambre de amarre en el precio unitario; enfierradura subcontratada a suma alzada: +1 % sobre cubicación de planos
- R12: NCh353 6.3: emplantillados por superficie o volumen indicando espesor; fundaciones por volumen real; radier por superficie con espesor
- R13: NCh353 6.4 a 6.6 y 6.10.2: alturas de muros entre niveles superiores de losas o hasta el fondo de viga; vigas por luz libre; intersecciones en orden 1° pilares y muros, 2° vigas, 3° losas
- R29: Moldaje por superficie de contacto con el hormigón, en partida por elemento (NCh353 6.1.4); incluye fondos bajo dinteles y tapas de extremos; madera tradicional ~3 usos (hasta 5)
- R32: NCh204:2020: masas nominales 6 mm 0.222, 8 mm 0.395, 10 mm 0.617, 12 mm 0.888, 16 mm 1.58 kg/m; largos normales 6 y 12 m; diámetros hasta 16 mm en rollo; tolerancia de masa ±3.5 %
- R33: NCh170:2016: grados G05 a G60 por resistencia cilíndrica fc' (MPa); la designación incluye grado, fracción defectuosa, tamaño máximo de árido y asentamiento. EETT con 'H-xx' usan la designación antigua: pedir el grado G equivalente al proveedor [Por verificar la equivalencia]
- R40: Anclajes y empalmes: NCh1928 6.1.5 traslapo >= 40 veces el menor diámetro; en huecos menores que 6 veces el diámetro mayor solo empalme soldado, mecánico o traslapo dentro de la cadena; 6.1.6 anclajes según hormigón armado. ACI 318-19 25.4.2.3: ld = fy ψt ψe ψg db / (2.1 λ √f'c) para barras <= 19 mm con espaciamiento y recubrimiento suficientes, >= 300 mm; 25.5.2.1 traslapo clase B = 1.3 ld; Tabla 25.3.1 ganchos de 90° y 180° con diámetro interior 6 db. A440-280H con G25: ld = 27 d y clase B = 35 d (40 d cubre); A630-420H con G25: ld = 40 d y clase B = 52 d (40 d no alcanza). NCh430 adopta ACI 318-05 [Por verificar que la ecuación coincide]
- R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]

### Techumbre y cubierta
- R20: NCh353 9.5 y 9.6: estructura de techumbre por superficie proyectada horizontal (incluye canes de una pieza); aleros por ml con ancho; forros, canes a la vista y frontones aparte
- R21: NCh353 13: cubiertas por superficie de vertientes sin traslapos; incluye elementos intermedios entre cubierta y estructura (costaneras, entablado)
- R22: NCh353 12: caballetes, limatesas y forros por longitud sin traslapos y con ancho desarrollado; canales y bajadas por longitud incluyendo curvas, tes y ves; anclajes en el precio
- R23: NCh353 14: aislación e impermeabilización en láminas por superficie con retornos y sin traslapos; vanos <=1 m² no se descuentan, mayores se descuentan en el exceso
- R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]

### Terminaciones
- R19: NCh353 9.1.1: tabiques de madera por longitud con altura, sin descontar vanos menores a 3 m² si el dintel es del mismo material
- R23: NCh353 14: aislación e impermeabilización en láminas por superficie con retornos y sin traslapos; vanos <=1 m² no se descuentan, mayores se descuentan en el exceso
- R24: NCh353 15 y 16: pavimentos y cielos por superficie efectiva entre paramentos terminados; cielo incluye sobre vanos sin dintel; radier en partida aparte del pavimento
- R25: NCh353 18.2: cerámicos por superficie a la vista, sin descontar superficies no revestidas menores a 0.5 m²; biselado 0.5 ml por m² en el APU
- R26: NCh353 11: estucos por superficie proyectada; espesor supuesto 2.5 cm salvo EETT; descuento de vanos según 11.3
- R27: NCh353 24: pinturas por superficie recubierta, partida por clase de pintura
- R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]

### Movimiento de tierras
- R03: NCh353 5.1.5 y Tabla 1: sobreancho de excavación solo si la fundación lleva moldaje (0.20 m por lado hasta 0.5 m de alto; 0.40 hasta 1.0; 0.50 hasta 1.5; 0.70 hasta 2.5; 0.80 sobre 2.5); con talud, 0.10 m por lado (5.1.6); zanja de cañería: diámetro exterior + 0.45 m (5.1.7)
- R04: NCh353 5.2 y Tabla 2: transporte de excedentes = volumen en banco + esponjamiento (10, 15, 25, 30 % o más según terreno); el asentamiento en el transporte no se descuenta
- R05: NCh353 5.3.1: rellenos por volumen neto rellenado; rellenos de excavaciones de fundación en partida separada de los rellenos de piso; compactación estimable con Tabla 3
- R06: NCh353 5.4.1: escarpes por superficie explanada
- R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]

## Lista de control por partida

### Excavaciones y rellenos
- Regla R03: NCh353 5.1.5 y Tabla 1: sobreancho de excavación solo si la fundación lleva moldaje (0.20 m por lado hasta 0.5 m de alto; 0.40 hasta 1.0; 0.50 hasta 1.5; 0.70 hasta 2.5; 0.80 sobre 2.5); con talud, 0.10 m por lado (5.1.6); zanja de cañería: diámetro exterior + 0.45 m (5.1.7)
- Regla R04: NCh353 5.2 y Tabla 2: transporte de excedentes = volumen en banco + esponjamiento (10, 15, 25, 30 % o más según terreno); el asentamiento en el transporte no se descuenta
- Regla R05: NCh353 5.3.1: rellenos por volumen neto rellenado; rellenos de excavaciones de fundación en partida separada de los rellenos de piso; compactación estimable con Tabla 3
- Regla R06: NCh353 5.4.1: escarpes por superficie explanada
- Regla R44: Visita a terreno y lista de antecedentes (accesos, agua, energía, botaderos, suelo, napa, mano de obra local) antes de cerrar precios
- Regla R47: Las EETT fijan el alcance de cada partida (dónde va, qué incluye) y prevalecen sobre la costumbre
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]
- Error X04: Unidad equivocada (m² con valor de m³) o magnitud incoherente -> chequeo: Unidad contra magnitud: espesor implícito = volumen / área
- Error X06: Alcance de EETT ignorado (cerámica en todo el interior; relleno sobre la huella) -> chequeo: Leer la EETT de cada partida antes de cubicarla y anotar su alcance en Datos
- Error X10: Coincidencia artificial: calzar con la referencia -> chequeo: Recubicación ciega antes de mirar la referencia; coincidencias exactas se revisan igual

### Hormigones (fundación, sobrecimiento, cadena)
- Regla R01: NCh353 1.3: las pérdidas (despuntes, mortero caído, envases rotos, excesos) no van en la cubicación sino en el rendimiento del precio unitario
- Regla R02: NCh353 4.4: lo que pertenece a la vez a más de un elemento se mide una sola vez (esquinas, encuentros, cruces)
- Regla R07: NCh353 6.1: hormigón por volumen sin descontar armaduras ni tuberías hasta 0.25 m; se descuentan aberturas mayores a 0.05 m²; partidas separadas por tipo de hormigón, elemento y moldaje
- Regla R12: NCh353 6.3: emplantillados por superficie o volumen indicando espesor; fundaciones por volumen real; radier por superficie con espesor
- Regla R13: NCh353 6.4 a 6.6 y 6.10.2: alturas de muros entre niveles superiores de losas o hasta el fondo de viga; vigas por luz libre; intersecciones en orden 1° pilares y muros, 2° vigas, 3° losas
- Regla R14: NCh353 7.1 a 7.3: cadenas por volumen real medido como vigas; pilares de refuerzo sin el hormigón entre endentados; apoyo de dintel no indicado = 0.30 m por extremo
- Regla R28: NCh353 Anexo A: el APU se desglosa en materiales, mano de obra (rendimiento y leyes sociales), herramientas o equipos menores y subcontratos
- Regla R30: NCh1156/1 a /3: secciones 0 informaciones generales, 1 gastos adicionales, obras provisionales y trabajos previos, 2 obras de construcción (2/1 obra gruesa, 2/2 terminaciones), 3 instalaciones, 4 obras complementarias; la medición de cada partida remite a NCh353 (7.8)
- Regla R31: Partidas medibles, presupuestables y controlables, con código y unidad; una partida omitida es pérdida para el contratista
- Regla R33: NCh170:2016: grados G05 a G60 por resistencia cilíndrica fc' (MPa); la designación incluye grado, fracción defectuosa, tamaño máximo de árido y asentamiento. EETT con 'H-xx' usan la designación antigua: pedir el grado G equivalente al proveedor [Por verificar la equivalencia]
- Regla R41: Presupuesto de venta = costo directo + gastos generales de obra + gastos generales indirectos (financiero, garantías, oficina central) + imprevistos + utilidad + IVA
- Regla R42: Costo de materiales puesto en obra, cotizado por proveedor; incluye pérdidas por robo, mal almacenamiento y transporte; P.U. = total de la partida / cantidad
- Regla R43: Mano de obra: rendimiento real (trabajo productivo, contributorio y no contributorio) y costo con leyes sociales
- Regla R45: Incertidumbre: por partida relevante, valores optimista, más probable y pesimista; simular o usar PERT para el rango del costo
- Regla R46: Precios de referencia: tabla MINVU DS27 de la región y cotizaciones; justificar cada P.U.
- Regla R48: Plano sin cotas no se cubica: se consulta; trabajar por ejes y pisos sin agrupar
- Regla R49: NCh1928 7.1: todo hueco que aloja armadura se llena con hormigón de relleno, por etapas de altura limitada según el hueco (5 cm: 30 cm; 8 cm: 120 cm; >= 12 cm: 240 cm). Se cubica el volumen de huecos rellenos en m³, como partida propia o declarado dentro del APU de albañilería
- Regla R50: Albañilería confinada (NCh2123 vía apunte INACAP) [Por verificar]: espesor >= 14 cm con ladrillo a máquina y 15 cm artesanal; paño <= 12.5 m² y <= 6 m entre pilares; pilares en bordes libres e intersecciones; cadenas a nivel de piso y techo de ancho >= espesor del muro; mortero 5 MPa artesanal y 10 MPa a máquina
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]
- Error X11: Verificación circular: supuesto elegido porque coincide -> chequeo: Un supuesto nunca se justifica por coincidir; marcarlo S o I y dar su sensibilidad
- Error X12: Error de fórmula o de rango en la planilla -> chequeo: Hoja Control planilla contra script de Python; recalc sin errores; auditor de estilo
- Error X14: Elemento exigido por EETT o norma sin partida (armadura de sobrecimiento; refuerzo horizontal en base de vanos) -> chequeo: Recorrer EETT capítulo por capítulo y los mínimos de R37-R38 contra el itemizado; lo que falte va a partidas omitidas
- Error X16: Brecha presupuestaria por alcance mal definido -> chequeo: Lista de supuestos y exclusiones aceptada por el cliente antes de cubicar
- Error X17: Designación de hormigón obsoleta (H-xx por cubo) usada para cotizar -> chequeo: Traducir a grado G de NCh170:2016 con el proveedor antes del APU
- Error X21: Hormigón de relleno de huecos sin partida ni APU en albañilería armada -> chequeo: Volumen de huecos con armadura (NCh1928 7.1) en m³: partida propia o declarado en el APU de albañilería
- Error X22: Ejecutar con una norma parcial, secundaria o ausente sin advertirlo -> chequeo: Tabla de literatura por sistema (cerebro.py literatura) revisada; lo que no esté vista se pide a Nicolás antes de ejecutar

### Radieres y emplantillados
- Regla R12: NCh353 6.3: emplantillados por superficie o volumen indicando espesor; fundaciones por volumen real; radier por superficie con espesor
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]

### Moldajes
- Regla R29: Moldaje por superficie de contacto con el hormigón, en partida por elemento (NCh353 6.1.4); incluye fondos bajo dinteles y tapas de extremos; madera tradicional ~3 usos (hasta 5)
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]

### Enfierraduras, escalerillas y tensores
- Regla R01: NCh353 1.3: las pérdidas (despuntes, mortero caído, envases rotos, excesos) no van en la cubicación sino en el rendimiento del precio unitario
- Regla R02: NCh353 4.4: lo que pertenece a la vez a más de un elemento se mide una sola vez (esquinas, encuentros, cruces)
- Regla R08: NCh353 6.2.1 a 6.2.3: barras por masa nominal x largo total (resistentes, repartición, suples y estribos); por diámetro y largo comercial indicar número de barras y masa; barras de más de 12 m aparte
- Regla R09: NCh353 6.2.4 y 6.2.5: +5 % sobre la masa medida (4 % trabas, patas, guías, elementos de posición y despuntes; 1 % sobredimensión), salvo que el proyecto cuantifique trabas y patas
- Regla R10: NCh353 6.2.7 y 6.2.8: verticales de pilares y muros empalmadas 40 d en el piso superior; penetración en fundaciones no detallada = 40 d (la norma impresa dice 'quedando 10,1 m sobre el fondo', errata evidente: interpretar 0.1 m) [Por verificar la errata]
- Regla R11: NCh353 6.2.6 y 6.2.10: alambre de amarre en el precio unitario; enfierradura subcontratada a suma alzada: +1 % sobre cubicación de planos
- Regla R17: NCh353 8.1.6: refuerzos de acero en las juntas entre hiladas (escalerilla) se incluyen en la partida de albañilería, no en fierro
- Regla R32: NCh204:2020: masas nominales 6 mm 0.222, 8 mm 0.395, 10 mm 0.617, 12 mm 0.888, 16 mm 1.58 kg/m; largos normales 6 y 12 m; diámetros hasta 16 mm en rollo; tolerancia de masa ±3.5 %
- Regla R36: Junta de albañilería de 10 a 15 mm (rango de validez de NCh2123 y NCh1928): fija el escantillón y el número de hiladas y de filas de escalerilla
- Regla R37: NCh1928 6.4.1.1 y 6.4.3.2 a 6.4.3.5, 6.4.3.8: espesor >= máx(1/25 de la menor dimensión libre; 14 cm); cuantía >= 0.06 % por dirección y >= 0.15 % total, contando solo barras que recorren todo el ancho o alto; vertical >= 8 mm a <= 6e y <= 120 cm; en cada borde libre y encuentro al menos una barra de 12 mm; verticales fijadas cada <= 300 d y <= 3 m
- Regla R38: NCh1928 6.1.2 y 6.4.3.6: armadura de junta de diámetro <= mitad del espesor de la junta; refuerzo horizontal en el remate de cimientos, base y remate de vanos, nivel de piso, techo y parapetos; verticales >= 10 mm a cada lado de vano, prolongadas 60 cm más allá de las esquinas
- Regla R40: Anclajes y empalmes: NCh1928 6.1.5 traslapo >= 40 veces el menor diámetro; en huecos menores que 6 veces el diámetro mayor solo empalme soldado, mecánico o traslapo dentro de la cadena; 6.1.6 anclajes según hormigón armado. ACI 318-19 25.4.2.3: ld = fy ψt ψe ψg db / (2.1 λ √f'c) para barras <= 19 mm con espaciamiento y recubrimiento suficientes, >= 300 mm; 25.5.2.1 traslapo clase B = 1.3 ld; Tabla 25.3.1 ganchos de 90° y 180° con diámetro interior 6 db. A440-280H con G25: ld = 27 d y clase B = 35 d (40 d cubre); A630-420H con G25: ld = 40 d y clase B = 52 d (40 d no alcanza). NCh430 adopta ACI 318-05 [Por verificar que la ecuación coincide]
- Regla R50: Albañilería confinada (NCh2123 vía apunte INACAP) [Por verificar]: espesor >= 14 cm con ladrillo a máquina y 15 cm artesanal; paño <= 12.5 m² y <= 6 m entre pilares; pilares en bordes libres e intersecciones; cadenas a nivel de piso y techo de ancho >= espesor del muro; mortero 5 MPa artesanal y 10 MPa a máquina
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]
- Error X01: Doble conteo en esquinas y encuentros en T -> chequeo: Muro pasante entero y el que llega cortado en la cara (NCh353 4.4); contraste con área de muros / espesor
- Error X07: Pérdidas metidas en la cubicación, o criterio confundido con error -> chequeo: Cantidad neta en Cubicación (NCh353 1.3); pérdidas solo en APU; conciliación declara el criterio
- Error X08: Masa por metro mal tomada (escalerilla al doble) -> chequeo: Masa = π/4 d² ρ por alambre; contrastar kg/m² de muro con referencias
- Error X09: Armadura sin estribos, traslapos, patas ni penetración en fundación -> chequeo: kg/m teórico del elemento con NCh353 6.2.4 a 6.2.8 contra la cantidad
- Error X14: Elemento exigido por EETT o norma sin partida (armadura de sobrecimiento; refuerzo horizontal en base de vanos) -> chequeo: Recorrer EETT capítulo por capítulo y los mínimos de R37-R38 contra el itemizado; lo que falte va a partidas omitidas
- Error X18: Fierro sin número de barras por diámetro y largo comercial -> chequeo: Tabla de corte: por diámetro, largo de 6 o 12 m, número de barras y masa (NCh353 6.2.2; NCh204 4.3.2)
- Error X19: Diseño bajo mínimos normativos sin advertir al cliente (Sede C: 10 mm en encuentros; NCh1928 6.4.3.5 exige 12 mm) -> chequeo: Contrastar EETT con R37 a R40 y reportar como consulta, sin rediseñar
- Error X20: Escalerilla presupuestada como fierro aparte y además dentro del m² de albañilería -> chequeo: Ubicar la escalerilla en una sola partida (NCh353 8.1.6) y decirlo en el itemizado
- Error X22: Ejecutar con una norma parcial, secundaria o ausente sin advertirlo -> chequeo: Tabla de literatura por sistema (cerebro.py literatura) revisada; lo que no esté vista se pide a Nicolás antes de ejecutar
- Error X23: EETT contradictorias entre cláusulas para un mismo elemento (Sede C: cadena 6φ10 en 3.4 y 12 mm en 3.5) -> chequeo: Cruzar cada elemento entre todas las cláusulas de EETT que lo nombran; la contradicción va a consultas con su efecto en kg

### Albañilería
- Regla R01: NCh353 1.3: las pérdidas (despuntes, mortero caído, envases rotos, excesos) no van en la cubicación sino en el rendimiento del precio unitario
- Regla R02: NCh353 4.4: lo que pertenece a la vez a más de un elemento se mide una sola vez (esquinas, encuentros, cruces)
- Regla R15: NCh353 8.1.1 y Tabla 4.a: albañilería por superficie efectiva; vanos en ladrillo a máquina: <1.5 m² 0 % (50 % con pilar), 1.5 a 3.0 m² 50 % (75 %), >3.0 m² 100 %. Tabla 4.b para ladrillo a mano
- Regla R16: NCh353 8.1.3: se descuentan de la albañilería los espacios de cadenas, dinteles, vigas y pilares embutidos; muros endentados desde el ladrillo más saliente
- Regla R17: NCh353 8.1.6: refuerzos de acero en las juntas entre hiladas (escalerilla) se incluyen en la partida de albañilería, no en fierro
- Regla R18: NCh353 8.1.2 y 8.1.4: partidas separadas por naturaleza y espesor; la mano de obra de formar vanos de 2 m² o más va en el precio unitario del muro
- Regla R19: NCh353 9.1.1: tabiques de madera por longitud con altura, sin descontar vanos menores a 3 m² si el dintel es del mismo material
- Regla R28: NCh353 Anexo A: el APU se desglosa en materiales, mano de obra (rendimiento y leyes sociales), herramientas o equipos menores y subcontratos
- Regla R30: NCh1156/1 a /3: secciones 0 informaciones generales, 1 gastos adicionales, obras provisionales y trabajos previos, 2 obras de construcción (2/1 obra gruesa, 2/2 terminaciones), 3 instalaciones, 4 obras complementarias; la medición de cada partida remite a NCh353 (7.8)
- Regla R31: Partidas medibles, presupuestables y controlables, con código y unidad; una partida omitida es pérdida para el contratista
- Regla R34: NCh169.Of2001: clases MqM, MqP, MqH y grados 1, 2, 3; tolerancias largo ±5 mm, ancho y alto ±3 mm. Armada exige grado 1 o 2 [Por verificar en NCh1928]; confinada exige MqM o MqP (NCh2123 5.2.1)
- Regla R35: NCh2256/1.Of2001: grados de mortero M0.5 a M30; mortero de junta con Dn de arena <= 1/3 de la junta, consistencia 180 a 220 mm, resistencia según NCh1928 o NCh2123
- Regla R36: Junta de albañilería de 10 a 15 mm (rango de validez de NCh2123 y NCh1928): fija el escantillón y el número de hiladas y de filas de escalerilla
- Regla R38: NCh1928 6.1.2 y 6.4.3.6: armadura de junta de diámetro <= mitad del espesor de la junta; refuerzo horizontal en el remate de cimientos, base y remate de vanos, nivel de piso, techo y parapetos; verticales >= 10 mm a cada lado de vano, prolongadas 60 cm más allá de las esquinas
- Regla R39: NCh1928 A.3.2 y A.4: mortero fm >= 10 MPa (fracción defectuosa 4 %), retentividad >= 70 %; sin ensayos, 1:0.22:4 en peso (cemento:cal:arena) con cono <= 18 cm; árido del hormigón de relleno <= 12.5 mm; resistencia del relleno 17.5 MPa [Por verificar: cifra del curso, ilegible en A.4]
- Regla R41: Presupuesto de venta = costo directo + gastos generales de obra + gastos generales indirectos (financiero, garantías, oficina central) + imprevistos + utilidad + IVA
- Regla R42: Costo de materiales puesto en obra, cotizado por proveedor; incluye pérdidas por robo, mal almacenamiento y transporte; P.U. = total de la partida / cantidad
- Regla R43: Mano de obra: rendimiento real (trabajo productivo, contributorio y no contributorio) y costo con leyes sociales
- Regla R45: Incertidumbre: por partida relevante, valores optimista, más probable y pesimista; simular o usar PERT para el rango del costo
- Regla R46: Precios de referencia: tabla MINVU DS27 de la región y cotizaciones; justificar cada P.U.
- Regla R48: Plano sin cotas no se cubica: se consulta; trabajar por ejes y pisos sin agrupar
- Regla R49: NCh1928 7.1: todo hueco que aloja armadura se llena con hormigón de relleno, por etapas de altura limitada según el hueco (5 cm: 30 cm; 8 cm: 120 cm; >= 12 cm: 240 cm). Se cubica el volumen de huecos rellenos en m³, como partida propia o declarado dentro del APU de albañilería
- Regla R50: Albañilería confinada (NCh2123 vía apunte INACAP) [Por verificar]: espesor >= 14 cm con ladrillo a máquina y 15 cm artesanal; paño <= 12.5 m² y <= 6 m entre pilares; pilares en bordes libres e intersecciones; cadenas a nivel de piso y techo de ancho >= espesor del muro; mortero 5 MPa artesanal y 10 MPa a máquina
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]
- Error X01: Doble conteo en esquinas y encuentros en T -> chequeo: Muro pasante entero y el que llega cortado en la cara (NCh353 4.4); contraste con área de muros / espesor
- Error X02: Vanos descontados al 100 % o no descontados, sin la Tabla 4 de NCh353 -> chequeo: Lista de vanos con área y si llevan pilar; aplicar NCh353 Tabla 4.a fila por fila
- Error X03: Escala mal calibrada o asumida (vistas a escalas distintas en la misma lámina) -> chequeo: Calibrar cada vista con dos cotas independientes y declarar el factor
- Error X07: Pérdidas metidas en la cubicación, o criterio confundido con error -> chequeo: Cantidad neta en Cubicación (NCh353 1.3); pérdidas solo en APU; conciliación declara el criterio
- Error X12: Error de fórmula o de rango en la planilla -> chequeo: Hoja Control planilla contra script de Python; recalc sin errores; auditor de estilo
- Error X15: Plano o EETT en versión desactualizada -> chequeo: Registrar versión y fecha de cada documento en Datos
- Error X20: Escalerilla presupuestada como fierro aparte y además dentro del m² de albañilería -> chequeo: Ubicar la escalerilla en una sola partida (NCh353 8.1.6) y decirlo en el itemizado
- Error X21: Hormigón de relleno de huecos sin partida ni APU en albañilería armada -> chequeo: Volumen de huecos con armadura (NCh1928 7.1) en m³: partida propia o declarado en el APU de albañilería
- Error X22: Ejecutar con una norma parcial, secundaria o ausente sin advertirlo -> chequeo: Tabla de literatura por sistema (cerebro.py literatura) revisada; lo que no esté vista se pide a Nicolás antes de ejecutar

### Techumbre y cubierta
- Regla R20: NCh353 9.5 y 9.6: estructura de techumbre por superficie proyectada horizontal (incluye canes de una pieza); aleros por ml con ancho; forros, canes a la vista y frontones aparte
- Regla R21: NCh353 13: cubiertas por superficie de vertientes sin traslapos; incluye elementos intermedios entre cubierta y estructura (costaneras, entablado)
- Regla R23: NCh353 14: aislación e impermeabilización en láminas por superficie con retornos y sin traslapos; vanos <=1 m² no se descuentan, mayores se descuentan en el exceso
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]
- Error X03: Escala mal calibrada o asumida (vistas a escalas distintas en la misma lámina) -> chequeo: Calibrar cada vista con dos cotas independientes y declarar el factor
- Error X13: Rótulo del plano contradice el dibujo (pendiente 60 % rotulada, 40 % dibujada) -> chequeo: Medir en corte y elevación; reportar la contradicción como consulta

### Hojalatería (canales, bajadas, forros)
- Regla R22: NCh353 12: caballetes, limatesas y forros por longitud sin traslapos y con ancho desarrollado; canales y bajadas por longitud incluyendo curvas, tes y ves; anclajes en el precio
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]
- Error X05: Cifra copiada entre partidas (canales = bajadas = forros) -> chequeo: Buscar valores repetidos en el itemizado y justificar cada uno

### Cerámicos y revestimientos
- Regla R25: NCh353 18.2: cerámicos por superficie a la vista, sin descontar superficies no revestidas menores a 0.5 m²; biselado 0.5 ml por m² en el APU
- Regla R47: Las EETT fijan el alcance de cada partida (dónde va, qué incluye) y prevalecen sobre la costumbre
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]
- Error X06: Alcance de EETT ignorado (cerámica en todo el interior; relleno sobre la huella) -> chequeo: Leer la EETT de cada partida antes de cubicarla y anotar su alcance en Datos
- Error X10: Coincidencia artificial: calzar con la referencia -> chequeo: Recubicación ciega antes de mirar la referencia; coincidencias exactas se revisan igual

### Pavimentos y cielos
- Regla R24: NCh353 15 y 16: pavimentos y cielos por superficie efectiva entre paramentos terminados; cielo incluye sobre vanos sin dintel; radier en partida aparte del pavimento
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]

### Estucos y pinturas
- Regla R26: NCh353 11: estucos por superficie proyectada; espesor supuesto 2.5 cm salvo EETT; descuento de vanos según 11.3
- Regla R27: NCh353 24: pinturas por superficie recubierta, partida por clase de pintura
- Regla R51: Antes de ejecutar: listar por sistema las fuentes que citan sus reglas; si una está parcial, secundaria o falta, pedirla a Nicolás y esperar; sin ella se trabaja solo con su OK y con las reglas afectadas marcadas [Por verificar]

## Lecturas pendientes
- NCh1928 en copia de mejor resolución, solo para A.4 (resistencia del hormigón de relleno) (F_NCh1928, F_cursoInsp)
- NCh2123 completa (requisitos de pilares y cadenas), no solo la modificación de materiales (F_NCh2123)
- ACI 318-05 o NCh430 completa para confirmar que ld y las clases de empalme coinciden con 318-19 (R40) (F_NCh430, F_ACI318)
- Ficha técnica de escalerilla de fabricante para el kg/m² de muro (X08, X20) (F_fichaEscalerilla, F_FSPR2019)
- Manual de tolerancias CDT para cotejar escantillón y alturas (F_CDT_tol)
- Tabla MINVU de la región del cliente para APU (F_MINVU_precios)
- Capítulo QTO de Civil 3D para movimiento de tierras (F_C3D_QTO)
- Ensayo de cono de morteros solo si un encargo pide control de calidad (F_NCh2257)

## Fuentes
- F_NCh353 [vista]: NCh353.Of2000 Construcción - Cubicación de obras de edificación - Requisitos (texto completo leído, copia escaneada)
- F_NCh1156 [vista]: NCh1156/1 a /3.Of1999 Especificaciones técnicas - Ordenación y designación de partidas (partes 1, 2 y 3 leídas)
- F_NCh169 [vista]: NCh169.Of2001 Ladrillos cerámicos - Clasificación y requisitos
- F_NCh204 [vista]: NCh204:2020 Barras laminadas en caliente para hormigón armado (tabla 4 masas nominales; 4.3.2 largos; 4.6 tolerancias)
- F_NCh2123 [parcial]: NCh2123.Of1997 Mod. 2003 Albañilería confinada (copia parcial: solo cláusula 5 Materiales y Anexo B)
- F_NCh1928 [vista]: NCh1928.Of1993 Mod. 2009 Albañilería armada (copia de 54 ppi leída página a página: cláusulas 6, 7 y Anexo A; la resistencia del hormigón de relleno en A.4 no se lee)
- F_ACI318 [vista]: ACI 318-19 Building Code Requirements for Structural Concrete (cap. 25: 25.3 ganchos, 25.4 desarrollo, 25.5 empalmes; copia en unidades inch-pound)
- F_NCh2123_inacap [secundaria]: INACAP, apunte de albañilería confinada que resume NCh2123 (fuente secundaria; texto escaneado de baja calidad)
- F_fichaEscalerilla [falta]: Ficha técnica de escalerilla de un fabricante (masa por metro y ancho según espesor de muro)
- F_NCh430 [parcial]: NCh430-2007 Hormigón armado (solo las modificaciones nacionales al ACI 318-05; anclajes y empalmes se leyeron en ACI 318-19, no en la versión 318-05 que adopta)
- F_NCh170 [vista]: NCh170:2016 Hormigón - Requisitos generales (grados G por resistencia cilíndrica; designación 5.2)
- F_NCh2256 [vista]: NCh2256/1.Of2001 Morteros - Requisitos generales (grados M; 7.1 mortero de junta)
- F_NCh2257 [vista]: NCh2257/3.Of1996 Morteros - Consistencia por asentamiento de cono (método de ensayo)
- F_Solminihac [vista]: Solminihac y Thenoux, Procesos y Técnicas de Construcción, 5ª ed., Ediciones UC (cap. 5 presupuesto; cap. 10 albañilería; 14.3 techumbre)
- F_cursoInsp [secundaria]: Curso 'Capacitación Inspectores Albañilería' (resume NCh1928 y NCh2123; fuente secundaria)
- F_guiaMineduc [secundaria]: Mineduc, guía 'Cubicación de materiales e insumos' (resume NCh353; reemplazada por el texto de la norma) — https://www.curriculumnacional.cl/614/articles-228610_recurso_6.docx
- F_CDT_tol [secundaria]: CDT, Manual de tolerancias para edificaciones — https://cdt.cl/download/76541
- F_MINVU_precios [secundaria]: MINVU, Tabla de precios referenciales DS27 por región (UF por partida) — https://www.minvu.gob.cl/wp-content/uploads/2026/09/TABLA-DE-PRECIOS-REFERENCIALES-DS27-REGION-DE-AYSEN-2026.pdf
- F_tesisPerdidas [secundaria]: Hidalgo (2008), U. de Chile: pérdidas de materiales en edificación en extensión — https://repositorio.uchile.cl/handle/2250/104976
- F_UDD_brechas [secundaria]: Mancilla (2023), UDD: brechas presupuestarias en proyectos de construcción — https://repositorio.udd.cl/bitstreams/685a8b7e-a239-4bf3-bbee-9ae6817c5ca8/download
- F_C3D_QTO [secundaria]: Mastering AutoCAD Civil 3D (Sybex), cap. Quantity Takeoff; Autodesk Help QTO — https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-Tutorials/files/GUID-E870AEEA-4E45-480B-9DA3-BE6846A41A8F.htm
- F_ACAD_area [secundaria]: AutoCAD: MEASUREGEOM, AREA/LIST, hatch con campos, DATAEXTRACTION — https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-LT/files/GUID-5D5B0EE1-DD90-47AE-8A55-642FBFF5E4E4.htm
- F_FSPR2019 [secundaria]: Presupuestos FSPR 2019: escalerilla 1.03 a 1.13 kg/m² de muro — https://subinterior-2018.interior.gob.cl/media/2019/02/ANEXO-3.1-PRESUPUESTO-SEDE-SOCIAL.pdf
- F_SedeC [caso]: Caso propio: Sede C FSPR 2023 (revisión en frío y conciliación)
