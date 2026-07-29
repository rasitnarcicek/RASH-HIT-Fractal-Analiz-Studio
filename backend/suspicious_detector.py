# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

"""
suspicious_detector.py — Boundary-Touch Cell Verification Detector.
Provides spatial index utilities for verifying boundary cell occupancy using Shapely/GEOS.
"""

from __future__ import annotations
from typing import List, Set, Tuple, Dict, Any
from shapely.geometry import box
from shapely.strtree import STRtree

from backend.geometry_engine import ParsedGeometry
from backend.grid_planner import GridPlan, GridLevel


def verify_boundary_cells(
    parsed_geometries: List[ParsedGeometry],
    level: GridLevel,
    grid_plan: GridPlan,
    candidate_cell_ids: Set[int]
) -> Set[int]:
    """Verifies cell intersection with geometry using Shapely STRtree index."""
    cols = level.cols
    cell_w = level.cell_w
    cell_h = level.cell_h
    verified_filled = set()

    valid_geoms = [g for g in parsed_geometries if g.shapely_obj is not None and not g.shapely_obj.is_empty]
    if not valid_geoms or not candidate_cell_ids:
        return verified_filled

    shapely_objs = [g.shapely_obj for g in valid_geoms]
    tree = STRtree(shapely_objs)

    for cell_id in candidate_cell_ids:
        r = cell_id // cols
        c = cell_id % cols
        xmin = grid_plan.xmin + c * cell_w
        ymin = grid_plan.ymin + r * cell_h
        cell_box = box(xmin, ymin, xmin + cell_w, ymin + cell_h)
        cand_indices = tree.query(cell_box)

        if len(cand_indices) > 0:
            for idx in cand_indices:
                geom = valid_geoms[idx]
                s_obj = geom.shapely_obj
                if geom.geom_type == 'fill':
                    if s_obj.intersects(cell_box):
                        verified_filled.add(cell_id)
                        break
                elif geom.geom_type == 'stroke':
                    w = geom.stroke_width
                    if w <= 0.0:
                        if s_obj.intersects(cell_box):
                            verified_filled.add(cell_id)
                            break
                    else:
                        if s_obj.distance(cell_box) <= w / 2.0:
                            verified_filled.add(cell_id)
                            break

    return verified_filled
