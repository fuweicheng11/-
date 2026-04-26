param(
    [string]$ProjectRoot
)

$root = (Resolve-Path $ProjectRoot).Path
$runner = Join-Path $root "scripts\run_app.ps1"
$arguments = @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $runner,
    "-ProjectRoot",
    $root
)

Start-Process -FilePath "powershell.exe" -ArgumentList $arguments -WindowStyle Hidden
