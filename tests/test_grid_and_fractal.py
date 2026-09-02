# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

"""Unit tests for grid planning and fractal regression."""

import math
import unittest

from src.backend.fractal_analyzer import compute_fractal_dimension
from src.backend.grid_planner import GridLevel, GridPlan, create_grid_plan
from src.backend.intersection_cpu import CPULevelResult


class TestGridLevel(unittest.TestCase):

    def test_cell_metrics(self):
        lvl = GridLevel(1, 4, 2, 100.0, 50.0)
        self.assertEqual(lvl.total_cells, 8)
        self.assertEqual((lvl.cell_w, lvl.cell_h), (25.0, 25.0))
        self.assertEqual(lvl.cell_aspect_ratio, 1.0)
        self.assertAlmostEqual(lvl.scale_epsilon, 0.25)
        self.assertAlmostEqual(lvl.log_inv_epsilon, math.log(4.0))

    def test_degenerate_dimensions_fall_back_to_defaults(self):
        lvl = GridLevel(1, 1, 1, 0.0, 0.0)
        self.assertEqual(lvl.cell_aspect_ratio, 1.0)
        self.assertEqual(lvl.scale_epsilon, 1.0)
        self.assertEqual(lvl.log_inv_epsilon, 0.0)

    def test_to_dict_rounds_values(self):
        d = GridLevel(3, 3, 3, 10.0, 10.0).to_dict()
        self.assertEqual(d['level'], 3)
        self.assertEqual(d['total_cells'], 9)
        self.assertAlmostEqual(d['cell_w'], 3.3333)


class TestCreateGridPlan(unittest.TestCase):

    def test_viewbox_takes_priority(self):
        plan = create_grid_plan((10.0, 20.0, 200.0, 100.0), 999.0, 999.0, num_levels=1)
        self.assertEqual((plan.xmin, plan.ymin, plan.xmax, plan.ymax), (10.0, 20.0, 210.0, 120.0))
        self.assertAlmostEqual(plan.aspect_ratio, 2.0)

    def test_width_height_used_when_viewbox_missing(self):
        plan = create_grid_plan(None, 80.0, 40.0, num_levels=1)
        self.assertEqual((plan.xmax, plan.ymax), (80.0, 40.0))

    def test_geometry_bounds_used_as_last_resort(self):
        plan = create_grid_plan(None, 0.0, 0.0, geometry_bounds=(1.0, 2.0, 11.0, 12.0), num_levels=1)
        self.assertEqual((plan.xmin, plan.ymin, plan.xmax, plan.ymax), (1.0, 2.0, 11.0, 12.0))

    def test_emergency_default_box(self):
        plan = create_grid_plan(None, 0.0, 0.0, num_levels=1)
        self.assertEqual((plan.xmax, plan.ymax), (100.0, 100.0))

    def test_zero_size_viewbox_is_rejected(self):
        plan = create_grid_plan((0.0, 0.0, 0.0, 0.0), 30.0, 15.0, num_levels=1)
        self.assertEqual((plan.xmax, plan.ymax), (30.0, 15.0))

    def test_levels_double_each_step_for_wide_canvas(self):
        plan = create_grid_plan((0.0, 0.0, 200.0, 100.0), 200.0, 100.0, num_levels=3, base_cells=4)
        self.assertEqual([(l.cols, l.rows) for l in plan.levels], [(8, 4), (16, 8), (32, 16)])
        self.assertEqual([l.level_idx for l in plan.levels], [1, 2, 3])

    def test_levels_for_tall_canvas(self):
        plan = create_grid_plan((0.0, 0.0, 100.0, 200.0), 100.0, 200.0, num_levels=2, base_cells=4)
        self.assertEqual([(l.cols, l.rows) for l in plan.levels], [(4, 8), (8, 16)])

    def test_manual_grids_override_automatic_planning(self):
        plan = create_grid_plan((0.0, 0.0, 100.0, 100.0), 100.0, 100.0,
                                manual_grids=[(3, 5), (0, 0)])
        self.assertEqual([(l.cols, l.rows) for l in plan.levels], [(3, 5), (1, 1)])

    def test_degenerate_bounds_are_clamped(self):
        plan = GridPlan((5.0, 5.0, 5.0, 5.0), [])
        self.assertEqual(plan.width, 1e-6)
        self.assertEqual(plan.height, 1e-6)


class TestFractalAnalyzer(unittest.TestCase):

    def test_compute_fractal_dimension_empty(self):
        res = compute_fractal_dimension([])
        self.assertEqual(res.fractal_dimension_db, 0.0)
        self.assertEqual(res.r2_score, 0.0)

    def test_compute_fractal_dimension_line(self):
        lvl1 = GridLevel(1, 4, 4, 100.0, 100.0)
        lvl2 = GridLevel(2, 8, 8, 100.0, 100.0)
        lvl3 = GridLevel(3, 16, 16, 100.0, 100.0)

        # 1D line: N doubles when scale doubles (4 -> 8 -> 16)
        r1 = CPULevelResult(lvl1, filled_count=4, empty_count=12, execution_time_ms=1.0)
        r2 = CPULevelResult(lvl2, filled_count=8, empty_count=56, execution_time_ms=1.0)
        r3 = CPULevelResult(lvl3, filled_count=16, empty_count=240, execution_time_ms=1.0)

        res = compute_fractal_dimension([r1, r2, r3])
        self.assertAlmostEqual(res.fractal_dimension_db, 1.0, places=4)
        self.assertAlmostEqual(res.r2_score, 1.0, places=4)


if __name__ == "__main__":
    unittest.main()
