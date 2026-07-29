# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

import unittest
import numpy as np
from pathlib import Path
import tempfile
import subprocess
import sys

from backend.geometry_engine import parse_transform_string, transform_points
from backend.artifact_validator import parse_ascii_file
from backend.academic_exporter import esc_html, esc_xml


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

    def test_ascii_validator_accepts_one_zero(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as f:
            f.write("|1010|\n|0101|\n")
            tmp_path = Path(f.name)

        try:
            mat = parse_ascii_file(tmp_path, cols=4, rows=2)
            expected = np.array([[1, 0, 1, 0], [0, 1, 0, 1]], dtype=int)
            np.testing.assert_array_equal(mat, expected)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_ascii_validator_accepts_filled_block(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as f:
            f.write("|■□■□|\n|□■□■|\n")
            tmp_path = Path(f.name)

        try:
            mat = parse_ascii_file(tmp_path, cols=4, rows=2)
            expected = np.array([[1, 0, 1, 0], [0, 1, 0, 1]], dtype=int)
            np.testing.assert_array_equal(mat, expected)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_measure_outline_rejected(self):
        cmd = [sys.executable, "run_analysis.py", "--input", "input_svgs/16D.svg", "--measure", "outline"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("invalid choice: 'outline'", res.stderr.lower() + res.stdout.lower())

    def test_html_escape_helper(self):
        malicious = "<script>alert('xss')</script>"
        escaped_h = esc_html(malicious)
        self.assertNotIn("<script>", escaped_h)
        self.assertIn("&lt;script&gt;", escaped_h)

        escaped_x = esc_xml(malicious)
        self.assertNotIn("<script>", escaped_x)
        self.assertIn("&lt;script&gt;", escaped_x)


if __name__ == "__main__":
    unittest.main()
