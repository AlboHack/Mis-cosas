<#
Perfil del Nitro 5: ajustes de Windows tomados de repositorios técnicos (ver ajustes.json, campo "fuente"),
aplicados con respaldo del valor real previo y reversibles uno por uno. Diseño de datos inspirado en
ChrisTitusTech/winutil (MIT): cada ajuste es un dato, no código suelto.
#>
Set-StrictMode -Version Latest
$script:Catalogo = if ($env:PERFIL_NITRO_CATALOGO) { $env:PERFIL_NITRO_CATALOGO } else { Join-Path $PSScriptRoot 'ajustes.json' }
$script:DirRespaldo = if ($env:PERFIL_NITRO_RESPALDO) { $env:PERFIL_NITRO_RESPALDO }
                      elseif ($env:LOCALAPPDATA) { Join-Path $env:LOCALAPPDATA 'PerfilNitro\respaldo' }
                      else { Join-Path ([IO.Path]::GetTempPath()) 'PerfilNitro\respaldo' }

function Get-Catalogo {
    param([string]$Ruta = $script:Catalogo)
    (Get-Content $Ruta -Raw -Encoding UTF8 | ConvertFrom-Json).ajustes
}

function Resolve-ValorAjuste {
    # "RAM_KB" se resuelve a la RAM instalada en KB (umbral de svchost); el resto pasa tal cual.
    param($Valor)
    if ($Valor -eq 'RAM_KB') {
        return [int]((Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum).Sum / 1KB)
    }
    $Valor
}

function Get-Propiedad($Objeto, [string]$Nombre) {
    $p = $Objeto.PSObject.Properties[$Nombre]
    if ($p) { $p.Value } else { $null }
}

function Test-GpuDedicadaWddm27 {
    # Mismas condiciones que Sophia Script GPUScheduling: GPU no integrada y WDDM >= 2.7
    $dedicada = Get-CimInstance CIM_VideoController | Where-Object { $_.AdapterDACType -and $_.AdapterDACType -ne 'Internal' }
    $wddm = [Microsoft.Win32.Registry]::GetValue('HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\FeatureSetUsage', 'WddmVersion_Min', 0)
    [bool]$dedicada -and $wddm -ge 2700
}

$script:CodigoDxgi = @'
using System;
using System.Runtime.InteropServices;
[StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
public struct DXGI_ADAPTER_DESC1 {
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)] public string Description;
    public uint VendorId, DeviceId, SubSysId, Revision;
    public UIntPtr DedicatedVideoMemory, DedicatedSystemMemory, SharedSystemMemory;
    public uint LuidLow; public int LuidHigh; public uint Flags;
}
[ComImport, Guid("29038f61-3839-4626-91fd-086879011a05"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IDXGIAdapter1 {
    [PreserveSig] int SetPrivateData(); [PreserveSig] int SetPrivateDataInterface(); [PreserveSig] int GetPrivateData(); [PreserveSig] int GetParent();
    [PreserveSig] int EnumOutputs(); [PreserveSig] int GetDesc(); [PreserveSig] int CheckInterfaceSupport();
    [PreserveSig] int GetDesc1(out DXGI_ADAPTER_DESC1 desc);
}
[ComImport, Guid("770aae78-f26f-4dba-a829-253c83d1b387"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IDXGIFactory1 {
    [PreserveSig] int SetPrivateData(); [PreserveSig] int SetPrivateDataInterface(); [PreserveSig] int GetPrivateData(); [PreserveSig] int GetParent();
    [PreserveSig] int EnumAdapters(); [PreserveSig] int MakeWindowAssociation(); [PreserveSig] int GetWindowAssociation(); [PreserveSig] int CreateSwapChain(); [PreserveSig] int CreateSoftwareAdapter();
    [PreserveSig] int EnumAdapters1(uint index, out IDXGIAdapter1 adapter);
}
public static class Dxgi {
    [DllImport("dxgi.dll")] static extern int CreateDXGIFactory1(ref Guid riid, [MarshalAs(UnmanagedType.Interface)] out IDXGIFactory1 factory);
    public static DXGI_ADAPTER_DESC1[] Adaptadores() {
        Guid g = typeof(IDXGIFactory1).GUID; IDXGIFactory1 f;
        if (CreateDXGIFactory1(ref g, out f) != 0) return new DXGI_ADAPTER_DESC1[0];
        var lista = new System.Collections.Generic.List<DXGI_ADAPTER_DESC1>();
        for (uint i = 0; ; i++) {
            IDXGIAdapter1 a;
            if (f.EnumAdapters1(i, out a) != 0) break;
            DXGI_ADAPTER_DESC1 d; if (a.GetDesc1(out d) == 0) lista.Add(d);
        }
        return lista.ToArray();
    }
}
'@

function Get-AdaptadoresGpu {
    # Nombre de cada adaptador con su LUID en el formato de los contadores '\GPU Engine(*)' (luid_0xHIGH_0xLOW)
    if (-not ('Dxgi' -as [type])) { Add-Type -TypeDefinition $script:CodigoDxgi }
    foreach ($d in [Dxgi]::Adaptadores()) {
        [pscustomobject]@{
            Nombre    = $d.Description
            Luid      = ('luid_0x{0:x8}_0x{1:x8}' -f $d.LuidHigh, $d.LuidLow)
            VramMB    = [math]::Round([double]$d.DedicatedVideoMemory.ToUInt64() / 1MB)
        }
    }
}

function Get-GpuDeProceso {
    # Adaptadores en que un proceso tiene motores 3D activos, por nombre
    param([Parameter(Mandatory)][int]$ProcesoId)
    $mapa = @{}; Get-AdaptadoresGpu | ForEach-Object { $mapa[$_.Luid] = $_.Nombre }
    $luids = (Get-Counter '\GPU Engine(*)\Utilization Percentage' -ErrorAction SilentlyContinue).CounterSamples |
        Where-Object InstanceName -match "^pid_$($ProcesoId)_(luid_0x[0-9a-f]{8}_0x[0-9a-f]{8})_.*engtype_3d" |
        ForEach-Object { $Matches[1] } | Select-Object -Unique
    foreach ($l in $luids) { [pscustomobject]@{ Luid = $l; Adaptador = $mapa[$l] } }
}

function Get-ValorRegistro {
    param([string]$Ruta, [string]$Nombre)
    $item = Get-ItemProperty -Path $Ruta -Name $Nombre -ErrorAction SilentlyContinue
    if ($null -eq $item) { return [pscustomobject]@{ Existe = $false; Valor = $null; Tipo = $null } }
    $tipo = (Get-Item $Ruta).GetValueKind($Nombre).ToString()
    [pscustomobject]@{ Existe = $true; Valor = $item.$Nombre; Tipo = $tipo }
}

function Test-Aplicado {
    param([Parameter(Mandatory)]$Ajuste)
    foreach ($r in @(Get-Propiedad $Ajuste 'registro')) {
        if (-not $r) { continue }
        $v = Get-ValorRegistro $r.ruta $r.nombre
        if (Get-Propiedad $r 'eliminar') { if ($v.Existe) { return $false } else { continue } }
        if (-not $v.Existe -or "$($v.Valor)" -ne "$(Resolve-ValorAjuste $r.valor)") { return $false }
    }
    foreach ($s in @(Get-Propiedad $Ajuste 'servicios')) {
        if (-not $s) { continue }
        $svc = Get-Service -Name $s.nombre -ErrorAction SilentlyContinue
        if ($svc -and "$($svc.StartType)" -ne $s.inicio) { return $false }
    }
    $cmd = Get-Propiedad $Ajuste 'comando'
    if ($cmd) { return [bool](Invoke-Expression $cmd.estado) }
    $true
}

function Get-EstadoAjustes {
    foreach ($a in Get-Catalogo) {
        $req = Get-Propiedad $a 'requiere'
        [pscustomobject]@{
            Id        = $a.id
            Activo    = [bool]$a.activo
            Aplicado  = Test-Aplicado $a
            Requisito = if ($req) { [bool](& $req) } else { $true }
            Riesgo    = $a.riesgo
        }
    }
}

function Save-Respaldo {
    # Guarda el estado real previo del ajuste. Si ya hay respaldo, se conserva: es el valor original.
    param([Parameter(Mandatory)]$Ajuste)
    $archivo = Join-Path $script:DirRespaldo "$($Ajuste.id).json"
    if (Test-Path $archivo) { return $archivo }
    New-Item -ItemType Directory -Path $script:DirRespaldo -Force | Out-Null
    $previo = [ordered]@{ id = $Ajuste.id; fecha = (Get-Date).ToString('s'); registro = @(); servicios = @() }
    foreach ($r in @(Get-Propiedad $Ajuste 'registro')) {
        if (-not $r) { continue }
        $v = Get-ValorRegistro $r.ruta $r.nombre
        $previo.registro += [ordered]@{ ruta = $r.ruta; nombre = $r.nombre; existe = $v.Existe; valor = $v.Valor; tipo = $v.Tipo }
    }
    foreach ($s in @(Get-Propiedad $Ajuste 'servicios')) {
        if (-not $s) { continue }
        $svc = Get-Service -Name $s.nombre -ErrorAction SilentlyContinue
        if ($svc) { $previo.servicios += [ordered]@{ nombre = $s.nombre; inicio = "$($svc.StartType)" } }
    }
    $previo | ConvertTo-Json -Depth 5 | Set-Content $archivo -Encoding UTF8
    $archivo
}

function Set-Ajustes {
    # Aplica los ajustes indicados (por defecto, los activos del catálogo). Usar primero con -WhatIf.
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
    param([string[]]$Ids)
    $todos = Get-Catalogo
    $lista = if ($Ids) { $todos | Where-Object { $Ids -contains $_.id } } else { $todos | Where-Object activo }
    foreach ($a in $lista) {
        $req = Get-Propiedad $a 'requiere'
        if ($req -and -not (& $req)) { Write-Warning "$($a.id): no cumple el requisito $req; se omite."; continue }
        if (Test-Aplicado $a) { Write-Host "$($a.id): ya aplicado."; continue }
        if (-not $PSCmdlet.ShouldProcess($a.id, $a.nombre)) { continue }
        $resp = Save-Respaldo $a
        foreach ($r in @(Get-Propiedad $a 'registro')) {
            if (-not $r) { continue }
            if (Get-Propiedad $r 'eliminar') { Remove-ItemProperty -Path $r.ruta -Name $r.nombre -ErrorAction SilentlyContinue; continue }
            if (-not (Test-Path $r.ruta)) { New-Item -Path $r.ruta -Force | Out-Null }
            $valor = Resolve-ValorAjuste $r.valor
            if ($r.tipo -eq 'Binary') { $valor = [byte[]]@($valor) }
            New-ItemProperty -Path $r.ruta -Name $r.nombre -Value $valor -PropertyType $r.tipo -Force | Out-Null
        }
        foreach ($s in @(Get-Propiedad $a 'servicios')) {
            if (-not $s) { continue }
            if (Get-Service -Name $s.nombre -ErrorAction SilentlyContinue) {
                Set-Service -Name $s.nombre -StartupType $s.inicio
                if ($s.inicio -eq 'Disabled') { Stop-Service -Name $s.nombre -Force -ErrorAction SilentlyContinue }
            }
        }
        $cmd = Get-Propiedad $a 'comando'
        if ($cmd) { Invoke-Expression $cmd.aplicar | Out-Null }
        Write-Host "$($a.id): aplicado (respaldo en $resp)."
    }
}

function Undo-Ajustes {
    # Devuelve cada ajuste al valor que tenía antes de aplicarlo, según su respaldo.
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
    param([Parameter(Mandatory)][string[]]$Ids)
    $todos = Get-Catalogo
    foreach ($id in $Ids) {
        $archivo = Join-Path $script:DirRespaldo "$id.json"
        $a = $todos | Where-Object id -eq $id
        if (-not $a) { Write-Warning "$id no está en el catálogo."; continue }
        if (-not $PSCmdlet.ShouldProcess($id, 'Deshacer')) { continue }
        if (Test-Path $archivo) {
            $previo = Get-Content $archivo -Raw -Encoding UTF8 | ConvertFrom-Json
            foreach ($r in @($previo.registro)) {
                if (-not $r) { continue }
                if ($r.existe) {
                    if (-not (Test-Path $r.ruta)) { New-Item -Path $r.ruta -Force | Out-Null }
                    $valor = if ($r.tipo -eq 'Binary') { [byte[]]@($r.valor) } else { $r.valor }
                    New-ItemProperty -Path $r.ruta -Name $r.nombre -Value $valor -PropertyType $r.tipo -Force | Out-Null
                }
                else { Remove-ItemProperty -Path $r.ruta -Name $r.nombre -ErrorAction SilentlyContinue }
            }
            foreach ($s in @($previo.servicios)) { if ($s) { Set-Service -Name $s.nombre -StartupType $s.inicio } }
        }
        $cmd = Get-Propiedad $a 'comando'
        if ($cmd) { Invoke-Expression $cmd.deshacer | Out-Null }
        if (Test-Path $archivo) { Remove-Item $archivo }
        Write-Host "${id}: deshecho."
    }
}

Export-ModuleMember -Function Get-AdaptadoresGpu, Get-GpuDeProceso, Get-Catalogo, Get-EstadoAjustes, Set-Ajustes, Undo-Ajustes, Test-Aplicado, Test-GpuDedicadaWddm27, Resolve-ValorAjuste
