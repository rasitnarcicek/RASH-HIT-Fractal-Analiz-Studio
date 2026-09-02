# Code Provenance & Authorship Statement

## 1. Original Development Statement
RASH-HIT Fractal Analysis was developed as an original academic and computational geometry software project by Mehmet Raşit Narçiçek.

## 2. Scope & Intellectual Property Boundaries
The project does not claim ownership over NumPy, standard box-counting theory, or general supercover line-rasterization theory.

The original contribution of this project lies in:
- SVG vector boundary geometry extraction and CSS style resolution pipeline
- FIXED_ORIGIN fixed-point integer lattice grid construction with aspect-ratio rule
- Exact supercover cell set box-counting on transformed vector segments (touch_counts policy)
- Pure terminal fractal dimension and regression analysis

---

## 3. Module Provenance Directory

| Module / File Path | Author | Provenance & Description |
|:---|:---|:---|
| `run_analysis.py` | Mehmet Raşit Narçiçek | Original command-line entry point & terminal reporting manager. |
| `bin/cli.js` | Mehmet Raşit Narçiçek | Original npm runner & automatic dependency installer. |
| `backend/svg_loader.py` | Mehmet Raşit Narçiçek | Original SVG parsing, CSS style resolution, and ViewBox scale engine. |
| `backend/geometry_engine.py` | Mehmet Raşit Narçiçek | Original vector path extraction & 2D transform matrix resolver; v1.2.0 pure segment emission. |
| `backend/grid_planner.py` | Mehmet Raşit Narçiçek | Original aspect-ratio-aware grid plan generator. |
| `backend/supercover_reference.py` | Mehmet Raşit Narçiçek | Original pure NumPy supercover engine: FIXED_ORIGIN lattice, fixed-point int64, exact Liang-Barsky closed-box intersection. |
| `backend/geometric_contact_pipeline.py` | Mehmet Raşit Narçiçek | Original geometric-contact analysis pipeline: SVG segment extraction & supercover box-counting manifest. |
| `backend/intersection_cpu.py` | Mehmet Raşit Narçiçek | Original CPU data models and level result structures. |
| `backend/fractal_analyzer.py` | Mehmet Raşit Narçiçek | Original log-log regression & Db calculation engine. |
