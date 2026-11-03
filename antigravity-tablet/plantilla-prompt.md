# Plantilla de pedido y de reporte

Lo que funciona con AG: pedidos numerados y cerrados, con comandos literales, que terminan con el formato exacto del reporte y un máximo de líneas. Si se le deja razonar, consulta a Gemini y escribe informes largos.

## Pedido (en `PEDIDOS.md` o pegado por Nicolás)
```
[Claude → AG] P<n> · <objetivo>. Una sola pasada, sin consultar otros modelos.
1. cd ~/Mis-cosas && git fetch origin && git checkout <rama> && git pull --ff-only
2. Corre UNA vez: <pruebas, p. ej. python3 scripts/pruebas/test_novedades.py>. Si algo falla, reporta y NO sigas.
3. Si todo pasa: git checkout main && git merge --squash <rama> && git commit -m "<mensaje>" && ALLOW_MAIN_PUSH=1 git push origin main
4. <ejecución real, si corresponde>
REPORTE (máx. N líneas): [AG] REPORTE P<n>: <campos>
```
En la tablet no existe `/tmp` (Android): los logs van en `${TMPDIR:-$PREFIX/tmp}`.

El paso 3 se omite cuando el pedido incluye borrados o cambios que esperan la confirmación de Nicolás.

## Reporte de AG
```
[AG] REPORTE P<n>: paso 1 OK <hash>
[AG] REPORTE P<n>: paso 2 Resultado T29: PASS | Resultado T28: PASS | código 0
[AG] REPORTE P<n>: paso 3 merge <hash main>
```
Una línea por paso, salida literal, sin interpretación. En el canal va en `RESPUESTAS.md` bajo `## P<n>`, y cada paso además como línea `PASO`/`OK`/`ERROR` en `BITACORA.md`.

## Verificar lo que reporta AG
Los números que entrega AG se comprueban antes de usarlos. Ejemplo: informó que la Tarea 2 de FICA vencía el 10-nov; el timestamp `1794279540` corresponde al 09-nov 23:59 (UTC−3).
