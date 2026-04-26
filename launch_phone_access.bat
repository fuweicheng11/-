@echo off
setlocal

set "APP_ROOT=%~dp0"
if "%APP_ROOT:~-1%"=="\" set "APP_ROOT=%APP_ROOT:~0,-1%"

call "%APP_ROOT%\launch_mini_app.bat"

powershell -NoProfile -ExecutionPolicy Bypass -File "%APP_ROOT%\scripts\start_phone_tunnel.ps1" -ProjectRoot "%APP_ROOT%"
if errorlevel 1 (
    echo [ERROR] Failed to create the phone access URL.
    pause
    exit /b 1
)

if exist "%APP_ROOT%\logs\phone_url.txt" (
    set /p PHONE_URL=<"%APP_ROOT%\logs\phone_url.txt"
    echo Phone URL: %PHONE_URL%
)

echo The URL has also been written to logs\phone_url.txt
pause
