@echo off
REM Frees port 8000 — the process start-backup.bat launched.
setlocal enabledelayedexpansion
set FOUND=0
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":8000 .*LISTENING"') do (
    taskkill /PID %%p /F >nul 2>&1
    echo Stopped PID %%p
    set FOUND=1
)
if "!FOUND!"=="0" echo Nothing was listening on port 8000.
endlocal
