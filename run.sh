#!/usr/bin/env bash
# ShorterMusic - Interactive Runner (Linux/macOS)
set -u

cd "$(dirname "$0")"

# Pick a Python interpreter to create the venv. Prefer 3.11 (matches requirements.txt).
PY_CREATE=""
for candidate in python3.11 python3.12 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PY_CREATE="$candidate"
        break
    fi
done

if [ -z "$PY_CREATE" ]; then
    echo "[ERROR] No suitable Python found. Install Python 3.10-3.12."
    exit 1
fi

if [ ! -x "venv/bin/python" ]; then
    echo "[INFO] Creating virtual environment: $PY_CREATE ..."
    "$PY_CREATE" -m venv venv || { echo "[ERROR] Failed to create venv."; exit 1; }
fi

# Self-healing: if a key dependency (numpy) does not import, (re)install requirements.
if ! venv/bin/python -c "import numpy" >/dev/null 2>&1; then
    echo "[INFO] Installing dependencies..."
    venv/bin/python -m pip install -r requirements.txt || { echo "[ERROR] Failed to install dependencies."; exit 1; }
    echo "[OK] Environment ready."
    echo
fi

echo
echo "[INFO] Starting ShorterMusic..."
venv/bin/python interactive.py
EXIT_CODE=$?

DOWNLOAD_DIR="data/downloads"
if [ -d "$DOWNLOAD_DIR" ]; then
    echo
    echo "Clear the downloads folder?"
    echo "(if you keep the files, the next mix will use every file in that folder)"
    read -r -p "Type Y to delete, or press Enter to keep [default N]: " ANSWER
    case "${ANSWER:-N}" in
        [Yy]*)
            echo "Clearing \"$DOWNLOAD_DIR\"..."
            if rm -rf "${DOWNLOAD_DIR:?}/"* 2>/dev/null; then
                echo "[OK] Downloads folder cleared."
            else
                echo "[WARN] Could not clear the downloads folder."
            fi
            ;;
        *)
            echo "Keeping files in \"$DOWNLOAD_DIR\"."
            ;;
    esac
fi

exit $EXIT_CODE
