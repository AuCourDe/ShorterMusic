#!/bin/bash

# ShorterMusic - Interactive Runner
# Skrypt aktywujący środowisko wirtualne i uruchamiający interactive.py

# Przejdź do katalogu projektu
cd "$(dirname "$0")"

# Sprawdź czy środowisko wirtualne istnieje
if [ ! -d "venv" ]; then
    echo "Środowisko wirtualne 'venv' nie istnieje!"
    echo "Utwórz je za pomocą: python3 -m venv venv"
    exit 1
fi

# Uruchom skrypt interaktywny używając pythona ze środowiska wirtualnego
venv/bin/python interactive.py

# Zapisz kod wyjścia
EXIT_CODE=$?

# Zwróć kod wyjścia
exit $EXIT_CODE
