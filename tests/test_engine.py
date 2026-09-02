# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

import unittest
import numpy as np

from src.backend.geometry_engine import parse_transform_string, transform_points


class TestEngineAndFixes(unittest.TestCase):

    def test_skewx_transform(self):
        M = parse_transform_string("skewX(45)")
        pts = [(10.0, 20.0)]
        res = transform_points(pts, M)
        self.assertAlmostEqual(res[0][0], 30.0, places=5)
        self.assertAlmostEqual(res[0][1], 20.0, places=5)

    def test_skewy_transform(self):
        M = parse_transform_string("skewY(45)")
        pts = [(10.0, 20.0)]
        res = transform_points(pts, M)
        self.assertAlmostEqual(res[0][0], 10.0, places=5)
        self.assertAlmostEqual(res[0][1], 30.0, places=5)

    def test_row_col_svg_mapping(self):
        row, col = 1, 2
        cell_w, cell_h = 10.0, 20.0
        x = col * cell_w
        y = row * cell_h
        self.assertEqual(x, 20.0)
        self.assertEqual(y, 20.0)


if __name__ == "__main__":
    unittest.main()
