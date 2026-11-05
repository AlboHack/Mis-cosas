---
name: "seguridad-scripts"
description: "Usar al escribir o revisar un script que borra, mueve o sobrescribe archivos, cambia el registro de Windows, pide permisos de administrador, usa un token o una contraseña, o instala una dependencia o un plugin que ejecuta código."
---

# Seguridad de scripts

Adaptado de `security-and-hardening` (addyosmani/agent-skills, MIT). Solo las secciones que aplican a los scripts de este repo (sincronización con Aula, `antigravity-pc/`, `utfsm-calc/`); lo de aplicaciones web (XSS, CSP, sesiones) se omite. El repositorio es público.

## Operaciones destructivas
Un borrado vale tanto como el valor que nombra su objetivo. Antes de borrar, mover o sobrescribir una ruta, exigir las tres condiciones:
1. La ruta resuelta (con enlaces simbólicos resueltos) está **dentro de una raíz permitida**. La lista es corta y nombra carpetas concretas (`D:\Descargas Opera`), nunca una unidad entera: con `D:\` como raíz, `D:\Modelos RUN` o `D:\Matlab` quedarían al alcance. Una lista de rutas prohibidas no la reemplaza, porque deja borrable todo lo que nadie pensó en prohibir.
2. Está **al menos un nivel por debajo** de esa raíz. Una unidad, `C:\Users` o la carpeta de perfil nunca son objetivo.
3. Hay **evidencia de que es nuestra**, leída antes de actuar: figura en el manifiesto o en el JSON de configuración.

Si falla una, registrar la ruta rechazada y detenerse; no recurrir a una ruta más amplia. Toda acción destructiva admite simulación (`-WhatIf` en PowerShell, `--dry-run` en rclone) y se corre primero así. En el repo: `Test-RutaResiduoSegura`, el tope de 20 retiros de `sincronizar_aula_semanal.py` y `rclone copy`, nunca `sync`.

## Secretos
- El token vive fuera del repo (`~/.moodle_token`, permisos 600) y se enmascara en logs y manifiestos; hay una prueba que lo verifica (T10).
- Antes de cada commit, buscar en lo preparado: `git diff --cached | grep -iE "token|secret|password|key"`.
- **Un secreto que llegó a un remoto está comprometido desde ese momento: primero rotarlo, después limpiar el historial.**

## Permisos elevados
Pedirlos solo para lo que los exige y en un script aparte, de solo lectura cuando se pueda. Las acciones que cambian el sistema guardan el valor previo y se pueden deshacer (`PerfilNitro.psm1`). Ejecutar con administrador un script cuyo contenido no se ha leído está fuera de la tarea.

## Dependencias y plugins que ejecutan código
Fijar la versión (`pip install graphifyy==X`, `ref` de un tag en `extraKnownMarketplaces`). Leer antes los hooks y los scripts de instalación. Una auditoría solo detecta fallas conocidas; un nombre casi igual al correcto (`graphify` frente a `graphifyy`) hay que comprobarlo contra el repositorio oficial.

## Pedir confirmación de Nicolás
Borrar datos, desinstalar programas, cambiar cuentas, subir algo al repo público.
