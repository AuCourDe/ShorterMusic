#!/bin/bash

# ShorterMusic - Automatic Installer and Launcher (Linux/macOS)
# This script automatically downloads and configures all dependencies

set -e

echo "============================================================"
echo "       ShorterMusic - Automatyczna konfiguracja"
echo "============================================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"

# === STEP 1: Check Python ===
echo "[1/5] Sprawdzanie Pythona..."

PYTHON_CMD=""

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYVER=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    echo "      Python $PYVER znaleziony."
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    if python --version 2>&1 | grep -q "Python 3"; then
        PYTHON_CMD="python"
        PYVER=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
        echo "      Python $PYVER znaleziony."
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "      Python nie znaleziony. Instalowanie..."

    if [ "$OS" = "Linux" ]; then
        # Try different package managers
        if command -v apt-get &> /dev/null; then
            echo "      Wykryto apt (Debian/Ubuntu)"
            sudo apt-get update -qq
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v dnf &> /dev/null; then
            echo "      Wykryto dnf (Fedora/RHEL)"
            sudo dnf install -y python3 python3-pip
        elif command -v pacman &> /dev/null; then
            echo "      Wykryto pacman (Arch)"
            sudo pacman -S --noconfirm python python-pip
        elif command -v zypper &> /dev/null; then
            echo "      Wykryto zypper (openSUSE)"
            sudo zypper install -y python3 python3-pip
        else
            echo "[BLAD] Nie rozpoznano menedzera pakietow."
            echo "       Zainstaluj Python 3.8+ recznie."
            exit 1
        fi
        PYTHON_CMD="python3"
    elif [ "$OS" = "Darwin" ]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "      Instalowanie przez Homebrew..."
            brew install python@3.12
            PYTHON_CMD="python3"
        else
            echo "[BLAD] Homebrew nie znaleziony."
            echo "       Zainstaluj Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "       Lub pobierz Python z: https://www.python.org/downloads/"
            exit 1
        fi
    fi

    if ! command -v $PYTHON_CMD &> /dev/null; then
        echo "[BLAD] Instalacja Pythona nie powiodla sie."
        exit 1
    fi
    echo "      Python zainstalowany pomyslnie!"
fi

# Check Python version (minimum 3.8)
PY_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo $PY_VERSION | cut -d'.' -f1)
PY_MINOR=$(echo $PY_VERSION | cut -d'.' -f2)

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]); then
    echo "[BLAD] Wymagany Python 3.8+, masz $PY_VERSION"
    exit 1
fi
echo ""

# === STEP 2: Check/download FFmpeg ===
echo "[2/5] Sprawdzanie FFmpeg..."

FFMPEG_DIR="$SCRIPT_DIR/files/bin/ffmpeg"
FFMPEG_BIN="$FFMPEG_DIR/ffmpeg"

if [ -x "$FFMPEG_BIN" ]; then
    echo "      FFmpeg znaleziony."
elif command -v ffmpeg &> /dev/null; then
    echo "      FFmpeg znaleziony w systemie."
else
    echo "      FFmpeg nie znaleziony. Pobieram..."
    mkdir -p "$FFMPEG_DIR"

    if [ "$OS" = "Linux" ]; then
        if [ "$ARCH" = "x86_64" ]; then
            FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        elif [ "$ARCH" = "aarch64" ]; then
            FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz"
        else
            echo "[BLAD] Nieobslugiwana architektura: $ARCH"
            echo "       Zainstaluj FFmpeg recznie: sudo apt install ffmpeg"
            exit 1
        fi

        echo "      Pobieranie FFmpeg dla Linux $ARCH..."
        curl -L "$FFMPEG_URL" -o /tmp/ffmpeg.tar.xz
        tar -xf /tmp/ffmpeg.tar.xz -C /tmp
        cp /tmp/ffmpeg-*-static/ffmpeg "$FFMPEG_DIR/"
        cp /tmp/ffmpeg-*-static/ffprobe "$FFMPEG_DIR/"
        chmod +x "$FFMPEG_DIR/ffmpeg" "$FFMPEG_DIR/ffprobe"
        rm -rf /tmp/ffmpeg.tar.xz /tmp/ffmpeg-*-static

    elif [ "$OS" = "Darwin" ]; then
        if command -v brew &> /dev/null; then
            echo "      Instalowanie FFmpeg przez Homebrew..."
            brew install ffmpeg
        else
            echo "      Pobieranie FFmpeg dla macOS..."
            if [ "$ARCH" = "arm64" ]; then
                FFMPEG_URL="https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
            else
                FFMPEG_URL="https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
            fi
            curl -L "$FFMPEG_URL" -o /tmp/ffmpeg.zip
            unzip -o /tmp/ffmpeg.zip -d "$FFMPEG_DIR/"
            chmod +x "$FFMPEG_DIR/ffmpeg"
            rm /tmp/ffmpeg.zip
        fi
    fi

    if [ -x "$FFMPEG_BIN" ] || command -v ffmpeg &> /dev/null; then
        echo "      FFmpeg zainstalowany pomyslnie!"
    else
        echo "[BLAD] Instalacja FFmpeg nie powiodla sie."
        echo "       Zainstaluj recznie: sudo apt install ffmpeg (Linux)"
        echo "                          brew install ffmpeg (macOS)"
        exit 1
    fi
fi
echo ""

# === STEP 3: Check/download yt-dlp ===
echo "[3/5] Sprawdzanie yt-dlp..."

YTDLP_DIR="$SCRIPT_DIR/files/bin/yt-dlp"
YTDLP_BIN="$YTDLP_DIR/yt-dlp"

if [ -x "$YTDLP_BIN" ]; then
    echo "      yt-dlp znaleziony."
elif command -v yt-dlp &> /dev/null; then
    echo "      yt-dlp znaleziony w systemie."
else
    echo "      yt-dlp nie znaleziony. Pobieram..."
    mkdir -p "$YTDLP_DIR"

    YTDLP_URL="https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
    curl -L "$YTDLP_URL" -o "$YTDLP_BIN"
    chmod +x "$YTDLP_BIN"

    if [ -x "$YTDLP_BIN" ]; then
        echo "      yt-dlp zainstalowany pomyslnie!"
    else
        echo "[BLAD] Nie mozna pobrac yt-dlp."
        exit 1
    fi
fi
echo ""

# === STEP 4: Setup Python environment ===
echo "[4/5] Konfiguracja srodowiska Python..."

VENV_DIR="$SCRIPT_DIR/files/venv"
REQUIREMENTS="$SCRIPT_DIR/files/requirements.txt"

if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "      Srodowisko wirtualne istnieje."
else
    echo "      Tworzenie srodowiska wirtualnego..."
    $PYTHON_CMD -m venv "$VENV_DIR"

    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        echo "[BLAD] Nie mozna utworzyc srodowiska wirtualnego."
        exit 1
    fi
fi

source "$VENV_DIR/bin/activate"

# Check if dependencies are installed
if ! pip show librosa &> /dev/null; then
    echo "      Instalowanie zaleznosci (moze to potrwac)..."
    pip install --upgrade pip -q
    pip install -r "$REQUIREMENTS" -q

    if [ $? -ne 0 ]; then
        echo "[BLAD] Instalacja zaleznosci nie powiodla sie."
        exit 1
    fi
    echo "      Zaleznosci zainstalowane!"
else
    echo "      Zaleznosci juz zainstalowane."
fi
echo ""

# === STEP 5: Run application ===
echo "[5/5] Uruchamianie ShorterMusic..."
echo ""
echo "============================================================"
echo ""

# Add local binaries to PATH
export PATH="$FFMPEG_DIR:$YTDLP_DIR:$PATH"

cd "$SCRIPT_DIR/files"
python interactive.py
EXIT_CODE=$?

echo ""
echo "============================================================"
echo "Aplikacja zakonczona."

exit $EXIT_CODE
