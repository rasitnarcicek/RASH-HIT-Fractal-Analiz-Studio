# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""GEOMETRIC_CONTACT pipeline tests (pure NumPy port).

Verifies: (1) SVG -> segment extraction, (2) the CPU reference manifest,
(3) ground truth Db values carried over from the RASH-HIT v1.0 engine test
suite (measured values validated there against hand-derived cell sets).
"""
import unittest
from pathlib import Path

from src.backend.geometric_contact_pipeline import (
    extract_line_segments, run_geometric_contact,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "svg_reference"


# --- segment extraction -------------------------------------------------------


class TestExtractLineSegments(unittest.TestCase):

    def test_extract_line_element(self):
        vb, segs = extract_line_segments(
            '<svg viewBox="0 0 100 100"><line x1="10" y1="50" x2="90" y2="50"/></svg>')
        self.assertEqual(vb, (0.0, 0.0, 100.0, 100.0))
        self.assertEqual(segs, [(10.0, 50.0, 90.0, 50.0)])

    def test_extract_path_mlhvz(self):
        vb, segs = extract_line_segments(
            '<svg viewBox="0 0 10 10"><path d="M1 1 L5 1 H8 V5 L2 5 Z"/></svg>')
        expected = [(1, 1, 5, 1), (5, 1, 8, 1), (8, 1, 8, 5), (8, 5, 2, 5), (2, 5, 1, 1)]
        self.assertEqual(segs, expected)

    def test_extract_path_relative(self):
        vb, segs = extract_line_segments(
            '<svg viewBox="0 0 10 10"><path d="m1 1 l4 0 h3 v4 l-6 0 z"/></svg>')
        expected = [(1, 1, 5, 1), (5, 1, 8, 1), (8, 1, 8, 5), (8, 5, 2, 5), (2, 5, 1, 1)]
        self.assertEqual(segs, expected)

    def test_extract_polyline(self):
        vb, segs = extract_line_segments(
            '<svg viewBox="0 0 10 10"><polyline points="0,0 5,5 10,0"/></svg>')
        self.assertEqual(segs, [(0.0, 0.0, 5.0, 5.0), (5.0, 5.0, 10.0, 0.0)])

    def test_extract_polygon_closes_ring(self):
        vb, segs = extract_line_segments(
            '<svg viewBox="0 0 10 10"><polygon points="0,0 5,5 10,0"/></svg>')
        # polygon = polyline edges + explicit closing edge back to the start
        self.assertEqual(segs, [
            (0.0, 0.0, 5.0, 5.0),
            (5.0, 5.0, 10.0, 0.0),
            (10.0, 0.0, 0.0, 0.0),
        ])

    def test_extract_polygon_fixture_simple_polygon(self):
        vb, segs = extract_line_segments(
            (FIXTURES / "simple_polygon.svg").read_text("utf-8"))
        self.assertEqual(vb, (0.0, 0.0, 100.0, 100.0))
        self.assertEqual(len(segs), 3)  # triangle: 2 polyline edges + closing edge

    def test_extract_fixture_horizontal_line(self):
        vb, segs = extract_line_segments((FIXTURES / "horizontal_line.svg").read_text("utf-8"))
        self.assertEqual(vb, (0.0, 0.0, 100.0, 100.0))
        self.assertEqual(len(segs), 1)

    def test_empty_input_raises(self):
        with self.assertRaises(ValueError):
            extract_line_segments("")


# --- CPU reference manifest ----------------------------------------------------


class TestRunGeometricContact(unittest.TestCase):

    def test_cpu_manifest_horizontal_line_near_one(self):
        m = run_geometric_contact(FIXTURES / "horizontal_line.svg", max_level=7)
        self.assertEqual(m["schema_version"], "rashhit.geometric_contact/v1")
        self.assertEqual(m["measure_mode"], "geometric_contact")
        self.assertEqual(m["engine"], "cpu_reference_supercover")
        self.assertEqual(m["grid_policy"], "fixed_origin")
        self.assertEqual(m["boundary_policy"], "touch_counts")
        # y = 50 lies exactly on a row boundary -> double rows (touch_counts);
        # endpoints 10/90 sit inside cells, so N is not an exact power series and
        # Db lands slightly below 1 (measured: 0.9412, R² 0.9990).
        self.assertAlmostEqual(m["fractal_dimension"], 0.941195, delta=1e-4)
        self.assertGreater(m["r_squared"], 0.99)
        counts = [m["per_level"][str(lv)]["occupied_cells"] for lv in range(1, 8)]
        self.assertEqual(counts, [8, 16, 28, 52, 104, 208, 412])

    def test_cpu_manifest_diagonal_line_sane(self):
        m = run_geometric_contact(FIXTURES / "diagonal_line.svg", max_level=7)
        self.assertAlmostEqual(m["fractal_dimension"], 0.979029, delta=1e-4)
        self.assertGreater(m["r_squared"], 0.99)
        for lv in range(1, 8):
            p = m["per_level"][str(lv)]
            self.assertEqual(p["total_cells"], p["occupied_cells"] + p["empty_cells"])

    def test_cpu_manifest_shape_contract(self):
        m = run_geometric_contact(FIXTURES / "horizontal_line.svg", max_level=5)
        self.assertEqual(set(m["per_level"].keys()), {"1", "2", "3", "4", "5"})
        for lv in range(1, 6):
            p = m["per_level"][str(lv)]
            self.assertEqual(p["cols"], p["rows"])
            self.assertEqual(p["cols"], 4 * (2 ** (lv - 1)))
            self.assertGreater(p["occupied_cells"], 0)


if __name__ == "__main__":
    unittest.main()
