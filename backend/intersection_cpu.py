# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

"""
intersection_cpu.py — CPU Exact Vector Geometry Box-Counting Engine.
Uses Shapely 2.0 C++ vectorized STRtree spatial indexing to bulk-query grid cell boxes
against exact polygon fills and buffered stroke lines.
"""

from __future__ import annotations
import time
import math
from typing import List, Tuple, Dict, Any, Set, Optional
import numpy as np
import shapely
from shapely.geometry import box
from shapely.strtree import STRtree

from backend.geometry_engine import ParsedGeometry
from backend.grid_planner import GridPlan, GridLevel


class CellDebugInfo:
    """Stores detailed debug information for a filled grid cell."""
    def __init__(
        self,
        level_idx: int,
        col: int,
        row: int,
        reason: str,
        geometry_id: int,
        geometry_type: str,
        fill_or_stroke: str,
        stroke_width: float,
        cell_bounds: Tuple[float, float, float, float]
    ):
        self.level_idx = level_idx
        self.col = col
        self.row = row
        self.reason = reason
        self.geometry_id = geometry_id
        self.geometry_type = geometry_type
        self.fill_or_stroke = fill_or_stroke
        self.stroke_width = stroke_width
        self.cell_bounds = cell_bounds

    def to_dict(self) -> Dict[str, Any]:
        return {
            'level': int(self.level_idx),
            'col': int(self.col),
            'row': int(self.row),
            'reason': str(self.reason),
            'geometry_id': int(self.geometry_id),
            'geometry_type': str(self.geometry_type),
            'fill_or_stroke': str(self.fill_or_stroke),
            'stroke_width': float(round(self.stroke_width, 4)),
            'cell_bounds': [float(round(b, 4)) for b in self.cell_bounds]
        }


class CPULevelResult:
    """Stores box-counting result for a single grid level."""
    def __init__(
        self,
        level: GridLevel,
        filled_count: int,
        empty_count: int,
        execution_time_ms: float,
        filled_cells_indices: List[Tuple[int, int]] = None,
        debug_cells: List[CellDebugInfo] = None
    ):
        self.level = level
        self.filled_count = filled_count
        self.empty_count = empty_count
        self.total_cells = level.total_cells
        self.fill_ratio = (filled_count / level.total_cells) if level.total_cells > 0 else 0.0
        self.execution_time_ms = execution_time_ms
        self.filled_cells_indices = filled_cells_indices or []
        self.debug_cells = debug_cells or []

    def to_dict(self) -> Dict[str, Any]:
        d = self.level.to_dict()
        d.update({
            'filled_cells': self.filled_count,
            'empty_cells': self.empty_count,
            'fill_ratio': round(self.fill_ratio, 4),
            'execution_time_ms': round(self.execution_time_ms, 2),
            'mode': 'CPU'
        })
        return d


def analyze_grid_cpu(
    parsed_geometries: List[ParsedGeometry],
    grid_plan: GridPlan,
    return_cell_indices: bool = False,
    collect_debug_info: bool = False
) -> List[CPULevelResult]:
    """
    Executes CPU exact GEOS vector box-counting for all levels in grid_plan.
    Uses Shapely 2.0 C++ bulk STRtree spatial indexing to query all cell boxes in parallel.
    """
    results: List[CPULevelResult] = []

    valid_geoms: List[ParsedGeometry] = [
        g for g in parsed_geometries if g.shapely_obj and not g.shapely_obj.is_empty
    ]
    if not valid_geoms:
        for lvl in grid_plan.levels:
            results.append(CPULevelResult(lvl, 0, lvl.total_cells, 0.0))
        return results

    # Separate polygon fills and buffered stroke lines
    eval_objs = []
    for g in valid_geoms:
        if g.geom_type == 'fill':
            eval_objs.append(g.shapely_obj)
        elif g.geom_type == 'stroke':
            w = g.stroke_width
            if w > 0.0:
                eval_objs.append(g.shapely_obj.buffer(w / 2.0))
            else:
                eval_objs.append(g.shapely_obj)

    tree = STRtree(eval_objs)

    for lvl in grid_plan.levels:
        print(f"  [+] Computing Level {lvl.level_idx:02d} ({lvl.cols}x{lvl.rows} = {lvl.total_cells:,} cells)...", flush=True)
        t0 = time.perf_counter()

        cols, rows = lvl.cols, lvl.rows
        cell_w, cell_h = lvl.cell_w, lvl.cell_h

        # Build 1D/2D vectorized grid cell boxes in C++
        c_idx, r_idx = np.meshgrid(np.arange(cols), np.arange(rows))
        r_flat = r_idx.ravel()
        c_flat = c_idx.ravel()

        x0 = grid_plan.xmin + c_flat * cell_w
        y0 = grid_plan.ymin + r_flat * cell_h
        x1 = x0 + cell_w
        y1 = y0 + cell_h

        cell_boxes = shapely.box(x0, y0, x1, y1)

        # C++ STRtree Bulk Query
        matches = tree.query(cell_boxes, predicate='intersects')
        matched_cell_flat_indices = np.unique(matches[0]) if len(matches[0]) > 0 else np.array([], dtype=int)

        filled_count = len(matched_cell_flat_indices)
        empty_count = lvl.total_cells - filled_count

        filled_indices: List[Tuple[int, int]] = []
        if return_cell_indices and filled_count > 0:
            for idx in matched_cell_flat_indices:
                c = int(c_flat[idx])
                r = int(r_flat[idx])
                filled_indices.append((c, r))

        t1 = time.perf_counter()
        total_time_ms = (t1 - t0) * 1000.0

        res = CPULevelResult(
            level=lvl,
            filled_count=filled_count,
            empty_count=empty_count,
            execution_time_ms=total_time_ms,
            filled_cells_indices=filled_indices if return_cell_indices else None,
            debug_cells=[]
        )
        results.append(res)
        print(f"      ✔ Level {lvl.level_idx:02d} Completed! Filled: {filled_count:,} / {lvl.total_cells:,} ({res.fill_ratio*100.0:.2f}%) in {total_time_ms:.2f} ms", flush=True)

    return results
