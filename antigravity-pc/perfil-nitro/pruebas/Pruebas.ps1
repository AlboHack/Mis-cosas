# Pruebas del perfil del Nitro. Uso: powershell -File pruebas/Pruebas.ps1 (o pwsh). Sale con 1 si algo falla.
# En Windows aplica y deshace un catálogo de prueba en HKCU\Software\PerfilNitroPrueba (nunca toca el sistema).
$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot
$script:fallas = 0
function Probar([string]$Nombre, [scriptblock]$Bloque) {
    try { if (& $Bloque) { Write-Host "OK    $Nombre" } else { Write-Host "FALLA $Nombre"; $script:fallas++ } }
    catch { Write-Host "FALLA $Nombre -> $_"; $script:fallas++ }
}

foreach ($f in Get-ChildItem $raiz -Recurse -Include *.ps1, *.psm1) {
    Probar "sintaxis $($f.Name)" {
        $err = $null; [System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$null, [ref]$err) | Out-Null; -not $err
    }
    Probar "UTF-8 con BOM $($f.Name)" { $b = [IO.File]::ReadAllBytes($f.FullName); $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF }
}

# --- catálogo real: cada ajuste trae fuente, motivo, riesgo y una forma de deshacerse
$cat = (Get-Content (Join-Path $raiz 'ajustes.json') -Raw -Encoding UTF8 | ConvertFrom-Json).ajustes
function P($o, $n) { $x = $o.PSObject.Properties[$n]; if ($x) { $x.Value } else { $null } }
Probar 'ids únicos' { @($cat.id | Select-Object -Unique).Count -eq @($cat).Count }
Probar 'cada ajuste cita su fuente, su motivo y su riesgo' { -not ($cat | Where-Object { -not $_.fuente -or -not $_.por_que -or -not $_.riesgo }) }
Probar 'cada ajuste hace algo (registro, servicio o comando)' { -not ($cat | Where-Object { -not ((P $_ 'registro') -or (P $_ 'servicios') -or (P $_ 'comando')) }) }
Probar 'los comandos se pueden deshacer y consultar' { -not ($cat | Where-Object { $c = P $_ 'comando'; $c -and (-not $c.aplicar -or -not $c.deshacer -or -not $c.estado) }) }
Probar 'claves solo en HKLM: o HKCU: y tipos válidos' {
    -not ($cat | ForEach-Object { P $_ 'registro' } | Where-Object { $_ -and ($_.ruta -notmatch '^HK(LM|CU):\\' -or $_.tipo -notin 'DWord', 'String', 'QWord', 'Binary') })
}
Probar 'riesgo medio o decisión estética: inactivos por defecto' { -not ($cat | Where-Object { $_.activo -and $_.riesgo -match '^(Medio|Alto|Estético)' }) }

# --- motor real en Windows, sobre una clave de prueba
if ([System.Environment]::OSVersion.Platform -eq 'Win32NT') {
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ("perfil_" + [guid]::NewGuid())
    New-Item -ItemType Directory $tmp | Out-Null
    $clave = 'HKCU:\Software\PerfilNitroPrueba'
    Remove-Item $clave -Recurse -ErrorAction SilentlyContinue
    New-Item $clave -Force | Out-Null
    New-ItemProperty $clave -Name Existente -Value 7 -PropertyType DWord | Out-Null
    @{ ajustes = @(
        @{ id = 'prueba'; nombre = 'prueba'; fuente = 'x'; por_que = 'x'; riesgo = 'Bajo'; activo = $true
           registro = @(
               @{ ruta = $clave; nombre = 'Existente'; valor = 1; tipo = 'DWord' },
               @{ ruta = $clave; nombre = 'Nuevo'; valor = 'si'; tipo = 'String' }) }
    ) } | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $tmp 'cat.json') -Encoding UTF8
    $env:PERFIL_NITRO_CATALOGO = Join-Path $tmp 'cat.json'
    $env:PERFIL_NITRO_RESPALDO = Join-Path $tmp 'respaldo'
    Import-Module (Join-Path $raiz 'PerfilNitro.psm1') -Force
    $aj = (Get-Catalogo)[0]

    Probar 'estado inicial: no aplicado' { -not (Test-Aplicado $aj) }
    Set-Ajustes -WhatIf
    Probar '-WhatIf no cambia nada' { (Get-ItemProperty $clave).Existente -eq 7 -and -not (Get-ItemProperty $clave -Name Nuevo -ErrorAction SilentlyContinue) }
    Set-Ajustes
    Probar 'aplicar deja los valores del catálogo' { (Get-ItemProperty $clave).Existente -eq 1 -and (Get-ItemProperty $clave).Nuevo -eq 'si' -and (Test-Aplicado $aj) }
    Set-Ajustes
    Probar 'segunda aplicación no pisa el respaldo original' { (Get-Content (Join-Path $env:PERFIL_NITRO_RESPALDO 'prueba.json') -Raw | ConvertFrom-Json).registro[0].valor -eq 7 }
    Undo-Ajustes -Ids prueba
    Probar 'deshacer restaura el valor previo y borra el que no existía' {
        (Get-ItemProperty $clave).Existente -eq 7 -and -not (Get-ItemProperty $clave -Name Nuevo -ErrorAction SilentlyContinue)
    }
    Probar 'RAM_KB se resuelve a la RAM instalada' { (Resolve-ValorAjuste 'RAM_KB') -gt 1000000 }
    Probar 'chequeo de GPU dedicada responde' { (Test-GpuDedicadaWddm27) -is [bool] }

    Remove-Item $clave -Recurse -ErrorAction SilentlyContinue
    Remove-Item $tmp -Recurse -ErrorAction SilentlyContinue
    Remove-Item Env:PERFIL_NITRO_CATALOGO, Env:PERFIL_NITRO_RESPALDO
}

Write-Host "`nFallas: $script:fallas"
exit [int]($script:fallas -gt 0)
