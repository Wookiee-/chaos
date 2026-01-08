@echo off
set ACTION=%1
set CFG=%2

if "%CFG%"=="" (
    echo Usage: multi_chaos.bat ^<start^|stop^> ^<config_file^>
    echo Example: multi_chaos.bat start server1.cfg
    pause
    exit /b
)

set SESSION=Chaos_%CFG%

if "%ACTION%"=="start" (
    echo [*] Starting instance for %CFG%...
    start "%SESSION%" /min python chaos.py %CFG%
)

if "%ACTION%"=="stop" (
    echo [*] Stopping instance for %CFG%...
    taskkill /FI "WINDOWTITLE eq %SESSION%*" /F
)