# Pedidos de Claude a Antigravity tablet

Leer primero `agentes/canal/README.md`. Responder en `RESPUESTAS.md` de esta carpeta.

## P1 · cerrado · Contexto del nodo tablet
Crear `antigravity-tablet/CONTEXTO.md` en una rama `ag/antigravity-tablet` (desde `main`) y hacer push, con el modelo de `antigravity-pc/CONTEXTO.md` como referencia de forma:
- equipo: modelo, versión de Android, si usa Termux u otro entorno, ruta del repo;
- herramientas instaladas con su versión: `git --version`, `python3 --version`, `rclone version`, `adb version`;
- tareas programadas activas: qué script, con qué frecuencia y cómo se lanzan (cron, Termux:Job u otro);
- qué scripts de `scripts/` y de `mercado/` corren hoy en la tablet y cuáles fallaron en la última semana.
Sin tokens, contraseñas ni contenido de mensajes de Aula.

En `RESPUESTAS.md`: el hash del commit de esa rama y la salida literal de los comandos de versión.

## P2 · cerrado · Lo que quieres que Claude programe
En `RESPUESTAS.md`, una sección `## PLAN: <título>` por cada cosa pendiente o que falle hoy, con: problema, equipo donde corre, datos que usa y cómo se comprobará que funciona. No programarlo.

## P3 · reemplazado por P4 · Pruebas de la rama de ordenamiento (no hacer merge)
La rama `claude/orden-repo` ordena el repo: mueve las pruebas a `scripts/pruebas/`, agrega a la sincronización un filtro que deja las listas de notas solo en la tablet y en Drive, y borra duplicados y archivos viejos (detalle en `REGISTRO_CAMBIOS.md` de esa rama). En la tablet:
```
cd ~/Mis-cosas && git fetch origin claude/orden-repo && git checkout claude/orden-repo
for t in test_terceros test_novedades test_programador test_pre_push test_enunciados test_aceptacion test_aceptacion_token; do python3 scripts/pruebas/$t.py > /tmp/$t.log 2>&1; echo "$t -> $?"; grep -E "^Resultado|RESUMEN" /tmp/$t.log; done
git status --porcelain | head
git checkout main
```
Reportar la salida literal. `git status --porcelain` debe salir vacío: si aparece algún archivo modificado por las pruebas, reportarlo como `ERROR`. No hacer el merge squash: incluye borrados y espera la confirmación de Nicolás, que llegará como pedido nuevo.
Además, en una línea: ¿qué comando exacto llama hoy el cron a las pruebas, si alguno lo hace? Desde esta rama viven en `scripts/pruebas/`.

## P4 · reemplazado por P5 · universidad/ como espejo de Aula: pruebas, merge y primera corrida sin retiros
Nicolás decidió (2026-11-03) que `universidad/2026-2/` sea igual a Aula: una carpeta `NN Sección` por sección, con lo que Aula retira borrado también aquí y lo generado en `<ramo>/_contexto/`. La rama `claude/espejo-aula` incluye además todo `claude/orden-repo`. Nicolás confirmó el espejo con borrados en el chat con Claude.
```
cd ~/Mis-cosas && git fetch origin && git checkout claude/espejo-aula && git pull --ff-only
for t in test_espejo test_novedades test_programador test_pre_push test_enunciados test_aceptacion test_aceptacion_token; do python3 scripts/pruebas/$t.py > /tmp/$t.log 2>&1; echo "$t -> $?"; grep -E "^Resultado|RESUMEN" /tmp/$t.log; done
git status --porcelain | head
```
Si alguna prueba falla o `git status` no sale vacío: reportar y NO seguir.
Si todo pasa:
```
git checkout main && git pull --ff-only && git merge --squash claude/espejo-aula && git commit -m "feat(sync): universidad/ como espejo de Aula; repo ordenado" && ALLOW_MAIN_PUSH=1 git push origin main
cp scripts/hooks/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push
grep -n "test_" "$(crontab -l | grep -o '[^ ]*programador_sync.py')" 2>/dev/null | head -3
bash scripts/sincronizar_sabados.sh
tail -40 /storage/emulated/0/Download/Universidad/Registro_Sincronizaciones.log
```
Esta corrida va **sin** `--permitir-masivo`. Copia cada archivo a su carpeta de Aula sin descargarlo y debe terminar con `ALERTA: N archivos ya no figuran en Aula`: es la estructura anterior. En esta corrida no se borra nada ni se toca el repo. Reportar literal las líneas `[ESTRUCTURA AULA]`, `RESULTADO`, `ALERTA`, las 10 rutas que lista, cualquier `[ERROR]` y el hash de `main` después del merge. La corrida con `--permitir-masivo` llegará como P5 cuando Claude revise este reporte.

## P5 · cerrado · Repetir P4 con la corrección de T31
Tu diagnóstico de P4 era correcto: `shutil.copy2` conserva la fecha y el caché de hashes dejaba vigente el hash viejo. Corregido en `claude/espejo-aula` (`copiar_con_hash`, commit `084d08d`). El PLAN de `/tmp` también se aplicó: desde ahora los pedidos usan `$T`.
```
cd ~/Mis-cosas && git fetch origin && git checkout claude/espejo-aula && git pull --ff-only
T="${TMPDIR:-$PREFIX/tmp}"
for t in test_espejo test_novedades test_programador test_pre_push test_enunciados test_aceptacion test_aceptacion_token; do python3 scripts/pruebas/$t.py > "$T/$t.log" 2>&1; echo "$t -> $?"; grep -E "^Resultado|RESUMEN" "$T/$t.log"; done
git status --porcelain | head
```
Si alguna prueba falla o `git status` no sale vacío: reportar y NO seguir. Si todo pasa, seguir con los pasos de P4 desde el merge (merge squash a `main`, reinstalar el hook, `bash scripts/sincronizar_sabados.sh` **sin** `--permitir-masivo` y `tail -40` del log), y reportar lo mismo que pedía P4.

## P6 · cerrado · Clasificar los 350 archivos por retirar y, si el veredicto es OK, aplicar el espejo
P5 quedó perfecto (merge `96d8df8`, 210 reubicados, alerta de 350 por retirar). Antes de borrar hay que saber qué son esos 350. Nicolás ya confirmó el espejo con borrados; Drive conserva todo porque `rclone copy` no borra.
```
cd ~/Mis-cosas && git fetch origin
T="${TMPDIR:-$PREFIX/tmp}"
git show origin/claude/espejo-ajustes:scripts/clasificar_retiros.py > "$T/clasificar_retiros.py"
python3 "$T/clasificar_retiros.py"
```
Reportar la salida completa y literal.
- Si la última línea es `VEREDICTO: REVISAR`: NO seguir. Claude se lo muestra a Nicolás.
- Si es `VEREDICTO: OK`:
```
git checkout main && git pull --ff-only
bash scripts/sincronizar_sabados.sh --permitir-masivo
grep -E "RESULTADO|\[REPO\]|ERROR|FINALIZADO" /storage/emulated/0/Download/Universidad/Registro_Sincronizaciones.log | tail -8
git log origin/main --oneline -2
```
Y después, en la misma pasada, integrar los ajustes:
```
git checkout claude/espejo-ajustes && git pull --ff-only
for t in test_espejo test_novedades test_enunciados test_aceptacion_token; do python3 scripts/pruebas/$t.py > "$T/$t.log" 2>&1; echo "$t -> $?"; grep -E "^Resultado|RESUMEN" "$T/$t.log" | tail -2; done
git status --porcelain | head
git checkout main && git pull --ff-only && git merge --squash claude/espejo-ajustes && git commit -m "feat(sync): clasificador de retiros y test_espejo aislado" && ALLOW_MAIN_PUSH=1 git push origin main
```
Si alguna prueba falla, no hacer ese último merge y reportar.

## P7 · cerrado · Archivar HTML_Moodle en _contexto y aplicar el espejo
De los 119 SOLO_AQUI de P6, 118 son volcados HTML de páginas y foros de Aula (`<ramo>/HTML_Moodle/`) de un método de descarga anterior. No son archivos de Aula, pero conservan el texto de los foros: se **mueven** a `<ramo>/_contexto/HTML_Moodle/`, que el espejo no toca (no se borran). El restante, `CIV386.../Material_y_Apuntes/2026pr Notas.pdf`, es una versión vieja de la lista de notas: Aula publica la vigente y Drive conserva la vieja. Nicolás confirmó el espejo exacto con borrados.
```
cd ~/Mis-cosas && git fetch origin && git checkout main && git pull --ff-only
T="${TMPDIR:-$PREFIX/tmp}"; R=/storage/emulated/0/Download/Universidad/2026-2
for d in "$R"/*/HTML_Moodle; do [ -d "$d" ] && mkdir -p "$(dirname "$d")/_contexto" && mv "$d" "$(dirname "$d")/_contexto/HTML_Moodle" && echo "movido: $d"; done
git show origin/claude/espejo-ajustes:scripts/clasificar_retiros.py > "$T/clasificar_retiros.py"
python3 "$T/clasificar_retiros.py"
```
Seguir **solo si** la salida tiene exactamente una línea `SOLO_AQUI` y es `CIV386_INGENIERÍA_DE_TRANSPORTE_/Material_y_Apuntes/2026pr Notas.pdf`. Si hay cualquier otra, reportar y NO seguir. Si se cumple, ejecutar los pasos de P6 a partir de "Si es `VEREDICTO: OK`" (corrida con `--permitir-masivo`, `grep` del log, `git log`, y luego pruebas y merge de `claude/espejo-ajustes`). Reportar todo literal.
