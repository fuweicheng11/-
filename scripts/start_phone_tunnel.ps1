param(
    [string]$ProjectRoot
)

$root = (Resolve-Path $ProjectRoot).Path
$logDir = Join-Path $root "logs"
$logFile = Join-Path $logDir "phone_tunnel.log"
$urlFile = Join-Path $logDir "phone_url.txt"
$pidFile = Join-Path $logDir "phone_tunnel.pid"

$attemptLimit = 5
$attemptTimeoutSeconds = 12
$retryPauseSeconds = 2

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Stop-TunnelProcess {
    param([int]$ProcessId)

    if ($ProcessId -gt 0) {
        Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function Get-TunnelUrlFromLog {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return $null
    }

    $text = Get-Content -LiteralPath $Path -Raw -ErrorAction SilentlyContinue
    $match = [regex]::Match($text, 'https://[-a-z0-9]+\.trycloudflare\.com')
    if ($match.Success) {
        return $match.Value
    }

    return $null
}

function Get-TunnelErrorFromLog {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return $null
    }

    $text = Get-Content -LiteralPath $Path -Raw -ErrorAction SilentlyContinue
    $patterns = @(
        '"level":"error".*"message":"([^"]+)"',
        '"level":"error".*"error":"([^"]+)"',
        'Error unmarshaling QuickTunnel response: [^\r\n]+',
        'Failed to request quick Tunnel: [^\r\n]+'
    )

    foreach ($pattern in $patterns) {
        $match = [regex]::Match($text, $pattern)
        if ($match.Success) {
            if ($match.Groups.Count -gt 1 -and $match.Groups[1].Value) {
                return $match.Groups[1].Value
            }
            return $match.Value
        }
    }

    return $null
}

if (Test-Path $pidFile) {
    $oldPid = Get-Content -LiteralPath $pidFile -ErrorAction SilentlyContinue
    if ($oldPid -match '^\d+$') {
        Stop-TunnelProcess -ProcessId ([int]$oldPid)
    }
}

Remove-Item $logFile, $urlFile, $pidFile -ErrorAction SilentlyContinue

$cloudflared = (Get-Command cloudflared -ErrorAction Stop).Source
$arguments = @(
    "tunnel",
    "--url",
    "http://127.0.0.1:7863",
    "--no-autoupdate",
    "--logfile",
    $logFile
)

$url = $null
$lastError = $null
$activeProcess = $null

for ($attempt = 1; $attempt -le $attemptLimit; $attempt++) {
    Remove-Item $logFile -ErrorAction SilentlyContinue
    $activeProcess = Start-Process -FilePath $cloudflared -ArgumentList $arguments -WorkingDirectory $root -PassThru -WindowStyle Hidden

    $deadline = (Get-Date).AddSeconds($attemptTimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 500

        $url = Get-TunnelUrlFromLog -Path $logFile
        if ($url) {
            break
        }

        $lastError = Get-TunnelErrorFromLog -Path $logFile
        if ($lastError) {
            break
        }

        if ($activeProcess.HasExited) {
            $lastError = "Tunnel process exited before a URL was created."
            break
        }
    }

    if ($url) {
        break
    }

    Stop-TunnelProcess -ProcessId $activeProcess.Id
    $activeProcess = $null

    if ($attempt -lt $attemptLimit) {
        Start-Sleep -Seconds $retryPauseSeconds
    }
}

if (-not $url) {
    Remove-Item $pidFile -ErrorAction SilentlyContinue
    $message = if ($lastError) { $lastError } else { "Phone access URL was not created in time." }
    throw "Failed to create phone access URL after $attemptLimit attempts. $message"
}

Set-Content -LiteralPath $pidFile -Value $activeProcess.Id -Encoding ascii
Set-Content -LiteralPath $urlFile -Value $url -Encoding ascii

try {
    Set-Clipboard -Value $url
} catch {
}

Write-Output "PHONE_URL=$url"
