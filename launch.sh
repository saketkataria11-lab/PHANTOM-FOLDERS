#!/bin/bash
echo "========================================"
echo "  PHANTOM FOLDERS - Encrypted Vault"
echo "========================================"
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Try python3 first, then python
if command -v python3 &>/dev/null; then
    python3 main.py "$@"
elif command -v python &>/dev/null; then
    python main.py "$@"
elif [ -f ".venv/bin/python" ]; then
    .venv/bin/python main.py "$@"
elif [ -f "venv/bin/python" ]; then
    venv/bin/python main.py "$@"
else
    echo "[ERROR] Python not found. Please install Python 3.10+."
    echo "        Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "        macOS: brew install python3"
    exit 1
fi
