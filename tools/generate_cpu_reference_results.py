# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Generate / verify CPU reference results for Stage 3 (3.5 / 3.6).

Runs the EXISTING CPU engine on every reference fixture and freezes L1-L10
results. Results are produced by the real engine (never hand-written).

Usage:
  # generate (or refresh) references — explicit, separate command:
  .venv\\Scripts\\python.exe tools/generate_cpu_reference_results.py --confirm-update

  # verify (default): run engine, compare counts/Db/R2 against frozen JSON;
  # never writes files unless --confirm-update is passed.
  .venv\\Scripts\\python.exe tools/generate_cpu_reference_results.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.processor import AnalysisProcessor  # noqa: E402

FIXTURE_DIR = ROOT / "tests" / "fixtures" / "svg_reference"
RESULT_DIR = ROOT / "tests" / "reference_results"
SCHEMA_VERSION = "rashhit.cpu.reference/v1"
APP_VERSION = "1.0.0"
LEVELS = 10
# Tolerances for Db / R2 comparison (existing math is deterministic; small slack
# guards against float repr differences only, not algorithmic change).
DB_TOL = 1e-6
R2_TOL = 1e-6


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def deps_versions():
    import importlib.metadata as md
    out = {}
    for pkg in ("numpy", "shapely", "taichi"):
        try:
            out[pkg] = md.version(pkg)
        except Exception:
            out[pkg] = "n/a"
    return out


def run_one(svg: Path) -> dict:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        proc = AnalysisProcessor(input_path=svg, output_dir=td, levels=LEVELS, export_artifacts=False)
        res = proc.run()
        if res.status != "SUCCESS":
            raise RuntimeError(f"{svg.name} -> {res.status}: {res.errors}")
        # Re-read the produced level rows from result.json
        result_json = Path(td) / res.package_id / "result.json"
        data = json.loads(result_json.read_text(encoding="utf-8"))
        # Per-level grid geometry lives in result['level_grid'] (added in Stage 3).
        lgrid = {int(r["level"]): r for r in data.get("level_grid", [])}
        ref = {
            "schema_version": SCHEMA_VERSION,
            "application_version": APP_VERSION,
            "fixture_name": svg.name,
            "input_sha256": sha256_of_file(svg),
            "engine": "cpu",
            "levels": LEVELS,
            "per_level": {
                str(lv): {
                    "grid_label": lgrid[lv]["grid_label"],
                    "rows": lgrid[lv]["rows"],
                    "columns": lgrid[lv]["columns"],
                    "total_cells": lgrid[lv]["total_cells"],
                    "occupied_cells": lgrid[lv]["filled_cells"],
                    "empty_cells": lgrid[lv]["empty_cells"],
                    "occupancy_ratio": round(lgrid[lv]["occupancy_percent"] / 100.0, 6),
                }
                for lv in sorted(lgrid.keys())
            },
            "fractal_dimension": round(res.fractal_dimension, 6),
            "r_squared": round(res.r_squared, 6),
            "dependency_versions": deps_versions(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python": f"{platform.python_version()} {platform.machine()}",
        }
        return ref


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm-update", action="store_true",
                   help="Regenerate reference JSON files (explicit override).")
    args = ap.parse_args()

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    svgs = sorted(FIXTURE_DIR.glob("*.svg"))
    if not svgs:
        print(f"ERROR: no fixtures in {FIXTURE_DIR}; run tools/generate_reference_fixtures.py first")
        return 2

    failures = 0
    print(f"{'UPDATE' if args.confirm_update else 'VERIFY'} {len(svgs)} fixtures @ L1-L{LEVELS}")
    for svg in svgs:
        if svg.name == "empty.svg":
            print(f"  [SKIP]  {svg.name} (no shapes — no CPU reference to freeze)")
            continue
        try:
            cur = run_one(svg)
        except Exception as e:
            print(f"  [ERROR] {svg.name}: {e}")
            failures += 1
            continue

        out_path = RESULT_DIR / f"{svg.stem}.json"
        if not out_path.exists():
            if args.confirm_update:
                out_path.write_text(json.dumps(cur, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"  [NEW]   {svg.stem}.json")
            else:
                print(f"  [MISS]  {svg.stem}.json (run with --confirm-update to create)")
                failures += 1
            continue

        if args.confirm_update:
            out_path.write_text(json.dumps(cur, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  [WRITE] {svg.stem}.json")
            continue

        # VERIFY mode: compare counts + Db/R2, and detect input change.
        old = json.loads(out_path.read_text(encoding="utf-8"))
        problems = []
        if old.get("input_sha256") != cur["input_sha256"]:
            problems.append("input SHA-256 changed (fixture edited)")
        if old["fractal_dimension"] != cur["fractal_dimension"] and abs(old["fractal_dimension"] - cur["fractal_dimension"]) > DB_TOL:
            problems.append(f"Db {old['fractal_dimension']} != {cur['fractal_dimension']}")
        if old["r_squared"] != cur["r_squared"] and abs(old["r_squared"] - cur["r_squared"]) > R2_TOL:
            problems.append(f"R2 {old['r_squared']} != {cur['r_squared']}")
        for lv in cur["per_level"]:
            o = old["per_level"].get(lv)
            c = cur["per_level"][lv]
            if o is None:
                problems.append(f"L{lv} missing in reference")
                continue
            for key in ("rows", "columns", "total_cells", "occupied_cells", "empty_cells"):
                if o[key] != c[key]:
                    problems.append(f"L{lv}.{key} {o[key]} != {c[key]}")
        if problems:
            print(f"  [FAIL]  {svg.stem}.json: " + "; ".join(problems))
            failures += 1
        else:
            print(f"  [OK]    {svg.stem}.json")

    print(f"\nRESULT: {failures} problem(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
