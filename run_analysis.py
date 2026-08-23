# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

"""
RASH-HIT Fractal Analiz Studio - Vector Geometry Box-Counting Engine
Version: 1.0.1
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import List

from backend.svg_loader import SVGLoader
from backend.geometry_engine import extract_node_geometries, ParsedGeometry
from backend.grid_planner import create_grid_plan
from backend.intersection_cpu_area import analyze_grid_cpu_area
from backend.fractal_analyzer import compute_fractal_dimension


def process_single_file(input_file: str, levels: int = 7):
    if levels < 1:
        print(f"Error: Invalid --levels '{levels}'. Number of grid levels must be >= 1.", file=sys.stderr)
        sys.exit(1)

    input_path = Path(input_file)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    # 1. Load SVG
    t0_load = time.perf_counter()
    try:
        loader = SVGLoader(str(input_path))
        elements = loader.get_elements()
        geoms: List[ParsedGeometry] = []
        for node, style in elements:
            geoms.extend(extract_node_geometries(node, style))
    except Exception as e:
        print(f"[ERROR] Failed to load or parse SVG file '{input_file}': {e}", file=sys.stderr)
        sys.exit(1)
    t1_load = time.perf_counter()

    vw, vh = loader.viewbox[2], loader.viewbox[3]

    # 2. Create Grid Plan
    grid_plan = create_grid_plan(loader.viewbox, vw, vh, num_levels=levels)

    # 3. Execute Engine
    t0_calc = time.perf_counter()
    results = analyze_grid_cpu_area(geoms, grid_plan, return_cell_indices=False)
    t1_calc = time.perf_counter()
    calc_time_ms = (t1_calc - t0_calc) * 1000.0

    # 4. Compute Fractal Dimension
    fractal_res = compute_fractal_dimension(results)

    # 5. Output Box-Counting Terminal Report Table (Main Project Design)
    motif_name = input_path.stem
    print("+------------------------------------------------------------------------------+")
    print("|               RASH-HIT FRACTAL ANALIZ STUDIO - ANALYSIS REPORT               |")
    print("+------------------------------------------------------------------------------+")
    print(f"  Motif Loaded       : {motif_name} ({vw:.2f} x {vh:.2f})")
    print(f"  Geometries         : {len(geoms):,} vector elements")
    print("  Analysis Engine    : cpu")
    print("  Selected Engine    : CPU Exact Vector Geometry Engine (Shapely/GEOS)")
    print("+------------------------------------------------------------------------------+")
    print("| Level | Grid     | Total Cells | Filled Cells | Empty Cells | Occupancy % | Time ms  |")
    print("+-------+----------+-------------+--------------+-------------+-------------+----------+")

    for r in results:
        grid_label = f"{r.level.cols}x{r.level.rows}"
        print(
            f"|  L{r.level.level_idx:02d}  | {grid_label:<8} | {r.level.total_cells:>11,} | "
            f"{r.filled_count:>12,} | {r.empty_count:>11,} | {r.fill_ratio*100:>10.2f}% | "
            f"{r.execution_time_ms:>8.2f} |"
        )

    print("+-------+----------+-------------+--------------+-------------+-------------+----------+")
    print(f"  [RESULT] Box-Counting Fractal Dimension Db = {fractal_res.fractal_dimension_db:.4f}")
    print(f"  [RESULT] Linear Regression Fit R2           = {fractal_res.r2_score:.4f}")
    print(f"  [RESULT] Total Execution Time               = {calc_time_ms:.2f} ms")
    print("+------------------------------------------------------------------------------+")


def main():
    parser = argparse.ArgumentParser(description="RASH-HIT Fractal Analiz Studio - Vector Geometry Box-Counting Engine")
    _input_group = parser.add_mutually_exclusive_group(required=False)
    _input_group.add_argument("-i", "--input", type=str, help="Input SVG file path")
    _input_group.add_argument("-d", "--dir", type=str, help="Directory path for batch processing all SVG files")
    parser.add_argument("-l", "--levels", type=int, default=7, help="Number of grid levels (default: 7)")
    parser.add_argument("-v", "--version", action="version", version="RASH-HIT Fractal Analiz Studio v1.0.1")

    args = parser.parse_args()

    target_input = args.input or args.dir
    if not target_input:
        parser.print_help()
        return

    if args.levels < 1:
        print(f"Error: Invalid --levels '{args.levels}'. Number of grid levels must be >= 1.", file=sys.stderr)
        sys.exit(1)

    target_path = Path(target_input)
    if target_path.is_file():
        process_single_file(str(target_path), levels=args.levels)
    elif target_path.is_dir():
        svg_files = sorted(list(target_path.glob("*.svg")))
        if not svg_files:
            print(f"[!] No SVG files found in directory: {target_path}", file=sys.stderr)
            sys.exit(1)

        print("+------------------------------------------------------------------------------+")
        print(f"| BATCH PROCESSING MODE: {len(svg_files):<3} SVG Files Found                                   |")
        print("+------------------------------------------------------------------------------+")
        for svg_file in svg_files:
            process_single_file(str(svg_file), levels=args.levels)
            print()
    else:
        print(f"[ERROR] Path not found: {target_input}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
