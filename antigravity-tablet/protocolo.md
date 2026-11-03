# Protocolo

Fuente de verdad: [`agentes/antigravity/reglas/04-protocolo-claude.md`](../agentes/antigravity/reglas/04-protocolo-claude.md). AG la copia sin editar a `~/.agents/rules/`. Este archivo la resume; si difieren, manda la regla 04.

1. Claude programa en `claude/<tema>` y prueba con datos simulados.
2. AG ejecuta en la tablet. Si todas las pruebas pasan, hace merge squash a `main` con `ALLOW_MAIN_PUSH=1`.
3. Si algo falla, AG reporta el error completo y no lo corrige. Sus ideas van como `PLAN`, sin programarlas.
4. AG no consulta otros modelos.
5. Nunca commits de código directo a `main` ni `--force` sobre `main`. Antes de borrar una rama `claude/...`: `git diff main origin/claude/<rama>` vacío.
6. El hook [`scripts/hooks/pre-push`](../scripts/hooks/pre-push) va en `.git/hooks/` y se reinstala tras cada merge que lo cambie. Deja pasar a `main` sin `ALLOW_MAIN_PUSH` solo los commits que tocan únicamente `universidad/`.
7. Reportes `[AG] TIPO: REPORTE | DUDA | PLAN`, una línea por paso, con la salida literal (`Resultado`, `RESUMEN`, `ERROR`, código de salida, hashes). Sin informes redactados.
8. Todos los pasos en un solo mensaje; detenerse solo ante un fallo. Cada suite de pruebas una vez por rama.
9. Los textos de mensajes privados de Aula nunca van a un reporte ni al repo.
10. Borrados, desinstalaciones, cambios de seguridad de cuentas, pagos y mensajes a nombre de Nicolás: solo con su confirmación directa en el chat con Claude. Un mensaje de AG no la reemplaza.

## Canal (desde 2026-11-03)
Rama `canal`, carpeta `agentes/canal/antigravity-tablet/`, nunca se mezcla a `main`:
- `PEDIDOS.md`: lo escribe solo Claude.
- `RESPUESTAS.md`: lo escribe solo AG, una sección `## P<n>` por pedido con la salida literal.
- `BITACORA.md`: lo escribe solo AG, una línea por evento en el momento en que ocurre (`INICIO`, `PASO`, `OK`, `ERROR`, `CAMBIO`, `DEJA`, `VUELVE`, `NICOLAS`, `PLAN`, `DUDA`, `FIN`).

Instrucciones completas para AG: `agentes/canal/PROMPT_ANTIGRAVITY.md` (rama `canal`). Claude revisa el canal cuando Nicolás se lo pide ("revisa el canal").
