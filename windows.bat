@echo off
setlocal ENABLEEXTENSIONS

rem ShorterMusic - Portable Launcher (Windows)
rem This script navigates to the files directory and runs the application

cd /d "%~dp0files"
if errorlevel 1 (
    echo [ERROR] Nie mozna znalezc folderu "files"
    pause
    exit /b 1
)

call run.bat
set "EXIT_CODE=%ERRORLEVEL%"

cd /d "%~dp0"
endlocal & exit /b %EXIT_CODE%
