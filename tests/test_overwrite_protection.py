# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""
test_overwrite_protection.py - Package Versioning & Overwrite Protection v1 tests.
"""

import unittest
import tempfile
from pathlib import Path

from backend.academic_exporter import (
    AnalysisReportModel,
    LevelReportModel,
    export_academic_package_v3,
    make_unique_package_dir,
    sanitize_output_slug,
)
from backend.output_profiles import OutputProfile
from backend.package_index import scan_all_packages, build_package_id


def _minimal_model(motif="16D", generated_at="2026-08-01 18:10:20"):
    lvl = LevelReportModel(
        level=1, cols=4, rows=8, grid_label="4x8",
        total_cells=32, filled_cells=28, empty_cells=4, fill_ratio=0.875,
        occupancy_percent=87.5, cell_w=35.43, cell_h=35.43, execution_time_ms=1.0,
        filled_set={(0, 0), (0, 1), (1, 0)},
    )
    return AnalysisReportModel(
        motif=motif,
        safe_name=sanitize_output_slug(motif) or motif,
        generated_at=generated_at,
        source_file=f"{motif}.svg",


        viewbox_width=141.73, viewbox_height=283.46, aspect_ratio=0.5,
        vector_geometry_count=10, analysis_engine="Test Engine",
        db=1.6095, r2=0.9976, total_time_ms=100.0,
        levels=[lvl],
    )


def _minimal_profile():
    return OutputProfile(
        name="test",
        generate_workbook=False, generate_xlsx_tables=False, generate_tables_html=False,
        generate_map_svgs=False, generate_map_svgs_legacy=False,
        generate_html_report=False, generate_pdf_report=False, generate_markdown_report=False,
        generate_manifest=False, generate_terminal_log=False,
        generate_ascii=False, generate_ascii_book=False, generate_masks=False, generate_rle=False,
        generate_raw_csv=False, generate_levels_csv=False, generate_levels_json=False,
        generate_summary_json=False,
    )


class TestUniquePackageDir(unittest.TestCase):

    def test_plain_folder_used_when_free(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = make_unique_package_dir(root, "16D", "2026-08-01 18:10:20")
            self.assertEqual(p.name, "16D")

    def test_timestamped_folder_when_collision(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "16D").mkdir()
            p = make_unique_package_dir(root, "16D", "2026-08-01 18:10:20")
            self.assertEqual(p.name, "16D_20260801_181020")

    def test_suffix_added_on_timestamp_collision(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "16D").mkdir()
            (root / "16D_20260801_181020").mkdir()
            p = make_unique_package_dir(root, "16D", "2026-08-01 18:10:20")
            self.assertEqual(p.name, "16D_20260801_181020_001")

    def test_sanitizes_unsafe_stem(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = make_unique_package_dir(root, "../../etc/passwd", None)
            self.assertNotIn("..", p.name)
            self.assertNotIn("/", p.name)
            self.assertNotIn(chr(92), p.name)

    def test_turkish_chars_normalized(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = make_unique_package_dir(root, "16İmotif", None)
            # UTF-8 Turkish preservation requirement
            self.assertEqual(sanitize_output_slug("16İmotif"), "16İmotif")


class TestExportOverwriteBehavior(unittest.TestCase):

    def test_default_no_overwrite_keeps_existing_package(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            existing = root / "16D"
            existing.mkdir()
            marker = existing / "KEEP_ME.txt"
            marker.write_text("original data", encoding="utf-8")

            out = export_academic_package_v3(
                _minimal_model(), root, profile=_minimal_profile(), overwrite=False,
            )

            self.assertTrue(marker.exists(), "Existing package must NOT be wiped by default")
            self.assertEqual(marker.read_text(encoding="utf-8"), "original data")
            self.assertNotEqual(out.name, "16D")
            self.assertTrue(out.name.startswith("16D_"))
            self.assertTrue(out.is_dir())

    def test_explicit_overwrite_replaces_existing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            existing = root / "16D"
            existing.mkdir()
            marker = existing / "KEEP_ME.txt"
            marker.write_text("original data", encoding="utf-8")

            out = export_academic_package_v3(
                _minimal_model(), root, profile=_minimal_profile(), overwrite=True,
            )

            self.assertEqual(out.name, "16D")
            self.assertFalse(marker.exists(), "overwrite=True must replace the old package")

    def test_second_default_run_produces_second_version(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            m1 = _minimal_model(generated_at="2026-08-01 18:10:20")
            m2 = _minimal_model(generated_at="2026-08-01 18:30:45")
            out1 = export_academic_package_v3(m1, root, profile=_minimal_profile(), overwrite=False)
            out2 = export_academic_package_v3(m2, root, profile=_minimal_profile(), overwrite=False)
            names = sorted(p.name for p in root.iterdir() if p.is_dir())
            self.assertEqual(names, ["16D", "16D_20260801_183045"])
            self.assertNotEqual(out1, out2)


class TestPackageIndexMultipleVersions(unittest.TestCase):

    def test_index_lists_both_versions_with_unique_ids(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for sub, gen_at, db in [
                ("16D", "2026-08-01 18:10:20", 1.6095),
                ("16D_20260801_183045", "2026-08-01 18:30:45", 1.7012),
            ]:
                pkg_dir = root / sub
                pkg_dir.mkdir()
                (pkg_dir / "result.json").write_text(
                    '{"motif_profile": {"motif": "16D"}, "generated_at": "%s", '
                    '"fractal_dimension": %.4f, "r_squared": 0.9991, '
                    '"computed_levels_count": 7}' % (gen_at, db),
                    encoding="utf-8",
                )

            pkgs = scan_all_packages(root)
            self.assertEqual(len(pkgs), 2)
            ids = {p["package_id"] for p in pkgs}
            self.assertEqual(len(ids), 2, f"package_ids must be unique, got {ids}")
            folders = {p["folder"] for p in pkgs}
            self.assertEqual(folders, {"16D", "16D_20260801_183045"})

            versioned = next(p for p in pkgs if p["folder"] == "16D_20260801_183045")
            self.assertEqual(versioned["package_version"], "v20260801_183045")
            self.assertEqual(versioned["original_motif"], "16D")
            self.assertEqual(versioned["package_folder"], "16D_20260801_183045")
            self.assertTrue(versioned["run_id"])

    def test_build_package_id_unique_per_timestamp(self):
        id1 = build_package_id("16D", "16D", "2026-08-01 18:10:20")
        id2 = build_package_id("16D", "16D", "2026-08-01 18:30:45")
        self.assertNotEqual(id1, id2)


if __name__ == "__main__":
    unittest.main()
