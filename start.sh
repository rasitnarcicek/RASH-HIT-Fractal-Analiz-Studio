#!/usr/bin/env bash
cd "$(dirname "$0")"

# Check and activate virtual environment if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Starting RASH-HIT Fractal Studio Launcher..."
python3 launcher.py
