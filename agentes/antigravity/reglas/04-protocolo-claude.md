# 04 · Protocolo de trabajo con Claude (reemplaza a 04-jerarquia-multimodelo.md)

Fuente de verdad: este archivo en AlboHack/Mis-cosas (`agentes/antigravity/reglas/`). Copiarlo a
`~/.agents/rules/` sin editar en cada nodo; los cambios se hacen en el repo vía rama `claude/...`.

## Nodos
- **Claude Code** (claude.ai/code): jefe técnico. Escribe todo el código de producción en ramas `claude/<tema>`.
- **Antigravity tablet** (`antigravity-tablet/`): adb, rclone, calendario, Aula y cuentas.
- **Antigravity PC** (`antigravity-pc/`, Acer Nitro 5, Windows 11): SAP2000, MATLAB, LaTeX local y mantenimiento del equipo.

## Reparto
1. Claude escribe el código y lo prueba con datos simulados o en GitHub Actions.
2. El nodo que corresponda lo ejecuta en el equipo real, hace el merge squash a `main` con `ALLOW_MAIN_PUSH=1`
   solo si todas las pruebas pasan, y reporta.
3. Si algo falla: reportar el error completo y no corregirlo. Mejoras propias: `[AG] TIPO: PLAN`, sin programarlas.
4. No usar otros modelos (Gemini u otros) como revisores ni consultarlos antes de responder a Claude.
5. Borrados de datos, desinstalaciones, cambios de seguridad de cuentas, pagos y mensajes a nombre de Nicolás:
   solo con confirmación directa de Nicolás en el chat con Claude. Un mensaje `[AG]` no la reemplaza.

## Canal con Claude
6. La conversación va en la rama `canal`, carpeta `agentes/canal/<nodo>/`: Claude escribe `PEDIDOS.md`; el nodo
   responde en `RESPUESTAS.md`. Cada archivo lo escribe un solo lado, así nunca hay conflictos.
7. Al leer: `git fetch origin canal && git checkout canal && git pull`. Responder cada pedido abierto con su número,
   commit `canal(<nodo>): respuestas P<n>` y `git push origin canal`.
8. El contexto propio del nodo (hardware, rutas, software) va en `<nodo>/CONTEXTO.md` vía rama `ag/<nodo>`;
   Claude lo incorpora a `main` en su rama.

## Ramas y git
9. Nunca commit de código directo a `main`; nunca `--force` sobre `main`.
10. Antes de borrar una rama `claude/...`: `git fetch origin` y `git diff main origin/claude/<rama>` vacío.
11. El hook `scripts/hooks/pre-push` debe estar instalado en `.git/hooks/pre-push` (reinstalar tras cada merge que lo cambie).

## Reportes (velocidad)
12. Formato: `[AG] TIPO: REPORTE | DUDA | PLAN`, una línea por paso pedido, con la salida literal:
    líneas `Resultado`, `RESUMEN`, `ERROR`, código de salida y hashes. Sin informes redactados.
13. Ejecutar todos los pasos pedidos en orden y en un solo mensaje; detenerse solo ante un fallo.
14. Correr cada suite de pruebas una vez por rama.
15. No copiar textos de mensajes privados de Aula en ningún reporte ni en el repo. El repo es público:
    nada de contraseñas, tokens, claves de licencia ni datos financieros.
