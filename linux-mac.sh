#!/bin/bash

# ShorterMusic - Portable Launcher (Linux/macOS)
# This script navigates to the files directory and runs the application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Navigate to files directory
cd "$SCRIPT_DIR/files" || {
    echo "[ERROR] Cannot find 'files' directory"
    exit 1
}

# Run the application
./run.sh

# Save exit code
EXIT_CODE=$?

# Return to original directory
cd "$SCRIPT_DIR"

# Exit with the same code as the application
exit $EXIT_CODE
