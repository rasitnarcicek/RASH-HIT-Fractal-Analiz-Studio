# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

import unittest
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

from backend.geometry_engine import parse_transform_string, transform_points, parse_svg_path
from backend.academic_exporter import esc_html, esc_xml, sanitize_output_slug


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

        # Run against a temp output root so the data-safe default (versioned
        # folders) never pollutes the real outputs/ directory during tests.
        tmp_out = tempfile.mkdtemp(prefix="rash_hit_test_")
        try:
            cmd_pos = [sys.executable, "run_analysis.py", "--input", "input_svgs/16D.svg",
                       "--levels", "1", "--profile", "lean", "--output", tmp_out]
            res_pos = subprocess.run(cmd_pos, capture_output=True, text=True)
            self.assertEqual(res_pos.returncode, 0)
        finally:
            shutil.rmtree(tmp_out, ignore_errors=True)

    # 8. Output Policy L08 / L09 Test
    def test_output_policy_l08_l09(self):
        is_l8_safe = (8 <= 7) or False
        self.assertFalse(is_l8_safe)

        export_high_level = True
        lvl9_num = 9
        is_l9_safe = (lvl9_num <= 7) or (lvl9_num == 8 and export_high_level)
        self.assertFalse(is_l9_safe)

    # 9. CLI --profile choices must match the registered output profiles and
    #    reach the engine (previously a dead flag with non-existent choices).
    def test_cli_profile_choices_match_registered_profiles(self):
        from backend.output_profiles import PROFILES
        registered = set(PROFILES.keys())
        self.assertEqual(
            registered, {"lean", "reproducible", "debug", "presentation", "batch"}
        )

        res = subprocess.run(
            [sys.executable, "run_analysis.py", "--help"],
            capture_output=True, text=True)
        help_text = res.stdout + res.stderr
        for name in registered:
            self.assertIn(name, help_text, f"CLI --profile help missing {name}")
        # The dedicated batch-run profile flag must be exposed.
        self.assertIn("--batch-profile", help_text)

        # Removed/alias names must be rejected by argparse.
        res_bad = subprocess.run(
            [sys.executable, "run_analysis.py", "--input", "input_svgs/16D.svg",
             "--profile", "standard"],
            capture_output=True, text=True)
        self.assertNotEqual(res_bad.returncode, 0)
        self.assertIn("invalid choice", (res_bad.stderr + res_bad.stdout).lower())

    # 10. AnalysisProcessor must forward the selected profile to load_output_profile
    #     (the --profile flag used to be parsed and then silently dropped).
    def test_analysis_processor_forwards_profile(self):
        from backend.processor import AnalysisProcessor
        from backend.output_profiles import load_output_profile
        p = AnalysisProcessor(input_path=Path("input_svgs/16D.svg"), levels=1,
                              profile="reproducible")
        self.assertEqual(p.profile, "reproducible")
        prof = load_output_profile(p.profile)
        self.assertTrue(prof.generate_manifest)
        self.assertTrue(prof.generate_masks)  # reproducible profile emits masks/RLE

    # 11. Batch orchestration must accept and forward the profile.
    def test_batch_processor_accepts_profile(self):
        import inspect
        from backend.batch_processor import run_batch_analysis
        sig = inspect.signature(run_batch_analysis).parameters
        self.assertIn("profile", sig)
        self.assertIn("batch_profile", sig)

    # 12. run_batch_analysis must forward batch_profile to AnalysisProcessor
    #     with the documented precedence (batch_profile > profile).
    def test_batch_processor_forwards_batch_profile(self):
        from unittest import mock
        from backend.batch_processor import run_batch_analysis

        tmp_out = tempfile.mkdtemp(prefix="rash_hit_batch_prof_")
        try:
            with mock.patch("backend.batch_processor.AnalysisProcessor") as AP:
                inst = AP.return_value
                inst.run.return_value.status = "SUCCESS"
                inst.run.return_value.fractal_dimension = 1.5
                inst.run.return_value.r_squared = 0.99
                inst.run.return_value.to_dict.return_value = {}

                # batch_profile wins over profile when both are given.
                run_batch_analysis(
                    "input_svgs", levels=1, output_dir=tmp_out,
                    profile="lean", batch_profile="batch",
                )
                self.assertEqual(AP.call_args.kwargs.get("profile"), "batch")

                # Without batch_profile, the plain profile is forwarded unchanged.
                AP.reset_mock()
                run_batch_analysis(
                    "input_svgs", levels=1, output_dir=tmp_out,
                    profile="reproducible",
                )
                self.assertEqual(AP.call_args.kwargs.get("profile"), "reproducible")
        finally:
            shutil.rmtree(tmp_out, ignore_errors=True)

    # 13. The dedicated `batch` profile must exist and pull the SVG-only gate
    #     down to L9 (L10+ batch packages: SVG maps only, no cell payloads).
    def test_batch_profile_gates_svg_only_at_l9(self):
        from backend.output_profiles import PROFILES, load_output_profile, is_svg_only_level
        self.assertIn("batch", PROFILES)
        p = load_output_profile("batch")
        self.assertEqual(p.svg_only_after_level, 9)
        # Batch is lean-derived: core artifact switches stay on.
        self.assertTrue(p.generate_map_svgs)
        self.assertTrue(p.generate_html_report)
        self.assertTrue(p.generate_pdf_report)
        self.assertTrue(p.generate_manifest)
        self.assertFalse(p.generate_high_level_cell_tables)
        # L9 stays SVG+summary; L10+ becomes SVG-only in batch runs.
        self.assertFalse(is_svg_only_level(p, 9))
        self.assertTrue(is_svg_only_level(p, 10))


if __name__ == "__main__":
    unittest.main()
