param(
    [string]$ProjectRoot
)

$root = (Resolve-Path $ProjectRoot).Path
$appFile = Join-Path $root "app.py"
$logDir = Join-Path $root "logs"
$stdoutLog = Join-Path $logDir "app_stdout.log"
$stderrLog = Join-Path $logDir "app_stderr.log"

$env:APP_HOST = "0.0.0.0"
$env:APP_PORT = "7863"

Set-Location $root
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python $appFile 1>> $stdoutLog 2>> $stderrLog
    exit $LASTEXITCODE
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $appFile 1>> $stdoutLog 2>> $stderrLog
    exit $LASTEXITCODE
}

throw "Python was not found in PATH."
