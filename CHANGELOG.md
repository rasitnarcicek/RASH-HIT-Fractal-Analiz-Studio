# Changelog

All notable changes to RASH-HIT Fractal Analysis are documented in this file.

## [Unreleased] — Studio soneki kaldırıldı

### Renamed — paket ve başlıklar
- **Project name:** `RASH-HIT Fractal Analiz Studio` → `RASH-HIT Fractal Analysis`.
- **PyPI package:** `rash-hit-fractal-analiz-studio` → `rash-hit-fractal-analysis`.
- **npm package:** `rash-hit-fractal-analiz-studio` → `rash-hit-fractal-analysis`.
- **GitHub repo (planned):** `rasitnarcicek/RASH-HIT-Fractal-Analiz-Studio` → `rasitnarcicek/RASH-HIT-Fractal-Analysis`.
- **Windows launcher:** `RASH-HIT-Studio.bat` → `RASH-HIT-Analysis.bat`.
- **Logo altı yazı:** `F R A C T A L   S T U D I O` → `F R A C T A L   A N A L Y S I S`.
- **CLI komutu ve motor adı korunur:** `rash-hit-fractal` ve `RASH-HIT Fractal Analysis Engine` değişmedi.
- Bu sürüm CPU konsol aracıdır; web arayüzlü sürüm ileride ayrı bir paket (Studio sonekiyle) olarak yayınlanacaktır.

## [1.2.0] — 2026-09-01

### Removed — GEOS/Shapely dependency eliminated
- **The Shapely/GEOS `area` engine is removed.** The pure NumPy supercover
  engine (v1.1's `geometric-contact` mode) is now the single engine. Rationale:
  L9 benchmarking on `16D.svg` showed the GEOS engine spends 1,836.7 ms at
  L9 (1,512,080 candidate cells) while the pure NumPy engine computes the same
  level in 5.45 ms — **203x faster with identical exactness on the lattice**
  — and scales cleanly to L10 (20.5 ms) and L11 (44.1 ms), where per-cell
  predicate engines spend seconds.
- Deleted: `backend/intersection_hierarchical.py` (STRtree/GEOS core),
  `backend/intersection_cpu_area.py` (area engine wrapper),
  `tests/test_intersection_engines.py` (STRtree tests).
- Removed CLI `--mode` flag (single engine) and the Shapely dependency from
  `requirements.txt`, `pyproject.toml`, `bin/cli.js`, and `uv.lock`.

### Changed — measurement semantics for filled motifs
- **Filled-motif outputs now report line-contact (geometric-contact) values.**
  This is the same engine that v1.1 exposed under `--mode geometric-contact`;
  it is now the only engine. Filled shapes are measured by their contacted
  line geometry (boundary-ring segments) rather than by filled-area point-set
  occupancy. Example: `16D.svg` (rect with fill+stroke) Db ≈ 1.0 (the
  mathematically expected value for a 1D line set), in contrast to the
  previous area-mode value of 1.8675. Stroke-only motifs (lines, open
  polylines, simple_polygon) are unchanged in result.
- `backend/geometry_engine.py`: `ParsedGeometry` now holds pure segment lists
  (`.segments`, `.bounds` via NumPy, `.area` via shoelace over closed rings,
  `.is_valid()` finiteness check) instead of a Shapely object; fill-rule
  repair/buffer/difference/union operations removed — geometric-contact
  measures the drawn boundary set, where a hole's contour is drawn exactly
  like a solid's contour.
- `run_analysis.py` is single-engine; `--version` → v1.2.0.
- Dependencies reduced to `numpy`, `defusedxml`, `tinycss2` — all CPU-only.

### Unchanged
- The supercover engine itself (`supercover_reference.py`,
  `geometric_contact_pipeline.py`) and its ground-truth test suite are
  byte-identical to v1.1: hand-derived cell sets (horizontal/diagonal
  supercovers, boundary-aligned lines, corner touches) still pass; measured
  Db anchors (horizontal_line.svg Db = 0.9412 with counts 8, 16, 28, 52,
  104, 208, 412; diagonal_line.svg Db = 0.9790) are unchanged.

## [1.1.0] — 2026-09-01

### Added
- **Pure NumPy supercover engine (`geometric-contact` mode):** a second analysis
  engine ported from the RASH-HIT v1.0 reference implementation, requiring only
  `numpy` (no Shapely/GEOS on its code path).
  - `backend/supercover_reference.py` — FIXED_ORIGIN grid
    (`cols = rows = 4·2^(level-1)`, aspect-ratio rule for non-square viewBox,
    extreme-aspect guard 1e-3..1e3), fixed-point int64 conversion
    (`round((coord − origin) · scale)`, overflow-clamped), exact Liang-Barsky
    closed-box segment intersection (touch_counts boundary policy: interior,
    edge, and corner contacts all count), deduplicated lexicographically sorted
    (row, column) cell sets.
  - `backend/geometric_contact_pipeline.py` — standalone SVG segment extractor
    (line / polyline / polygon / rect / circle / ellipse / path incl. Bézier and
    arc flattening) and the end-to-end box-counting manifest
    (`rashhit.geometric_contact/v1`).
  - CLI: `--mode area` (default, unchanged exact Shapely/GEOS engine) or
    `--mode geometric-contact`.
  - Tests ported verbatim from the reference suite: every expected cell set is
    hand-derived from the supercover definition (`tests/test_supercover_reference.py`),
    plus extraction and manifest tests with measured ground-truth Db values
    (`tests/test_geometric_contact_pipeline.py`, e.g. horizontal_line.svg
    Db = 0.9412, R² = 0.9990; level counts 8, 16, 28, 52, 104, 208, 412).

### Changed
- Version 1.0.1 → 1.1.0; description and keywords updated for the dual-engine
  architecture.

### Notes
- `area` mode remains the default and is unchanged: results for existing
  workflows are bit-identical to v1.0.1.

## [1.0.1] — 2026 (previous release)

- Initial GitHub/PyPI/npm publication of the exact vector geometry engine.
