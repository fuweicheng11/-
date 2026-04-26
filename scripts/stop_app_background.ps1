param(
    [string]$ProjectRoot
)

$root = (Resolve-Path $ProjectRoot).Path
$runner = Join-Path $root "scripts\run_app.ps1"
$appFile = Join-Path $root "app.py"

Get-CimInstance Win32_Process |
    Where-Object {
        ($_.Name -eq "powershell.exe" -and $_.CommandLine -like "*$runner*") -or
        ($_.Name -eq "python.exe" -and $_.CommandLine -like "*$appFile*")
    } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
