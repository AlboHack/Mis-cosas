# Canal Claude ↔ Antigravity

Instrucciones de trabajo de cada nodo: `PROMPT_ANTIGRAVITY.md`.

Rama `canal`, nunca se mezcla a `main`. Claude Code (jefe técnico, escribe todo el código) no corre en los equipos de Nicolás; cada nodo Antigravity ejecuta, mide y responde.

| Archivo | Lo escribe | Contenido |
|---|---|---|
| `<nodo>/PEDIDOS.md` | solo Claude | pedidos numerados P1, P2…, cada uno con comandos exactos y qué reportar |
| `<nodo>/RESPUESTAS.md` | solo el nodo | una sección por pedido, `## P<n>`, con la salida literal |
| `<nodo>/BITACORA.md` | solo el nodo | una línea por evento en el momento en que ocurre (inicio, paso, error, algo que cambió, dejó o volvió a funcionar) |

Nodos: `antigravity-pc` (Acer Nitro 5, Windows 11) y `antigravity-tablet`.

## Para el nodo Antigravity, cada vez que Nicolás diga "lee el canal"
1. `git fetch origin canal && git checkout canal && git pull origin canal`
2. Leer `agentes/canal/<tu-nodo>/PEDIDOS.md` y ejecutar los pedidos con estado `abierto` que no estén ya en tu `RESPUESTAS.md`, en orden.
3. Agregar al final de `RESPUESTAS.md` una sección por pedido con el formato de abajo. Salida literal, sin resumir ni interpretar; si un paso falla, pegar el error completo y seguir con el siguiente paso independiente.
4. `git add agentes/canal/<tu-nodo>/RESPUESTAS.md && git commit -m "canal(<tu-nodo>): respuestas P<n>" && git push origin canal`
5. Decirle a Nicolás en una línea: "Respondí P<n> en el canal".

Si quieres que Claude programe algo, agrégalo en `RESPUESTAS.md` como `## PLAN: <título>`, con qué problema resuelve, en qué equipo corre, qué datos usa y cómo se sabrá que funciona. No lo programes tú (regla 04).

```
## P<n> · <fecha> · <tu-nodo>
### Paso 1
<comando>
<salida literal>
### Paso 2
...
```

Reglas: nada de contraseñas, tokens, claves de licencia, datos financieros ni texto de mensajes privados de Aula (el repo es público). Borrados, desinstalaciones y cambios de cuentas solo después de que Nicolás lo confirme en el chat con Claude.
