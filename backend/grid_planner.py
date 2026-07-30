# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

"""
grid_planner.py — Aspect-Ratio Aware Automatic Grid Generator.
Calculates the exact analysis bounding box, aspect ratio AR = W/H,
and generates optimal multi-level grid series where cells are as square as possible (W_cell ≈ H_cell).
"""

from __future__ import annotations
import math
from typing import List, Tuple, Dict, Any, Optional


class GridLevel:
    """Represents a single grid resolution level in box-counting analysis."""
    def __init__(self, level_idx: int, cols: int, rows: int, analysis_w: float, analysis_h: float):
        self.level_idx = level_idx
        self.cols = cols
        self.rows = rows
        self.total_cells = cols * rows
        self.cell_w = analysis_w / cols
        self.cell_h = analysis_h / rows
        self.cell_aspect_ratio = self.cell_w / self.cell_h if self.cell_h > 0 else 1.0

        # Scale parameter epsilon = max(cell_w, cell_h) / max(analysis_w, analysis_h)
        max_dim = max(analysis_w, analysis_h)
        self.scale_epsilon = max(self.cell_w, self.cell_h) / max_dim if max_dim > 0 else 1.0
        self.log_inv_epsilon = math.log(1.0 / self.scale_epsilon) if self.scale_epsilon > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'level': self.level_idx,
            'cols': self.cols,
            'rows': self.rows,
            'total_cells': self.total_cells,
            'cell_w': round(self.cell_w, 4),
            'cell_h': round(self.cell_h, 4),
            'cell_aspect_ratio': round(self.cell_aspect_ratio, 4),
            'scale_epsilon': round(self.scale_epsilon, 6),
            'log_inv_epsilon': round(self.log_inv_epsilon, 6),
        }


class GridPlan:
    """Holds analysis bounding box and the list of generated grid levels."""
    def __init__(self, bounds: Tuple[float, float, float, float], levels: List[GridLevel]):
        self.xmin, self.ymin, self.xmax, self.ymax = bounds
        self.width = max(1e-6, self.xmax - self.xmin)
        self.height = max(1e-6, self.ymax - self.ymin)
        self.aspect_ratio = self.width / self.height
        self.levels = levels


def create_grid_plan(
    svg_viewbox: Optional[Tuple[float, float, float, float]],
    svg_width: float,
    svg_height: float,
    geometry_bounds: Optional[Tuple[float, float, float, float]] = None,
    num_levels: int = 7,
    base_cells: int = 4,
    manual_grids: Optional[List[Tuple[int, int]]] = None
) -> GridPlan:
    """
    Determines analysis bounding box and generates optimal grid levels.
    Priority order for analysis area:
      1. viewBox (if valid)
      2. width / height (if valid)
      3. Geometry bounds (fallback)
    """
    # 1. Determine Analysis Bounds
    if svg_viewbox and svg_viewbox[2] > 0 and svg_viewbox[3] > 0:
        bounds = (svg_viewbox[0], svg_viewbox[1], svg_viewbox[0] + svg_viewbox[2], svg_viewbox[1] + svg_viewbox[3])
    elif svg_width > 0 and svg_height > 0:
        bounds = (0.0, 0.0, svg_width, svg_height)
    elif geometry_bounds and (geometry_bounds[2] > geometry_bounds[0]) and (geometry_bounds[3] > geometry_bounds[1]):
        bounds = geometry_bounds
    else:
        # Emergency default box
        bounds = (0.0, 0.0, 100.0, 100.0)

    analysis_w = bounds[2] - bounds[0]
    analysis_h = bounds[3] - bounds[1]
    ar = analysis_w / analysis_h

    levels: List[GridLevel] = []

    if manual_grids:
        for idx, (c, r) in enumerate(manual_grids, start=1):
            levels.append(GridLevel(idx, max(1, c), max(1, r), analysis_w, analysis_h))
    else:
        # Automatic Square-like Grid Planner
        # Determine base resolution once at Level 0 to guarantee strict 2x quadtree doubling
        if ar >= 1.0:
            base_rows = base_cells
            base_cols = max(1, int(round(base_rows * ar)))
        else:
            base_cols = base_cells
            base_rows = max(1, int(round(base_cols / ar)))

        for i in range(num_levels):
            multiplier = 2 ** i
            cols = base_cols * multiplier
            rows = base_rows * multiplier
            levels.append(GridLevel(i + 1, cols, rows, analysis_w, analysis_h))

    return GridPlan(bounds, levels)
