# RASH-HIT Fractal Studio

License: Apache-2.0
Python: 3.9+
ORCID: https://orcid.org/0009-0005-3423-255X

**RASH-HIT Fractal Studio** is a research-oriented computational software project for SVG-based vector geometry analysis, grid occupancy mapping, box-counting fractal dimension estimation, SVG Coordinate Map generation, and publication-ready research output generation.

The project analyzes design, pattern, ornament, motif, textile, visual heritage, architectural drawing, and other SVG-based design artifacts directly from their vector geometry. Instead of converting SVG files into raster images, the system reads SVG code and geometry definitions, extracts fill and stroke shapes, overlays a multilevel grid on the SVG coordinate space, and counts whether each grid cell is filled or empty according to vector geometry intersection.

RASH-HIT Fractal Studio uses a **CPU Exact Vector Geometry Engine** based on Shapely/GEOS predicates to perform raster-free box-counting analysis directly on SVG fill and stroke geometries.

---

## Overview

Many design and motif studies work with visual forms that are already stored as vector data. When these designs are converted into PNG or other raster images before analysis, geometric detail can be affected by resolution, anti-aliasing, scaling, and pixel-level artifacts.

RASH-HIT Fractal Studio avoids this by working directly with SVG vector geometry.

The system reads:
- SVG `viewBox`
- SVG width and height
- `path`, `polygon`, `polyline`, `line`, `rect`, `circle`, and `ellipse` elements
- fill attributes
- stroke attributes
- stroke width
- inline styles
- class-based CSS styles
- transform matrices
- curves and arcs converted into vector segments

The software then creates a multilevel grid over the SVG coordinate space. A grid cell is counted as **filled** when any SVG fill or stroke geometry touches, crosses, covers, or intersects the cell. A grid cell is counted as **empty** when no fill or stroke geometry contacts the cell.

The filled cell counts across grid levels are used to estimate the box-counting fractal dimension (`Db`).

---

## Design and Motif Analysis Context

RASH-HIT Fractal Studio is intended for computational analysis of visual design structures stored as SVG files.

Typical use cases include:
- Traditional or contemporary motifs
- Textile and pattern designs
- Decorative ornaments
- Symbolic forms
- Architectural details
- Visual heritage drawings
- Vector-based design studies
- Experimental computational design artifacts

The main idea is simple:

```text
Design object saved as SVG
→ SVG code is read directly
→ fill and stroke geometry is extracted
→ grid cells are placed over SVG coordinate space
→ each cell is tested for vector geometry contact
→ filled and empty cells are counted
→ box-counting fractal dimension is estimated
```

This keeps the analysis tied to the original vector geometry instead of a rasterized image approximation.

---

## Key Features

- **Raster-free SVG geometry analysis**  
  The system analyzes SVG code and vector geometry directly, without using exported PNG or pixel images.

- **Design and motif research workflow**  
  Suitable for computational analysis of motifs, ornaments, textile patterns, architectural details, symbolic forms, decorative compositions, and other SVG-based design objects.

- **Direct fill and stroke handling**  
  Filled polygons, closed paths, line paths, polylines, polygons, and stroke-based geometry are included in the occupancy decision.

- **Aspect-ratio-aware grid planning**  
  Grid levels are generated according to the SVG `viewBox` ratio so that the analysis space preserves the original design proportions.

- **CPU Exact Vector Geometry Engine**  
  Uses Shapely/GEOS geometry predicates to evaluate whether SVG fill or stroke geometry intersects each grid cell.

- **Filled and empty cell accounting**  
  Each level reports total cells, filled cells, empty cells, fill ratio, and occupancy percentage.

- **Box-counting fractal dimension estimation**  
  Estimates `Db` using log-log regression based on occupied cell counts across grid levels.

- **Publication-ready output package**  
  Generates PDF, HTML, Markdown, Excel workbook, per-level XLSX tables, SVG coordinate maps, terminal log, and manifest metadata.

- **High-level output export policy**  
  Full cell-level XLSX exports are kept to practical levels by default. Higher levels remain available in summary reports and manifest metadata.

- **Reproducibility metadata**  
  Exports input SHA-256 hash, software version, engine settings, grid labels, dependency versions, runtime environment data, and output metadata.

---

## Computational Workflow

RASH-HIT Fractal Studio follows this workflow:

```text
SVG file
→ SVG parser
→ style and transform resolver
→ fill/stroke geometry extraction
→ curve and arc flattening
→ viewBox-aware grid planning
→ vector-grid cell intersection
→ filled/empty box counts
→ log-log regression
→ Db, R², reports, tables, SVG maps, and manifest
```

---

## SVG Geometry Handling

The system supports common SVG structures:
- `path`
- `polygon`
- `polyline`
- `line`
- `rect`
- `circle`
- `ellipse`
- group transforms
- inline style attributes
- class-based styles
- `fill`
- `stroke`
- `stroke-width`
- `viewBox`

SVG path commands may include:
`M`, `L`, `H`, `V`, `C`, `S`, `Q`, `T`, `A`, `Z`

Curves and arcs are converted into sampled vector segments before geometric intersection analysis.

---

## Fill and Stroke Interpretation

In area mode, the system evaluates both filled regions and stroke geometry.

A grid cell is counted as **filled** when at least one of the following is true:
- a fill polygon intersects the cell
- a fill polygon covers the cell
- a fill polygon boundary touches the cell
- a stroke line intersects the cell
- a stroke line touches the cell
- a stroke with width reaches the cell

A grid cell is counted as **empty** when:
- no fill geometry contacts the cell
- no stroke geometry contacts the cell
- no vector geometry crosses or touches the cell

This means that design features such as closed motif surfaces, contour lines, internal paths, and stroke-based details can all contribute to the filled cell count.

---

## Mathematical Method

The box-counting fractal dimension (`Db`) estimates how the number of occupied boxes changes as the spatial scale becomes finer.

For each grid level:
- `N(epsilon)` = number of filled grid cells
- `epsilon` = spatial scale associated with grid cell size
- `Db` = slope of the log-log regression

The regression model is:
```text
log(N(epsilon)) = Db * log(1 / epsilon) + C
```

The coefficient of determination is reported as R²:
```text
R² = 1 - SS_res / SS_tot
```

Where:
- `SS_res = sum((y_i - y_hat_i)^2)`
- `SS_tot = sum((y_i - mean(y))^2)`

R² is used as a regression fit indicator across selected grid levels.

---

## Grid Levels

By default, the software analyzes seven grid levels:
`L01–L07`

Higher levels can be requested:
```bash
python run_analysis.py --input input_svgs/16D.svg --levels 10
```

Higher levels increase computational cost and output size. Each added level typically increases the number of cells by approximately four times.

---

## System Requirements

- Python 3.9 or newer
- Windows, Linux, or macOS

Recommended:
- Python 3.11 or 3.12
- 16 GB RAM or more for high-resolution analyses
- 64-bit operating system

---

## Installation

Clone the repository:
```bash
git clone https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio.git
cd RASH-HIT-Fractal-Studio
```

Install dependencies:
```bash
pip install -r requirements.txt
```

PDF export uses PyMuPDF through the fitz interface. Review PyMuPDF licensing terms if packaging or redistributing binary distributions.

---

## Quick Start

Run the default analysis on the sample SVG:
```bash
python run_analysis.py --input input_svgs/16D.svg
```

Default behavior:
- Engine: CPU Exact Vector Geometry Engine
- Measurement: area
- Grid levels: L01..L07
- Output profile: lean
- Output folder: outputs/

---

## CLI Usage

### Single File Analysis
```bash
python run_analysis.py --input input_svgs/16D.svg
```

### High-Resolution Analysis
```bash
python run_analysis.py --input input_svgs/16D.svg --levels 10
```

### Batch Directory Analysis
```bash
python run_analysis.py --dir input_svgs/ --levels 7
```

### Custom Output Directory
```bash
python run_analysis.py --input input_svgs/16D.svg --output-dir outputs/
```

### Export Level 08 Full Tables
```bash
python run_analysis.py --input input_svgs/16D.svg --levels 8 --export-high-level-tables
```

---

## CLI Options

- `--input`: Path to a single SVG input file.
- `--dir`: Path to a directory containing SVG files for batch processing.
- `--engine`: Engine selection. Default: cpu.
- `--measure`: Measurement mode. Default: area.
- `--levels`: Number of grid levels. Default: 7.
- `--profile`: Output profile. Available profiles: lean, reproducible, debug, presentation.
- `--output-dir`: Custom output directory. Default: outputs/.
- `--export-high-level-tables`: Enables full cell-level XLSX table export for Level 08.

---

## Output Package Structure

Each analyzed SVG file produces a self-contained output package:

```text
outputs/
└── [motif_name]/
    ├── report/
    │   ├── report.pdf
    │   ├── report.html
    │   └── report.md
    ├── excel/
    │   └── workbook.xlsx
    ├── tables/
    │   ├── 01_4x8_cells.xlsx
    │   ├── 02_8x16_cells.xlsx
    │   ├── ...
    │   └── tables.html
    ├── figures/
    │   ├── 01_4x8_map.svg
    │   ├── 02_8x16_map.svg
    │   └── ...
    ├── terminal/
    │   └── terminal.txt
    └── manifest/
        └── manifest.json
```

---

## Output Files

- `report.pdf`: A formatted PDF research report containing analysis metadata, grid summaries, regression results, and output notes.
- `report.html`: An HTML report for browser-based review.
- `report.md`: A Markdown report suitable for GitHub, documentation, or academic notes.
- `workbook.xlsx`: A multi-sheet Excel workbook containing summary metrics and structured analysis tables.
- `tables/*.xlsx`: Per-level cell tables for safe grid levels.
- `figures/*.svg`: Pure vector SVG grid maps showing filled and empty cell patterns.
- `terminal.txt`: Plain-text execution log.
- `manifest.json`: Reproducibility manifest containing metadata such as software version, input file hash, engine, measurement mode, grid levels, grid labels, runtime environment, dependency versions, and output metadata.

---

## High-Level Output Export Policy

Microsoft Excel worksheet limits can make very high-level full cell tables impractical. Therefore, full cell-level XLSX export is limited to safe analysis levels by default.

Policy:
- **L01–L07**: Full cell-level XLSX tables are generated by default.
- **L08**: Full cell-level XLSX export is optional with `--export-high-level-tables`.
- **L09+**: Full cell-level XLSX tables are skipped. Summary metrics, reports, SVG maps, and manifest metadata remain available.

This keeps output packages readable and portable while preserving high-level analysis summaries.

---

## Reproducibility

RASH-HIT Fractal Studio records reproducibility metadata in `manifest.json`.

Typical metadata includes:
- `software_version`
- `engine`
- `measurement_mode`
- `levels`
- `grid_labels`
- `input_svg_sha256`
- `python_version`
- `platform`
- `numpy_version`
- `shapely_version`
- `geos_version`
- `runtime_timestamp`

For reproducible results, use the same input SVG, software version, engine, measurement mode, grid levels, curve tolerance, stroke/fill interpretation, and dependency versions.

---

## Dependency Notes

RASH-HIT Fractal Studio relies on third-party open-source Python libraries.

Core dependencies include:
- NumPy
- Shapely
- GEOS
- openpyxl
- PyMuPDF
- PyYAML
- Pillow
- tinycss2
- pytest

Shapely/GEOS is used for vector geometry predicates in the CPU Exact Vector Geometry Engine.

PDF export uses PyMuPDF. Review PyMuPDF licensing terms for redistribution requirements if packaging or redistributing binary distributions.

See `THIRD_PARTY_NOTICES.md` for dependency and license details.

---

## Citation

If you use RASH-HIT Fractal Studio in your research, please cite the software using one of the following formats:

### BibTeX
```bibtex
@software{Narcicek_RASH_HIT_Fractal_Studio_2026,
  author    = {Nar{\c{c}}i{\c{c}}ek, Mehmet Ra{\s}it},
  title     = {RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine},
  year      = {2026},
  version   = {1.0.0},
  publisher = {GitHub},
  url       = {https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio},
  orcid     = {https://orcid.org/0009-0005-3423-255X},
  license   = {Apache-2.0}
}
```

### RIS
```ris
TY  - COMP
AU  - Narçiçek, Mehmet Raşit
TI  - RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine
PY  - 2026
ET  - 1.0.0
PB  - GitHub
UR  - https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio
ER  - 
```

### APA 7
> Narçiçek, M. R. (2026). *RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine* (Version 1.0.0) [Computer software]. GitHub. https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio

### AMA
> 1. Narçiçek MR. RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine. Version 1.0.0. GitHub; 2026. Available from: https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio

### Chicago (Author-Date)
> Narçiçek, Mehmet Raşit. 2026. "RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine." Version 1.0.0. GitHub. https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio.

### EndNote
> Narçiçek MR (2026) RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine (Version 1.0.0) [Computer software]. GitHub. https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio

### IEEE
> [1] M. R. Narçiçek, "RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine," Version 1.0.0, GitHub, 2026. [Online]. Available: https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio

### ISNAD
> Narçiçek, Mehmet Raşit. "RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine". Version 1.0.0. GitHub, 2026. https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio.

### JAMA
> 1. Narçiçek MR. RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine. Version 1.0.0. GitHub; 2026. https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio

### MLA (9th Edition)
> Narçiçek, Mehmet Raşit. *RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine*. Version 1.0.0, GitHub, 2026, https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio.

### Vancouver
> 1. Narçiçek MR. RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine [Computer software]. Version 1.0.0. GitHub; 2026. Available from: https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio

---

## License

RASH-HIT Fractal Studio is released under the Apache License, Version 2.0.

See `LICENSE` for license details.

Copyright © 2026 Mehmet Raşit Narçiçek.

---

## Author

Mehmet Raşit Narçiçek  
ORCID: https://orcid.org/0009-0005-3423-255X
