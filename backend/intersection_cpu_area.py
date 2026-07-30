# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

"""
intersection_cpu_area.py — CPU Exact Vector Geometry Occupancy Engine

This module uses the CPU exact vector geometry pipeline for area-mode SVG box-counting.
It avoids AABB-only final decisions and counts cells based on actual fill/stroke geometry contact.
"""

from __future__ import annotations
from typing import List

from backend.geometry_engine import ParsedGeometry
from backend.grid_planner import GridPlan
from backend.intersection_cpu import CPULevelResult
from backend.intersection_hierarchical import analyze_grid_hierarchical

def analyze_grid_cpu_area(
    parsed_geometries: List[ParsedGeometry],
    grid_plan: GridPlan,
    return_cell_indices: bool = False,
    collect_debug_info: bool = False
) -> List[CPULevelResult]:
    """
    CPU Exact Vector Geometry Engine.
    Evaluates exact cell occupancy using Shapely/GEOS vector intersection predicates.
    """
    hier_results, _ = analyze_grid_hierarchical(
        parsed_geometries=parsed_geometries,
        grid_plan=grid_plan,
        return_cell_indices=return_cell_indices,
        collect_debug_info=collect_debug_info
    )

    results: List[CPULevelResult] = []
    for hr in hier_results:
        inner_res = getattr(hr, 'level_result', hr)
        f_indices = getattr(inner_res, 'filled_cells_indices', None)
        
        res = CPULevelResult(
            level=hr.level,
            filled_count=hr.filled_count,
            empty_count=hr.empty_count,
            execution_time_ms=hr.execution_time_ms,
            filled_cells_indices=f_indices
        )
        results.append(res)

    return results
