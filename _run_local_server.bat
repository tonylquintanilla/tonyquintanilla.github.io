@echo off
REM ================================================================
REM  PALOMA'S ORRERY - LOCAL GALLERY SERVER
REM ================================================================
REM  Project: Paloma's Orrery - Astronomical Visualization System
REM  Author: Tony Quintanilla
REM  Contact: tonyquintanilla@gmail.com
REM  Version: 1.0
REM
REM  Description:
REM    Serves THIS repo over http://localhost:8000 and opens the
REM    assembler dev page in the default browser.
REM
REM    Why a server is needed at all: the dev page uses fetch() to
REM    pull the assembler's Python files and the served cache off
REM    disk, and browsers refuse fetch() from a file:// page. Opening
REM    the .html by double-clicking will NOT work.
REM
REM  Place this file in the ROOT of tonyquintanilla.github.io --
REM  the folder containing data\ and gallery\. It serves from its own
REM  location, so the page's ..\data\ paths resolve.
REM
REM  To stop the server: press Ctrl+C in this window, or just close it.
REM
REM  Philosophy: "Data Preservation is Climate Action"
REM ================================================================

echo.
echo ============================================================
echo     PALOMA'S ORRERY - Local Gallery Server
echo ============================================================
echo     "Data Preservation is Climate Action"
echo ============================================================
echo.

set SCRIPT_DIR=%~dp0
set PORT=8000
set PAGE=gallery/solar_system_earth_test2.html

REM ---- Python present? -------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Install Python 3.11 or later from
    echo https://www.python.org/downloads/ and make sure
    echo "Add Python to PATH" is checked.
    echo.
    pause
    exit /b 1
)

REM ---- Are we in the right folder? --------------------------------
REM Serving from the wrong directory is the failure that looks like a
REM broken page: the page loads and every fetch 404s. Check first.
if not exist "%SCRIPT_DIR%data\solar-system\coverage_index.json" (
    echo ERROR: served cache not found.
    echo.
    echo Expected: %SCRIPT_DIR%data\solar-system\coverage_index.json
    echo.
    echo This batch file must sit in the ROOT of the gallery repo
    echo ^(tonyquintanilla.github.io^), beside data\ and gallery\.
    echo If the folder is right but the cache is missing, run the
    echo gallery cache builder first.
    echo.
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%%PAGE:/=\%" (
    echo ERROR: %PAGE% not found under %SCRIPT_DIR%
    echo.
    pause
    exit /b 1
)

cd /d "%SCRIPT_DIR%"

REM ---- Is the port already taken? ---------------------------------
REM If a server is already running, starting a second one fails with a
REM confusing socket error. Detect it and just open the browser.
netstat -ano | findstr /r /c:"LISTENING" | findstr /c:":%PORT% " >nul 2>&1
if %errorlevel% equ 0 (
    echo A server is already listening on port %PORT%.
    echo Opening the page against the existing server.
    echo.
    start "" "http://localhost:%PORT%/%PAGE%"
    echo If that page is stale, close the OTHER server window first,
    echo then run this file again.
    echo.
    pause
    exit /b 0
)

echo Serving:  %cd%
echo Address:  http://localhost:%PORT%/
echo Page:     %PAGE%
echo.
echo The server runs in THIS window and prints one line per request.
echo That is the server working, not a hang.
echo Press Ctrl+C or close this window to stop it.
echo.

REM Open the browser a moment after the server starts listening.
start "" /b cmd /c "timeout /t 2 >nul & start "" "http://localhost:%PORT%/%PAGE%""

python -m http.server %PORT%

echo.
echo Server stopped.
echo.
timeout /t 2
