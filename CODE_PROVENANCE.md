# Code Provenance & Authorship Statement

## 1. Original Development Statement
RASH-HIT Fractal Studio was developed as an original personal academic software project by Mehmet Raşit Narçiçek.

## 2. Scope & Intellectual Property Boundaries
The project does not claim ownership over GEOS, Shapely, box-counting theory, or general quadtree algorithms.

The original contribution of this project lies in:
- SVG fill and stroke geometry extraction pipeline
- Aspect-ratio-aware grid planning algorithms
- Automated academic export engine (PDF, HTML, Excel, SVG maps, manifest metadata)
- Fully reproducible SHA-256 manifest system

---

## 3. Module Provenance Directory

| Module / File Path | Author | Provenance & Description |
|:---|:---|:---|
| `run_analysis.py` | Mehmet Raşit Narçiçek | Original CLI entry point & analysis pipeline manager. |
| `backend/svg_loader.py` | Mehmet Raşit Narçiçek | Original SVG parsing and ViewBox scale engine. |
| `backend/geometry_engine.py` | Mehmet Raşit Narçiçek | Original vector path extraction & style resolver. |
| `backend/grid_planner.py` | Mehmet Raşit Narçiçek | Original aspect-ratio-aware grid plan generator. |
| `backend/intersection_cpu.py` | Mehmet Raşit Narçiçek | Original CPU data models and level result wrappers. |
| `backend/intersection_cpu_area.py` | Mehmet Raşit Narçiçek | Original CPU Exact Vector Geometry Engine. |
| `backend/intersection_hierarchical.py` | Mehmet Raşit Narçiçek | Original quadtree spatial pruning engine. |
| `backend/fractal_analyzer.py` | Mehmet Raşit Narçiçek | Original log-log regression & Db calculation engine. |
| `backend/academic_exporter.py` | Mehmet Raşit Narçiçek | Original multi-format academic report exporter. |
| `backend/output_profiles.py` | Mehmet Raşit Narçiçek | Original output profile management system. |
