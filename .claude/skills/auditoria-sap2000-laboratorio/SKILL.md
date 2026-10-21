---
name: "auditoria-sap2000-laboratorio"
description: "Usar al comparar cálculo manual con SAP2000/ETABS/EPANET/HEC-RAS, procesar datos de laboratorio, analizar concesiones MOP (UF, VPI, IMG) o revisar macros pendientes de un informe."
---

# Auditoría SAP2000, laboratorio y concesiones

## 1. Convenciones antes de comparar
Declarar y mapear explícitamente:
- Manual: $N > 0$ tracción; $M > 0$ fibra inferior traccionada; $\Delta$ en la dirección de la carga virtual.
- SAP2000: desplazamientos y reacciones globales ($U_1, U_3, R_2$) y esfuerzos locales de elemento ($P, V_2, M_3$) según ejes locales 1-2-3.

## 2. Verificación independiente en Python
- Enrejados: equilibrio en nudos no usados en la resolución, método de Ritter y cinemática de cuerpo rígido ($\theta = \delta/L$).
- Vigas y marcos: integral de Mohr con Simpson $\frac{L}{6}(M_a m_a + 4 M_c m_c + M_b m_b)$, contrastada simbólicamente con SymPy.
- Diseño: $\sigma = N/A$ vs. $F_y$ (p. ej. ASTM A36) y $P_{cr} = \frac{\pi^2 EI}{(KL)^2}$.
- Si no es posible ejecutar código en la conversación, entregar el script completo listo para correr y marcar los valores como no verificados.

## 3. Tabla de comparación
Columnas: Valor teórico, Valor SAP2000, Error relativo (%). Usar booktabs y columnas S de siunitx.

Gotcha: si el valor teórico es $0$, no calcular error porcentual. Reportar `---` y declarar el residuo absoluto.

## 4. Diagnóstico de discrepancias
Revisar en este orden antes de atribuir nada a redondeo:
1. Deformación por corte: SAP2000 usa $A_v = A/\kappa$ por defecto; el cálculo manual Euler-Bernoulli supone $GA \to \infty$.
2. Self Weight Multiplier (0 vs. 1).
3. Deformación axial en marcos ($EA$ finito vs. inextensible).
4. Orientación de ejes locales 1-2-3.

Nunca atribuir una diferencia a "error de redondeo" sin haber descartado $GA_v$ y $EA$.

## 5. Datos de laboratorio
- Mínimos cuadrados con $R^2$, error estándar e intervalos de confianza.
- Propagación de incertidumbre $\delta f = \sqrt{\sum_i (\frac{\partial f}{\partial x_i} \delta x_i)^2}$, con derivadas obtenidas en SymPy.

## 6. Concesiones MOP / FICA (CIV222)
- Flujos en UF.
- $\text{VPI}_m = \sum_{t=1}^m \frac{I_t}{(1+r)^t}$ comparado con ITC.
- Reajuste tarifario $T_t = T_0(1 + \Delta \text{IPC})$ y activación de IMG.
- Matriz de riesgos: MOP, Sociedad Concesionaria, ITO.

## 7. Checkpoint de entrega
Escanear `\pend` y `\completar{...}` y clasificar cada uno en:
(a) calculado y listo para inyectar;
(b) pendiente de captura externa (`img/P1_SAP_...`, `anexos/`);
(c) análisis o conclusión en borrador.