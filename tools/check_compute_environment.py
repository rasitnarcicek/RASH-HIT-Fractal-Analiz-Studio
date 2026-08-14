#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""tools/check_compute_environment.py

Stage 2.12 — prints a terminal compute-environment report and writes a safe
JSON snapshot (diagnostics/compute_environment.json) WITHOUT embedding personal
user paths.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root (containing ``backend``) is importable.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.compute import diagnostics


def main() -> int:
    report = diagnostics.build_report()
    diagnostics.print_report(report)
    path = diagnostics.write_json(report)
    print(f"\nJSON report written to: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
