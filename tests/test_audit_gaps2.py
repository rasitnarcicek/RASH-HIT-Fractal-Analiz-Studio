# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

import unittest
import math
import numpy as np
from pathlib import Path
import tempfile
import json
import xml.etree.ElementTree as ET

from backend.grid_planner import create_grid_plan, GridLevel
from backend.geometry_engine import parse_svg_path, extract_node_geometries
from backend.svg_loader import SVGNode
from backend.artifact_validator import (
    parse_ascii_file, parse_mask_file, parse_rle_file, parse_svg_rects_xml
)
from backend.fractal_analyzer import compute_fractal_dimension
from backend.intersection_cpu import CPULevelResult


class TestAuditGaps2(unittest.TestCase):

    def test_grid_planner_strict_doubling(self):
        """Verify grid levels strictly double in resolution (powers of 2) without drift."""
        plan = create_grid_plan(None, 1600.0, 1000.0, num_levels=7, base_cells=4)
        base_rows = plan.levels[0].rows
        base_cols = plan.levels[0].cols
        for i, lvl in enumerate(plan.levels):
            expected_rows = base_rows * (2 ** i)
            expected_cols = base_cols * (2 ** i)
            self.assertEqual(lvl.rows, expected_rows, f"Level {lvl.level_idx} rows mismatch")
            self.assertEqual(lvl.cols, expected_cols, f"Level {lvl.level_idx} cols mismatch")

    def test_malformed_svg_path_bounds_check(self):
        """Verify truncated or malformed SVG paths raise clear ValueError instead of IndexError."""
        malformed_paths = [
            "M 10",
            "C 1 2 3 4 5",
            "L 5",
            "A 10 10 0 0 1",
        ]
        for path in malformed_paths:
            with self.assertRaises(ValueError, msg=f"Should raise ValueError for '{path}'"):
                parse_svg_path(path)

    def test_artifact_validator_mask_format(self):
        """Verify parse_mask_file handles R01 | 1 0 1 exporter mask format."""
        content = "R01 | 1 0 1\nR02 | 0 1 0\n"
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(content)
            f_path = Path(f.name)

        try:
            matrix = parse_mask_file(f_path, cols=3, rows=2)
            expected = np.array([[1, 0, 1], [0, 1, 0]])
            np.testing.assert_array_equal(matrix, expected)
        finally:
            f_path.unlink(missing_ok=True)

    def test_artifact_validator_rle_format(self):
        """Verify parse_rle_file handles flat rle_runs format."""
        rle_data = {
            "level": 1, "cols": 2, "rows": 2, "total_cells": 4, "filled_cells": 2,
            "rle_runs": [[1, 2], [0, 2]]
        }
        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write(json.dumps(rle_data))
            f_path = Path(f.name)

        try:
            matrix = parse_rle_file(f_path, cols=2, rows=2)
            expected = np.array([[1, 1], [0, 0]])
            np.testing.assert_array_equal(matrix, expected)
        finally:
            f_path.unlink(missing_ok=True)

    def test_artifact_validator_svg_fill_color(self):
        """Verify parse_svg_rects_xml recognizes #60A5FA exporter fill color."""
        svg_content = (
            '<svg xmlns="http://www.w3.org/2000/svg">'
            '<rect x="0" y="0" width="10" height="10" fill="#60A5FA"/>'
            '<rect x="10" y="0" width="10" height="10" fill="#ffffff"/>'
            '</svg>'
        )
        with tempfile.NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as f:
            f.write(svg_content)
            f_path = Path(f.name)

        try:
            matrix, info = parse_svg_rects_xml(f_path, cols=2, rows=1)
            self.assertEqual(info["filled_rects_count"], 1)
            self.assertEqual(matrix[0, 0], 1)
            self.assertEqual(matrix[0, 1], 0)
        finally:
            f_path.unlink(missing_ok=True)

    def test_fractal_analyzer_level_zero_epsilon(self):
        """Verify compute_fractal_dimension includes Level 1 where log(1/eps) == 0."""
        grid_l1 = GridLevel(1, 1, 1, 100.0, 100.0)
        grid_l2 = GridLevel(2, 2, 2, 100.0, 100.0)

        res1 = CPULevelResult(grid_l1, 1, 0, 1.0)
        res2 = CPULevelResult(grid_l2, 4, 0, 1.0)

        result = compute_fractal_dimension([res1, res2])
        self.assertEqual(len(result.scaling_levels_used), 2)
        self.assertIn(1, result.scaling_levels_used)
        self.assertIn(2, result.scaling_levels_used)


if __name__ == '__main__':
    unittest.main()
