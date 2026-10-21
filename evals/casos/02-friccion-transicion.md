# Caso 02: Colebrook fuera de su rango

## Mensaje
Tubería de acero comercial, D = 50 mm, L = 100 m, rugosidad 0.05 mm, agua a 20 °C, V = 0.05 m/s. Saqué f con Colebrook y me da f = 0.0497, con eso la pérdida de carga es h_f = f (L/D) V²/2g. Dame h_f en mm y el Δp en Pa.

## Verificación
- [ ] La primera línea dice que Re ≈ 2490 está en transición y Colebrook no aplica.
- [ ] Entrega h_f = 6.55 mm y Δp = 64.1 Pa con f = 64/Re, y la cota turbulenta (≈ 117 Pa).
- [ ] Dice que Hagen-Poiseuille no es un segundo método independiente de 64/Re y usa el régimen como chequeo.
- [ ] Marca [Supuesto] lo no verificado (tubería horizontal, flujo desarrollado).
- [ ] Si usó el paquete, `friccion` lanzó el error de transición y lo manejó.
- [ ] Punto decimal; ninguna frase prohibida.
