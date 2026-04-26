@echo off
setlocal

set "APP_ROOT=%~dp0"
if "%APP_ROOT:~-1%"=="\" set "APP_ROOT=%APP_ROOT:~0,-1%"

powershell -NoProfile -ExecutionPolicy Bypass -File "%APP_ROOT%\scripts\stop_app_background.ps1" -ProjectRoot "%APP_ROOT%"
powershell -NoProfile -ExecutionPolicy Bypass -File "%APP_ROOT%\scripts\stop_local_mysql.ps1" -ProjectRoot "%APP_ROOT%"

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":7863" ^| findstr "LISTENING"') do taskkill /pid %%p /f >nul 2>nul

if exist "%APP_ROOT%\logs\phone_tunnel.pid" (
    for /f "usebackq delims=" %%p in ("%APP_ROOT%\logs\phone_tunnel.pid") do taskkill /pid %%p /f >nul 2>nul
)

del "%APP_ROOT%\logs\phone_tunnel.pid" >nul 2>nul
del "%APP_ROOT%\logs\phone_url.txt" >nul 2>nul
del "%APP_ROOT%\logs\phone_tunnel.log" >nul 2>nul

echo Tried to stop the mini app, phone tunnel, and local MySQL.
ping -n 3 127.0.0.1 >nul
