# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
import unittest
from backend.grid_planner import create_grid_plan
from backend.intersection_cpu import CPULevelResult

class TestEngine(unittest.TestCase):
    def test_grid_plan(self):
        plan = create_grid_plan((0, 0, 100, 200), 100, 200, num_levels=3)
        self.assertEqual(len(plan.levels), 3)
        self.assertEqual(plan.levels[0].cols, 4)
        self.assertEqual(plan.levels[0].rows, 8)

if __name__ == '__main__':
    unittest.main()
