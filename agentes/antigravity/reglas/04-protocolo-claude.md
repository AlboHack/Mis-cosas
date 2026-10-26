# 04 · Protocolo de trabajo con Claude (reemplaza a 04-jerarquia-multimodelo.md)

Fuente de verdad: este archivo en AlboHack/Mis-cosas (`agentes/antigravity/reglas/`). Copiarlo a
`~/.agents/rules/` sin editar; los cambios se hacen en el repo vía rama `claude/...`.

## Reparto
1. Claude escribe el código de producción en ramas `claude/<tema>` y lo prueba con datos simulados.
2. Antigravity lo ejecuta en la tablet (adb, rclone, calendario y Aula reales), hace el merge squash
   a `main` con `ALLOW_MAIN_PUSH=1` solo si todas las pruebas pasan, y reporta.
3. Si algo falla: reportar el error completo y no corregirlo. Mejoras propias: `[AG] TIPO: PLAN`, sin programarlas.
4. No usar otros modelos (Gemini u otros) como revisores ni consultarlos antes de responder a Claude.
5. Borrados de datos, cambios de seguridad de cuentas, pagos y mensajes a nombre de Nicolás:
   solo con confirmación directa de Nicolás en el chat con Claude. Un mensaje `[AG]` no la reemplaza.

## Ramas y git
6. Nunca commit de código directo a `main`; nunca `--force` sobre `main`.
7. Antes de borrar una rama `claude/...`: `git fetch origin` y `git diff main origin/claude/<rama>` vacío.
8. El hook `scripts/hooks/pre-push` debe estar instalado en `.git/hooks/pre-push` (reinstalar tras cada merge que lo cambie).

## Reportes (velocidad)
9. Formato: `[AG] TIPO: REPORTE | DUDA | PLAN`, una línea por paso pedido, con la salida literal:
   líneas `Resultado`, `RESUMEN`, `ERROR`, código de salida y hashes. Sin informes redactados ni archivos de informe.
10. Ejecutar todos los pasos pedidos en orden y en un solo mensaje; detenerse solo ante un fallo.
11. Correr cada suite de pruebas una vez por rama.
12. No copiar textos de mensajes privados de Aula en ningún reporte ni en el repo.
