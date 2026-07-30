# RASH-HIT Fractal Studio

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![Concept DOI](https://img.shields.io/badge/Concept_DOI-10.5281%2Fzenodo.21693694-blue.svg)](https://doi.org/10.5281/zenodo.21693694)
[![Version DOI](https://img.shields.io/badge/Version_DOI-10.5281%2Fzenodo.21694567-blue.svg)](https://doi.org/10.5281/zenodo.21694567)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0005--3423--255X-green.svg)](https://orcid.org/0009-0005-3423-255X)

**RASH-HIT Fractal Studio** is a research-grade, raster-free computational software system for SVG vector geometry analysis, aspect-ratio-aware grid occupancy mapping, box-counting fractal dimension ($D_b$) estimation, SVG Coordinate Map rendering, and publication-ready academic package generation.

Unlike conventional image-processing tools that convert vector artwork into PNG/JPEG pixel rasters—introducing resolution dependency, anti-aliasing distortion, edge blurring, and scaling artifacts—RASH-HIT Fractal Studio evaluates raw SVG vector geometry directly in continuous floating-point coordinate space using C++ GEOS spatial predicates via Shapely 2.0.

---

## Table of Contents

1. [Research Context & Motivation](#research-context--motivation)
2. [Key Architecture & Features](#key-architecture--features)
3. [Mathematical Methodology](#mathematical-methodology)
4. [Computational Geometry Pipeline](#computational-geometry-pipeline)
5. [Aspect-Ratio-Aware Grid Planning](#aspect-ratio-aware-grid-planning)
6. [Performance Optimization & Complexity Analysis](#performance-optimization--complexity-analysis)
7. [Installation & Dependencies](#installation--dependencies)
8. [CLI Usage & Command Matrix](#cli-usage--command-matrix)
9. [Academic Output Package Specifications](#academic-output-package-specifications)
10. [Reproducibility & Audit Controls](#reproducibility--audit-controls)
11. [Academic Citation](#academic-citation)
12. [License & Authorship](#license--authorship)

---

## Research Context & Motivation

Design, architectural, motif, visual heritage, and pattern research frequently rely on visual forms natively stored as Scalable Vector Graphics (SVG). Standard software workflows often convert these vector files into rasterized bitmap images before applying box-counting algorithms.

Rasterization distorts mathematical fractal measurements in several ways:
- **Pixel Grid Discretization**: Fine geometric details below pixel resolution are merged or deleted.
- **Anti-Aliasing Fringing**: Boundary pixels become partially transparent or shaded, altering occupancy decisions.
- **Scale Dependence**: The measured fractal dimension varies depending on the arbitrary pixel resolution chosen for rasterization.

**RASH-HIT Fractal Studio** eliminates rasterization entirely. It parses raw SVG elements (`path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`), evaluates 2D affine transform stacks, flattens Bézier curves and elliptical arcs, and evaluates geometric intersections directly against floating-point grid bounding boxes using C++ GEOS spatial predicates.

---

## Key Architecture & Features

```text
SVG File Input
   │
   ├──▶ 1. SVGLoader & Secure XML Parser (defusedxml)
   │      └── Extract ViewBox, Dimensions, Styling & Node Hierarchy
   │
   ├──▶ 2. Geometry Engine (geometry_engine.py)
   │      ├── 2D Affine Transform Matrix Stack (3x3 Homogeneous M)
   │      ├── Curve Flattening (Cubic/Quadratic Bézier & Arc Parameterization)
   │      └── Fill Rule Topology Resolution (nonzero: unary_union / evenodd: symmetric_difference)
   │
   ├──▶ 3. Aspect-Ratio-Aware Grid Planner (grid_planner.py)
   │      └── Automatic base grid determination & strict 2^i power-of-two resolution doubling
   │
   ├──▶ 4. CPU Exact Vector Geometry Engine (intersection_cpu.py)
   │      └── C++ STRtree vectorized bulk query against grid bounding boxes
   │
   ├──▶ 5. Mathematical Fractal Analyzer (fractal_analyzer.py)
   │      └── OLS Log-Log Regression for Db slope, R² fit & level statistics
   │
   └──▶ 6. Multi-Format Academic Exporter (academic_exporter.py)
          └── Publication PDF, Interactive HTML, Markdown, XLSX Workbooks, Vector SVG Maps & Manifest
```

---

## Mathematical Methodology

### Box-Counting Fractal Dimension ($D_b$)
The software places a series of spatial grids over the SVG analysis bounding box and evaluates occupancy for each grid cell. The relationship between grid scale $arepsilon$ and occupied box count $N(arepsilon)$ follows a power law:

$$N(arepsilon) \propto \left(rac{1}{arepsilon}ight)^{D_b}$$

Taking the natural logarithm yields the linear regression model:

$$\log N(arepsilon) = D_b \cdot \log\left(rac{1}{arepsilon}ight) + C$$

Where:
- $N(arepsilon)$ = Number of filled (occupied) grid cells at scale $arepsilon$.
- $arepsilon = rac{\max(W_{	ext{cell}}, H_{	ext{cell}})}{\max(W_{	ext{analysis}}, H_{	ext{analysis}})}$ = Normalized grid scale parameter.
- $\log(1/arepsilon) = \ln(1 / arepsilon)$ = Logarithm of inverse scale factor.
- $D_b = rac{\sum (x_i - ar{x})(y_i - ar{y})}{\sum (x_i - ar{x})^2}$ = Box-counting fractal dimension (OLS regression slope).
- $C$ = Regression intercept constant.

### Fit Quality ($R^2$ Score)
The coefficient of determination $R^2$ measures regression fit quality across analyzed levels:

$$R^2 = 1 - rac{SS_{	ext{res}}}{SS_{	ext{tot}}} = 1 - rac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - ar{y})^2}$$

If all occupied cell counts across levels are identical ($	ext{Var}(y) = 0$), $R^2$ evaluates to `NaN` to signal a degenerate regression state rather than overstating quality.

### Occupancy Percentage
For each grid level with $C$ columns and $R$ rows ($N_{	ext{total}} = C 	imes R$):

$$	ext{Fill Ratio} = rac{N_{	ext{filled}}}{N_{	ext{total}}}, \quad 	ext{Occupancy \%} = 	ext{Fill Ratio} 	imes 100\%$$

---

## Computational Geometry Pipeline

### 1. Affine Transformation Matrix Stack
SVG elements inherit coordinate transformations from parent `<g>` groups and element `transform="..."` attributes. The engine builds a 3x3 homogeneous transformation matrix $M$ for each element:

$$M_{	ext{cumulative}} = \prod_{k=1}^{m} T_k$$

Supported transformation functions:
- `matrix(a, b, c, d, e, f)` $ightarrow egin{bmatrix} a & c & e \ b & d & f \ 0 & 0 & 1 \end{bmatrix}$
- `translate(tx, ty)` $ightarrow egin{bmatrix} 1 & 0 & t_x \ 0 & 1 & t_y \ 0 & 0 & 1 \end{bmatrix}$
- `scale(sx, sy)` $ightarrow egin{bmatrix} s_x & 0 & 0 \ 0 & s_y & 0 \ 0 & 0 & 1 \end{bmatrix}$
- `rotate(angle, cx, cy)` $ightarrow T(c_x, c_y) \cdot R(	heta) \cdot T(-c_x, -c_y)$
- `skewX(angle)` $ightarrow egin{bmatrix} 1 & 	anlpha & 0 \ 0 & 1 & 0 \ 0 & 0 & 1 \end{bmatrix}$
- `skewY(angle)` $ightarrow egin{bmatrix} 1 & 0 & 0 \ 	anlpha & 1 & 0 \ 0 & 0 & 1 \end{bmatrix}$

### 2. Curve & Arc Vector Flattening
SVG paths contain parametric curves that are adaptively sampled into linear segments:

- **Cubic Bézier ($C, S$)**: $B(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + 3(1-t) t^2 P_2 + t^3 P_3, \quad t \in [0, 1]$
- **Quadratic Bézier ($Q, T$)**: $B(t) = (1-t)^2 P_0 + 2(1-t) t P_1 + t^2 P_2, \quad t \in [0, 1]$
- **Elliptical Arcs ($A$)**: Converted from SVG endpoint parameterization $(x_1, y_1, r_x, r_y, \phi, f_A, f_S, x_2, y_2)$ to center parameterization $(c_x, c_y, 	heta_1, \Delta	heta)$ before trigonometric evaluation.

### 3. Fill Rule Topology Resolution
Subpath polylines are converted into Shapely `Polygon` objects:
- **`nonzero` Fill Rule**: Uses `shapely.ops.unary_union(polygons)` to merge overlapping vector subpaths into a unified topology.
- **`evenodd` Fill Rule**: Evaluates sequential subpaths using `symmetric_difference` to create holes for inner nested rings.

---

## Aspect-Ratio-Aware Grid Planning

SVG artwork rarely forms a perfect 1:1 square bounding box. Forcing non-square graphics into a square grid distorts cell aspect ratios.

`grid_planner.py` automatically determines the analysis bounding box priority:
1. Valid SVG `viewBox` $[x_0, y_0, W, H]$
2. Valid SVG `width` and `height` attributes
3. Accumulated vector geometry bounds $[x_{\min}, y_{\min}, x_{\max}, y_{\max}]$

Given analysis dimensions $W_{	ext{analysis}}$ and $H_{	ext{analysis}}$, aspect ratio is $AR = rac{W_{	ext{analysis}}}{H_{	ext{analysis}}}$.

At Level 01, base grid dimensions $(C_1, R_1)$ are calculated to make cells as square as possible ($W_{	ext{cell}} pprox H_{	ext{cell}}$):
$$	ext{If } AR \ge 1.0: \quad R_1 = N_{	ext{base}}, \quad C_1 = \max(1, 	ext{round}(R_1 \cdot AR))$$
$$	ext{If } AR < 1.0: \quad C_1 = N_{	ext{base}}, \quad R_1 = \max(1, 	ext{round}(C_1 / AR))$$

For all subsequent levels $i \ge 1$, resolution doubles strictly:
$$C_i = C_1 \cdot 2^{i-1}, \quad R_i = R_1 \cdot 2^{i-1}$$

This **strict $2^i$ doubling** guarantees quadtree parent-child cell alignment across levels without aspect-ratio rounding drift.

---

## Performance Optimization & Complexity Analysis

### Unlimited Level Depth & Scaling Workload
There is **no hard limit** on the number of requested grid levels (`--levels N`, $N \ge 1$). However, because resolution doubles along both axes at every level, total grid cell count scales quadratically (approximately **$4	imes$ cell expansion per level**):

| Level | Grid Resolution | Total Cells ($N_{	ext{total}}$) | Memory & STRtree Workload Scale |
|:---|:---|:---|:---|
| **L01** | $4 	imes 8$ | 32 | $1	imes$ (Base) |
| **L02** | $8 	imes 16$ | 128 | $pprox 4	imes$ |
| **L03** | $16 	imes 32$ | 512 | $pprox 16	imes$ |
| **L04** | $32 	imes 64$ | 2,048 | $pprox 64	imes$ |
| **L05** | $64 	imes 128$ | 8,192 | $pprox 256	imes$ |
| **L06** | $128 	imes 256$ | 32,768 | $pprox 1,024	imes$ |
| **L07** | $256 	imes 512$ | 131,072 | $pprox 4,096	imes$ (Default CLI Depth) |
| **L08** | $512 	imes 1024$ | 524,288 | $pprox 16,384	imes$ |
| **L09** | $1024 	imes 2048$ | 2,097,152 | $pprox 65,536	imes$ |
| **L10** | $2048 	imes 4096$ | 8,388,608 | $pprox 262,144	imes$ |

### Complementary Empty Cell Accounting
For a grid with $N_{	ext{total}}$ cells, testing every cell individually against geometry would require $O(N_{	ext{total}})$ evaluations.
`intersection_cpu.py` uses vectorized NumPy grid bounding boxes queried against a C++ GEOS `STRtree` spatial index:
1. `cell_boxes` are queried in bulk: `tree.query(cell_boxes, predicate='intersects')`.
2. Occupied cell indices are collected: `matched_indices = np.unique(matches[0])`.
3. Filled cell count is $N_{	ext{filled}} = |	ext{matched\_indices}|$.
4. Empty cell count is calculated by complementary subtraction: $N_{	ext{empty}} = N_{	ext{total}} - N_{	ext{filled}}$.

This avoids allocating or storing empty cell geometry objects, keeping performance fast even for grids with millions of cells.

### High-Level XLSX Export Policy
Microsoft Excel worksheets support up to 1,048,576 rows. Full per-cell XLSX exports for levels $L08$ ($524,288$ cells) and $L09$ ($2,097,152$ cells) can lead to massive file sizes or exceed worksheet bounds.

**Export Policy**:
- **L01--L07**: Full per-cell XLSX tables are generated by default.
- **L08**: Per-cell XLSX tables are omitted by default; enabled via `--export-high-level-tables`.
- **L09+**: Per-cell XLSX tables are skipped. Summary metrics, PDF/HTML reports, SVG maps, and manifest metadata remain fully generated.

---

## Installation & Dependencies

### Requirements
- Python 3.9 or newer (Python 3.11 / 3.12 recommended)
- 64-bit Operating System (Windows, Linux, macOS)

```bash
git clone https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio.git
cd RASH-HIT-Fractal-Studio
pip install -r requirements.txt
```

### Core Dependency Stack
- **Shapely** ($\ge 2.0.0$): Vector geometry objects, spatial predicates (`intersects`, `contains`, `touches`), and `STRtree` C++ spatial index (BSD 3-Clause).
- **NumPy** ($\ge 1.22.0$): Vectorized 2D grid matrix generation and numerical regression operations (BSD 3-Clause).
- **defusedxml** ($\ge 0.7.1$): Secure XML parsing protecting against XXE entity expansion attacks (PSFL).
- **openpyxl** ($\ge 3.0.0$): Multi-sheet Excel workbook (`workbook.xlsx`) and per-level cell table generation (MIT).
- **PyMuPDF** / `fitz` ($\ge 1.20.0$): High-resolution PDF research report compilation (AGPL v3.0 / Commercial).
- **PyYAML**, **Pillow**, **tinycss2**: Configuration serialization, image validation, and inline CSS style parsing.

See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for full licensing details.

---

## CLI Usage & Command Matrix

### Quick Start (Default 7 Levels)
```bash
python run_analysis.py --input input_svgs/16D.svg
```

### Deep Analysis (10 Levels)
```bash
python run_analysis.py --input input_svgs/16D.svg --levels 10
```

### Batch Directory Analysis
```bash
python run_analysis.py --dir input_svgs/ --levels 7
```

### Command-Line Arguments Reference

| Argument | Type | Default | Description |
|:---|:---|:---|:---|
| `--input` | Path | `None` | Path to a single input SVG file. Mutually exclusive with `--dir`. |
| `--dir` | Path | `None` | Path to a directory containing SVG files for batch processing. Mutually exclusive with `--input`. |
| `--levels` | Int | `7` | Number of grid levels to calculate ($N \ge 1$). Default runs $L01$--$L07$. |
| `--measure` | String | `area` | Measurement mode. Default: `area` (evaluates fill area & stroke width). |
| `--engine` | String | `cpu` | Computational engine. Default: `cpu` (CPU Exact GEOS Engine). |
| `--profile` | String | `lean` | Export profile: `lean`, `reproducible`, `debug`, or `presentation`. |
| `--output-dir` | Path | `outputs/` | Root directory for exported research packages. |
| `--export-high-level-tables` | Flag | `False` | Forces per-cell XLSX dataset generation for Level 08. |

---

## Academic Output Package Specifications

Each analyzed SVG file produces an isolated research output package:

```text
outputs/[motif_name]/
├── report/
│   ├── report.pdf      # Publication PDF research report
│   ├── report.html     # Browser-based report with image-free first screen
│   └── report.md       # Clean Markdown report for documentation
├── excel/
│   └── workbook.xlsx   # Multi-sheet Excel workbook with summary metrics & validation
├── tables/
│   ├── 01_4x8_cells.xlsx
│   ├── 02_8x16_cells.xlsx
│   ├── ...
│   └── tables.html     # Interactive cell data table viewer with search filter
├── figures/
│   ├── 01_4x8_map.svg  # Pure vector SVG grid occupancy map
│   ├── 02_8x16_map.svg
│   └── ...
├── terminal/
│   └── terminal.txt    # Execution log with step timings
└── manifest/
    └── manifest.json   # Reproducibility metadata with SHA-256 checksum
```

### Key Output Features
- **Pure Vector SVG Grid Maps (`figures/*.svg`)**: Rendered directly as crisp SVG vector paths showing occupied cells (`#60A5FA`) and empty cells (`#FFFFFF`) overlaying the design.
- **Interactive HTML Report (`report/report.html`)**: Features an **image-free first screen** for fast loading, containing executive summaries, regression statistics, and data tables.
- **Reproducibility Manifest (`manifest/manifest.json`)**: Contains SHA-256 hash of the input SVG, software version, exact grid dimensions, GEOS/Shapely version details, timestamp, and platform metadata.

---

## Reproducibility & Audit Controls

RASH-HIT Fractal Studio incorporates automated validation tools to ensure dataset integrity:

1. **License & Notice Validator**:
   ```bash
   python tools/validate_license_docs.py
   ```
2. **Citation Validator**:
   ```bash
   python scripts/validate_citation.py
   ```
3. **Public Security Scan**:
   ```bash
   python tools/final_public_scan.py
   ```
4. **Unit Test Suite** (30 Tests):
   ```bash
   python -m unittest discover tests
   ```

---

## Academic Citation

If you use RASH-HIT Fractal Studio in your research, please cite the software using one of the following academic citation styles:

- **Concept DOI**: [10.5281/zenodo.21693694](https://doi.org/10.5281/zenodo.21693694)
- **Version DOI (v1.0.4)**: [10.5281/zenodo.21694567](https://doi.org/10.5281/zenodo.21694567)

### BibTeX
```bibtex
@software{Narcicek_RASH_HIT_Fractal_Studio_2026,
  author    = {Nar{\c{c}}i{\c{c}}ek, Mehmet Ra{\s}it},
  title     = {RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine},
  year      = {2026},
  version   = {1.0.4},
  publisher = {GitHub},
  doi       = {10.5281/zenodo.21694567},
  url       = {https://doi.org/10.5281/zenodo.21694567},
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
ET  - 1.0.4
PB  - GitHub
DO  - 10.5281/zenodo.21694567
UR  - https://doi.org/10.5281/zenodo.21694567
ER  - 
```

### APA 7
> Narçiçek, M. R. (2026). *RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine* (Version 1.0.4) [Computer software]. GitHub. https://doi.org/10.5281/zenodo.21694567

### AMA
> 1. Narçiçek MR. RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine. Version 1.0.4. GitHub; 2026. doi: 10.5281/zenodo.21694567. Available from: https://doi.org/10.5281/zenodo.21694567

### Chicago (Author-Date)
> Narçiçek, Mehmet Raşit. 2026. "RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine." Version 1.0.4. GitHub. https://doi.org/10.5281/zenodo.21694567.

### EndNote
> Narçiçek MR (2026) RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine (Version 1.0.4) [Computer software]. GitHub. https://doi.org/10.5281/zenodo.21694567

### IEEE
> [1] M. R. Narçiçek, "RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine," Version 1.0.4, GitHub, 2026, doi: 10.5281/zenodo.21694567.

### ISNAD
> Narçiçek, Mehmet Raşit. "RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine". Version 1.0.4. GitHub, 2026. https://doi.org/10.5281/zenodo.21694567.

### JAMA
> 1. Narçiçek MR. RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine. Version 1.0.4. GitHub; 2026. https://doi.org/10.5281/zenodo.21694567

### MLA (9th Edition)
> Narçiçek, Mehmet Raşit. *RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine*. Version 1.0.4, GitHub, 2026, https://doi.org/10.5281/zenodo.21694567.

### Vancouver
> 1. Narçiçek MR. RASH-HIT Fractal Studio: Vector Geometry Analysis and Box-Counting Engine [Computer software]. Version 1.0.4. GitHub; 2026. Available from: https://doi.org/10.5281/zenodo.21694567

---

## License & Authorship

RASH-HIT Fractal Studio is licensed under the **Apache License, Version 2.0**. See [`LICENSE`](LICENSE) for complete terms.

- **Author**: Mehmet Raşit Narçiçek
- **ORCID**: [0009-0005-3423-255X](https://orcid.org/0009-0005-3423-255X)
- **Concept DOI**: [10.5281/zenodo.21693694](https://doi.org/10.5281/zenodo.21693694)
- **Version DOI**: [10.5281/zenodo.21694567](https://doi.org/10.5281/zenodo.21694567)
- **Copyright**: © 2026 Mehmet Raşit Narçiçek
