@echo off
setlocal ENABLEEXTENSIONS

rem ShorterMusic - Interactive Runner (Windows)

cd /d "%~dp0"

rem Prefer Python 3.11 (matches the pinned versions in requirements.txt).
rem Python 3.13/3.14 has no wheels for numpy 1.26 etc.
set "PY_CREATE="
py -3.11 --version >nul 2>&1
if not errorlevel 1 set "PY_CREATE=py -3.11"
if not defined PY_CREATE (
    py -3.12 --version >nul 2>&1
    if not errorlevel 1 set "PY_CREATE=py -3.12"
)
if not defined PY_CREATE (
    py -3.10 --version >nul 2>&1
    if not errorlevel 1 set "PY_CREATE=py -3.10"
)
if not defined PY_CREATE set "PY_CREATE=python"

if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment: %PY_CREATE% ...
    %PY_CREATE% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv. Check that Python is installed.
        pause
        exit /b 1
    )
)

rem Self-healing: if a key dependency (numpy) does not import, (re)install requirements.
"venv\Scripts\python.exe" -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    "venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [OK] Environment ready.
    echo.
)

echo.
echo [INFO] Starting ShorterMusic...
call "venv\Scripts\activate" >nul 2>&1
python interactive.py
set "EXIT_CODE=%ERRORLEVEL%"
call deactivate >nul 2>&1

set "DOWNLOAD_DIR=data\downloads"
if not exist "%DOWNLOAD_DIR%" goto end_script

echo.
echo Clear the downloads folder?
echo (if you keep the files, the next mix will use every file in that folder)
set "ANSWER=N"
set /p "ANSWER=Type Y to delete, or press Enter to keep [default N]: "
if /I "%ANSWER%"=="Y" goto clean_downloads
goto skip_cleanup

:clean_downloads
    echo.
    echo Clearing "%DOWNLOAD_DIR%"...
    powershell -NoProfile -Command "if (Test-Path '%DOWNLOAD_DIR%') { Get-ChildItem -LiteralPath '%DOWNLOAD_DIR%' -Force | Remove-Item -Recurse -Force }"
    if errorlevel 1 (
        echo [WARN] Could not clear the downloads folder.
    ) else (
        echo [OK] Downloads folder cleared.
    )
    goto end_script

:skip_cleanup
    echo.
    echo Keeping files in "%DOWNLOAD_DIR%".
    goto end_script

:end_script
echo.
echo Closing...
endlocal & exit /b %EXIT_CODE%
