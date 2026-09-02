# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

import unittest
from pathlib import Path

from src.backend.ascii_exporter import (
    build_output_filename,
    build_book_filename,
    generate_ascii_file,
    generate_batch_ascii_book,
    now_stamp,
    ENGINE_NAME,
    SOFTWARE_VERSION,
)


def _small_manifest() -> dict:
    """A 4x8 grid with all boundary cells filled (8x4=32 cells around a 1x1 rect)."""
    return {
        "schema_version": "rashhit.geometric_contact/v1",
        "engine_mode": "cpu_reference",
        "backend": "cpu",
        "gpu_name": None,
        "measure_mode": "geometric_contact",
        "boundary_policy": "touch_counts",
        "grid_policy": "fixed_origin",
        "viewBox": [0.0, 0.0, 100.0, 200.0],
        "segment_count": 4,
        "fractal_dimension": 0.9997,
        "r_squared": 0.9998,
        "total_compute_seconds": 0.0211,
        "per_level": {
            "1": {
                "cols": 4, "rows": 8,
                "total_cells": 32, "occupied_cells": 16,
                "empty_cells": 16, "occupancy_ratio": 0.5,
            },
        },
    }


class TestBuildOutputFilename(unittest.TestCase):
    def test_format_includes_stem_level_and_full_stamp(self):
        name = build_output_filename("16D", 5, stamp="2026-09-01_22-56-30")
        self.assertEqual(name, "16D_L5_2026-09-01_22-56-30.txt")

    def test_default_stamp_is_now_seconds(self):
        name = build_output_filename("foo", 9)
        prefix = "foo_L9_"
        suffix = ".txt"
        self.assertTrue(name.startswith(prefix))
        self.assertTrue(name.endswith(suffix))
        stamp_part = name[len(prefix):-len(suffix)]
        import re
        self.assertRegex(stamp_part, r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$")
        self.assertEqual(stamp_part, now_stamp())


class TestBuildBookFilename(unittest.TestCase):
    def test_book_format(self):
        name = build_book_filename(3, stamp="2026-09-01_22-56-30")
        self.assertEqual(name, "ascii_book_L3_2026-09-01_22-56-30.txt")


class TestGenerateAsciiFile(unittest.TestCase):
    def test_writes_file_with_expected_sections(self):
        manifest = _small_manifest()
        manifest["per_level"]["1"]["occupied_cells"] = 20

        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as td:
            out = Path(td) / "16D_L1_2026-09-01_22-56-30.txt"
            generate_ascii_file(manifest, motif_stem="16D", levels=1,
                                out_path=out, stamp="2026-09-01_22-56-30")
            text = out.read_text(encoding="utf-8")

        self.assertIn(f"RASH-HIT FRACTAL ANALYSIS v{SOFTWARE_VERSION}", text)
        self.assertIn(ENGINE_NAME, text)
        self.assertIn("Motif     : 16D.svg", text)
        self.assertIn("Date      : 2026-09-01_22-56-30", text)
        self.assertIn("Levels    : L1", text)
        self.assertIn("Fractal Dimension Db = 0.9997", text)
        self.assertIn("R2           = 0.9998", text)
        # Numeric summary table is present
        self.assertIn("L01", text)
        self.assertIn("4x8", text)
        self.assertIn("32", text)
        self.assertIn("20", text)
        self.assertIn("62.50%", text)
        # No ASCII grid map (LEVEL / R00x / col headers) should appear
        self.assertNotIn("LEVEL 01", text)
        self.assertNotIn("R001", text)
        self.assertNotIn("C01", text)


class TestGenerateBatchAsciiBook(unittest.TestCase):
    def test_combines_two_motifs(self):
        m1 = _small_manifest()
        m2 = _small_manifest()
        m2["fixture_name"] = "diag"
        m2["fractal_dimension"] = 0.9849
        m2["r_squared"] = 0.9996
        m2["per_level"]["1"]["occupied_cells"] = 12

        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as td:
            out = Path(td) / "ascii_book.txt"
            generate_batch_ascii_book(
                per_motif=[("16D", m1), ("diag", m2)],
                levels=1, out_path=out, stamp="2026-09-01_22-56-30",
            )
            text = out.read_text(encoding="utf-8")

        self.assertIn("BATCH ASCII BOOK", text)
        self.assertIn("MASTER SUMMARY", text)
        self.assertIn("16D", text)
        self.assertIn("diag", text)
        self.assertIn("MOTIF: 16D.svg", text)
        self.assertIn("MOTIF: diag.svg", text)
        self.assertIn("0.9997", text)
        self.assertIn("0.9849", text)
        # No per-level ASCII grid map should appear
        self.assertNotIn("LEVEL 01", text)
        self.assertNotIn("R001", text)


if __name__ == "__main__":
    unittest.main()
