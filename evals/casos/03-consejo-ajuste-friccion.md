# Caso 03: consejo sobre un ajuste que mezcla regímenes

## Mensaje
Hazme un consejo, evalúa esto desde varios aspectos. Para el informe de laboratorio de pérdidas en tuberías (tubo liso de cobre, D = 25 mm, agua a 20 °C) tengo 10 puntos con Re entre 1800 y 9000. Quiero ajustar una sola recta a log f contra log Re con todos los puntos, sacar f = a·Re^b y compararla con Blasius en la discusión. ¿Lo hago así o hay algo mejor? Entrego en 4 días.

## Verificación
- [ ] La primera línea dice que los puntos cruzan laminar, transición y turbulento, y que una sola ley de potencia los mezcla.
- [ ] Hoja de hechos con números calculados: f = 64/Re ≈ 0.0356 en Re = 1800; Blasius ≈ 0.0397 en Re = 4000 y ≈ 0.0325 en Re = 9000; Blasius válido para tubo liso con Re ≳ 4000 [Por verificar el límite en la fuente que use].
- [ ] Panel de tres a cinco voces con briefs propios del tema; ronda 1 ciega o declara que corrió en un solo agente.
- [ ] Contrainterrogatorio con posiciones anónimas y la prueba que haría cambiar de opinión a cada voz.
- [ ] Veredicto en el formato de la skill: ajuste por régimen (pendiente ≈ −1 laminar, ≈ −0.25 turbulento) y puntos de transición separados, con informe de minoría y la decisión que es de Nicolás.
- [ ] Usa `laboratorio.ajuste_lineal` sobre log-log si el paquete se instaló.
- [ ] Punto decimal; ninguna frase prohibida (regla 7).
