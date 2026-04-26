param(
    [string]$ProjectRoot
)

$root = (Resolve-Path $ProjectRoot).Path
$pidFile = Join-Path $root "runtime\mysql\mysql.pid"
$mysqlExe = "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"

if (Test-Path $mysqlExe) {
    try {
        & $mysqlExe --protocol=tcp -h 127.0.0.1 -P 3306 -u root -e "SHUTDOWN;" 2>$null | Out-Null
        Start-Sleep -Seconds 2
    } catch {
    }
}

if (Test-Path $pidFile) {
    $pidText = Get-Content -LiteralPath $pidFile -ErrorAction SilentlyContinue
    if ($pidText -match '^\d+$') {
        Stop-Process -Id ([int]$pidText) -Force -ErrorAction SilentlyContinue
    }
    Remove-Item $pidFile -ErrorAction SilentlyContinue
    exit 0
}

$matches = netstat -ano | Select-String ":3306" | Select-String "LISTENING"
foreach ($match in $matches) {
    $parts = ($match.Line -replace "\s+", " ").Trim().Split(" ")
    if ($parts.Length -ge 5 -and $parts[1] -like "*:3306") {
        Stop-Process -Id ([int]$parts[4]) -Force -ErrorAction SilentlyContinue
    }
}
