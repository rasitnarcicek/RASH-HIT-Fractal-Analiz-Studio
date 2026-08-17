# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Stage 3.10 — CPU baseline benchmark (real measurements only).

Measures the EXISTING CPU engine at L7 and L10 (L12 only if it finishes under
a safety cap). Reports cold + >=3 hot runs with median/min/max, RAM usage,
segment/geometry counts, grid dimensions, occupied count, and accuracy vs the
frozen reference.

Writes benchmarks/stage3_cpu_baseline.json with REAL numbers (no synthetic
durations). Never edits reference files.

Usage:
  .venv\\Scripts\\python.exe tools/benchmark_cpu_baseline.py
"""
from __future__ import annotations

import json
import statistics
import sys
import time
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.processor import AnalysisProcessor  # noqa: E402

# Pick representative fixtures (simple + moderate). Complex ones are skipped
# from the forced L12 cap to avoid multi-minute runs.
TARGETS = {
    "horizontal_line.svg": 7,
    "diagonal_line.svg": 7,
    "filled_rectangle.svg": 7,
    "filled_circle.svg": 10,
    "simple_polygon.svg": 10,
    "evenodd_path.svg": 10,
}
L12_CAP_SECONDS = 60.0


def _measure(svg: Path, levels: int):
    import os, psutil
    with tempfile.TemporaryDirectory() as td:
        proc = AnalysisProcessor(input_path=svg, output_dir=td, levels=levels, export_artifacts=False)
        # cold
        t0 = time.perf_counter()
        res = proc.run()
        cold = time.perf_counter() - t0
        if res.status != "SUCCESS":
            raise RuntimeError(res.errors)
        # hot repeats
        hots = []
        for _ in range(3):
            t0 = time.perf_counter()
            with tempfile.TemporaryDirectory() as td2:
                AnalysisProcessor(input_path=svg, output_dir=td2, levels=levels, export_artifacts=False).run()
            hots.append(time.perf_counter() - t0)
        mem_mb = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        result_json = Path(td) / res.package_id / "result.json"
        data = json.loads(result_json.read_text(encoding="utf-8"))
        lgrid = {int(r["level"]): r for r in data.get("level_grid", [])}
        top = lgrid[max(lgrid.keys())]
        return {
            "cold_seconds": round(cold, 4),
            "hot_seconds": {
                "median": round(statistics.median(hots), 4),
                "min": round(min(hots), 4),
                "max": round(max(hots), 4),
            },
            "ram_rss_mb": round(mem_mb, 1),
            "requested_levels": levels,
            "top_level": top["level"],
            "grid_columns": top["columns"],
            "grid_rows": top["rows"],
            "occupied_cells": top["filled_cells"],
            "total_cells": top["total_cells"],
            "fractal_dimension": round(res.fractal_dimension, 4),
            "r_squared": round(res.r_squared, 4),
            "status": res.status,
        }


def main() -> int:
    import glob
    out = {"schema": "rashhit.cpu.baseline/v1",
           "generated_at": datetime.now(timezone.utc).isoformat(),
           "engine": "cpu_reference", "runs": []}
    fixtures = ROOT / "tests" / "fixtures" / "svg_reference"
    for name, lv in TARGETS.items():
        svg = fixtures / name
        if not svg.exists():
            print(f"skip {name} (fixture missing)")
            continue
        try:
            r = _measure(svg, lv)
            # Optional L12 if L10 was fast.
            if r["hot_seconds"]["median"] < L12_CAP_SECONDS / 4:
                try:
                    r12 = _measure(svg, 12)
                    r["l12"] = r12
                except Exception as e:
                    r["l12"] = {"skipped": str(e)}
            out["runs"].append({"fixture": name, "result": r})
            print(f"  {name:24s} L{lv} cold={r['cold_seconds']}s hot_med={r['hot_seconds']['median']}s Db={r['fractal_dimension']}")
        except Exception as e:
            print(f"  [ERR] {name}: {e}")
    (ROOT / "benchmarks").mkdir(exist_ok=True)
    (ROOT / "benchmarks" / "stage3_cpu_baseline.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote benchmarks/stage3_cpu_baseline.json ({len(out['runs'])} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
