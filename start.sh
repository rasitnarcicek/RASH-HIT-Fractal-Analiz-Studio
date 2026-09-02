#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
#
# RASH-HIT Fractal Analysis — single official daily launcher (Linux/macOS).
# Mirrors RASH-HIT-Analysis.bat on Windows; both files delegate to launcher.py.

set -e
cd "$(dirname "$0")"

# Activate virtual environment if present (consistent with Windows .bat).
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

PY=""
for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1; then
        PY="$cand"
        break
    fi
done

if [ -z "$PY" ]; then
    echo "[ERROR] Python 3.9+ not found. Install from https://www.python.org/downloads/" >&2
    exit 1
fi

# src/ layout: proje kökü + src PYTHONPATH'e eklenir, böylece
# `from src.backend...` ve `from launcher import main` aynı script'te çalışır.
export PYTHONPATH="$(dirname "$0"):$(dirname "$0")/src:${PYTHONPATH:-}"

echo "Starting RASH-HIT Fractal Analysis..."
exec "$PY" "$(dirname "$0")/launcher.py" "$@"
