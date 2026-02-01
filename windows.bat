@echo off
chcp 65001 >nul 2>&1
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

title ShorterMusic - Instalator i Launcher

echo ============================================================
echo        ShorterMusic - Automatyczna konfiguracja
echo ============================================================
echo.

cd /d "%~dp0"

REM === KROK 1: Sprawdz Python ===
echo [1/5] Sprawdzanie Pythona...

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
    echo       Python !PYVER! znaleziony.
    set "PYTHON_CMD=python"
    goto :check_python_version
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set PYVER=%%i
    echo       Python !PYVER! znaleziony.
    set "PYTHON_CMD=python3"
    goto :check_python_version
)

REM Python nie znaleziony - pobierz i zainstaluj
echo       Python nie znaleziony. Pobieram...
echo.

set "PYTHON_INSTALLER=%TEMP%\python_installer.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"

echo       Pobieranie Python 3.12.2...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}" 2>nul

if not exist "%PYTHON_INSTALLER%" (
    echo [BLAD] Nie mozna pobrac Pythona.
    echo        Pobierz recznie z: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo       Instalowanie Pythona (moze to potrwac)...
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

REM Odczekaj na instalacje
timeout /t 5 /nobreak >nul

REM Odswierz PATH
set "PATH=%LOCALAPPDATA%\Programs\Python\Python312\;%LOCALAPPDATA%\Programs\Python\Python312\Scripts\;%PATH%"

del "%PYTHON_INSTALLER%" 2>nul

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [BLAD] Instalacja Pythona nie powiodla sie.
    echo        Zrestartuj komputer i sprobuj ponownie.
    pause
    exit /b 1
)

set "PYTHON_CMD=python"
echo       Python zainstalowany pomyslnie!

:check_python_version
REM Sprawdz wersje Pythona (minimum 3.8)
for /f "tokens=1,2 delims=." %%a in ('!PYTHON_CMD! -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do (
    set "PY_MAJOR=%%a"
    set "PY_MINOR=%%b"
)
if !PY_MAJOR! LSS 3 (
    echo [BLAD] Wymagany Python 3.8+, masz !PY_MAJOR!.!PY_MINOR!
    pause
    exit /b 1
)
if !PY_MAJOR! EQU 3 if !PY_MINOR! LSS 8 (
    echo [BLAD] Wymagany Python 3.8+, masz !PY_MAJOR!.!PY_MINOR!
    pause
    exit /b 1
)
echo.

REM === KROK 2: Sprawdz/pobierz FFmpeg ===
echo [2/5] Sprawdzanie FFmpeg...

set "FFMPEG_DIR=%~dp0files\bin\ffmpeg"
set "FFMPEG_EXE=%FFMPEG_DIR%\ffmpeg.exe"

if exist "%FFMPEG_EXE%" (
    echo       FFmpeg znaleziony.
    goto :check_ytdlp
)

where ffmpeg >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo       FFmpeg znaleziony w systemie.
    goto :check_ytdlp
)

echo       FFmpeg nie znaleziony. Pobieram...
if not exist "%FFMPEG_DIR%" mkdir "%FFMPEG_DIR%"

set "FFMPEG_ZIP=%TEMP%\ffmpeg.zip"
set "FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%FFMPEG_URL%' -OutFile '%FFMPEG_ZIP%'}" 2>nul

if not exist "%FFMPEG_ZIP%" (
    echo [BLAD] Nie mozna pobrac FFmpeg.
    pause
    exit /b 1
)

echo       Rozpakowywanie FFmpeg...
powershell -Command "Expand-Archive -Path '%FFMPEG_ZIP%' -DestinationPath '%TEMP%\ffmpeg_temp' -Force" 2>nul

REM Znajdz i skopiuj pliki exe
for /r "%TEMP%\ffmpeg_temp" %%f in (ffmpeg.exe) do (
    copy "%%f" "%FFMPEG_DIR%\" >nul 2>&1
)
for /r "%TEMP%\ffmpeg_temp" %%f in (ffprobe.exe) do (
    copy "%%f" "%FFMPEG_DIR%\" >nul 2>&1
)

rd /s /q "%TEMP%\ffmpeg_temp" 2>nul
del "%FFMPEG_ZIP%" 2>nul

if exist "%FFMPEG_EXE%" (
    echo       FFmpeg zainstalowany pomyslnie!
) else (
    echo [BLAD] Instalacja FFmpeg nie powiodla sie.
    pause
    exit /b 1
)

:check_ytdlp
echo.

REM === KROK 3: Sprawdz/pobierz yt-dlp ===
echo [3/5] Sprawdzanie yt-dlp...

set "YTDLP_DIR=%~dp0files\bin\yt-dlp"
set "YTDLP_EXE=%YTDLP_DIR%\yt-dlp.exe"

if exist "%YTDLP_EXE%" (
    echo       yt-dlp znaleziony.
    goto :setup_venv
)

where yt-dlp >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo       yt-dlp znaleziony w systemie.
    goto :setup_venv
)

echo       yt-dlp nie znaleziony. Pobieram...
if not exist "%YTDLP_DIR%" mkdir "%YTDLP_DIR%"

set "YTDLP_URL=https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%YTDLP_URL%' -OutFile '%YTDLP_EXE%'}" 2>nul

if exist "%YTDLP_EXE%" (
    echo       yt-dlp zainstalowany pomyslnie!
) else (
    echo [BLAD] Nie mozna pobrac yt-dlp.
    pause
    exit /b 1
)

:setup_venv
echo.

REM === KROK 4: Konfiguracja srodowiska Python ===
echo [4/5] Konfiguracja srodowiska Python...

set "VENV_DIR=%~dp0files\venv"
set "REQUIREMENTS=%~dp0files\requirements.txt"

if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo       Srodowisko wirtualne istnieje.
    goto :install_deps
)

echo       Tworzenie srodowiska wirtualnego...
!PYTHON_CMD! -m venv "%VENV_DIR%"

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [BLAD] Nie mozna utworzyc srodowiska wirtualnego.
    pause
    exit /b 1
)

:install_deps
call "%VENV_DIR%\Scripts\activate.bat"

REM Sprawdz czy zaleznosci sa zainstalowane
pip show librosa >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo       Instalowanie zaleznosci (moze to potrwac)...
    pip install --upgrade pip >nul 2>&1
    pip install -r "%REQUIREMENTS%" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [BLAD] Instalacja zaleznosci nie powiodla sie.
        pause
        exit /b 1
    )
    echo       Zaleznosci zainstalowane!
) else (
    echo       Zaleznosci juz zainstalowane.
)

echo.

REM === KROK 5: Uruchom aplikacje ===
echo [5/5] Uruchamianie ShorterMusic...
echo.
echo ============================================================
echo.

REM Dodaj lokalne binarki do PATH
set "PATH=%FFMPEG_DIR%;%YTDLP_DIR%;%PATH%"

cd /d "%~dp0files"
python interactive.py

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================
echo Aplikacja zakonczona.
pause

cd /d "%~dp0"
endlocal
exit /b %EXIT_CODE%
