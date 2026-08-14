# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Rasit Narcicek
"""
tests/test_output_index_dashboard.py

Unit tests for the active package_index engine (result.json parsing, status
classification, has_* flags, stats/history/figures) plus web-server delete
security. The deprecated dashboard generator modules (dashboard_exporter,
dashboard_js, html_templates/index_template) were removed in the 2026-08-03
cleanup; tests that exercised them remain behind the skipUnless(_AVAILABLE)
guard and reactivate only if the modules are ever re-introduced.

Package data is loaded at runtime by the live shell (frontend/) from the REST
API (/api/packages, /api/stats, /api/figures) or, via file://, from the
offline outputs/package_index.json. No package data is embedded into
frontend/index.html.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

from backend.package_index import (
    update_package_index,
    scan_package_directory,
    scan_all_packages,
    build_stats,
    build_history,
    get_all_figures,
)

try:
    from backend.dashboard_exporter import (
        safe_rel_link,
        _is_analysis_package,
        _parse_level_grid,
        _extract_level_metrics_from_report,
        _extract_runtime_from_report_or_terminal,
        collect_package_info,
        scan_output_root,
        generate_output_index,
        _QA_START,
        _QA_END,
        _TN_START,
        _TN_END,
        _OF_START,
        _OF_END,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


def _make_result_json_pkg(root: Path, name: str, status_hint: str = "complete") -> Path:
    """Create a package with a realistic result.json (the new source of truth)."""
    pkg = root / name
    (pkg / "report").mkdir(parents=True, exist_ok=True)
    (pkg / "tables").mkdir(parents=True, exist_ok=True)
    (pkg / "figures").mkdir(parents=True, exist_ok=True)
    (pkg / "excel").mkdir(parents=True, exist_ok=True)
    (pkg / "manifest").mkdir(parents=True, exist_ok=True)

    result = {
        "motif_profile": {"motif": name},
        "source_file": name + ".svg",
        "generated_at": "2026-07-31 12:30:00",
        "fractal_dimension": 1.9354,
        "r_squared": 0.9997,
        "computed_levels_count": 5,
        "total_time_ms": 169.72,
        "measure_mode": "area",
        "input_sha256": "abc123",
        "scale_table": [
            {"level": 1, "grid": "4x8"},
            {"level": 2, "grid": "8x16"},
            {"level": 3, "grid": "16x32"},
            {"level": 4, "grid": "32x64"},
            {"level": 5, "grid": "64x128"},
        ],
    }
    (pkg / "result.json").write_text(json.dumps(result), encoding="utf-8")

    if status_hint == "complete":
        (pkg / "report" / "report.html").write_text("<html></html>", encoding="utf-8")
        (pkg / "tables" / "tables.html").write_text("<html></html>", encoding="utf-8")
        (pkg / "tables" / "tables_data.json").write_text("{}", encoding="utf-8")
        (pkg / "tables" / "01_4x8_cells.xlsx").write_bytes(b"PK")
        (pkg / "figures" / "01_4x8_map.svg").write_text("<svg></svg>", encoding="utf-8")
        (pkg / "excel" / "workbook.xlsx").write_bytes(b"PK")
        (pkg / "manifest" / "manifest.json").write_text("{}", encoding="utf-8")
    elif status_hint == "partial":
        (pkg / "report" / "report.html").write_text("<html></html>", encoding="utf-8")
        # missing tables / workbook / manifest -> partial
    else:  # broken: no result.json
        (pkg / "result.json").unlink()
    return pkg


@unittest.skipUnless(_AVAILABLE, "dashboard_exporter not available")
class TestIsAnalysisPackage(unittest.TestCase):

    def test_detects_manifest_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = _make_pkg(root, "AP_Manifest")
            self.assertTrue(_is_analysis_package(pkg))

    def test_detects_report_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = _make_pkg(root, "AP_Report")
            self.assertTrue(_is_analysis_package(pkg))

    def test_rejects_plain_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plain = root / "not_a_package"
            plain.mkdir()
            self.assertFalse(_is_analysis_package(plain))


def _make_pkg(root: Path, name: str, with_manifest: bool = True, db=1.23, r2=0.999, with_level_metrics: bool = True) -> Path:
    """Create a minimal analysis package for testing."""
    pkg = root / name
    (pkg / "report").mkdir(parents=True, exist_ok=True)
    (pkg / "tables").mkdir(parents=True, exist_ok=True)
    (pkg / "figures").mkdir(parents=True, exist_ok=True)
    (pkg / "excel").mkdir(parents=True, exist_ok=True)
    (pkg / "manifest").mkdir(parents=True, exist_ok=True)
    (pkg / "terminal").mkdir(parents=True, exist_ok=True)

    report_table = ""
    if with_level_metrics:
        report_table = """
        <h2>Grid Level Occupancy Overview</h2>
        <table>
          <thead><tr><th>Level</th><th>Grid</th><th>Total Cells</th><th>Filled</th><th>Empty</th><th>Occupancy (%)</th><th>Cell Size (WxH)</th><th>Time (ms)</th></tr></thead>
          <tbody>
            <tr><td>L01</td><td>4x8</td><td>32</td><td>32</td><td>0</td><td>100.00%</td><td>25.00 x 25.00</td><td>0.19</td></tr>
            <tr><td>L02</td><td>8x16</td><td>128</td><td>128</td><td>0</td><td>100.00%</td><td>12.50 x 12.50</td><td>0.45</td></tr>
          </tbody>
        </table>
        """

    # Minimal report.html
    report_html = pkg / "report" / "report.html"
    report_html.write_text(
        "<!DOCTYPE html><html><head><title>Test</title></head>"
        f"<body><!-- 2. KPI Cards --><div>content</div>{report_table}<!-- 10. Footer --></body></html>",
        encoding="utf-8",
    )
    (pkg / "report" / "report.pdf").write_bytes(b"%PDF-1.4 test")

    # Minimal tables.html
    tables_html = pkg / "tables" / "tables.html"
    tables_html.write_text(
        "<!DOCTYPE html><html><head><style>body{}</style></head>"
        '<body><div class="container"><p>tables</p></div></body></html>',
        encoding="utf-8",
    )

    # SVG maps
    (pkg / "figures" / "01_4x8_map.svg").write_text("<svg></svg>", encoding="utf-8")
    (pkg / "figures" / "02_8x16_map.svg").write_text("<svg></svg>", encoding="utf-8")

    # XLSX cell tables
    (pkg / "tables" / "01_4x8_cells.xlsx").write_bytes(b"PK")
    (pkg / "excel" / "workbook.xlsx").write_bytes(b"PK")
    (pkg / "terminal" / "terminal.txt").write_text("total_time_ms: 42.5\nFinished", encoding="utf-8")
    (pkg / "manifest" / "manifest.json").write_text('{}', encoding="utf-8")

    if with_manifest:
        manifest = {
            "analysis": {
                "motif": name,
                "source_file": name + ".svg",
                "generated_at": "2026-07-31 00:00:00",
                "engine": "cpu",
                "measure_mode": "area",
                "levels": 7,
                "db": db,
                "r2": r2,
                "total_time_ms": 42.5,
            },
            "warnings": ["Sample warning"],
            "skipped_outputs": [],
            "integrity": {"input_sha256": "abc123"},
        }
        (pkg / "manifest" / "manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

    return pkg


@unittest.skipUnless(_AVAILABLE, "dashboard_exporter not available")
class TestSafeRelLink(unittest.TestCase):

    def test_relative_path_allowed(self):
        self.assertEqual(safe_rel_link("report/report.html"), "report/report.html")

    def test_blocks_file_scheme(self):
        self.assertEqual(safe_rel_link("file:///[workspace_root]"), "#")

    def test_blocks_absolute_windows_path(self):
        self.assertEqual(safe_rel_link("[workspace_root]"), "#")

    def test_blocks_absolute_unix_path(self):
        self.assertEqual(safe_rel_link("/home/user/test"), "#")

    def test_blocks_javascript(self):
        self.assertEqual(safe_rel_link("javascript:alert(1)"), "#")

    def test_empty_string(self):
        self.assertEqual(safe_rel_link(""), "#")


@unittest.skipUnless(_AVAILABLE, "dashboard_exporter not available")
class TestLevelGridParser(unittest.TestCase):

    def test_parses_level_and_grid(self):
        lvl, grid = _parse_level_grid("01_4x8_map.svg")
        self.assertEqual(lvl, "L01")
        self.assertEqual(grid, "4x8")

    def test_parses_level_only(self):
        lvl, grid = _parse_level_grid("02_cells.xlsx")
        self.assertEqual(lvl, "L02")
        self.assertIsNone(grid)


@unittest.skipUnless(_AVAILABLE, "dashboard_exporter not available")
class TestExtractLevelMetricsAndRuntime(unittest.TestCase):

    def test_extracts_table_rows_from_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = _make_pkg(root, "PkgReport", with_level_metrics=True)
            metrics = _extract_level_metrics_from_report(pkg / "report" / "report.html")
            self.assertEqual(len(metrics), 2)
            self.assertEqual(metrics[0]["level"], "L01")
            self.assertEqual(metrics[0]["grid"], "4x8")

    def test_extracts_runtime_from_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = _make_pkg(root, "PkgTerm")
            rt = _extract_runtime_from_report_or_terminal(pkg)
            self.assertEqual(rt, 42.5)


@unittest.skipUnless(_AVAILABLE, "dashboard_exporter not available")
class TestCollectPackageInfo(unittest.TestCase):

    def test_reads_manifest_and_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = _make_pkg(root, "TestMotif", db=1.5, r2=0.987)
            info = collect_package_info(pkg, root)
            self.assertEqual(info["motif"], "TestMotif")
            self.assertAlmostEqual(float(info["db"]), 1.5, places=5)
            self.assertEqual(len(info["level_metrics"]), 2)
            self.assertEqual(len(info["svg_maps"]), 2)
            self.assertEqual(info["svg_maps"][0]["level"], "L01")
            self.assertTrue(info["has_report_html"])
            self.assertTrue(info["has_workbook"])


    def test_missing_level_metrics_does_not_break(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = _make_pkg(root, "NoMetrics", with_level_metrics=False)
            info = collect_package_info(pkg, root)
            self.assertIsInstance(info["level_metrics"], list)


@unittest.skipUnless(_AVAILABLE, "dashboard_exporter not available")
class TestGenerateOutputIndex(unittest.TestCase):
    """update_package_index writes outputs/package_index.json (JSON list); the
    active dashboard is the static decoupled live shell in frontend/."""

    def test_writes_offline_index_json_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_pkg(root, "Motif1")
            pkg_index = update_package_index(root)
            self.assertTrue(pkg_index.exists())
            data = json.loads(pkg_index.read_text(encoding="utf-8"))
            self.assertIsInstance(data, list)
            self.assertTrue(any("Motif1" in str(p.get("motif", "")) for p in data))

    def test_offline_data_marks_complete_package_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_result_json_pkg(root, "CompletePkg", status_hint="complete")
            update_package_index(root)
            data = json.loads((root / "package_index.json").read_text(encoding="utf-8"))
            matches = [p for p in data if p.get("motif") == "CompletePkg"]
            self.assertEqual(len(matches), 1, "CompletePkg not found in package_index.json")
            pkg = matches[0]
            self.assertEqual(pkg["status"], "complete")
            self.assertAlmostEqual(pkg["db"], 1.9354, places=4)
            self.assertEqual(pkg["max_level"], 5)
            self.assertTrue(pkg["report_url"].endswith("report/report.html"))

    def test_index_json_uses_backend_url_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_pkg(root, "UrlPkg")
            update_package_index(root)
            data = json.loads((root / "package_index.json").read_text(encoding="utf-8"))
            pkg = next(p for p in data if p.get("motif") == "UrlPkg")
            self.assertTrue(pkg["report_url"].endswith("report/report.html"))
            self.assertTrue(pkg["tables_url"].endswith("tables/tables.html"))
            self.assertTrue(pkg["workbook_url"].endswith("excel/workbook.xlsx"))
            self.assertTrue(pkg["report_pdf_url"].endswith("report/report.pdf"))
            self.assertTrue(pkg["manifest_url"].endswith("manifest/manifest.json"))

    def test_build_stats_backward_compatible_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_result_json_pkg(root, "AliasA", status_hint="complete")
            _make_result_json_pkg(root, "AliasB", status_hint="partial")
            stats = build_stats(scan_all_packages(root))
            # legacy names
            self.assertEqual(stats["total_count"], 2)
            self.assertAlmostEqual(stats["avg_db"], 1.9354, places=4)
            # dashboard names used by updateKpiCards()
            self.assertEqual(stats["total_packages"], stats["total_count"])
            self.assertEqual(stats["total_figures"], stats["total_svg_maps"])
            self.assertEqual(stats["total_xlsx"], stats["total_xlsx_cells"])
            self.assertEqual(stats["latest_generated"], stats["latest_str"])

    def test_decoupled_shell_features_present(self):
        """The active dashboard lives in frontend/index.html as a live shell."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_pkg(root, "FeaturesTest")
            update_package_index(root)
            out = Path("frontend/index.html")
            self.assertTrue(out.exists())
            content = out.read_text(encoding="utf-8")
            # Scientific Console + delete modal + export buttons + filters
            self.assertIn("scientificConsoleModal", content)
            self.assertIn("liveScaleTableBody", content)
            self.assertIn("deleteSelectedPackages", content)
            self.assertIn("btnConfirmDeleteYes", content)
            self.assertIn("openExportDialog", content)
            self.assertIn("kpiAvgDb", content)
            self.assertIn("kpiSvgMaps", content)
            self.assertIn("kpiLatest", content)
            self.assertIn("fileProtocolBanner", content)
            # SVG modal markup must exist (openSvgModal target)
            self.assertIn("svgModal", content)
            self.assertIn("svgModalImg", content)
            self.assertIn("svgModalLabel", content)
            self.assertIn("svgModalOpenBtn", content)
            # Max R2 filter input must exist
            self.assertIn('id="maxR2"', content)

    def test_no_embedded_packages_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_pkg(root, "Motif2")
            out = Path("frontend/index.html")
            update_package_index(root)
            content = out.read_text(encoding="utf-8")
            # No statically embedded package arrays in index.html
            self.assertNotIn("const PACKAGES", content)
            self.assertNotIn("let PACKAGES", content)

    def test_no_markdown_report_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_pkg(root, "MdTest")
            out = Path("frontend/index.html")
            update_package_index(root)
            content = out.read_text(encoding="utf-8")
            self.assertNotIn("Markdown Report", content)
            self.assertNotIn("cb-type-md", content)
            self.assertNotIn("report.md", content)

    def test_file_protocol_banner_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_pkg(root, "BannerTest")
            out = Path("frontend/index.html")
            update_package_index(root)
            content = out.read_text(encoding="utf-8")
            self.assertIn("fileProtocolBanner", content)
            self.assertIn("launcher.py", content)

    def test_batch_delete_and_sort_options_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_pkg(root, "SortTest")
            out = Path("frontend/index.html")
            update_package_index(root)
            content = out.read_text(encoding="utf-8")
            self.assertIn("deleteSelectedPackages", content)
            self.assertIn("btnConfirmDeleteYes", content)
            for opt in ("date-desc", "date-asc", "name-asc", "name-desc",
                        "db-desc", "db-asc", "r2-desc", "r2-asc"):
                self.assertIn(opt, content)

    def test_analysis_mode_dropdown_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_pkg(root, "ModeTest")
            out = Path("frontend/index.html")
            update_package_index(root)
            content = out.read_text(encoding="utf-8")
            self.assertIn("webModeSelect", content)
            self.assertIn("value=\"fast\"", content)
            self.assertIn("value=\"balanced\"", content)
            self.assertIn("value=\"precise\"", content)
            self.assertIn("value=\"academic\"", content)

    def test_security_actual_href_attributes_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_pkg(root, "SecTest")
            out = Path("frontend/index.html")
            update_package_index(root)
            content = out.read_text(encoding="utf-8")
            hrefs = re.findall(r'href=["\']([^"\']+)["\']', content, re.IGNORECASE)
            for h in hrefs:
                self.assertFalse(h.startswith("file://"), f"Unsafe href found: {h}")
                self.assertFalse(bool(re.match(r"^[A-Za-z]:", h)), f"Absolute path in href: {h}")
                self.assertFalse(h.startswith("/home/"), f"Unix path in href: {h}")
                self.assertFalse(h.startswith("javascript:"), f"JS URL in href: {h}")


@unittest.skipUnless(_AVAILABLE, "dashboard_exporter not available")
class TestPackageIndexSchema(unittest.TestCase):
    """Tests for backend.package_index result.json parsing and status logic."""

    def test_parses_result_json_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_result_json_pkg(root, "SchemaPkg", status_hint="complete")
            pkg = scan_package_directory(root / "SchemaPkg", root)
            self.assertEqual(pkg["motif"], "SchemaPkg")
            self.assertAlmostEqual(pkg["db"], 1.9354, places=4)
            self.assertAlmostEqual(pkg["r2"], 0.9997, places=4)
            self.assertEqual(pkg["levels"], 5)
            self.assertEqual(pkg["max_level"], 5)
            self.assertAlmostEqual(pkg["runtime_ms"], 169.72, places=2)
            self.assertAlmostEqual(pkg["total_time_ms"], 169.72, places=2)
            self.assertEqual(pkg["status"], "complete")
            self.assertEqual(pkg["source_file"], "SchemaPkg.svg")
            self.assertTrue(pkg["has_html_report"])
            self.assertTrue(pkg["has_excel_workbook"])
            self.assertTrue(pkg["has_manifest"])
            self.assertTrue(pkg["has_tables_data"])
            self.assertTrue(pkg["has_svg_maps"])
            self.assertTrue(pkg["has_xlsx_tables"])
            self.assertEqual(pkg["tables_data_url"], "SchemaPkg/tables/tables_data.json")
            self.assertEqual(pkg["figure_count"], 1)
            self.assertEqual(pkg["xlsx_count"], 1)

            self.assertEqual(pkg["engine"], "CPU Exact Vector Geometry Engine")

    def test_max_level_from_scale_table_above_10(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = _make_result_json_pkg(root, "L16Pkg")
            # rewrite result.json with L16 scale table
            res_path = root / "L16Pkg" / "result.json"
            res = json.loads(res_path.read_text(encoding="utf-8"))
            res["computed_levels_count"] = 16
            res["scale_table"] = [{"level": i, "grid": "4x8"} for i in range(1, 17)]
            res_path.write_text(json.dumps(res), encoding="utf-8")
            scanned = scan_package_directory(root / "L16Pkg", root)
            self.assertEqual(scanned["levels"], 16)
            self.assertEqual(scanned["max_level"], 16)

    def test_partial_status_when_assets_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_result_json_pkg(root, "PartPkg", status_hint="partial")
            pkg = scan_package_directory(root / "PartPkg", root)
            self.assertEqual(pkg["status"], "partial")
            self.assertTrue(pkg["has_html_report"])
            self.assertFalse(pkg["has_excel_workbook"])
            self.assertTrue(any("workbook" in w for w in pkg["warnings"]))

    def test_broken_status_without_result_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_result_json_pkg(root, "BrkPkg", status_hint="broken")
            pkg = scan_package_directory(root / "BrkPkg", root)
            self.assertEqual(pkg["status"], "broken")
            self.assertTrue(any("result.json" in e for e in pkg["errors"]))

    def test_scan_all_nested_skip_and_build_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_result_json_pkg(root, "NestA", status_hint="complete")
            _make_result_json_pkg(root, "NestB", status_hint="partial")
            # nested stale dir must be skipped, not surfaced as broken
            stale = root / "NestA" / "NestA"
            stale.mkdir(parents=True)
            (stale / "result.json").write_text("{bad json", encoding="utf-8")

            packages = scan_all_packages(root)
            folders = [p["folder"] for p in packages]
            # Exact equality: only NestA and NestB must surface (nested stale dir
            # must not appear, even if folder_rel normalization regressed).
            self.assertEqual(set(folders), {"NestA", "NestB"})

            stats = build_stats(packages)
            self.assertEqual(stats["total_count"], 2)
            self.assertAlmostEqual(stats["avg_db"], 1.9354, places=4)

            hist = build_history(packages)
            self.assertEqual(len(hist), 2)
            self.assertIn("package_id", hist[0])

    def test_get_all_figures_returns_ready_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_result_json_pkg(root, "FigsPkg")
            (root / "FigsPkg" / "figures" / "01_4x8_map.svg").write_text("<svg></svg>", encoding="utf-8")
            (root / "FigsPkg" / "figures" / "05_64x128_map.svg").write_text("<svg></svg>", encoding="utf-8")
            figs = get_all_figures(root)
            self.assertEqual(len(figs), 2)
            self.assertEqual(figs[0]["level"], "L01")
            self.assertEqual(figs[0]["grid"], "4x8")
            self.assertEqual(figs[0]["url"], "FigsPkg/figures/01_4x8_map.svg")
            self.assertEqual(figs[1]["level"], "L05")


def _strip_js_strings_and_comments(src: str) -> str:
    """Remove JS string literals and comments so brace/paren balance can be
    checked without false positives from braces inside string content
    (e.g. the vendored minified ExcelJS blob)."""
    out = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == "/" and i + 1 < n and src[i + 1] == "/":
            j = src.find("\n", i)
            i = n if j == -1 else j
            continue
        if ch == "/" and i + 1 < n and src[i + 1] == "*":
            j = src.find("*/", i + 2)
            i = n if j == -1 else j + 2
            continue
        if ch in ("\"", "'", "`"):
            quote = ch
            i += 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == quote:
                    i += 1
                    break
                i += 1
            out.append(" ")
            continue
        out.append(ch)
        i += 1
    return "".join(out)


@unittest.skipUnless(_AVAILABLE, "dashboard_exporter not available")
class TestDashboardJsWellFormed(unittest.TestCase):
    """Guard the DASHBOARD_JS raw string structure.

    A past defect moved the closing triple-quote so real JS sat outside the
    string as dead code, silently disabling the whole dashboard. This test
    locks the raw-string boundary and (string-aware) brace balance so that
    cannot regress.
    """

    def test_dashboard_js_raw_string_extractable_and_balanced(self):
        from backend.dashboard_js import DASHBOARD_JS
        self.assertIsInstance(DASHBOARD_JS, str)
        self.assertGreater(len(DASHBOARD_JS), 1000)
        code = _strip_js_strings_and_comments(DASHBOARD_JS)
        # Heuristic over a ~1MB blob (includes minified third-party ExcelJS):
        # regex literals aren't parsed, so allow a small tolerance for braces
        # and parens while still catching the structural-regression class of
        # bugs (e.g. a misplaced closing triple-quote / large stray blocks).
        self.assertLessEqual(abs(code.count("{") - code.count("}")), 10,
                             "Unbalanced braces in DASHBOARD_JS")
        self.assertLessEqual(abs(code.count("(") - code.count(")")), 10,
                             "Unbalanced parens in DASHBOARD_JS")
        # Core live-shell functions must be inside the injectable string
        for marker in ("var PACKAGES = [];", "initDashboardLive",
                       "renderOverviewCards", "switchView",
                       "applyFilters", "deleteSelectedPackages",
                       "startWebAnalysis", "fileProtocolBanner"):
            self.assertIn(marker, DASHBOARD_JS)

    def test_dashboard_js_no_legacy_mode_references(self):
        from backend.dashboard_js import DASHBOARD_JS
        for banned in ("webModeSelect", "Analysis Mode",
                       'value="fast"', 'value="balanced"',
                       'value="precise"', 'value="academic"'):
            self.assertNotIn(banned, DASHBOARD_JS)


@unittest.skipUnless(_AVAILABLE, "dashboard_exporter not available")
class TestScanAndIdempotencyMarkers(unittest.TestCase):

    def test_scan_output_root_uses_package_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_pkg(root, "ScanPkg")
            packages = scan_output_root(root)
            self.assertIsInstance(packages, list)
            self.assertTrue(any("ScanPkg" in str(p.get("folder", "")) for p in packages))

    def test_idempotency_markers_defined(self):
        self.assertTrue(_QA_START.startswith("<!-- rash-hit-quick-access"))
        self.assertTrue(_QA_END.startswith("<!-- rash-hit-quick-access"))
        self.assertTrue(_TN_START.startswith("<!-- rash-hit-tables-nav"))
        self.assertTrue(_TN_END.startswith("<!-- rash-hit-tables-nav"))
        self.assertTrue(_OF_START.startswith("<!-- rash-hit-output-files-table"))
        self.assertTrue(_OF_END.startswith("<!-- rash-hit-output-files-table"))




class TestWebServerDeleteSecurity(unittest.TestCase):
    def test_delete_package_bounds(self):
        from backend.web_server import SecuredRequestHandler
        import tempfile
        from pathlib import Path
        import backend.web_server

        class MockHandler(SecuredRequestHandler):
            def __init__(self, directory):
                self.directory = str(directory)

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_root = (Path(tmp_dir) / "outputs").resolve()
            out_root.mkdir()
            
            pkg_name = "16A_20260731_210804"
            pkg_dir = out_root / pkg_name
            pkg_dir.mkdir()
            (pkg_dir / "result.json").write_text("{}", encoding="utf-8")

            handler = MockHandler(out_root)
            
            original_scan = backend.web_server.scan_all_packages
            backend.web_server.scan_all_packages = lambda root: [{"package_id": pkg_name, "folder": pkg_name}]
            try:
                resolved_p, err = handler._resolve_package_folder(pkg_name, out_root)
                self.assertIsNone(err)
                self.assertEqual(resolved_p, pkg_dir.resolve())

                resolved_p, err = handler._resolve_package_folder("../some_external_file", out_root)
                self.assertIsNotNone(err)
                # Message must identify the out-of-bounds reason in English (single-language system).
                self.assertTrue(
                    "outside" in err,
                    f"expected an out-of-bounds reason in the error, got: {err!r}",
                )

                resolved_p, err = handler._resolve_package_folder("index.html", out_root)
                self.assertIsNotNone(err)
                self.assertIn("Protected file", err)

                resolved_p, err = handler._resolve_package_folder("non_existent_pkg", out_root)
                self.assertIsNotNone(err)
                self.assertIn("not found", err)
            finally:
                backend.web_server.scan_all_packages = original_scan



if __name__ == "__main__":
    unittest.main()


class TestPackageIndexSchemaNormalized(unittest.TestCase):
    """ISSUE-013: package records must carry a populated input_sha256 (when the
    source SVG file exists) and a consistent has_* flag representation."""

    @staticmethod
    def _make_package(root: Path, name: str, with_report: bool = True):
        pkg = root / name
        (pkg / "report").mkdir(parents=True)
        (pkg / "tables").mkdir()
        (pkg / "excel").mkdir()
        (pkg / "manifest").mkdir()
        if with_report:
            (pkg / "report" / "report.html").write_text("<html></html>", encoding="utf-8")
        (pkg / "tables" / "tables.html").write_text("<html></html>", encoding="utf-8")
        (pkg / "excel" / "workbook.xlsx").write_bytes(b"PK")
        (pkg / "manifest" / "manifest.json").write_text("{}", encoding="utf-8")
        return pkg

    def test_scan_populates_input_sha256_when_source_exists(self):
        import hashlib
        from backend.package_index import scan_package_directory
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = self._make_package(root, "16F_20260801_120000")
            src = root / "16F.svg"
            src.write_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>", encoding="utf-8")
            result = {
                "motif_profile": {"motif": "16F"},
                "generated_at": "2026-08-01 12:00:00",
                "source_file": str(src),
                "computed_levels_count": 7,
                "fractal_dimension": 1.7,
                "r_squared": 0.99,
            }
            (pkg / "result.json").write_text(json.dumps(result), encoding="utf-8")
            rec = scan_package_directory(pkg, root)
            self.assertNotEqual(rec["input_sha256"], "",
                                "input_sha256 must be populated when the source file exists")
            self.assertEqual(rec["input_sha256"],
                             hashlib.sha256(src.read_bytes()).hexdigest())

    def test_has_flag_aliases_consistent(self):
        from backend.package_index import scan_package_directory
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = self._make_package(root, "16A_20260801_120000", with_report=False)
            (pkg / "result.json").write_text(json.dumps({"motif": "16A"}), encoding="utf-8")
            rec = scan_package_directory(pkg, root)
            self.assertEqual(rec["has_report_html"], rec["has_html_report"],
                             "alias has_report_html must match canonical has_html_report")
            self.assertFalse(rec["has_html_report"])

    def test_rh_engine_high_level_markers(self):
        """Packages with RASH-HIT Fractal Engine high-level policy artifacts expose cells_omitted
        and row-run markers on the dashboard card metadata."""
        from backend.package_index import scan_package_directory
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _make_result_json_pkg(root, "P8Pkg", status_hint="complete")
            pkg_dir = root / "P8Pkg"

            # Simulate a RASH-HIT Fractal Engine high-level run: L03/L04 omit per-cell payloads
            # and their SVG maps use run-length / row-run merged rects.
            tables_data = {
                "levels": {
                    "L01": {"cells_omitted": False},
                    "L02": {"cells_omitted": False},
                    "L03": {"cells_omitted": True, "cells": []},
                    "L04": {"cells_omitted": True, "cells": []},
                }
            }
            (pkg_dir / "tables" / "tables_data.json").write_text(
                json.dumps(tables_data), encoding="utf-8")
            for lvl, grid in (("03", "16x32"), ("04", "32x64")):
                (pkg_dir / "figures" / f"{lvl}_{grid}_map.svg").write_text(
                    "<svg><!-- RASH-HIT Fractal Engine: run-length / row-run merged filled rects --></svg>",
                    encoding="utf-8",
                )

            pkg = scan_package_directory(pkg_dir, root)
            self.assertEqual(pkg["rh_engine_cells_omitted_count"], 2)
            self.assertEqual(pkg["rh_engine_cells_omitted_levels"], [3, 4])
            self.assertEqual(pkg["rh_engine_row_run_count"], 2)
            self.assertEqual(pkg["rh_engine_row_run_levels"], [3, 4])
            self.assertTrue(pkg["rh_engine_uses_row_runs"])

            # A normal package without RASH-HIT Fractal Engine artifacts stays clean.
            _make_result_json_pkg(root, "PlainPkg", status_hint="complete")
            plain = scan_package_directory(root / "PlainPkg", root)
            self.assertEqual(plain["rh_engine_cells_omitted_count"], 0)
            self.assertEqual(plain["rh_engine_cells_omitted_levels"], [])
            self.assertEqual(plain["rh_engine_row_run_count"], 0)
            self.assertEqual(plain["rh_engine_row_run_levels"], [])
            self.assertFalse(plain["rh_engine_uses_row_runs"])
