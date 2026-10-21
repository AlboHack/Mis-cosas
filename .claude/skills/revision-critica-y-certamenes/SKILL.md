---
name: "revision-critica-y-certamenes"
description: "Usar para revisión crítica o pre-entrega de un informe o diseño, preparar certámenes, abordar un problema abierto o cuando se pregunta qué se está pasando por alto."
---

# Revisión crítica y preparación de certámenes

Elegir el modo según la tarea.

## Modo A: Revisión crítica y pre-entrega
Evaluar con el rigor de un profesor o ayudante UTFSM.

1. **Auditoría de supuestos:** condiciones de borde, elasticidad de apoyos, modelo de riesgo de demanda, fórmulas de reajuste UF/IPC.
2. **Stress-test:** casos límite y vulnerabilidades (pandeo de Euler, sensibilidad a la demanda, convergencia numérica).
3. **Coherencia del informe:** cada objetivo planteado en la introducción debe responderse cuantitativamente en la conclusión. Auditar unidades y convenciones de signos.
4. **Macros pendientes:** listar todo `\pend` y `\completar{}` restante.
5. **Entrega:** lista priorizada en tres niveles (Crítico, Moderado, Pulido), cada ítem con el código LaTeX exacto de la corrección.

## Modo B: Certámenes y problemas abiertos

### Mapeo en 4 cuadrantes
- **Known Knowns:** geometría, propiedades ($EI, EA, \alpha, \nu, \rho, \mu$), grado de hiperestaticidad o indeterminación cinemática, parámetros contractuales (UF, tasa de descuento, BALI).
- **Known Unknowns:** reacciones, fuerzas internas $N_i$, desplazamientos $\Delta$, factor de fricción $f$, velocidad de onda de choque $w$, VPI/VAN/SPI.
- **Supuestos implícitos:** $EA \to \infty$ vs. $EA$ finito, pequeños desplazamientos, sección bruta no fisurada, distribución hidrostática, régimen permanente $\lambda < \mu$.
- **Trampas de certamen:** barras de fuerza cero, $\Delta T$ en sistemas isostáticos vs. hiperestáticos, apoyos inclinados, simetría/antisimetría, asentamientos de apoyo, transición laminar-turbulenta, cavitación ($P_v$), coeficientes $\alpha$ y $\beta$, compuertas curvas sumergidas, spillover de colas, paradoja de Braess, holguras en ruta crítica, activación de IMG.

### Barridos paramétricos
Plantear hipótesis en competencia y ejecutar barridos vectorizados en Python, expresando la sensibilidad en razones adimensionales ($L/h$, $\text{Re}$, $\rho = \lambda/\mu$, SPI). Si no es posible ejecutar código, entregar el script listo para correr.