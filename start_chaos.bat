@echo off
set SESSION_NAME=ChaosRPG
set SCRIPT=chaos.py

:menu
cls
echo ===========================================
echo    MBII CHAOS RPG MANAGEMENT (WINDOWS)
echo ===========================================
echo 1) Start Chaos (Detached)
echo 2) Stop Chaos
echo 3) Restart Chaos
echo 4) Status
echo 5) Exit
echo ===========================================
set /p choice="Choose an option (1-5): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" exit
goto menu

:start
tasklist /FI "WINDOWTITLE eq %SESSION_NAME%" | find /i "python.exe" >nul
if %errorlevel% equ 0 (
    echo [!] Chaos is already running!
    pause
    goto menu
)
echo [*] Starting Chaos in a new detached window...
:: Starts minimized so it stays out of your way
start "%SESSION_NAME%" /min python %SCRIPT%
echo [+] Chaos is now running in the background.
pause
goto menu

:stop
echo [*] Killing Chaos process...
taskkill /FI "WINDOWTITLE eq %SESSION_NAME%" /F >nul 2>&1
echo [+] Chaos has been stopped.
pause
goto menu

:restart
call :stop
timeout /t 2 >nul
call :start
goto menu

:status
tasklist /FI "WINDOWTITLE eq %SESSION_NAME%" | find /i "python.exe" >nul
if %errorlevel% equ 0 (
    echo [+] Chaos Status: RUNNING
) else (
    echo [-] Chaos Status: STOPPED
)
pause
goto menu