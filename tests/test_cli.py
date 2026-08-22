# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

import subprocess
import sys
import unittest
from pathlib import Path


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.script_path = self.root_dir / "run_analysis.py"
        self.sample_svg = self.root_dir / "input_svgs" / "16D.svg"

    def test_cli_help(self):
        res = subprocess.run(
            [sys.executable, str(self.script_path), "--help"],
            capture_output=True,
            text=True,
            cwd=str(self.root_dir)
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("RASH-HIT Fractal Studio", res.stdout)
        self.assertIn("--input", res.stdout)
        self.assertIn("--dir", res.stdout)

    def test_cli_version(self):
        res = subprocess.run(
            [sys.executable, str(self.script_path), "--version"],
            capture_output=True,
            text=True,
            cwd=str(self.root_dir)
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("1.0.0", res.stdout)

    def test_cli_single_file(self):
        res = subprocess.run(
            [sys.executable, str(self.script_path), "--input", str(self.sample_svg), "--levels", "5"],
            capture_output=True,
            text=True,
            cwd=str(self.root_dir)
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Fractal Dimension Db", res.stdout)
        self.assertIn("Linear Regression Fit R2", res.stdout)
        self.assertIn("ANALYSIS REPORT", res.stdout)
        self.assertIn("L05", res.stdout)

    def test_cli_batch_dir(self):
        svg_dir = self.root_dir / "input_svgs"
        res = subprocess.run(
            [sys.executable, str(self.script_path), "--dir", str(svg_dir), "--levels", "3"],
            capture_output=True,
            text=True,
            cwd=str(self.root_dir)
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("BATCH PROCESSING MODE", res.stdout)
        self.assertIn("16D", res.stdout)


if __name__ == "__main__":
    unittest.main()
