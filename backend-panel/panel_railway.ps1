param(
    [ValidateSet('check', 'runserver', 'iniciar_seguridad')]
    [string]$Accion = 'check',
    [string]$Email,
    [string]$Nombre = 'Responsable de seguridad'
)
$ErrorActionPreference = 'Stop'
$entornoPanel = Join-Path $PSScriptRoot '.env.railway'
if (!(Test-Path -LiteralPath $entornoPanel)) {
    throw 'Falta backend-panel/.env.railway, archivo privado que debe configurar el propietario.'
}
$env:LPN_ENV_FILE = $entornoPanel
$pythonPanel = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$managePanel = Join-Path $PSScriptRoot 'manage.py'
if ($Accion -eq 'runserver') {
    # Solo acceso HTTP de desarrollo en loopback; nunca es un servidor público.
    $env:DJANGO_DEBUG = 'true'
    $env:DJANGO_COOKIE_SECURE = 'false'
    & $pythonPanel $managePanel runserver 127.0.0.1:8000
} elseif ($Accion -eq 'iniciar_seguridad') {
    if (!$Email) { throw 'Indique -Email con el correo del propietario.' }
    & $pythonPanel $managePanel iniciar_seguridad --email $Email --nombre $Nombre
} else {
    & $pythonPanel $managePanel check --database default
}
if ($LASTEXITCODE -ne 0) { throw 'La operación no terminó correctamente.' }
