param(
    [string]$ProjectRoot
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path $ProjectRoot).Path
$mysqlBase = "C:\Program Files\MySQL\MySQL Server 8.4"
$mysqldExe = Join-Path $mysqlBase "bin\mysqld.exe"
$mysqlExe = Join-Path $mysqlBase "bin\mysql.exe"
$runtimeRoot = Join-Path $root "runtime\mysql"
$dataDir = Join-Path $runtimeRoot "data"
$tmpDir = Join-Path $runtimeRoot "tmp"
$logDir = Join-Path $runtimeRoot "logs"
$configFile = Join-Path $runtimeRoot "my.ini"
$appConfigFile = Join-Path $runtimeRoot "app_db.json"
$pidFile = Join-Path $runtimeRoot "mysql.pid"
$port = 3306
$databaseName = "camouflage_insect_app"
$appUser = "camouflage_app"
$appPassword = "Camouflage@2026"

function Get-MySqlListenerPid {
    $matches = netstat -ano | Select-String ":$port" | Select-String "LISTENING"
    foreach ($match in $matches) {
        $parts = ($match.Line -replace "\s+", " ").Trim().Split(" ")
        if ($parts.Length -ge 5 -and $parts[1] -like "*:$port") {
            return [int]$parts[4]
        }
    }
    return $null
}

if (-not (Test-Path $mysqldExe)) {
    throw "MySQL Server 8.4 is not installed: $mysqldExe"
}

New-Item -ItemType Directory -Force -Path $runtimeRoot, $dataDir, $tmpDir, $logDir | Out-Null

$configContent = @"
[mysqld]
basedir=$($mysqlBase.Replace('\', '/'))
datadir=$($dataDir.Replace('\', '/'))
port=$port
bind-address=127.0.0.1
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
default-time-zone=+08:00
max_allowed_packet=64M
tmpdir=$($tmpDir.Replace('\', '/'))
log-error=$((Join-Path $logDir 'mysql-error.log').Replace('\', '/'))
secure-file-priv=""
skip-symbolic-links

[client]
port=$port
default-character-set=utf8mb4
"@

Set-Content -LiteralPath $configFile -Value $configContent -Encoding ascii

$appConfig = @{
    host = "127.0.0.1"
    port = $port
    user = $appUser
    password = $appPassword
    database = $databaseName
} | ConvertTo-Json

Set-Content -LiteralPath $appConfigFile -Value $appConfig -Encoding utf8

$systemTables = Join-Path $dataDir "mysql.ibd"
if (-not (Test-Path $systemTables)) {
    Get-ChildItem -LiteralPath $dataDir -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    & $mysqldExe --defaults-file=$configFile --initialize-insecure
    if ($LASTEXITCODE -ne 0) {
        throw "MySQL data directory initialization failed."
    }
}

$listenerPid = Get-MySqlListenerPid
if (-not $listenerPid) {
    $process = Start-Process -FilePath $mysqldExe -ArgumentList @("--defaults-file=$configFile", "--standalone") -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 2

    $deadline = (Get-Date).AddSeconds(20)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 500
        $listenerPid = Get-MySqlListenerPid
        if ($listenerPid) {
            break
        }
    }

    if (-not $listenerPid) {
        throw "MySQL process started, but port $port did not open."
    }

    Set-Content -LiteralPath $pidFile -Value $listenerPid -Encoding ascii
}

$ready = $false
$deadline = (Get-Date).AddSeconds(20)
while ((Get-Date) -lt $deadline) {
    try {
        & $mysqlExe --protocol=tcp -h 127.0.0.1 -P $port -u root -e "SELECT 1;" | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $ready = $true
            break
        }
    } catch {
    }
    Start-Sleep -Milliseconds 800
}

if (-not $ready) {
    throw "MySQL process is running, but the root connection is not ready."
}

$setupSql = @"
CREATE DATABASE IF NOT EXISTS camouflage_insect_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$appUser'@'127.0.0.1' IDENTIFIED BY '$appPassword';
CREATE USER IF NOT EXISTS '$appUser'@'localhost' IDENTIFIED BY '$appPassword';
GRANT ALL PRIVILEGES ON camouflage_insect_app.* TO '$appUser'@'127.0.0.1';
GRANT ALL PRIVILEGES ON camouflage_insect_app.* TO '$appUser'@'localhost';
FLUSH PRIVILEGES;
"@

& $mysqlExe --protocol=tcp -h 127.0.0.1 -P $port -u root -e $setupSql
if ($LASTEXITCODE -ne 0) {
    throw "MySQL database or application user initialization failed."
}

Write-Output "MYSQL_HOST=127.0.0.1"
Write-Output "MYSQL_PORT=$port"
Write-Output "MYSQL_DATABASE=$databaseName"
Write-Output "MYSQL_USER=$appUser"
