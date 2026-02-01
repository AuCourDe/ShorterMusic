@echo off
setlocal ENABLEEXTENSIONS

rem ShorterMusic - Interactive Runner (Windows)

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [INFO] Tworzenie srodowiska wirtualnego...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Nie udalo sie utworzyc venv. Sprawdz czy Python jest zainstalowany.
        pause
        exit /b 1
    )
    echo [INFO] Instalowanie zaleznosci...
    call "venv\Scripts\pip" install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Nie udalo sie zainstalowac zaleznosci.
        pause
        exit /b 1
    )
    echo [OK] Srodowisko przygotowane.
    echo.
)

echo.
echo [INFO] Uruchamiam aplikacje ShorterMusic...
call "venv\Scripts\activate" >nul 2>&1
python interactive.py
set "EXIT_CODE=%ERRORLEVEL%"
call deactivate >nul 2>&1

set "DOWNLOAD_DIR=data\downloads"
if exist "%DOWNLOAD_DIR%" (
    echo.
    choice /C TN /M "Usunac zawartosc folderu \"Download\"? (jezeli nie usuniesz, to nastepny miks bedzie robiony ze wszystkich plikow w tym folderze)"
    if errorlevel 2 goto skip_cleanup
    if errorlevel 1 goto clean_downloads
) else (
    goto end_script
)

:clean_downloads
    echo.
    echo Czyszcze "%DOWNLOAD_DIR%"...
    powershell -NoProfile -Command "if (Test-Path '%DOWNLOAD_DIR%') { Get-ChildItem -LiteralPath '%DOWNLOAD_DIR%' -Force | Remove-Item -Recurse -Force }"
    if errorlevel 1 (
        echo [WARN] Nie udalo sie wyczyscic folderu downloads.
    ) else (
        echo [OK] Folder downloads zostal wyczyszczony.
    )
    goto end_script

:skip_cleanup
    echo.
    echo Pozostawiam pliki w "%DOWNLOAD_DIR%".
    echo (Nastepny miks wykorzysta wszystkie pliki pozostale w tym folderze.)
    goto end_script

:end_script
echo.
echo Zamykanie...
endlocal & exit /b %EXIT_CODE%
