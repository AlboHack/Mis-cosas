@proyecto/instrucciones.md
@proyecto/perfil.md

# Este repositorio
Fuente de verdad de la configuración del proyecto "Nicolás" en Claude: instrucciones (`proyecto/instrucciones.md`), skills (`.claude/skills/`), paquete de cálculo (`utfsm-calc/`) y casos de prueba (`evals/`). Las sesiones de Claude Code sobre este repo cargan las skills y estas reglas solas; en esas sesiones el paquete se instala con `pip install -e utfsm-calc`.

## Al cambiar algo
- utfsm-calc: toda función nueva lleva su prueba contra una solución cerrada en `utfsm-calc/tests/`; `pytest utfsm-calc/tests` en verde antes de cada commit. GitHub Actions lo vuelve a correr en cada push.
- Skills e instrucciones: un cambio se acepta solo si los casos de `evals/casos/` siguen pasando (ver `evals/README.md`). Registrar el porqué en `DECISIONES.md`.
- claude.ai no lee este repo solo: al llegar a main, cada skill sale como .zip en la release `skills` (workflow skills-zip) y Nicolás sube la que cambió; `proyecto/perfil.md` y `DECISIONES.md` entran al conocimiento del proyecto por la integración de GitHub con "Sync now"; un cambio en `proyecto/instrucciones.md` lo pega Nicolás en las instrucciones del proyecto.
- Repositorio público. Autorizado por Nicolás: su nombre, la UTFSM y su perfil académico. Prohibido: finanzas personales y memoria del proyecto.
