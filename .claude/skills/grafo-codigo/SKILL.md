---
name: "grafo-codigo"
description: "Usar al preguntar cómo está organizado el código de scripts/, utfsm-calc/ o antigravity-pc/: quién llama a una función, a qué llama, qué se rompe si se cambia, o la ruta entre dos funciones."
---

# Grafo del código

Adaptado de [graphify](https://github.com/Graphify-Labs/graphify) (Apache-2.0). Responde preguntas de estructura con un grafo de llamadas en vez de leer archivos enteros.

## Uso
```
scripts/grafo_codigo.sh explain "reflejar_en_repo"           # quién la llama y a quién llama, con línea
scripts/grafo_codigo.sh path "run_sync" "compute_file_sha256" # camino más corto entre dos funciones
scripts/grafo_codigo.sh query "dónde se calcula el hash"      # recorrido por palabras clave
```
La primera vez instala `graphifyy==0.9.102` (doble y) en una carpeta temporal y construye el grafo en unos 15 s; después lo reutiliza hasta que cambie el código. Solo analiza código con tree-sitter: sin modelo, sin claves y sin enviar nada. Cubre Python y PowerShell.

## Cómo leer el resultado
- `[EXTRACTED]`: relación presente en el código (llamada, definición). Se puede usar tal cual.
- `[INFERRED 0.85]`: relación supuesta por similitud. Se confirma con `grep` antes de apoyarse en ella.
- Un nombre ambiguo devuelve código 3: repetir con el nombre completo.

## Límites
- No ve llamadas dinámicas (`getattr`, `importlib`, nombres en cadenas): las pruebas de `scripts/pruebas/` cargan módulos así.
- No incluye `universidad/`; esa carpeta son PDF de Aula, no código.
- No se corre `graphify install` ni `graphify claude install`: este último escribe en `CLAUDE.md` y registra un hook, y `CLAUDE.md` es la fuente de verdad del proyecto.
- La salida (`graphify-out/`) no se sube al repo.
