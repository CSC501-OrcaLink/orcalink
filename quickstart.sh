#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ "$#" -gt 1 ]; then
    echo "Usage: bash quickstart.sh [--build-only|--rebuild]"
    exit 1
fi

MODE="${1:-}"
if [ -n "$MODE" ] && [ "$MODE" != "--build-only" ] && [ "$MODE" != "--rebuild" ]; then
    echo "Usage: bash quickstart.sh [--build-only|--rebuild]"
    exit 1
fi

# Create a Python environment if needed
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

PYTHON=".venv/bin/python"
"$PYTHON" -m pip install -r requirements.txt

# Build a fresh database or check the existing one
if [ "$MODE" = "--rebuild" ]; then
    "$PYTHON" scripts/build_database.py --rebuild
else
    "$PYTHON" scripts/build_database.py
fi

if [ "$MODE" = "--build-only" ]; then
    echo "Database ready"
    exit 0
fi

# Start Flask with the demo database
export ORCALINK_DB="$(pwd)/orcalink_demo.db"
echo "Open http://127.0.0.1:5000"
"$PYTHON" app.py