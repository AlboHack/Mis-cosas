# Mis-cosas

Configuración y herramientas de Claude para Ingeniería Civil UTFSM.

| Carpeta | Qué contiene |
|---|---|
| `proyecto/instrucciones.md` | Instrucciones del proyecto de claude.ai (se pegan tal cual) |
| `proyecto/perfil.md` | Perfil académico (copia de Perfil_Nicolas.md del proyecto) |
| `.claude/skills/` | Skills propias; Claude Code las carga solas en este repo |
| `utfsm-calc/` | Paquete de cálculo probado: `pip install "git+https://github.com/AlboHack/Mis-cosas#subdirectory=utfsm-calc"` |
| `evals/` | Casos con error escondido para probar cambios de configuración |
| `DECISIONES.md` | Qué se cambió y con qué evidencia |

## Llevar los cambios a claude.ai
1. Skills: descargar el .zip desde la release [skills](https://github.com/AlboHack/Mis-cosas/releases/tag/skills) y subirlo en claude.ai > Configuración > Capacidades > Skills (reemplaza la versión anterior).
2. Contexto: en el proyecto, Conocimiento > + > GitHub > este repo, seleccionar `proyecto/perfil.md`, `DECISIONES.md` y `utfsm-calc/README.md`; después de cada cambio, "Sync now".
3. Instrucciones: pegar `proyecto/instrucciones.md` cuando cambie.

Cada lunes una tarea programada de Claude Code revisa las fuentes externas y busca skills nuevas; lo que valga la pena llega como pull request.
