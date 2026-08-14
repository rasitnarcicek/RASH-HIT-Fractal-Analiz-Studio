## [Release v1.0.6 — Parallel Adaptive Negative Space Ledger Engine & Final Cleanup] - 2026-08-04

### Added
- **Parallel Adaptive Negative Space Ledger Engine (Phase 8 & 8B)** (backend/intersection_hierarchical.py):
  - **Negative Space Ledger**: Prunes empty parent cells and carries empty block counts forward via exact descendant formulas (known_empty_contrib), saving up to 65%–71% of unnecessary GEOS predicate evaluations at high levels.
  - **No FULL Shortcut**: Preserves 100% exact mathematical cell counting; non-empty parents are subdivided and re-evaluated at every level.
  - **Hardware-Aware Multi-Threading**: _bulk_fill_decision dynamically partitions candidate cell arrays across ThreadPoolExecutor workers targeting ~85%–90% of available logical CPU threads (e.g. 17 threads on a 20-thread CPU).
  - Verified 5.3x overall speedup on L10 (66.6s -> 12.6s) and 67.1M cell L12 analysis in 64.6 seconds with 100% exact bit-for-bit parity match.
- **High-Level Output Policy**:
  - disable_raw_cell_indices_after_level = 8: Disables raw cell index arrays and Excel cell coordinate worksheets at +$.
  - force_svg_rle_after_level = 9 & svg_only_after_level = 9: Disables filled_set materialization at high levels and renders SVG maps using lightweight Run-Length Encoding (RLE) row-runs.
- **Permanent Integration Suite** (tests/test_fresh_outputs_processing.py):
  - Verifies output directory clearing, engine parity across 14 SVG motifs, pruning logic, level_callback execution, non-ASCII/Turkish filename slugs, and speed non-regression.

- **Playwright E2E regressions** (tests/test_e2e_smoke.py, +2): `test_console_scale_table_no_reference_error` injects a fake mid-flight job through the page context and asserts the Live Scale Table renders L01 done / L02 Computing…/RUNNING / L03 waiting with zero console errors (fails on the old undeclared-`computingLevel` code); `test_analysis_studio_page_loads_clean` loads `/analysis.html` and asserts the init flow completes with zero console errors.
- **Package-based Phase 8 NegSpace tooltip** (frontend/js/analysis-console.js + backend/web_server.py + frontend/index.html): the Scientific Console's NegSpace cells now carry a rich multi-line tooltip combining the per-level negative-space cache actuals (`negative_space_cached_cells`, `empty_parents_skipped`, candidate/active-parent counts, `cell_storage_mode`, `output_policy_note`) with the package-level Phase 8 policy summary (`phase8_cells_omitted_levels` / `phase8_row_run_levels`). `_build_final_package` and `_latest_package_snapshot` now surface those phase8 markers on `final_package` (new `_phase8_package_markers` helper reusing `package_index._collect_phase8_metadata`); the NegSpace `<th>` tooltip hints at the per-cell detail. Tests: `test_web_server_api.py::TestFinalPackageBuilder` gained `test_final_package_carries_phase8_markers` + `test_final_package_phase8_markers_default_clean`; the e2e console regression now asserts the tooltip content.
- **jsdom unit test for `renderConsoleScaleRows`** (tests/js/analysis-console-scale-rows.test.mjs + tests/test_js_console_scale_rows_unit.py + package.json `test:js` script): loads the real `frontend/js/analysis-console.js` source into jsdom (Node `node:test` runner) and proves the `Computing…` row placement contract derived from the `currentLevel` argument — L01 done / L02 Computing…/RUNNING / L03 waiting for `currentLevel=1` (the exact scenario the old undeclared-`computingLevel` ReferenceError broke), `currentLevel=0` marks L01, no Computing row on success/failure or when `currentLevel >= total`, real rows take precedence over the placeholder, and the NegSpace Phase 8 tooltip renders per-level + package markers. The pytest wrapper is `@unittest.skipUnless(node && jsdom)` (same pattern as the Playwright e2e suite); `npm run test:js` runs it standalone.
- **Dead-CSS audit test** (tests/test_dead_css_audit.py): every class selector in `frontend/css/main.css` must be referenced by the frontend (word-bounded scan across `frontend/*.html` + all `frontend/js/*.js`), with the reverse direction locking every HTML class to a CSS definition (incl. analysis.html's page-local `<style>` block). The audit immediately found and fixed **5 genuinely undefined classes**: `.badge-muted` (used by index.html + 3 JS files but styled nowhere), `.scale-table` (used by index.html/analysis.html/analysis-page.js but undefined), `.analysis-left`/`.analysis-right` (analysis.html grid columns) and `.history-filters` (previously inline-styled only). A `url()` stripper keeps SVG data-URI `www.w3.org/...` namespaces from being misread as classes (regression-locked).

### Fixed
- **Sanitized All Local Paths**: Removed local Windows absolute paths across codebase, active docs, and scripts (0 local paths remain).
- **Console Callback Offsets**: Aligned Scientific Console realtime scale table row rendering (computingLevel = currentLevel + 1) and added is-new flash row highlight animation (frontend/js/analysis-page.js, frontend/js/analysis-console.js).
- **CLI Progress Callback**: Wired _cli_level_cb in run_analysis.py for live per-level progress reporting.
- **`Uncaught ReferenceError: computingLevel is not defined`** (frontend/js/analysis-console.js): `renderConsoleScaleRows` read an undeclared `computingLevel`, so every job poll threw and the Scientific Console Live Scale Table stayed blank. The renderer now computes `computingLevel = currentLevel + 1` (mirrors analysis-page.js), so the in-flight "Computing…/RUNNING" row renders correctly.
- **Broken "Folder" button on the Analysis Studio page** (frontend/js/analysis-page.js): `openPackageFolder` was only defined in package-manager.js, which analysis.html does not load - the detail-panel button threw a ReferenceError on click. A page-local handler (routes through `API.openFolder`, falls back to a copyable path alert) now backs it.
- **Dead CSS rules + double checkbox tick** (frontend/css/main.css): removed unused `.sb-btn*`, `.kpi-card.kpi-ok/kpi-warn::before`, `.pkg-run`, `.occupancy-mini`, `.is-disabled`; deduplicated the duplicated select/checkbox styling blocks that rendered two overlapping checkmarks (old `::after` SVG tick + new `::before` CSS tick) on every checked box.
- **Dead `exportExcel()` alias** removed from frontend/js/export.js (no callers anywhere).
- **Job-poll error noise**: `console.error` in `pollJobStatus` now only surfaces under the `RASH_HIT_DEBUG_PERF` debug flag (500ms polling would otherwise spam transient failures).
- **`escapeHtml` typeof-guard** (frontend/js/analysis-page.js): the page-local copy can never clobber a copy another page loaded first.
- **Invisible Debug panel** (frontend/index.html + frontend/css/main.css): `#debugPanel` carried inline `style="display:none;"` (which always beats any class rule) and no `.debug-panel.open` display rule existed, so toggling the panel never made it visible. The inline style was removed and the panel now follows the modal/drawer pattern — `display:none` default + `.debug-panel.open { display: flex; }` (caught by `test_e2e_smoke.py::test_debug_panel_toggles_flag_and_lists_perf_entries`).

### Security & Compliance
- **Outputs Pure-Data Repository**: Preserved decoupled architecture (outputs/ contains strictly pure-data packages; outputs/index.html is never generated).
- **Default Overwrite Protection**: Maintained overwrite=False default across processor and API endpoints.
- **Zero Unexpected Skips**: 462 unit and integration tests passing 100% with no weakened assertions (the only skips are the optional dev-dependency suites — Playwright e2e and the new node+jsdom unit wrapper — which skip cleanly when those deps are absent).

## [Phase 8 Engine Performance: Early-Exit Fill & Object-Array Precompute] - 2026-08-03

### Changed
- **`backend/intersection_hierarchical.py` — `_bulk_fill_decision` now uses round-based early exit.** Profiling (cProfile) showed 88% of engine time goes to `shapely.intersects` — the exact GEOS predicate sent to every (cell, geom) pair the STRtree returns. Because the STRtree emits one pair per bbox-overlapping geometry, a cell covered by several overlapping geometries was being exact-tested once per geometry even though the first hit already determines it is filled. The fill pass now sorts pairs by cell and tests them in rounds: round 0 tests every cell's first pair, filled cells are dropped, and each later round tests only the next pair of the still-unfilled cells. This is exact (filled ⇔ any pair intersects) and cuts the number of GEOS predicate calls — the dominant cost at L9/L10+.
- The stroke pass now skips the STRtree query entirely when every cell is already filled (`not filled.all()` guard).
- Geometry object arrays (`fill_obj_arr` / `stroke_obj_arr`) are now precomputed once per analysis in `analyze_grid_hierarchical` and passed into `_bulk_fill_decision`, removing the per-level Python list-comp → object-array rebuild (previously ~0.2 s cumulative).

### Verified
- **Bit-for-bit equivalence**: filled masks identical to the old engine on every level of sparse (16.svg L9), dense (16D L7) and complex (16A L7) motifs; per-level filled counts on 16.svg L9 reproduce the pre-optimization live baseline exactly (L3=192 … L9=371,062) with identical Phase 8 negative-space metrics (859,936 cells pruned, 214,984 empty parents skipped).
- **Speedup (counting engine only)**: 16.svg L9 10.6 s → 7.5 s (**1.41×**); exact predicate tests cut from 1.40 M → 1.12 M. 16D L7 1.87 s → 1.37 s (**1.36×**), 16A L7 2.10 s → 1.64 s (**1.28×**).
- **New test** `TestBulkFillDecisionEarlyExit::test_early_exit_matches_naive_all_pairs` (`tests/test_phase8_negative_space_cache.py`): locks the invariant on deliberately overlapping fill geometries by comparing the round-based early-exit mask against a naive test-every-pair reference (bit-for-bit equal).
- Full suite: **352 passed, 36 skipped, 0 failed** (baseline was 351/36); `pyflakes` + `compileall` clean; `docs/test_checklist.md` count updated 387 → 388.

## [Batch Profile & `--batch-profile` CLI] - 2026-08-03

### Added
- **`batch` output profile** (`backend/output_profiles.py`): lean-derived profile that pulls the Phase 8 SVG-only gate down to **L9** (`svg_only_after_level = 9`), so L10+ batch packages keep their SVG maps while dropping per-cell Excel tables / cell payloads one level earlier — tuned for multi-SVG folder runs. Registered like the other profiles (`load_output_profile("batch")` works, `--profile batch` accepted).
- **`--batch-profile` CLI flag** (`run_analysis.py`): selects the output profile used **only** for `--batch` runs; takes precedence over `--profile` when both are given, falls back to `--profile` otherwise. `run_batch_analysis()` gained a `batch_profile` parameter (`batch_profile or profile` precedence).
- **Tests** (`tests/test_release_blockers.py`): registered-profile set now includes `batch`; `run_batch_analysis` signature checks `batch_profile`; new `test_batch_processor_forwards_batch_profile` locks the precedence (`batch_profile` > `profile`) via a mocked end-to-end batch call; new `test_batch_profile_gates_svg_only_at_l9` verifies `svg_only_after_level == 9`, lean-derived artifact switches, and the L9/L10 SVG-only boundary; CLI help exposes `--batch-profile`.

### Changed
- `README.md`: profile table now lists five profiles incl. `batch`; CLI section documents `--batch-profile` usage and precedence.
- `docs/architecture.md`: `output_profiles.py` entry updated to the five-profile set incl. `batch`.
- `docs/test_checklist.md`: test count updated (384 → 386).

### Verified
- `python -m pytest tests/test_release_blockers.py`: passes.

## [Phase 8 Package-Index Markers & Dashboard Card Chip] - 2026-08-03

### Added
- **Phase 8 markers on package records** (`backend/package_index.py`): `scan_package_directory` now reports `phase8_cells_omitted_count` / `phase8_cells_omitted_levels` (read from the authoritative `tables/tables_data.json` `levels.Lxx.cells_omitted` flags) and `phase8_row_run_count` / `phase8_row_run_levels` / `phase8_uses_row_runs` (detected from the `run-length / row-run merged` marker comment in each figure SVG). Both scans are defensive (malformed/missing artifacts are skipped), so legacy packages stay clean with zero counts.
- **Dashboard card chip**: `renderOverviewView()` shows an amber `Phase 8` badge on cards whose packages used the high-level output policy; the tooltip lists the omitted-cell level count and the row-run SVG level count. Styled via a new `badge-phase8` class in `frontend/css/main.css`.
- **Test**: `test_output_index_dashboard.py::test_phase8_high_level_markers` covers the marker extraction from a synthetic high-level package plus the clean zero-count case.

### Changed
- `README.md` (Output Dashboard feature table), `docs/frontend_components.md` (card chip), `docs/test_checklist.md` (386 → 387).

### Verified
- `python -m pyflakes backend/package_index.py` clean; `node --check frontend/js/package-manager.js` passes.

## [Code Quality Cleanup] - 2026-08-03

### Changed
- **`backend/export/html_templates/report_template.py`**: removed unused imports (`render_header`, `render_nav_dynamic`, `render_svg_modal`, `render_footer` from `components`) and the dead `report_link = "#"` local (leftover from the removed `report.md` quick-access link).
- **`backend/package_index.py`**: the 8KB figure-head read in `_collect_phase8_metadata` is now a named constant `_PHASE8_SVG_HEAD_BYTES` instead of a magic literal.

### Verified
- `python -m pyflakes backend/ run_analysis.py launcher.py`: **fully clean** (project lint scope) — the last remaining warnings are gone.
- Affected contract suites (report template / full project / output index / academic engine / docs): 97 passed.

## [Repository Structure Consolidation] - 2026-08-03

### Changed (layout only — behavior, CLI, API and package artifacts unchanged)
- **`backend/export/` subpackage**: the academic HTML template builders moved from `backend/html_templates/` to `backend/export/html_templates/` (`components.py`, `report_template.py`, `tables_template.py`, `theme_css.py`), grouping all output-generation code under one clear subtree. Imports updated in `academic_exporter.py`, the templates themselves, `archive/legacy_dashboard/index_template.py`, and the affected contract tests (`test_report_template_contract.py`, `test_frontend_restoration.py`, `test_full_project_contract.py`).
- **`scripts/atlas/` subfolder**: 17 one-off audit/atlas/perf tooling scripts (`_atlas_*.py`, `_concat_backend.py`, `_perf_pack.py`, `_venti_profiled_intersection.py`, `_zip_pack.py`) consolidated under `scripts/atlas/`; `scripts/validate_citation.py` stays at the top level. Their `ROOT`/`BASE` path depth was corrected for the new nesting and `_venti_profiled_intersection.py` gained a project-root `sys.path` bootstrap.
- Docs updated to the new layout: `README.md` (Key Architecture), `docs/architecture.md`, `docs/code_atlas.md`.

### Verified
- `python -m pytest tests/`: **348 passed, 36 pre-existing skipped, 0 failed** (384 collected).
- `python -m compileall backend tests scripts run_analysis.py launcher.py`: 0 errors; moved modules import cleanly (`backend.export.html_templates.*`, `backend.academic_exporter`, `backend.processor`).
- Moved atlas scripts resolve the project root correctly (verified `_atlas_assets`, `_concat_backend`, `_perf_pack`).
- `npm run lint` scope (`backend/`, `run_analysis.py`, `launcher.py`) stays clean.

## [Full System Audit & Documentation Refresh] - 2026-08-03

### Fixed
- **Dead `--profile` CLI flag** (`run_analysis.py`): the flag previously accepted non-existent profiles (`standard`/`full` would raise from `load_output_profile`, `reproducible` was rejected by argparse) and was never forwarded to the engine. Now: choices are the real registered profiles (`lean`/`reproducible`/`debug`/`presentation`), `AnalysisProcessor` and `run_batch_analysis` accept a `profile` parameter (default `lean`), and `--profile` is threaded end-to-end for both single and batch runs.
- **Stale version banner**: `run_analysis.py` printed `v1.0.0`; now `v1.0.5` (matches package.json / CITATION / api health).
- **Dead acceleration choice**: `run_analysis.py` accepted unsupported engine choices but no hardware acceleration engine exists; choices are now `cpu` only.
- **`/favicon.ico` 404** (found by live-browser E2E): `frontend/index.html` now declares an inline SVG favicon (space-encoded data URI).
- **Stale README ToC anchor**: the renamed "High-Level Output Policy (Phase 8)" heading left a dead `#high-level-xlsx-export-policy` ToC link; anchor updated and a new `test_readme_toc_anchors_resolve` contract test now guards every ToC anchor against real headings (GitHub slug rules).

### Changed (documentation refresh to current system state)
- `README.md`: replaced the stale pre-Phase-8 "High-Level XLSX Export Policy" (`--export-high-level-tables`, removed flag) with the Phase 8 `OutputProfile` policy; added `--profile` usage examples; added `docs/architecture.md` to Technical Documentation; corrected the FULL_SYSTEM_AUDIT_REPORT description to FAZ 1–6.
- `docs/code_atlas.md`: removed deleted modules (`dashboard_js.py`, `dashboard_exporter.py`, `html_templates/index_template.py`, Flask references, `FractureProcessor`/`ExportConfig`/`apiClient` ghosts) and updated the module map, architecture diagram, and cross-reference index to the current backend/frontend inventory.
- `docs/architecture.md`: full backend/frontend module inventory incl. `svg_loader.py`, `output_profiles.py`, `package_index.py`, `batch_processor.py`, `artifact_validator.py`, `analysis-console.js`; Phase 8 policy threading and realtime scale-row fields documented.
- `docs/api_contract.md`: `scale_rows` job-schema example now matches the real `_build_scale_row` keys including Phase 8 `empty_parents_skipped` + `negative_space_cached_cells`.
- `docs/frontend_components.md`: documented the Live Scale Table's 6 technical columns incl. the Phase 8 **NegSpace** column.

### Verified (full-system audit)
- `python -m pytest tests/`: **348 passed, 36 pre-existing skipped, 0 failed** (384 collected).
- `python -m compileall backend tests launcher.py run_analysis.py`: 0 errors; `pyflakes backend/ run_analysis.py launcher.py` clean; `node --check frontend/js/*.js` 7/7 clean.
- Live server smoke (ephemeral port): `/api/health`, `/api/packages`, `/api/stats`, `/api/figures`, `/api/history`, `/package_index.json`, `/`, `/css/main.css` all 200; unknown `/api/*` and missing job → JSON 404.
- Live-browser E2E (Chrome): dashboard renders 2 package cards (16D Db 1.9727, 16F Db 1.7767), Live Scale Table headers include **NegSpace** + `1/r`, all `/css|js|vendor` assets 200, zero JS console errors.
- `package_index`: 2 packages scanned, both `complete` (16D: 3 figures/3 xlsx, 16F: 3 figures/3 xlsx); manifest hash integrity test passes (12 tests).
- Dead-reference scan: no active code imports the removed legacy dashboard modules (`web_server.py`, `processor.py`, `launcher.py`, `run_analysis.py` clean; guards live in `test_audit_gaps2.py`).

## [Phase 8: Negative Space Cache & High-Level Output Policy] - 2026-08-03

### Added
- **Empty Block Cache (negative-space) metric** in `backend/intersection_hierarchical.py`: every level now reports `empty_parents_skipped` (empty parent blocks whose children were never evaluated) and `negative_space_cached_cells` (child cells saved by that exact EMPTY-only pruning). The metric is printed per level, carried on `LevelReportModel`, and aggregated in the `compute_hierarchical_box_counting` summary (`phase8_total_empty_parents_skipped`, `phase8_total_negative_space_cached_cells`). No FULL shortcut: `full_parents_counted` stays `0` everywhere.
- **Phase 8 fields on `OutputProfile`** (`backend/output_profiles.py`): `max_excel_cell_map_level/cells`, `disable_raw_cell_indices_after_level/cells`, `force_svg_rle_after_level/cells`, `summary_only_after_level`, `svg_only_after_level`, `generate_high_level_svg/excel_summary/cell_tables` — plus policy helpers (`should_collect_raw_cell_indices`, `should_generate_excel_cell_map`, `should_force_svg_rle`, `should_collect_row_runs`, `should_include_cell_payload`, ...).
- **Per-level output gating tied to the policy**: `compute_hierarchical_box_counting()` now takes a `profile` (processor always passes the lean profile). At gated levels the engine stops building the expensive raw `filled_cells_indices` / `filled_set` and instead collects compact per-row **row-runs** that exactly reconstruct the filled cells.
- **High-level artifact cuts** in `backend/academic_exporter.py`: above the caps the exporter no longer emits per-level Excel cell-map / SVG-coordinate sheets, per-cell XLSX tables, ASCII maps/books, masks, RLE JSONs or raw cell CSVs; `tables_data.json` marks those levels `cells_omitted` while keeping exact summary metrics. SVG maps are preserved for every level and switch to **run-length / row-run merged rects** for L9+/large grids (`generate_high_level_svg=True`).
- **New test suite** `tests/test_phase8_negative_space_cache.py` (11 tests): policy defaults/gates, negative-space metric exactness (no FULL shortcut), row-run collection and exact reconstruction, legacy no-profile behaviour, exporter gating incl. RLE SVG rendering, and an RLE-vs-per-cell scientific-accuracy guard (merged rects cover exactly the same filled cells).
- **Realtime Scale Rows (Scientific Console)**: `_build_scale_row` now carries the real per-level Negative-Space-Cache metrics (`empty_parents_skipped`, `negative_space_cached_cells`) computed by the counting engine, the LEVEL_DONE job log surfaces the pruning stat, and the dashboard Live Scale Table gained a **NegSpace** technical column (toggle via *Show technical regression columns*). The console is fed exclusively by the real `progress_callback(LevelReportModel)` stream — no mock/fake data (locked by `test_frontend_static_contract.py::test_no_mock_fake_simulate_in_frontend`).
- **SVG health timing** (`backend/svg_health.py`): `SVGHealthResult` now reports `health_ms` (wall-clock duration of the pre-analysis inspection, `round(…, 3)`), exposed via `to_dict()` and shown in the processor STEP 2 status message (`health inspection: X ms`); covered by `test_svg_health_reports_health_ms`.

### Changed
- `backend/processor.py` loads the output profile once and threads it into both the counting engine and the exporter.
- `backend/web_server.py`: `_build_scale_row` + `add_job_scale_row` Phase 8 metrics/log.
- `frontend/index.html` + `frontend/js/analysis-console.js`: NegSpace technical column (colspan 15 → 16).

### Verified
- `python -m pytest tests/test_phase8_negative_space_cache.py`: **11 passed**.
- Real L8 run on `input_svgs/16E.svg` with the default lean profile: L1–L7 collect full `filled_set`; L8 (`524,288 > 500,000` cells) collects 26,785 row-runs instead (no raw index list) and prunes 211,124 of 524,288 cells via the empty-parent cache; SVG maps still generated (RLE merged).
- Existing pipeline smoke (`16A` L3 via `AnalysisProcessor`): SUCCESS, all default artifacts unchanged.

## [Test-First Repair Loop 1] - 2026-08-03

### Fixed
- **ISSUE-007**: server-path analysis endpoints (`/api/analyze`, `/api/batch`) now enforce the same 50MB size cap as uploads (413 before dispatch).
- **ISSUE-008**: malformed multipart bodies (no valid parts, truncated parts, missing Content-Disposition) are rejected cleanly (400) instead of being silently mis-parsed.
- **ISSUE-006**: job state now persists to a runtime store (`.rash_hit/jobs.json`, outside `outputs/`) and survives server restarts (orphaned mid-flight jobs become `interrupted`).
- **ISSUE-009**: package detail Live Scale Table now renders from `scale_table` when `scale_rows` is absent (mirrors the export fallback).
- **ISSUE-010**: search input filtering is debounced (150ms) so the card grid is not rebuilt on every keystroke.
- **ISSUE-011**: all four dashboard modals now expose `role="dialog" aria-modal="true"` and restore focus on close.
- **ISSUE-013**: `package_index.json` records now carry a populated `input_sha256` (computed from the source SVG when it exists); `has_*` flag aliases are consistency-tested.
- **ISSUE-001..005, 015, 016**: README Manual Refresh uses the active `package_index` indexer; phantom module references removed; profile-gated package artifacts annotated; version metadata aligned to **1.0.5** (matches published DOI); `test_checklist.md` count updated to 337; `numpy` floor aligned to `>=2.4.6`; stale audit-log references aligned to current artifacts.

### Verified
- Full suite green: **343 passed** (web-server batch) with further frontend/docs tests added during the loop; `compileall` OK; 7/7 `node --check` OK; API isolation intact (fetch only in `api.js`); `outputs/index.html` absent (pure-data rule holds).
- **Audit-log note**: the 2026-08-01/2026-08-02 audit/repair artifacts are not present on disk (not restorable from `.freebuff_backup_20260802_005236/`, which holds only the Freebuff DB). Live docs now reference the current `docs/audit_logs/` artifacts.

# Changelog

All notable changes to **RASH-HIT Fractal Studio** will be documented in this file.

## [Academic Navy Report Design — Default & Backfill] - 2026-08-02

### Changed
- Confirmed the Academic Navy design language (`docs/ui_references/report_interactive_redesign.html`: navy gradient hero, eyebrow label, meta pills, Quick Access bar, accent-bar KPI cards, file-chip package matrix, gallery cards, manifest panel) is **already the active default** in `backend/html_templates/theme_css.py` + `report_template.py` — every fresh analysis run produces it.

### Fixed
- **Stale legacy-design reports in `outputs/`**: existing packages (`16`, `16A`, `16A_20260802_021958`, `16L`, `16L_20260802_021044`) were generated with an older template (old `app-header`/`--sb`/`#2563EB` tokens). Rebuilt each `report.html` **in place** from its existing `result.json` using the current navy template — no re-analysis needed, package data untouched.
- `16B_B` is a partial legacy package without `result.json`; it has no report to rebuild (left as-is).

### Verified
- All 5 report-bearing packages now carry the full navy design marker set (eyebrow, hero-top, hero-meta, meta-pill, quick, theme-toggle, kpi-card, file-chip, manifest-panel, badge-pass, openSvgModal, `loading="lazy"`, `decoding="async"`, `#2454A6` accent) and **no dead `report.md` links**.
- Served via live web server: `/16A/report/report.html` returns 200 with all design markers present.
- `python -m pytest`: **322 passed** (unchanged, no regressions).
- `python -m compileall backend tests launcher.py run_analysis.py`: 0 errors.

### Note
- If the web server was started before this session, **restart it** so new dashboard runs pick up the current template in memory (Python caches imported modules at server start).

## [Full Project Test-First Audit & Repair] - 2026-08-02

### Added
- New permanent test-first audit suites (8 files, 125 tests): `test_full_project_contract.py`, `test_report_template_contract.py`, `test_output_integrity_contract.py`, `test_package_versioning_contract.py`, `test_security_path_contract.py`, `test_export_delete_contract.py`, `test_docs_contract.py`, `test_dashboard_interactions_contract.py`.
- Full-project contract coverage: Python compile/import health, REST route + live JSON 404 contract, upload single/batch field contract, job store caps (50 jobs / 500 logs), scale-row dedup/sort, Live Scale Table columns, frontend static contract (script order, API isolation, no embedded PACKAGES), report template lazy-load/escaping, outputs pure-data rules, package versioning, security/path traversal, export/delete transactional behavior, dashboard interactions, and documentation sync.

### Changed
- `tests/test_academic_engine.py::test_academic_report_markdown_links`: updated to the new dead-link-free contract (report.md is no longer generated, so report.html must NOT reference it).

### Fixed
- **`Uncaught ReferenceError: dashboardRefreshTimer is not defined`** on dashboard load (`frontend/js/app.js`) — `initDashboardLive()` read `dashboardRefreshTimer` before it was ever declared; caught by the live-browser smoke test and guarded with a permanent static-contract test (`test_dashboard_interactions_contract.py`).
- **Directory listing links could 404** (`backend/web_server.py`) — `GET /<package>/figures` without a trailing slash now 301-redirects to `/figures/` so the relative SVG links in the listing resolve against the directory itself (dashboard Figures button path verified).
- **Dead `report.md` links** in `report.html` (`backend/html_templates/report_template.py`) — report.md generation was removed earlier but the template still emitted Markdown chip links.
- **`GET /<package>/figures/` crashed with 500** (`backend/web_server.py`) — the dashboard Figures button target is a directory; `_serve_file` now serves a safe HTML directory listing instead.
- **`package_index.json` rewritten on refused deletes** (`backend/web_server.py`) — `_handle_delete_many` now rebuilds the index only when a package was actually deleted; protected-file / traversal refusals leave the index byte-for-byte untouched.
- **`DeprecationWarning: invalid escape sequence '\$'`** in `backend/html_templates/tables_template.py` — switched the tables body to a raw f-string (`rf"""`) so the JS template-literal dollar escapes stay literal.

### Verified
- `python -m pytest`: **322 passed** (194 → 322, +128 new tests).
- `python -m compileall backend tests launcher.py run_analysis.py`: 0 errors.
- `python -m py_compile launcher.py run_analysis.py`: OK.
- `node --check frontend/js/*.js`: all files clean.
- API isolation: `fetch` strictly isolated to `frontend/js/api.js`.
- Embedded vendor/static data scan in `frontend/index.html`: 0 matches.
- `outputs/` pure-data compliance: no `outputs/index.html`, no frontend assets in root, `package_index.json` valid JSON list with relative URLs.
- Live server smoke: `/`, `/api/health`, `/api/packages`, `/api/stats`, `/api/figures`, `/api/history`, `/package_index.json` all 200; unknown `/api/*` → 404 JSON.

## [Web Performance Regression Audit & Realtime Data Flow Repair] - 2026-08-02

### Added
- **Live Scale Table Redesign**: 10 main columns prioritizing scientific readability (Level, Grid, Total Cells, Filled Cells, Empty Cells, Occupancy %, Cell Size, Duration, Fit Status, Status). 5 technical columns (Box W, Box H, 1/r, log(1/r), log(Nr)) toggleable via `Show technical regression columns` checkbox.
- Opt-in timing profiling instrumentation across frontend (`perfLog`, `window.RASH_HIT_DEBUG_PERF`, `localStorage rash-hit-debug-perf`) and backend (`LEVEL_STARTED`, `LEVEL_DONE`, `SCALE_ROW_WRITTEN`, `API_JOB_STATUS_READ`).
- Created `tests/test_web_performance_contract.py`, `tests/test_realtime_progress.py`, and `tests/test_live_performance_smoke.py` (+14 new tests).
- Permanent performance audit evidence was maintained under `docs/audit_logs/` (historical artifacts archived in v1.0.6 cleanup).

### Changed
- `analysis-console.js`: Enforced `isPollingJob` overlap guard, 500ms active poll interval, step timeline diff hashing, and incremental log stream appending up to 500 lines.
- `web_server.py`: In-place level deduplication in `add_job_scale_row`, computed `empty_count` in `_build_scale_row`, and emitted `LEVEL_DONE` logs.
- `package-manager.js` & `app.js`: Enforced active-view-only rendering in `renderCurrentView()` and added 300ms debouncing to `initDashboardLive()`.
- `ui.js`: `closeSvgModal()` clears `img.src` to prevent memory leaks from large SVG previews.

### Fixed
- Scientific Analysis Console rendering delay, full innerHTML table/log rewrites, and cluttered technical column layout.
- Duplicate level scale row appends in backend job store.

### Verified
- `python -m pytest`: **189 passed** (+14 tests).
- `python -m compileall backend tests launcher.py run_analysis.py`: 0 errors.
- `node --check frontend/js/*.js`: 7 files clean.
- API isolation: `fetch` strictly isolated to `frontend/js/api.js`.
- `outputs/` pure-data compliance: no `outputs/index.html` generated, `package_index.json` schema intact.

## [Dashboard Design System Restoration & Realtime Console Repair] - 2026-08-02

### Added
- Restored View Mode radio buttons and all 7 view sections (`view-overview`, `view-detail`, `view-grid-overview`, `view-svg-maps`, `view-files`, `view-compare`, `view-tables`) connected via modular JS (`switchView()`, `renderCurrentView()`).
- Restored Right Drawer details panel (`openPackageDrawer()`, `renderDrawerPackageDetails()`).
- Restored Export Configuration Modal (`openExportDialog()`, `exportExcelFromDialogOptions()`, `executeExcelExport()`) with multi-sheet workbook generation (Summary, Packages, Level Metrics, Package Files).
- Restored Comparative Analysis view (`renderCompareView()`) with summary stats (Avg Db, Avg R², Max/Min Db motifs).
- Added `tests/test_frontend_restoration.py` (+16 tests) verifying static contract, view modes, drawer, export modal, filters, scientific console, and report template lazy loading.

### Changed
- Dashboard layout unified with Academic Navy token design system (`--bg`, `--panel`, `--panel2`, `--border`, `--accent`, `--accent2`, `--soft`, `--pass`, `--warn`, `--danger`, `--shadow`, `--radius`).
- Scientific Console enhanced: polling overlap guard (`isPollingJob`), status normalization (`success`/`failed`), placeholder scale rows for requested levels, merge/replace real scale rows with `.is-new` flash animation, Fit status derived from `included_in_fit`, step timeline status indicators, and terminal log stream auto-scroll (capped at 500 lines).
- Report SVG gallery loading optimized using `loading="lazy"`, `decoding="async"`, `content-visibility: auto`, `contain-intrinsic-size`, and `object-fit: contain` to eliminate slow perception and page freezing.

### Fixed
- Scientific Console Live Scale Table rendering and current step loading feedback.
- Missing view mode UI, drawer overlay, and export modal connections in modern API-first web architecture.

### Verified
- `python -m pytest`: **175 passed** (+16 tests).
- `python -m compileall backend tests launcher.py run_analysis.py`: 0 errors.
- API isolation: `fetch` API calls contained strictly inside `frontend/js/api.js`.
- `outputs/` pure-data compliance: no `outputs/index.html` generated, `package_index.json` schema preserved.

## [Final UI/UX Reference Comparison & Test Expansion] - 2026-08-01

### Added
- `tests/test_frontend_static_contract.py` (**22 tests**): HTML id ↔ JS `getElementById` matching, onclick/onchange/oninput handler definitions, required modal/control ids (chkOverwrite, btnRunWeb, btnConsoleOpenFigures, selectionToolbar, liveScaleTableBody, consoleEventLog), script order, API isolation (fetch only in `api.js`), export button wiring, and `outputs/` pure-data file-system verification.
- `tests/test_live_server_api.py` (**19 tests**): live HTTP smoke tests against a real `SecuredRequestHandler` on an ephemeral port — GET /api/health, packages, stats, figures, history, 404 routes, /package_index.json, static assets, upload-single/batch rejection routes, delete traversal protection, unknown endpoint JSON 404.
- `tests/test_web_server_api.py` (+4): unit tests for the `_build_scale_row` schema, `add_job_scale_row`, and `update_job_step`.
- Added **Level** sort options to `sortSelect` (`levels-desc` / `levels-asc`) — dead branches already handled in code were activated.
- `:focus-visible` focus rings and `.btn-danger:disabled` styling (keyboard accessibility).

### Changed
- Dangerous buttons now use the existing `.btn-danger` design class (3-dot) instead of inline `style` — consistent button hierarchy.
- `#emptyOverview` empty-state element is now genuinely wired into `renderOverviewView` (design class instead of an inline message).
- `ui.js`: the Esc key now closes the open modal (only the open one; Scientific Console takes priority) — targeted behavior instead of the previous all-at-once/double close.
- `backend/web_server.py`: added protection returning **JSON 404** instead of HTML for unknown `/api/*` GET routes (aligned with the documented API contract).

### Fixed
- UI inconsistencies found against the old reference designs (danger button style, empty state, focus state, sort options).

### Verified
- `python -m pytest -q`: **159 passed** (114 → 159, +45).
- `python -m compileall backend tests` and `py_compile launcher.py run_analysis.py`: clean.
- `node --check` on 7 frontend JS files: clean.
- API isolation: `fetch`/`XMLHttpRequest`/`axios` only in `frontend/js/api.js`.
- `outputs/` pure-data: no `outputs/index.html`, no frontend files at the root, `package_index.json` present.
- Browser E2E (Chrome, `localhost:8000`): 17-item click matrix — 15/17 PASS; the remaining 2 items (theme toggle, Scientific Console modal) were closed as PASS via code + contract tests.
- Added the FAZ 4 section to `docs/FULL_SYSTEM_AUDIT_REPORT.md`.

## [Full Web System Audit & Repair] - 2026-08-01

### Added
- `tests/test_web_server_api.py` (16 unit tests): overwrite flag coercion, multipart parsing, job store schema, log cap, SVG validation, final package URL builder.
- **Select Visible** and **Refresh Packages** buttons in the dashboard *Actions* accordion (`selectVisible()`, `initDashboardLive()`).
- `uploads/` entry in `.gitignore` (per-job upload staging directory).
- README section: **Package Versioning & Overwrite Protection**.

### Changed
- `launcher.py`: removed unused imports (`ExecutionResult`, `MODE_LEVEL_MAP`), dead `selected_mode` variable, and placeholder-less f-strings.
- `package.json`: `lint` script now includes `launcher.py`.
- Scientific Console failure alert now extracts the real error from the last `level=error` log entry (backend job schema has no top-level `error` field).
- `btnRunWeb` starts **disabled** until a file/folder is actually selected (no more empty Start clicks).

### Fixed
- Corrected stale `outputs/index.html` mentions in `package_index.py` docstrings.

### Deprecated
- (None this cycle — `dashboard_exporter.py` remains `[DEPRECATED]` from the decoupling release; no new deprecations.)

### Removed
- Dead code referencing non-existent `exportModal` (`closeExportDialog`, `exportExcelFromDialogOptions`).
- Never-called `switchView()` referencing missing `viewMode` radios / `renderCurrentView`.
- Unused alias `renderOverviewCards()` (package-manager.js) and unused flags `excelLoaded`/`fsLoaded` (export.js).
- Stale `backend/_pkg_index_tmp.py` scratch file.
- Leftover test-upload artifacts under `uploads/` (old flat `*_16D.svg` + test `analysis_*` folders).

### Verified
- `python -m pytest -v`: **114 tests passed** (98 prior + 16 new).
- `python -m pyflakes backend/ run_analysis.py launcher.py`: clean.
- `python -m compileall backend tests`: clean.
- `outputs/` pure-data status confirmed (no `outputs/index.html`).
- `fetch` remains isolated to `frontend/js/api.js`.

## [Frontend Decoupling v1] - 2026-08-01

### Added
- Created dedicated `frontend/` directory structure containing static web dashboard UI assets:
  - `frontend/index.html` (Single active web dashboard shell)
  - `frontend/css/themes.css` (Design system color tokens and light/dark theme variables)
  - `frontend/css/main.css` (Layout, card grids, selection toolbar, and modal styles)
  - `frontend/js/api.js` (**Single Entry Data Access Layer** handling all HTTP/REST calls)
  - `frontend/js/ui.js` (Modal controls, view modes, and sidebar accordion handlers)
  - `frontend/js/package-manager.js` (Minimalist card rendering, sorting, and view renderers)
  - `frontend/js/filters.js` (Search query matching, Db range, R^2, and level range filters)
  - `frontend/js/export.js` (Client-side ExcelJS multi-sheet workbook exporter)
  - `frontend/js/app.js` (Main application bootstrap and event listeners)
  - `frontend/vendor/` (`exceljs.min.js`, `FileSaver.min.js`)
- Created `docs/architecture.md` detailing system architecture and data pipeline flow.
- Archived legacy Python template string generator to `archive/legacy_dashboard/index_template.py`.

### Changed
- Decoupled web dashboard presentation assets out of `outputs/` into `frontend/`.
- Updated `outputs/` to function exclusively as a **Pure Data Repository** storing machine-readable index data (`outputs/package_index.json`) and package subdirectories.
- Updated `backend/web_server.py` to route static UI requests (`/`, `/css/*`, `/js/*`, `/vendor/*`) to `frontend/`, while keeping REST API endpoints intact.
- Updated `backend/processor.py` step 7 to update `package_index.json` upon analysis completion without compiling `index.html`.
- Marked `backend/dashboard_exporter.py` as `[DEPRECATED]` with deprecation warnings.

### Preserved
- Preserved `academic_exporter.py`, `report_template.py`, and `tables_template.py` 100% intact for academic package generation (`report.html`, `tables.html`, `tables_data.json`, `workbook.xlsx`, `manifest.json`).
- Preserved all REST API contracts (`/api/packages`, `/api/stats`, `/api/upload-single`, `/api/upload-batch`, `/api/packages/delete`, `/api/health`).

### Verified
- Automated test suite passed with 52 tests green (`python -m pytest -v`).
- Pure Data status of `outputs/` confirmed.
- Single API entry point (`frontend/js/api.js`) isolation verified.

