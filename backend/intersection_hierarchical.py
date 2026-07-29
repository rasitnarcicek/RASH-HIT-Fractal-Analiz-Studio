# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
#
# intersection_hierarchical.py -- Hierarchical Quadtree Area Engine (Vectorized v2)
#
# Key optimizations vs v1 (per-cell Python loop):
#   1. shapely.box(x0_arr,y0_arr,x1_arr,y1_arr) builds all cells in one C++ call.
#   2. STRtree.query(cell_array) -> (2,K) ndarray [geom_idxs; cell_idxs] in bulk C++.
#   3. shapely.intersects() / shapely.distance() ufuncs -- no Python iteration.
#   4. Active parent set is a NumPy (M,2) int32 array; child expansion is pure NumPy.
#
# Pruning rule (safe EMPTY-only):
#   EMPTY parent  -> children skipped (safe: if parent misses geometry, children do too).
#   PARTIAL/NON-EMPTY -> subdivided into 4 children, each re-evaluated exactly.
#   FULL shortcut NOT used (caused overcounting vs CPU baseline for dense SVGs).
#
# Expected to match CPU GEOS exact baseline; equivalence must be verified by benchmark.

from __future__ import annotations
import time
from typing import List, Tuple, Optional

import numpy as np
import shapely
from shapely.strtree import STRtree

from backend.geometry_engine import ParsedGeometry
from backend.grid_planner import GridPlan, GridLevel
from backend.intersection_cpu import CPULevelResult, CellDebugInfo


class HierarchicalLevelResult:
    def __init__(self, level_result, empty_parents_skipped, full_parents_counted,
                 partial_parents_subdivided, exact_geos_tests, pruning_time_ms):
        self.level_result               = level_result
        self.empty_parents_skipped      = empty_parents_skipped
        self.full_parents_counted       = full_parents_counted
        self.partial_parents_subdivided = partial_parents_subdivided
        self.exact_geos_tests           = exact_geos_tests
        self.pruning_time_ms            = pruning_time_ms

    # Proxy attributes -- callers can treat this like a CPULevelResult
    @property
    def level(self):             return self.level_result.level
    @property
    def filled_count(self):      return self.level_result.filled_count
    @property
    def empty_count(self):       return self.level_result.empty_count
    @property
    def fill_ratio(self):        return self.level_result.fill_ratio
    @property
    def total_cells(self):       return self.level_result.total_cells
    @property
    def execution_time_ms(self): return self.level_result.execution_time_ms


def _bulk_fill_decision(x0, y0, x1, y1,
                        fill_tree, fill_objs,
                        stroke_tree, stroke_objs, stroke_widths):
    """
    Returns bool ndarray (N,): True = cell is filled.

    STRtree.query(geometry_array) in Shapely 2.1.2 returns shape (2, K):
        row 0 = indices into the QUERY geometry array  (cell side)
        row 1 = indices into the TREE geometries       (geom side)
    Confirmed empirically: r[0].max() <= n_cells, r[1].max() <= n_tree_geoms.
    """
    n      = len(x0)
    filled = np.zeros(n, dtype=bool)

    cell_boxes = shapely.box(x0, y0, x1, y1)  # single C++ call

    # --- Fill geometries -------------------------------------------------
    if fill_tree is not None and n > 0:
        pairs = fill_tree.query(cell_boxes)    # (2, K) or (0,) if no hits
        if pairs.ndim == 2 and pairs.shape[1] > 0:
            cell_idxs = pairs[0]   # r[0] = cell indices
            geom_idxs = pairs[1]   # r[1] = geom indices
            g_arr = np.array([fill_objs[i] for i in geom_idxs], dtype=object)
            c_arr = cell_boxes[cell_idxs]
            hits  = shapely.intersects(g_arr, c_arr)
            filled[cell_idxs[hits]] = True

    # --- Stroke geometries -----------------------------------------------
    if stroke_tree is not None and n > 0:
        pairs = stroke_tree.query(cell_boxes)  # (2, K)
        if pairs.ndim == 2 and pairs.shape[1] > 0:
            cell_idxs = pairs[0]   # r[0] = cell indices
            geom_idxs = pairs[1]   # r[1] = geom indices
            unfilled  = ~filled[cell_idxs]
            if unfilled.any():
                gi     = geom_idxs[unfilled]
                ci     = cell_idxs[unfilled]
                g_arr  = np.array([stroke_objs[i] for i in gi], dtype=object)
                c_arr  = cell_boxes[ci]
                hw     = stroke_widths[gi] / 2.0
                zw     = hw <= 0.0
                if zw.any():
                    hits_z = shapely.intersects(g_arr[zw], c_arr[zw])
                    filled[ci[zw][hits_z]] = True
                if (~zw).any():
                    dists  = shapely.distance(g_arr[~zw], c_arr[~zw])
                    hits_d = dists <= hw[~zw]
                    filled[ci[~zw][hits_d]] = True

    return filled


def analyze_grid_hierarchical(parsed_geometries, grid_plan,
                               return_cell_indices=False,
                               collect_debug_info=False):
    """Vectorized hierarchical quadtree area engine.

    Returns (cpu_results_list, hierarchical_detail_list).
    cpu_results_list[i] is a CPULevelResult -- same interface as CPU engine.
    """
    results, details = [], []

    valid_geoms = [g for g in parsed_geometries
                   if g.shapely_obj and not g.shapely_obj.is_empty]
    if not valid_geoms:
        for lvl in grid_plan.levels:
            r = CPULevelResult(lvl, 0, lvl.total_cells, 0.0)
            results.append(r)
            details.append(HierarchicalLevelResult(r, 0, 0, 0, 0, 0.0))
        return results, details

    fill_geoms    = [g for g in valid_geoms if g.geom_type == 'fill']
    stroke_geoms  = [g for g in valid_geoms if g.geom_type == 'stroke']
    fill_objs     = [g.shapely_obj for g in fill_geoms]
    stroke_objs   = [g.shapely_obj for g in stroke_geoms]
    stroke_widths = np.array([g.stroke_width for g in stroke_geoms], dtype=np.float64)

    fill_tree   = STRtree(fill_objs)   if fill_objs   else None
    stroke_tree = STRtree(stroke_objs) if stroke_objs else None

    xmin, ymin     = grid_plan.xmin, grid_plan.ymin
    active_parents = None   # (M,2) int32; None means full grid at L1

    for lvl_idx, lvl in enumerate(grid_plan.levels):
        t0             = time.perf_counter()
        cols, rows     = lvl.cols, lvl.rows
        cell_w, cell_h = lvl.cell_w, lvl.cell_h

        # --- Generate candidate (row, col) pairs -------------------------
        if lvl_idx == 0 or active_parents is None or len(active_parents) == 0:
            rr, cc    = np.meshgrid(np.arange(rows, dtype=np.int32),
                                    np.arange(cols, dtype=np.int32), indexing='ij')
            cand_rows = rr.ravel()
            cand_cols = cc.ravel()
        else:
            pr = active_parents[:, 0]
            pc = active_parents[:, 1]
            cand_rows = np.stack([pr*2,   pr*2,     pr*2+1, pr*2+1], axis=1).ravel()
            cand_cols = np.stack([pc*2,   pc*2+1,   pc*2,   pc*2+1], axis=1).ravel()

        x0_a = xmin + cand_cols.astype(np.float64) * cell_w
        y0_a = ymin + cand_rows.astype(np.float64) * cell_h
        x1_a = x0_a + cell_w
        y1_a = y0_a + cell_h
        nc   = len(cand_rows)

        filled_mask = (_bulk_fill_decision(x0_a, y0_a, x1_a, y1_a,
                                           fill_tree, fill_objs,
                                           stroke_tree, stroke_objs, stroke_widths)
                       if nc > 0 else np.zeros(0, dtype=bool))

        filled_count  = int(filled_mask.sum())
        empty_skipped = int((~filled_mask).sum())
        partial_sub   = (len(active_parents)
                         if (lvl_idx > 0 and active_parents is not None) else 0)

        filled_indices = []
        if return_cell_indices and filled_mask.any():
            filled_indices = list(zip(cand_rows[filled_mask].tolist(),
                                      cand_cols[filled_mask].tolist()))

        t1            = time.perf_counter()
        ms            = (t1 - t0) * 1000.0
        empty_count   = lvl.total_cells - filled_count

        res = CPULevelResult(
            level=lvl, filled_count=filled_count, empty_count=empty_count,
            execution_time_ms=ms,
            filled_cells_indices=filled_indices if return_cell_indices else None,
            debug_cells=None)
        results.append(res)
        details.append(HierarchicalLevelResult(res, empty_skipped, 0, partial_sub, nc, ms))

        active_parents = (np.stack([cand_rows[filled_mask], cand_cols[filled_mask]], axis=1)
                          .astype(np.int32)
                          if filled_mask.any()
                          else np.empty((0, 2), dtype=np.int32))

        print(f'  [+] Computing Level {lvl.level_idx:02d} '
              f'({lvl.cols}x{lvl.rows} = {lvl.total_cells:,} cells)...', flush=True)
        print(f'      [OK] Level {lvl.level_idx:02d} Completed! '
              f'Filled: {filled_count:,} / {lvl.total_cells:,} '
              f'({res.fill_ratio*100.0:.2f}%) in {ms:.2f} ms', flush=True)

    return results, details
