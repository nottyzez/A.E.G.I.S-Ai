@echo off
REM A.E.G.I.S. LAN backup server.
REM Deliberately separate from deploy\digitalocean: this laptop is a *client* of
REM the "AEGIS" hotspot, so there is no Docker, no Nginx, the board dials port
REM 8000 directly, and AEGIS_REQUIRE_AUTH stays 0 (no dashboard token).
setlocal
cd /d "%~dp0..\.."
if not exist logs mkdir logs

netstat -ano | findstr /R /C:":8000 .*LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo Port 8000 is already in use.
    echo Run deploy\lan-backup\stop-backup.bat first.
    exit /b 1
)

echo Starting A.E.G.I.S. on http://0.0.0.0:8000  ^(TensorFlow needs ~30 s^)
echo Logs: logs\backup-server.out.log and .err.log

REM Not the script form (python main dot py): that closes stderr right after
REM the model loads on this machine ("lost sys.stderr"). The uvicorn CLI does not.
powershell -NoProfile -Command "Start-Process -FilePath 'python' -ArgumentList '-m','uvicorn','main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory (Get-Location) -WindowStyle Hidden -RedirectStandardOutput 'logs\backup-server.out.log' -RedirectStandardError 'logs\backup-server.err.log'"

echo.
echo Started. This machine's IP on the hotspot: run  ipconfig
echo Dashboard: http://^<ip^>:8000/dashboard
endlocal
