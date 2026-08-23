# Code Provenance & Authorship Statement

## 1. Original Development Statement
RASH-HIT Fractal Analiz Studio was developed as an original academic and computational geometry software project by Mehmet Raşit Narçiçek.

## 2. Scope & Intellectual Property Boundaries
The project does not claim ownership over GEOS, Shapely, standard box-counting theory, or general quadtree data structures.

The original contribution of this project lies in:
- SVG vector fill and stroke geometry extraction and CSS style resolution pipeline
- Aspect-ratio-aware hierarchical grid planning algorithm
- High-performance vector spatial intersection and box-counting calculation
- Pure terminal fractal dimension and regression analysis

---

## 3. Module Provenance Directory

| Module / File Path | Author | Provenance & Description |
|:---|:---|:---|
| `run_analysis.py` | Mehmet Raşit Narçiçek | Original CLI entry point & terminal reporting manager. |
| `bin/cli.js` | Mehmet Raşit Narçiçek | Original npm CLI runner & automatic dependency installer. |
| `backend/svg_loader.py` | Mehmet Raşit Narçiçek | Original SVG parsing, CSS style resolution, and ViewBox scale engine. |
| `backend/geometry_engine.py` | Mehmet Raşit Narçiçek | Original vector path extraction & 2D transform matrix resolver. |
| `backend/grid_planner.py` | Mehmet Raşit Narçiçek | Original aspect-ratio-aware grid plan generator. |
| `backend/intersection_cpu.py` | Mehmet Raşit Narçiçek | Original CPU data models and level result structures. |
| `backend/intersection_cpu_area.py` | Mehmet Raşit Narçiçek | Original CPU Exact Vector Geometry Engine (RASH-HIT Fractal Analiz Engine). |
| `backend/intersection_hierarchical.py` | Mehmet Raşit Narçiçek | Original quadtree spatial pruning intersection engine. |
| `backend/fractal_analyzer.py` | Mehmet Raşit Narçiçek | Original log-log regression & Db calculation engine. |
