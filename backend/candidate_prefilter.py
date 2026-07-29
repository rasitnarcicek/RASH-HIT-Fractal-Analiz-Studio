# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

"""
candidate_prefilter.py — Accelerated Candidate Cell Generator.
Generates candidate grid cells using fast AABB and segment bounding box mapping.
Designed to avoid false negatives; must be validated against CPU GEOS baseline.
Candidate prefilter is NEVER used to produce final area results directly.
"""

from __future__ import annotations
import math
import time
from typing import List, Tuple, Set, Dict, Any, Optional

from backend.geometry_engine import ParsedGeometry
from backend.grid_planner import GridPlan, GridLevel

# Cohen-Sutherland outcode constants for candidate filtering
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8


def _compute_outcode(x: float, y: float, xmin: float, ymin: float, xmax: float, ymax: float) -> int:
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP
    return code


def line_intersects_box_cs(x1: float, y1: float, x2: float, y2: float, xmin: float, ymin: float, xmax: float, ymax: float) -> bool:
    """Fast Cohen-Sutherland line clipping for candidate prefiltering."""
    c1 = _compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
    c2 = _compute_outcode(x2, y2, xmin, ymin, xmax, ymax)
    while True:
        if (c1 | c2) == 0:
            return True
        if (c1 & c2) != 0:
            return False
        c_out = c1 if c1 != 0 else c2
        if c_out & TOP:
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1) if y2 != y1 else x1
            y = ymax
        elif c_out & BOTTOM:
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1) if y2 != y1 else x1
            y = ymin
        elif c_out & RIGHT:
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1) if x2 != x1 else y1
            x = xmax
        elif c_out & LEFT:
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1) if x2 != x1 else y1
            x = xmin

        if c_out == c1:
            x1, y1 = x, y
            c1 = _compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
        else:
            x2, y2 = x, y
            c2 = _compute_outcode(x2, y2, xmin, ymin, xmax, ymax)


def generate_candidate_cells_for_geometries(
    geometries: List[ParsedGeometry],
    level: GridLevel,
    grid_plan: GridPlan
) -> Tuple[Set[Tuple[int, int]], Dict[str, Any]]:
    """
    Generates candidate grid cells (row, col) for a given level using AABB and segment range mapping.
    Designed to avoid false negatives; must be validated against CPU GEOS baseline.
    Never produces final area decisions directly.
    """
    t0 = time.perf_counter()
    candidate_cells: Set[Tuple[int, int]] = set()

    xmin, ymin = grid_plan.xmin, grid_plan.ymin
    cols, rows = level.cols, level.rows
    cell_w, cell_h = level.cell_w, level.cell_h

    for g in geometries:
        if not g.shapely_obj or g.shapely_obj.is_empty:
            continue

        b_xmin, b_ymin, b_xmax, b_ymax = g.shapely_obj.bounds

        c1 = max(0, min(cols - 1, int(math.floor((b_xmin - xmin) / cell_w))))
        c2 = max(0, min(cols - 1, int(math.floor((b_xmax - xmin) / cell_w))))
        r1 = max(0, min(rows - 1, int(math.floor((b_ymin - ymin) / cell_h))))
        r2 = max(0, min(rows - 1, int(math.floor((b_ymax - ymin) / cell_h))))

        if g.geom_type == 'fill':
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    candidate_cells.add((r, c))
        else:
            for r in range(r1, r2 + 1):
                cell_ymin = ymin + r * cell_h
                cell_ymax = cell_ymin + cell_h
                for c in range(c1, c2 + 1):
                    if (r, c) in candidate_cells:
                        continue
                    cell_xmin = xmin + c * cell_w
                    cell_xmax = cell_xmin + cell_w
                    if not (b_xmax < cell_xmin or b_xmin > cell_xmax or b_ymax < cell_ymin or b_ymin > cell_ymax):
                        candidate_cells.add((r, c))

    t1 = time.perf_counter()
    broad_phase_ms = (t1 - t0) * 1000.0

    stats = {
        "candidate_count": len(candidate_cells),
        "total_cells": level.total_cells,
        "broad_phase_ms": broad_phase_ms,
        "skipped_cells": level.total_cells - len(candidate_cells)
    }

    return candidate_cells, stats
