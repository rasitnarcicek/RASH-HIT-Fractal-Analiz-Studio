# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""
test_frontend_static_contract.py - Frontend static contract tests.

Verifies the decoupled dashboard wiring WITHOUT launching a browser:

1. Every getElementById(...) id referenced by frontend JS exists in frontend/index.html.
2. Every inline onclick / onchange / oninput handler maps to a defined JS function.
3. Required modal / control / console element ids are present (chkOverwrite, btnRunWeb,
   btnConsoleOpenFigures, selectionToolbar, liveScaleTableBody, consoleEventLog, ...).
4. fetch / XMLHttpRequest / axios are isolated to frontend/js/api.js.
5. Script order is correct (vendor -> api -> ui -> ... -> app).
6. Export functions are wired to the buttons that call them.
7. No outputs/index.html / legacy generation references leak into the active frontend.
8. CSS design tokens referenced by HTML classes exist in the stylesheets.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONT = ROOT / "frontend"
HTML_PATH = FRONT / "index.html"
ANALYSIS_HTML_PATH = FRONT / "analysis.html"
JS_DIR = FRONT / "js"
ANALYSIS_PAGE_JS_PATH = JS_DIR / "analysis-page.js"


def read_html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


def read_all_js() -> str:
    parts = []
    for p in sorted(JS_DIR.glob("*.js")):
        parts.append(p.read_text(encoding="utf-8"))
    return chr(10).join(parts)


def read_dashboard_js() -> str:
    """Dashboard JS only (excludes the standalone Analysis Studio controller,
    which targets analysis.html rather than index.html)."""
    parts = []
    for p in sorted(JS_DIR.glob("*.js")):
        if p.name == "analysis-page.js":
            continue
        parts.append(p.read_text(encoding="utf-8"))
    return chr(10).join(parts)


def html_ids() -> set:
    return set(re.findall(r'id="([a-zA-Z0-9_-]+)"', read_html()))


def js_ids(js: str | None = None) -> set:
    if js is None:
        js = read_all_js()
    ids = set()
    for marker in ("getElementById('", 'getElementById("'):
        idx = 0
        while True:
            pos = js.find(marker, idx)
            if pos < 0:
                break
            rest = js[pos + len(marker):]
            closing = rest.find("'") if marker.endswith("'") else rest.find('"')
            if closing > 0:
                ids.add(rest[:closing])
            idx = pos + len(marker)
    return ids


def inline_handlers(attr: str) -> set:
    html = read_html()
    return set(re.findall(attr + r'="([a-zA-Z0-9_]+)', html))


def js_function_names() -> set:
    # Scan JS files plus the inline <script> block in the HTML shell
    # (e.g. toggleTheme() is declared inline, not in a .js file).
    js = read_all_js()
    html = read_html()
    inline = "".join(re.findall(r"<script>(.*?)</script>", html, re.DOTALL))
    all_js = js + chr(10) + inline
    names = set(re.findall(r"function[ 	]+([a-zA-Z0-9_]+)", all_js))
    names |= set(re.findall(r"async[ 	]+function[ 	]+([a-zA-Z0-9_]+)", all_js))
    names |= set(re.findall(r"(?:const|let|var)[ 	]+([a-zA-Z0-9_]+)[ 	]*=", all_js))
    return names


class TestHtmlJsIdContract(unittest.TestCase):
    """Every id used by JS must exist in the HTML shell."""

    def test_all_js_ids_exist_in_html(self):
        # Dashboard JS only: the Analysis Studio controller targets analysis.html.
        missing = js_ids(read_dashboard_js()) - html_ids()
        self.assertEqual(missing, set(), "JS getElementById ids missing from HTML: " + str(missing))

    def test_analysis_page_js_ids_exist_in_analysis_html(self):
        self.assertTrue(ANALYSIS_HTML_PATH.exists(), "frontend/analysis.html must exist")
        self.assertTrue(ANALYSIS_PAGE_JS_PATH.exists(), "frontend/js/analysis-page.js must exist")
        ahtml = ANALYSIS_HTML_PATH.read_text(encoding="utf-8")
        ids = set(re.findall(r'id="([a-zA-Z0-9_-]+)"', ahtml))
        missing = js_ids(ANALYSIS_PAGE_JS_PATH.read_text(encoding="utf-8")) - ids
        self.assertEqual(missing, set(), "analysis-page.js ids missing in analysis.html: " + str(sorted(missing)))

    def test_required_control_ids_present(self):
        required = {
            "chkOverwrite", "btnRunWeb", "btnConsoleOpenFigures", "selectionToolbar",
            "liveScaleTableBody", "consoleEventLog", "btnTargetSingle", "btnTargetFolder",
            "btnBrowseTarget", "singleSvgInput", "folderBatchInput", "webLevelsInput",
            "webInputPath", "cardsGrid", "searchInput", "sortSelect",
            "scientificConsoleModal", "svgModal", "confirmDeleteModal",
            "consoleJobId", "consoleMode", "consoleStatusChip", "consoleProgressBar",
            "consoleStepsTimeline", "consoleRegressionCard", "consoleBatchQueueBody",
            "finalConsoleActions", "btnConsoleOpenReport", "btnConsoleOpenWorkbook",
            "btnConsoleOpenTables", "btnConsoleOpenManifest", "serverBadge", "emptyOverview",
            "kpiTotal", "kpiAvgDb", "kpiAvgR2", "kpiSvgMaps", "kpiXlsxTables", "kpiLatest",
        }
        present = html_ids()
        missing = required - present
        self.assertEqual(missing, set(), "Required control ids missing: " + str(missing))

    def test_modal_ids_have_open_mechanism(self):
        html = read_html()
        for modal_id in ("scientificConsoleModal", "svgModal", "confirmDeleteModal"):
            self.assertIn('id="' + modal_id + '"', html)
        css = (FRONT / "css" / "main.css").read_text(encoding="utf-8")
        self.assertIn(".modal.open", css)

    def test_overwrite_checkbox_present_and_unchecked(self):
        html = read_html()
        m = re.search(r'<input[^>]*id="chkOverwrite"[^>]*>', html)
        self.assertIsNotNone(m, "chkOverwrite input not found")
        self.assertNotIn("checked", m.group(0).lower())

    def test_start_button_initially_disabled(self):
        html = read_html()
        m = re.search(r'<button[^>]*id="btnRunWeb"[^>]*>', html)
        self.assertIsNotNone(m, "btnRunWeb button not found")
        self.assertIn("disabled", m.group(0))


class TestInlineHandlers(unittest.TestCase):
    """Every inline event handler must map to a defined JS function."""

    def setUp(self):
        self.html = read_html()
        self.funcs = js_function_names()

    def test_onclick_handlers_defined(self):
        handlers = inline_handlers("onclick")
        handlers.discard("event")  # event.stopPropagation() is not a function call
        missing = {h for h in handlers if h not in self.funcs}
        self.assertEqual(missing, set(), "onclick handlers missing function definitions: " + str(missing))

    def test_onchange_handlers_defined(self):
        handlers = inline_handlers("onchange")
        missing = {h for h in handlers if h not in self.funcs}
        self.assertEqual(missing, set(), "onchange handlers missing function definitions: " + str(missing))

    def test_oninput_handlers_defined(self):
        handlers = inline_handlers("oninput")
        missing = {h for h in handlers if h not in self.funcs}
        self.assertEqual(missing, set(), "oninput handlers missing function definitions: " + str(missing))

    def test_console_final_actions_wired(self):
        html = self.html
        for btn_id in ("btnConsoleOpenReport", "btnConsoleOpenTables",
                       "btnConsoleOpenWorkbook", "btnConsoleOpenFigures",
                       "btnConsoleOpenManifest"):
            self.assertIn('id="' + btn_id + '"', html)
        js = read_all_js()
        self.assertIn("btnConsoleOpenFigures", js)
        self.assertIn("figures_url", js)



class TestApiIsolation(unittest.TestCase):
    """Network calls must live only in frontend/js/api.js."""

    def test_fetch_only_in_api_js(self):
        offenders = []
        for p in sorted(JS_DIR.glob("*.js")):
            content = p.read_text(encoding="utf-8")
            if p.name == "api.js":
                continue
            for token in ("fetch(", "XMLHttpRequest", "axios"):
                if token in content:
                    offenders.append(p.name + ": contains " + token)
        self.assertEqual(offenders, [], "Network calls outside api.js: " + str(offenders))

    def test_api_js_defines_expected_endpoints(self):
        api = (JS_DIR / "api.js").read_text(encoding="utf-8")
        for endpoint in ("/api/health", "/api/jobs/", "/api/packages", "/api/stats",
                         "/api/packages/delete", "/api/upload-single", "/api/upload-batch"):
            self.assertIn(endpoint, api)


class TestScriptOrder(unittest.TestCase):
    """Script tags must load vendor libs before modules, api.js before consumers."""

    def test_script_order(self):
        html = read_html()
        order = re.findall(r'<script src="([^"]+)">', html)
        self.assertGreater(len(order), 5, "Expected multiple script tags, got: " + str(order))

        def _idx(name):
            return order.index(name)

        self.assertLess(_idx("vendor/exceljs.min.js"), _idx("js/export.js"))
        self.assertLess(_idx("vendor/FileSaver.min.js"), _idx("js/export.js"))
        self.assertLess(_idx("js/api.js"), _idx("js/export.js"))
        self.assertLess(_idx("js/api.js"), _idx("js/app.js"))

    def test_exceljs_vendor_files_exist(self):
        for name in ("exceljs.min.js", "FileSaver.min.js"):
            self.assertTrue((FRONT / "vendor" / name).is_file(), "vendor/" + name + " missing")

    def test_vendor_files_single_source(self):
        """ISSUE-006: vendored libs must live in exactly one place
        (frontend/vendor). The legacy backend/static/vendor copies are dead:
        the active server maps /vendor/* to frontend/, so a second copy would
        drift silently and double repo weight."""
        # The legacy backend/static tree (which only ever hosted duplicate
        # vendor copies) must not exist at all - no vendored lib may live
        # outside frontend/vendor.
        self.assertFalse(
            (ROOT / "backend" / "static").exists(),
            "legacy backend/static tree must not exist (duplicate vendor source)",
        )
        # The active frontend must reference only frontend/vendor.
        html = read_html()
        self.assertNotIn("backend/static/vendor", html)
        for name in ("vendor/exceljs.min.js", "vendor/FileSaver.min.js"):
            self.assertIn(name, html)


class TestExportWiring(unittest.TestCase):
    """Export dialog triggers must be backed by the ExcelJS exporter."""

    def test_open_export_dialog_defined_and_called(self):
        html = read_html()
        js = read_all_js()
        self.assertIn("openExportDialog(", js)
        # Every HTML onclick that invokes openExportDialog must exist verbatim,
        # and the function must be declared in the JS bundle.
        self.assertIn('onclick="openExportDialog(', html)
        self.assertGreater(html.count('onclick="openExportDialog('), 0)
        self.assertIn("function openExportDialog", js)

    def test_export_scopes_match_handlers(self):
        html = read_html()
        js = read_all_js()
        for scope in ("'current'", "'visible'", "'selected'"):
            self.assertIn(scope, html)
        self.assertIn("scope", js)
        self.assertIn("executeExcelExport", js)


class TestNoLegacyFrontendRefs(unittest.TestCase):
    """The active frontend must not reference the deprecated outputs/index.html flow."""

    def test_no_outputs_index_generation_refs(self):
        haystack = read_html() + chr(10) + read_all_js()
        for token in ("generate_output_index", "dashboard_js.py", "html_templates/index_template.py",
                      "outputs/index.html"):
            self.assertNotIn(token, haystack, "Legacy reference present in active frontend: " + token)

    def test_no_mock_fake_simulate_in_frontend(self):
        haystack = (read_html() + chr(10) + read_all_js()).lower()
        for token in ("mock", "fake", "simulate", "dummy"):
            self.assertNotIn(token, haystack, "Mock/fake artifact token in active frontend: " + token)


class TestCssClassBasics(unittest.TestCase):
    """CSS classes used by the HTML shell must exist in the stylesheets."""

    def setUp(self):
        css = ""
        for p in (FRONT / "css").glob("*.css"):
            css += p.read_text(encoding="utf-8")
        self.css = css

    def test_design_system_classes_defined(self):
        for cls in (".btn", ".btn-primary", ".btn-danger", ".btn-soft", ".btn-sm",
                    ".kpi-card", ".pkg-card", ".badge", ".badge-ok", ".badge-warn",
                    ".badge-missing", ".badge-version", ".console-modal-box",
                    ".console-status-panel", ".console-log", ".console-final-actions",
                    ".empty-state", ".overwrite-cb", ".modal", ".modal-box",
                    ".pkg-grid"):
            self.assertIn(cls, self.css, "CSS class " + cls + " not defined")

    def test_theme_tokens_defined(self):
        themes = (FRONT / "css" / "themes.css").read_text(encoding="utf-8")
        for token in ("--bg", "--panel", "--text", "--muted", "--border", "--accent",
                      "--accent2", "--soft", "--ok", "--warn", "--err"):
            self.assertIn(token, themes)

class TestDataTestIds(unittest.TestCase):
    """data-testid hooks must exist for stable test selectors.

    Playwright IS installed and tests/test_e2e_smoke.py drives Chromium
    headless against these hooks (package cards, view-mode radios, the details
    drawer, the export modal and the Scientific Console scale table). The
    hooks stay locked here statically so future e2e flows can target the same
    selectors without depending on CSS classes or visible text.
    """

    def setUp(self):
        self.html = read_html()
        self.pm_js = (JS_DIR / "package-manager.js").read_text(encoding="utf-8")

    def test_view_radio_testids_all(self):
        count = self.html.count('data-testid="view-radio"')
        # Library, Level Table, SVG Gallery, Package Files, Comparative Analysis,
        # Spatial Tables Viewer (Analysis Details was removed per the spec).
        self.assertEqual(count, 6, f"Expected 6 view-mode radio testids, found {count}")

    def test_drawer_testid(self):
        self.assertIn('id="drawer"', self.html)
        self.assertIn('data-testid="drawer"', self.html)

    def test_export_modal_testid(self):
        self.assertIn('id="exportModal"', self.html)
        self.assertIn('data-testid="export-modal"', self.html)
        for btn in ("export-close-btn", "export-cancel-btn", "export-confirm-btn"):
            self.assertIn('data-testid="' + btn + '"', self.html,
                          f"Missing data-testid {btn} in export modal")

    def test_selection_toolbar_testids(self):
        """Selection toolbar buttons (visible when packages are selected) must
        expose stable data-testid hooks for e2e flows."""
        self.assertIn('id="selectionToolbar"', self.html)
        for btn in ("sel-open-selected", "sel-export-selected", "sel-export-visible",
                    "sel-export-current", "sel-delete-selected", "sel-clear-selection"):
            self.assertIn('data-testid="' + btn + '"', self.html,
                          f"Missing selection toolbar testid {btn}")

    def test_svg_modal_testids(self):
        """SVG preview modal actions must expose data-testid hooks."""
        self.assertIn('id="svgModal"', self.html)
        for el in ("svg-open-full", "svg-close-btn"):
            self.assertIn('data-testid="' + el + '"', self.html,
                          f"Missing SVG modal testid {el}")

    def test_delete_modal_testids(self):
        """Deletion confirmation modal actions must expose data-testid hooks."""
        self.assertIn('id="confirmDeleteModal"', self.html)
        for btn in ("delete-cancel-btn", "delete-confirm-btn"):
            self.assertIn('data-testid="' + btn + '"', self.html,
                          f"Missing delete modal testid {btn}")

    def test_pkg_card_testid(self):
        self.assertIn('data-testid="pkg-card"', self.pm_js,
                      "renderOverviewView must emit data-testid=\"pkg-card\" on each card")

    def test_accordion_testids(self):
        for acc in ("acc-run", "acc-view", "acc-library", "acc-sections",
                    "acc-outputs", "acc-lvl", "acc-metrics", "acc-act"):
            self.assertIn('data-testid="' + acc + '"', self.html,
                          f"Missing accordion testid {acc}")

    def test_console_modal_testids(self):
        self.assertIn('data-testid="console-close-btn"', self.html)
        for btn in ("console-report-btn", "console-tables-btn", "console-workbook-btn",
                    "console-figures-btn", "console-manifest-btn"):
            self.assertIn('data-testid="' + btn + '"', self.html,
                          f"Missing console action testid {btn}")

    def test_sidebar_action_testids(self):
        # Simplified Actions panel: a single EXPORT button plus a contextual
        # Clear Selection (shown only when cards are selected). The removed
        # Apply/Reset/Select Visible/Refresh/Delete buttons are intentional.
        for btn in ("action-export", "action-clear-selection"):
            self.assertIn('data-testid="' + btn + '"', self.html,
                          f"Missing sidebar action testid {btn}")
        for removed in ("action-apply-filters", "action-reset-filters", "action-select-visible",
                        "action-refresh", "action-export-current", "action-export-selected",
                        "action-export-visible", "action-delete-selected"):
            self.assertNotIn('data-testid="' + removed + '"', self.html,
                              f"Removed action testid {removed} should no longer be present")

    def test_card_action_testids(self):
        """The slimmed-down card action set: Open Report, Open Folder and the
        hardcoded Details button. The removed per-artifact buttons must NOT
        reappear on the cards (artifacts live in the details drawer / files view)."""
        for btn in ("card-report-btn", "card-folder-btn", "card-details-btn"):
            self.assertIn(btn, self.pm_js,
                          f"Missing card action testid {btn}")
        for removed in ("card-pdf-btn", "card-tables-btn", "card-workbook-btn",
                        "card-figures-btn", "card-manifest-btn"):
            self.assertNotIn(removed, self.pm_js,
                             f"Removed card action testid {removed} must not exist")


class TestAnalysisStudio(unittest.TestCase):
    """The standalone Analysis Studio page must be wired to the dashboard nav
    and ship the controller needed for realtime runs + history."""

    def test_analysis_studio_page_exists(self):
        html = ANALYSIS_HTML_PATH.read_text(encoding="utf-8")
        self.assertIn('href="index.html"', html, "Analysis page must link back to the dashboard")
        self.assertIn('src="js/analysis-page.js"', html)
        for el in ("streamScaleBody", "jobHistoryList", "recentFilesList",
                   "webModeSelect", "webLevelsInput", "btnRunWeb",
                   "pkgDetailPanel", "pkgDetailBody"):
            self.assertIn('id="' + el + '"', html, f"Missing analysis page id {el}")

    def test_analysis_history_filters_present(self):
        """Advanced history panel: time-range + motif filters and per-job
        package delete must be wired on the Analysis Studio page."""
        html = ANALYSIS_HTML_PATH.read_text(encoding="utf-8")
        for el in ("jobTimeFilter", "jobMotifFilter"):
            self.assertIn('id="' + el + '"', html, f"Missing history filter id {el}")
        js = ANALYSIS_PAGE_JS_PATH.read_text(encoding="utf-8")
        for fn in ("applyJobFilters", "populateJobMotifFilter", "clearJobFilters",
                   "deleteJobPackage"):
            self.assertIn("function " + fn, js, f"Missing history controller function {fn}")
        self.assertIn("API.deletePackages", js,
                      "History delete must route through API.deletePackages")
        self.assertIn("data-testid=\"job-delete-btn\"", js,
                      "renderJobHistory must emit a data-testid=job-delete-btn hook")

    def test_dashboard_nav_links_to_analysis_studio(self):
        html = read_html()
        self.assertIn('href="analysis.html"', html,
                      "Dashboard nav must link to the Analysis Studio")

    def test_analysis_page_controller_wiring(self):
        js = ANALYSIS_PAGE_JS_PATH.read_text(encoding="utf-8")
        for fn in ("beginStreaming", "pollStream", "renderStreamScaleRows",
                   "refreshHistory", "refreshRecentFiles", "viewJob", "updateModeDefaultLevels",
                   "showPackageDetail", "closePackageDetail", "renderPackageDetail"):
            self.assertIn("function " + fn, js, f"Missing analysis controller function {fn}")
        self.assertIn("API.getJobs", js)
        self.assertIn("API.runSingleAnalysis", js)
        self.assertIn("API.runBatchAnalysis", js)
        self.assertIn("API.getPackage", js)


class TestOutputsPureData(unittest.TestCase):
    """outputs/ must remain a pure data repository (decoupled dashboard)."""

    def test_no_outputs_index_html(self):
        self.assertFalse((ROOT / "outputs" / "index.html").exists(),
                         "outputs/index.html must NOT be generated")

    def test_no_frontend_assets_in_outputs_root(self):
        out_root = ROOT / "outputs"
        for ext in ("*.html", "*.css", "*.js"):
            offenders = [f.name for f in out_root.glob(ext) if f.is_file()]
            self.assertEqual(offenders, [], f"outputs/ root must be pure data: {offenders}")

    def test_package_index_exists_and_is_valid(self):
        import json
        import tempfile
        # Build the fixture itself (no dependency on another test's side effect).
        # Use a throwaway isolated root so the real outputs/ is never touched.
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            pkg_dir = tmp_root / "16A"
            pkg_dir.mkdir(parents=True, exist_ok=True)
            (pkg_dir / "result.json").write_text(
                json.dumps({"package_id": "16A", "motif": "test"}), encoding="utf-8")
            from backend.package_index import update_package_index
            idx = update_package_index(tmp_root)
            self.assertTrue(idx.is_file(), "package_index.json not produced by update_package_index")
            data = json.loads(idx.read_text(encoding="utf-8"))
            self.assertIsInstance(data, list)

if __name__ == "__main__":
    unittest.main()


class TestModalA11yContract(unittest.TestCase):
    """ISSUE-011: dashboard modals must expose ARIA dialog semantics and
    restore focus on close (WCAG 2.2)."""

    def setUp(self):
        self.html = HTML_PATH.read_text(encoding="utf-8")
        self.js_all = "\n".join(
            p.read_text(encoding="utf-8")
            for p in sorted(JS_DIR.glob("*.js"))
        )

    def test_modals_have_dialog_roles(self):
        for modal_id in ("scientificConsoleModal", "svgModal", "confirmDeleteModal", "exportModal"):
            m = re.search(r'<div id="' + modal_id + r'"[^>]*>', self.html)
            self.assertIsNotNone(m, f"modal {modal_id} not found")
            self.assertIn('role="dialog"', m.group(0), f"{modal_id} missing role=dialog")
            self.assertIn('aria-modal="true"', m.group(0), f"{modal_id} missing aria-modal")

    def test_focus_restore_mechanism(self):
        self.assertIn("_prevFocus", self.js_all,
                      "modal open/close must track the previously focused element")
        self.assertIn(".focus()", self.js_all,
                      "modal close must restore focus to the previously focused element")

    def test_modal_focus_trap_present(self):
        """ISSUE-003: while a modal/drawer is open, Tab/Shift+Tab focus must be
        trapped (cycled) inside it and never leak to the page behind."""
        self.assertIn("trapFocusInModal", self.js_all,
                      "ui.js must define the focus trap entry point")
        self.assertIn("e.key !== 'Tab'", self.js_all,
                      "focus trap must act on the Tab key only")
        # Focusable-element selector must cover interactive controls so the
        # trap can compute the first/last boundary to cycle between.
        self.assertIn("a[href]", self.js_all, "focus trap must collect links")
        self.assertIn("button:not([disabled])", self.js_all,
                      "focus trap must collect enabled buttons")
        self.assertIn("input:not([disabled])", self.js_all,
                      "focus trap must collect enabled inputs")
        self.assertIn("[tabindex]", self.js_all,
                      "focus trap must respect tabindex controls")
        # Cycling behavior: first element reached backwards wraps to last, and
        # last element reached forwards wraps to first.
        self.assertIn("focusable[focusable.length - 1]", self.js_all,
                      "focus trap must wrap Tab from last to first")
        self.assertIn("focusable[0]", self.js_all,
                      "focus trap must wrap Shift+Tab from first to last")
        self.assertIn("e.preventDefault()", self.js_all,
                      "focus trap must prevent default Tab navigation")
        self.assertIn("addEventListener('keydown', trapFocusInModal)", self.js_all,
                      "focus trap must be wired to the keydown listener")
