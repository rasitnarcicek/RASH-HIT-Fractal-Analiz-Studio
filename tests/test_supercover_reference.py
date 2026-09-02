# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Tests for the pure NumPy supercover segment reference.

Every expected set below was derived BY HAND from the supercover definition
(cell box CLOSED and INTERSECTING the segment, touch_counts policy), so the
engine is validated against ground truth, not against itself.  Ported
verbatim from the RASH-HIT v1.0 engine test suite.
"""
import unittest
from pathlib import Path

import numpy as np

from src.backend.supercover_reference import (
    SupercoverGrid, build_supercover_grid, supercover_cells,
    supercover_cells_for_polyline, to_fixed_point,
)

# L1 grid over viewBox (0,0,4,4): 4x4 cells, cw=ch=1, origin (0,0).
GRID = build_supercover_grid((0.0, 0.0, 4.0, 4.0), level=1, fixed_point_scale=1000)


def _cells(seg, grid=GRID):
    return supercover_cells(to_fixed_point([seg], grid), grid)


def _set(cells) -> set:
    return {tuple(r) for r in cells.tolist()}


class TestGridDefinition(unittest.TestCase):

    def test_grid_definition_matches_engine_rule(self):
        self.assertEqual((GRID.cols, GRID.rows), (4, 4))
        self.assertEqual(GRID.cell_w, 1000)
        self.assertEqual(GRID.cell_h, 1000)
        self.assertEqual((GRID.origin_x, GRID.origin_y), (0, 0))
        # L2 -> 8x8, L10 -> 2048x2048 (same rule the area engine uses)
        g2 = build_supercover_grid((0.0, 0.0, 100.0, 100.0), 2)
        g10 = build_supercover_grid((0.0, 0.0, 100.0, 100.0), 10)
        self.assertEqual((g2.cols, g2.rows), (8, 8))
        self.assertEqual((g10.cols, g10.rows), (2048, 2048))


class TestSupercoverSets(unittest.TestCase):

    def test_horizontal_line_one_row(self):
        self.assertEqual(_set(_cells((0.5, 0.5, 3.5, 0.5))), {(0, 0), (0, 1), (0, 2), (0, 3)})

    def test_vertical_line_one_column(self):
        self.assertEqual(_set(_cells((0.5, 0.5, 0.5, 3.5))), {(0, 0), (1, 0), (2, 0), (3, 0)})

    def test_diagonal_crosses_four_cells(self):
        # Passes through grid corners (1,1), (2,2) and (3,3): each corner's four
        # closed boxes count (corner touch), so the set is the 10-cell supercover.
        self.assertEqual(_set(_cells((0.5, 0.5, 3.5, 3.5))), {
            (0, 0), (1, 0), (0, 1), (1, 1), (2, 1),
            (1, 2), (2, 2), (3, 2), (2, 3), (3, 3)})

    def test_boundary_aligned_vertical_counts_both_columns(self):
        # x = 1.0 lies exactly ON the shared edge of columns 0 and 1: supercover
        # counts BOTH columns for every row the segment covers (touch_counts).
        self.assertEqual(_set(_cells((1.0, 0.5, 1.0, 3.5))), {
            (0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1)})

    def test_boundary_aligned_horizontal_counts_both_rows(self):
        # y = 2.0 is the shared edge of rows 1 and 2: supercover counts BOTH rows
        # for every column the segment covers (touch_counts).
        self.assertEqual(_set(_cells((0.5, 2.0, 3.5, 2.0))), {
            (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)})

    def test_corner_touch_counts_four_neighbours(self):
        # Segment passes exactly through grid corner (1,1): all four closed boxes
        # touching that corner count (supercover).
        self.assertEqual(_set(_cells((0.5, 0.5, 2.5, 2.5))), {
            (0, 0), (1, 0), (0, 1), (1, 1), (2, 1), (1, 2), (2, 2)})

    def test_endpoint_on_boundary_includes_neighbour(self):
        # Start endpoint (1.0, 0.5) lies exactly on the shared edge of columns 0
        # and 1: both columns at that row count, so the run covers 4 columns.
        self.assertEqual(_set(_cells((1.0, 0.5, 3.5, 0.5))), {
            (0, 0), (0, 1), (0, 2), (0, 3)})

    def test_zero_length_segment_single_containing_cell(self):
        self.assertEqual(_set(_cells((1.5, 1.5, 1.5, 1.5))), {(1, 1)})

    def test_segment_fully_outside_is_empty(self):
        self.assertEqual(_set(_cells((10.0, 10.0, 12.0, 12.0))), set())

    def test_partially_clipped_segment_only_in_area_cells(self):
        # Endpoint (2.0, 0.5) lies exactly on the boundary of column 2: the closed
        # box of column 2 touches it, so it counts too (touch_counts).
        self.assertEqual(_set(_cells((-1.0, 0.5, 2.0, 0.5))), {(0, 0), (0, 1), (0, 2)})

    def test_negative_coordinates_offset_ok(self):
        # viewBox at negative origin; FIXED_ORIGIN anchors at viewBox min.
        g = build_supercover_grid((-4.0, -4.0, 4.0, 4.0), 1, fixed_point_scale=1000)
        cells = supercover_cells(to_fixed_point([(-3.5, -3.5, -0.5, -3.5)], g), g)
        self.assertEqual(_set(cells), {(0, 0), (0, 1), (0, 2), (0, 3)})

    def test_polyline_dedups_and_sorts(self):
        pts = [(0.5, 0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5), (0.5, 0.5)]
        cells = supercover_cells_for_polyline(pts, GRID)
        tuples = [tuple(r) for r in cells.tolist()]
        self.assertEqual(tuples, sorted(set(tuples)))  # dedup + lexicographic (row, col)
        self.assertIn((0, 1), tuples)
        self.assertIn((1, 1), tuples)
        self.assertIn((1, 0), tuples)

    def test_output_dtype_and_order(self):
        cells = _cells((0.5, 0.5, 3.5, 0.5))
        self.assertEqual(cells.dtype, np.int64)
        self.assertEqual(cells.shape[1], 2)
        self.assertEqual(cells.tolist(), sorted(cells.tolist()))

    def test_fixed_point_rounding_exactness(self):
        # round((x - 0) * 1000) must land on exact lattice integers.
        fp = to_fixed_point([(0.5, 0.5, 3.5, 0.5)], GRID)
        self.assertEqual(fp.tolist(), [[500, 500, 3500, 500]])

    def test_scale_variation_keeps_set_identical(self):
        """A higher fixed-point scale must not change the cell SET (only precision)."""
        g_hi = build_supercover_grid((0.0, 0.0, 4.0, 4.0), 1, fixed_point_scale=10_000)
        lo = _set(_cells((0.55, 0.5, 3.45, 0.5)))
        hi = _set(supercover_cells(to_fixed_point([(0.55, 0.5, 3.45, 0.5)], g_hi), g_hi))
        self.assertEqual(lo, hi)


if __name__ == '__main__':
    unittest.main()
