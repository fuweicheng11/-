@echo off
setlocal

set "APP_ROOT=%~dp0"
if "%APP_ROOT:~-1%"=="\" set "APP_ROOT=%APP_ROOT:~0,-1%"
set "RUNTIME_DRIVE=%APP_ROOT%\runtime\CamouflageDriveQ"

powershell -NoProfile -ExecutionPolicy Bypass -File "%APP_ROOT%\scripts\setup_local_mysql.ps1" -ProjectRoot "%APP_ROOT%"
if errorlevel 1 (
    echo [ERROR] Local MySQL could not be prepared.
    pause
    exit /b 1
)

if not exist "%RUNTIME_DRIVE%\08\fusion_results\fusion_best.pth" (
    echo [ERROR] Runtime assets are missing: %RUNTIME_DRIVE%
    pause
    exit /b 1
)

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":7863" ^| findstr "LISTENING"') do set "APP_PID=%%p"
if defined APP_PID (
    echo Mini app is already running: http://127.0.0.1:7863
    exit /b 0
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%APP_ROOT%\scripts\start_app_background.ps1" -ProjectRoot "%APP_ROOT%"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$deadline=(Get-Date).AddSeconds(30); $ready=$false; while((Get-Date)-lt $deadline){ try { $r=Invoke-WebRequest -Uri 'http://127.0.0.1:7863/' -UseBasicParsing -TimeoutSec 5; if($r.StatusCode -eq 200){ $ready=$true; break } } catch {}; Start-Sleep -Milliseconds 700 }; if(-not $ready){ exit 1 }"
if errorlevel 1 (
    echo [ERROR] Mini app failed to warm up on http://127.0.0.1:7863
    pause
    exit /b 1
)

echo Mini app started: http://127.0.0.1:7863
echo Phone access: run launch_phone_access.bat
ping -n 3 127.0.0.1 >nul
