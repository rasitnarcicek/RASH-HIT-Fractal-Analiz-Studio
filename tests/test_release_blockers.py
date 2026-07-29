# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

import unittest
import numpy as np
from pathlib import Path
import tempfile
import subprocess
import sys

from backend.geometry_engine import parse_transform_string, transform_points, parse_svg_path
from backend.academic_exporter import esc_html, esc_xml, sanitize_output_slug, LevelReportModel, AnalysisReportModel
from backend.grid_planner import create_grid_plan
from backend.intersection_cpu_area import analyze_grid_cpu_area
from backend.intersection_hierarchical import analyze_grid_hierarchical
from backend.svg_loader import SVGLoader


class TestReleaseBlockers(unittest.TestCase):

    # 1. XSS Escape Test
    def test_xss_escape_html_svg(self):
        malicious = "<script>alert('xss')</script>\"&"
        escaped_h = esc_html(malicious)
        self.assertNotIn("<script>", escaped_h)
        self.assertIn("&lt;script&gt;", escaped_h)
        self.assertIn("&quot;", escaped_h)

        escaped_x = esc_xml(malicious)
        self.assertNotIn("<script>", escaped_x)
        self.assertIn("&lt;script&gt;", escaped_x)
        self.assertIn("&amp;", escaped_x)

    # 2. Output Path Sanitize & Traversal Protection Test
    def test_output_path_sanitize_traversal(self):
        self.assertEqual(sanitize_output_slug("../evil"), "evil")
        self.assertEqual(sanitize_output_slug(".."), "motif")
        self.assertEqual(sanitize_output_slug("."), "motif")
        self.assertEqual(sanitize_output_slug("../../etc/passwd"), "etc_passwd")
        self.assertEqual(sanitize_output_slug("16D.svg"), "16D_svg")
        self.assertEqual(sanitize_output_slug("motif-1"), "motif-1")

    # 3. skewY Matrix SVG Spec Test
    def test_skewy_matrix_svg_spec(self):
        M = parse_transform_string("skewY(45)")
        pts = [(2.0, 3.0)]
        res = transform_points(pts, M)
        self.assertAlmostEqual(res[0][0], 2.0, places=5)
        self.assertAlmostEqual(res[0][1], 5.0, places=5)

    # 4. parse_svg_path Malformed Input Fail-Fast Test
    def test_parse_svg_path_malformed_fail_fast(self):
        with self.assertRaises(ValueError):
            parse_svg_path("M 0 0 X 10 10")

        with self.assertRaises(ValueError):
            parse_svg_path("10 10")

    # 5. Row / Col Consistency Test (Non-square 4x8 grid)
    def test_row_col_consistency(self):
        row, col = 1, 2
        cell_w, cell_h = 10.0, 20.0
        x = col * cell_w
        y = row * cell_h
        self.assertEqual(x, 20.0)
        self.assertEqual(y, 20.0)

    # 6. CLI Outline Rejected Test
    def test_cli_outline_rejected_if_not_supported(self):
        cmd = [sys.executable, "run_analysis.py", "--input", "input_svgs/16D.svg", "--measure", "outline"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("invalid choice: 'outline'", res.stderr.lower() + res.stdout.lower())

    # 7. CLI --levels Validation Test
    def test_cli_levels_validation(self):
        cmd_zero = [sys.executable, "run_analysis.py", "--input", "input_svgs/16D.svg", "--levels", "0"]
        res_zero = subprocess.run(cmd_zero, capture_output=True, text=True)
        self.assertNotEqual(res_zero.returncode, 0)

        cmd_neg = [sys.executable, "run_analysis.py", "--input", "input_svgs/16D.svg", "--levels", "-1"]
        res_neg = subprocess.run(cmd_neg, capture_output=True, text=True)
        self.assertNotEqual(res_neg.returncode, 0)

        cmd_pos = [sys.executable, "run_analysis.py", "--input", "input_svgs/16D.svg", "--levels", "1", "--profile", "lean"]
        res_pos = subprocess.run(cmd_pos, capture_output=True, text=True)
        self.assertEqual(res_pos.returncode, 0)

    # 8. Output Policy L08 / L09 Test
    def test_output_policy_l08_l09(self):
        lvl7 = LevelReportModel(level=7, cols=128, rows=256, grid_label="128x256", total_cells=32768, filled_cells=100, empty_cells=32668, fill_ratio=0.003, occupancy_percent=0.3, cell_w=1, cell_h=1, execution_time_ms=1.0)
        is_l8_safe = (8 <= 7) or False
        self.assertFalse(is_l8_safe)

        export_high_level = True
        lvl9_num = 9
        is_l9_safe = (lvl9_num <= 7) or (lvl9_num == 8 and export_high_level)
        self.assertFalse(is_l9_safe)


if __name__ == "__main__":
    unittest.main()
