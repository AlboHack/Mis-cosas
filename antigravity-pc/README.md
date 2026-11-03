# Antigravity PC — Estación de Trabajo Acer Nitro 5

Espacio de trabajo y configuración técnica para la instancia de **Antigravity** que corre localmente en el notebook Acer Nitro 5 de Nicolás Albornoz.

## Estructura del Directorio

```text
antigravity-pc/
├── CONTEXTO.md              # Perfil técnico de hardware, software, rutas y rol en el ecosistema
├── README.md                # Este archivo de referencia
└── mantenimiento/           # Mantenimiento de Windows con simulación previa y pruebas (ver su README)
```

## Flujo de Trabajo Tripartito (Claude $\leftrightarrow$ Tablet $\leftrightarrow$ PC)

1. **Claude (Navegador Brave):** Redacta código de producción, arquitectura de software y solvers avanzados. Realiza cambios en ramas `claude/<tema>`.
2. **Antigravity (Tablet):** Orquesta tareas de nube, sincronización con Aula UTFSM y servicios externos.
3. **Antigravity (PC):** Ejecuta y prueba los entornos en Windows 11 nativo, ejecuta modelos en SAP2000 v27 y MATLAB R2025a, compila documentos LaTeX locales y mantiene la telemetría del equipo.

Para conocer las especificaciones completas de hardware y directivas de cálculo, consultar [`CONTEXTO.md`](./CONTEXTO.md).
