// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Mehmet Raşit Narçiçek

/**
 * analysis-console-scale-rows.test.mjs
 *
 * jsdom unit test for renderConsoleScaleRows() in frontend/js/analysis-console.js.
 *
 * Proves the 'Computing…' row placement contract derived from the `currentLevel`
 * argument. The historical implementation read an undeclared `computingLevel`
 * variable which threw a ReferenceError on every job poll and left the Live
 * Scale Table blank. The fixed renderer derives the computing level locally:
 *
 *     const computingLevel = isSuccess ? null
 *       : (currentLevel < total ? currentLevel + 1 : null);
 *
 * Run: node --test tests/js/analysis-console-scale-rows.test.mjs
 */

import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { JSDOM } from "jsdom";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CONSOLE_SRC = readFileSync(
  join(__dirname, "..", "..", "frontend", "js", "analysis-console.js"),
  "utf-8",
);

// Harness constraint: the console source is a classic (non-module, non-strict)
// script, so window.eval puts its `function` declarations on the window object
// and its top-level `let`/`const` into the shared global lexical environment
// that those functions close over. If analysis-console.js ever gains top-level
// "use strict" or import/export, this harness must be revisited.

// Production escapeHtml() lives in package-manager.js; the console shares that
// same global helper, so replicate the exact same implementation here.
const ESCAPE_HTML_SRC = `
function escapeHtml(str) {
  if (str == null) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
`;

/** Fresh jsdom window carrying the real analysis-console.js module source. */
function loadConsoleWindow() {
  const dom = new JSDOM(
    '<!DOCTYPE html><html><body>'
      + '<table><tbody id="liveScaleTableBody"></tbody></table>'
      + '</body></html>',
    { url: "http://localhost/", runScripts: "outside-only", pretendToBeVisual: true },
  );
  const { window } = dom;
  window.eval(
    "if (typeof performance === 'undefined') { window.performance = { now: () => Date.now() }; }",
  );
  window.eval(ESCAPE_HTML_SRC);
  window.eval(CONSOLE_SRC);
  return window;
}

/** Build a real LevelReportModel-shaped scale row (same shape as _build_scale_row). */
function completedRow(overrides = {}) {
  return {
    level: 1,
    grid_label: "4x8",
    box_size_w: 250,
    box_size_h: 125,
    inv_box_size: 0.0053,
    occupied_count: 12,
    total_count: 32,
    empty_count: 20,
    occupancy_percent: 37.5,
    duration_seconds: 0.8,
    included_in_fit: true,
    status: "DONE",
    empty_parents_skipped: 296,
    negative_space_cached_cells: 1184,
    candidate_count: 512,
    active_parent_count: 32,
    empty_candidate_count: 480,
    cell_storage_mode: "row-runs",
    output_policy_note: "SVG rendered with run-length / row-run merged rects",
    ...overrides,
  };
}

function scaleRows(window) {
  return [...window.document.querySelectorAll("#liveScaleTableBody tr.scale-row")];
}

function textOf(row) {
  return row.textContent.replace(/\s+/g, " ").trim();
}

test("currentLevel=1 with L01 done renders L01 done / L02 Computing / L03 waiting", () => {
  const window = loadConsoleWindow();
  const realRows = [completedRow({ level: 1 })];
  // Must not throw (the historical undeclared `computingLevel` ReferenceError).
  window.renderConsoleScaleRows(realRows, 3, 1, false, false);

  const rows = scaleRows(window);
  assert.equal(rows.length, 3, "three rows for three requested levels");
  assert.ok(rows[0].classList.contains("is-done"), "L01 done");
  assert.match(textOf(rows[1]), /Computing/);
  assert.match(textOf(rows[1]), /RUNNING/);
  assert.ok(rows[2].classList.contains("is-waiting"), "L03 waiting");
  assert.match(textOf(rows[2]), /WAITING/);
});

test("currentLevel=0 marks L01 as the Computing level", () => {
  const window = loadConsoleWindow();
  window.renderConsoleScaleRows([], 3, 0, false, false);
  const rows = scaleRows(window);
  assert.equal(rows.length, 3);
  assert.match(textOf(rows[0]), /Computing/);
  assert.match(textOf(rows[0]), /RUNNING/);
});

test("completed job (isSuccess) renders no Computing row", () => {
  const window = loadConsoleWindow();
  const realRows = [
    completedRow({ level: 1 }),
    completedRow({ level: 2, grid_label: "8x8", box_size_w: 125, box_size_h: 125,
      inv_box_size: 0.008, occupied_count: 20, total_count: 64, empty_count: 44,
      occupancy_percent: 31.25, duration_seconds: 0.9 }),
    completedRow({ level: 3, grid_label: "16x16", box_size_w: 62.5, box_size_h: 62.5,
      inv_box_size: 0.016, occupied_count: 40, total_count: 256, empty_count: 216,
      occupancy_percent: 15.625, duration_seconds: 1.1 }),
  ];
  window.renderConsoleScaleRows(realRows, 3, 3, true, false);
  const rows = scaleRows(window);
  assert.equal(rows.length, 3);
  for (const row of rows) {
    assert.ok(row.classList.contains("is-done"), "all rows done on success");
    assert.doesNotMatch(textOf(row), /Computing/, "no Computing row on success");
  }
});

test("failed job (isFailed) renders no Computing row", () => {
  const window = loadConsoleWindow();
  window.renderConsoleScaleRows([completedRow({ level: 1 })], 3, 1, false, true);
  const rows = scaleRows(window);
  assert.equal(rows.length, 3);
  assert.doesNotMatch(textOf(rows[1]), /Computing/, "no Computing row on failure");
});

test("currentLevel at or beyond total renders no Computing row", () => {
  const window = loadConsoleWindow();
  // current_level 7 == requested 7 -> computingLevel null -> L07 waiting.
  window.renderConsoleScaleRows([], 7, 7, false, false);
  const rows = scaleRows(window);
  assert.equal(rows.length, 7);
  assert.match(textOf(rows[6]), /WAITING/);
  assert.doesNotMatch(textOf(rows[6]), /RUNNING/);
});

test("real row at the computing level takes precedence over the placeholder", () => {
  const window = loadConsoleWindow();
  const realRows = [
    completedRow({ level: 1 }),
    completedRow({ level: 2, grid_label: "8x8", box_size_w: 125, box_size_h: 125,
      inv_box_size: 0.008, occupied_count: 20, total_count: 64, empty_count: 44,
      occupancy_percent: 31.25, duration_seconds: 0.9 }),
  ];
  window.renderConsoleScaleRows(realRows, 3, 2, false, false);
  const rows = scaleRows(window);
  assert.equal(rows.length, 3);
  assert.ok(rows[1].classList.contains("is-done"), "L02 real data wins");
  assert.match(textOf(rows[2]), /Computing/, "L03 is the next computing level");
  assert.match(textOf(rows[2]), /RUNNING/);
});

test("NegSpace cell keeps the RASH-HIT tooltip (per-level + package markers)", () => {
  const window = loadConsoleWindow();
  const job = {
    final_package: {
      folder: "__unit_sample_pkg__",
      rh_engine_cells_omitted_levels: [2],
      rh_engine_row_run_levels: [2],
      rh_engine_uses_row_runs: true,
    },
  };
  window.renderConsoleScaleRows([completedRow({ level: 1 })], 3, 1, false, false, job);
  const rows = scaleRows(window);
  const negCell = rows[0].querySelector('td[title*="RASH-HIT"]');
  assert.ok(negCell, "NegSpace cell carries a RASH-HIT title");
  const tip = negCell.getAttribute("title");
  assert.match(tip, /negative-space cache/);
  assert.match(tip, /empty parents skipped: 296/);
  assert.match(tip, /Package RASH-HIT policy/);
  assert.match(tip, /per-cell data omitted at: L02/);
  assert.match(tip, /row-run SVG maps at: L02/);
});
