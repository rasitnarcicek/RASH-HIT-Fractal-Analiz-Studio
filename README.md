# RASH-HIT Fractal Studio

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![Concept DOI](https://img.shields.io/badge/Concept_DOI-10.5281%2Fzenodo.21693694-blue.svg)](https://doi.org/10.5281/zenodo.21693694)
[![Version DOI](https://img.shields.io/badge/Version_DOI-10.5281%2Fzenodo.21694567-blue.svg)](https://doi.org/10.5281/zenodo.21694567)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0005--3423--255X-green.svg)](https://orcid.org/0009-0005-3423-255X)

**RASH-HIT Fractal Studio** is a research-grade, raster-free computational software engine for SVG vector geometry analysis, aspect-ratio-aware grid occupancy mapping, box-counting fractal dimension ($D_b$) estimation, SVG Coordinate Map rendering, and academic research package generation.

Unlike conventional image-processing tools that convert vector artwork into PNG/JPEG pixel rasters—introducing resolution dependency, anti-aliasing distortion, edge blurring, and scaling artifacts—RASH-HIT Fractal Studio evaluates raw SVG vector geometry directly in continuous floating-point coordinate space using C++ GEOS spatial predicates via Shapely 2.0.

---

## Table of Contents

1. [Research Context & Motivation](#research-context--motivation)
2. [Key Architecture & System Modules](#key-architecture--system-modules)
3. [Mathematical Methodology & Regression](#mathematical-methodology--regression)
4. [Computational Geometry Pipeline](#computational-geometry-pipeline)
   - [SVG Element & Styling Resolution](#svg-element--styling-resolution)
   - [CSS Unit Conversions](#css-unit-conversions)
   - [2D Affine Transformation Matrix Stack](#2d-affine-transformation-matrix-stack)
   - [Curve & Arc Vector Flattening](#curve--arc-vector-flattening)
   - [Fill Rule Topology Resolution](#fill-rule-topology-resolution)
5. [Aspect-Ratio-Aware Grid Planning](#aspect-ratio-aware-grid-planning)
6. [Performance Optimization & Complexity Analysis](#performance-optimization--complexity-analysis)
   - [Unlimited Level Depth & Workload Scaling](#unlimited-level-depth--workload-scaling)
   - [Complementary Empty Cell Accounting](#complementary-empty-cell-accounting)
   - [RLE Compression & Spatial Indexing](#rle-compression--spatial-indexing)
   - [High-Level XLSX Export Policy](#high-level-xlsx-export-policy)
7. [Output Profiles & Execution Modes](#output-profiles--execution-modes)
8. [Academic Output Package Specifications](#academic-output-package-specifications)
9. [Installation & Dependencies](#installation--dependencies)
10. [CLI Usage & Command Matrix](#cli-usage--command-matrix)
11. [Reproducibility & Validation Controls](#reproducibility--validation-controls)
12. [Academic Citation](#academic-citation)
13. [License & Authorship](#license--authorship)

---

## Research Context & Motivation

Design, architectural, motif, visual heritage, and pattern research frequently rely on visual forms natively stored as Scalable Vector Graphics (SVG). Standard software workflows often convert these vector files into rasterized bitmap images before applying box-counting algorithms.

Rasterization distorts mathematical fractal measurements in several ways:
- **Pixel Grid Discretization**: Fine geometric details below pixel resolution are merged or deleted.
- **Anti-Aliasing Fringing**: Boundary pixels become partially transparent or shaded, altering occupancy decisions.
- **Scale Dependence**: The measured fractal dimension varies depending on the arbitrary pixel resolution chosen for rasterization.

**RASH-HIT Fractal Studio** eliminates rasterization entirely. It parses raw SVG elements (`path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`), evaluates 2D affine transform stacks, flattens Bézier curves and elliptical arcs, and evaluates geometric intersections directly against floating-point grid bounding boxes using C++ GEOS spatial predicates.

---

## Key Architecture & System Modules

The codebase is organized into decoupled, specialized backend modules:

```text
SVG File Input
   │
   ├──▶ 1. SVGLoader & Secure XML Parser (backend/svg_loader.py)
   │      ├── defusedxml XXE Security Hardening
   │      ├── ViewBox & Scale Resolution (viewBox ➔ width/height ➔ geometry bounds ➔ 100x100 fallback)
   │      ├── CSS Rule Parser (tinycss2 + regex fallback) & Inline Style Resolver
   │      ├── CSS Length Unit Normalization (px, pt, mm, cm, in, pc, em, rem, %)
   │      └── Effective Opacity & Visibility Filtering (opacity, fill-opacity, stroke-opacity, display, visibility)
   │
   ├──▶ 2. Geometry Engine (backend/geometry_engine.py)
   │      ├── 3x3 Homogeneous Affine Transformation Stack (translate, rotate, scale, skewX, skewY, matrix)
   │      ├── Curve & Arc Flattening (Cubic/Quadratic Bézier & Elliptical Arc parameterization)
   │      ├── Transformed Stroke Width Scaling: w_effective = w_stroke * sqrt(|det(M)|)
   │      └── Polygon Fill Rule Topology Resolution (nonzero: unary_union / evenodd: symmetric_difference)
   │
   ├──▶ 3. Aspect-Ratio-Aware Grid Planner (backend/grid_planner.py)
   │      └── Base grid resolution setup & strict 2^i power-of-two resolution doubling across levels
   │
   ├──▶ 4. Spatial Candidate Prefilter (backend/candidate_prefilter.py)
   │      └── Bounding-box candidate pruning & Cohen-Sutherland line clipping algorithms
   │
   ├──▶ 5. CPU Exact Vector Geometry Engine (backend/intersection_cpu.py)
   │      ├── C++ STRtree vectorized bulk query against grid bounding boxes
   │      ├── CellDebugInfo tracking (level, col, row, reason, geom_id, stroke_width, bounds)
   │      └── Complementary empty cell calculation (N_empty = N_total - N_filled)
   │
   ├──▶ 6. Mathematical Fractal Analyzer (backend/fractal_analyzer.py)
   │      └── OLS Log-Log Regression for Db slope, R² fit & zero-variance NaN safeguards
   │
   ├──▶ 7. Output Profiles & Suspicious Detector (backend/output_profiles.py, suspicious_detector.py)
   │      └── Profile management (lean, reproducible, debug, presentation) & degenerate geometry detection
   │
   └──▶ 8. Multi-Format Academic Exporter (backend/academic_exporter.py)
          ├── Pure Vector SVG Grid Maps (figures/*.svg)
          ├── Interactive HTML Table Viewer (tables/tables.html) & PDF Report Compilation (report/report.pdf)
          ├── Multi-Sheet Excel Workbooks (excel/workbook.xlsx) & per-level cell CSV/XLSX exports
          ├── Run-Length Encoded (RLE) JSON & ASCII Map Books (tables/*.txt)
          └── Reproducibility Manifest with SHA-256 Checksum (manifest/manifest.json)
```

---

## Mathematical Methodology & Regression

### Box-Counting Fractal Dimension ($D_b$)
The software places a series of spatial grids over the SVG analysis bounding box and evaluates occupancy for each grid cell. The relationship between grid scale $\varepsilon$ and occupied box count $N(\varepsilon)$ follows a power law:

$$N(\varepsilon) \propto \left(\frac{1}{\varepsilon}\right)^{D_b}$$

Taking the natural logarithm yields the linear regression model:

$$\log N(\varepsilon) = D_b \cdot \log\left(\frac{1}{\varepsilon}\right) + C$$

Where:
- $N(\varepsilon)$ = Number of filled (occupied) grid cells at scale $\varepsilon$.
- $\varepsilon = \frac{\max(W_{\text{cell}}, H_{\text{cell}})}{\max(W_{\text{analysis}}, H_{\text{analysis}})}$ = Normalized grid scale parameter.
- $\log(1/\varepsilon) = \ln(1 / \varepsilon)$ = Logarithm of inverse scale factor.
- $D_b = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - ar{x})^2}$ = Box-counting fractal dimension (Ordinary Least Squares regression slope).
- $C$ = Regression intercept constant.

### Fit Quality ($R^2$ Score)
The coefficient of determination $R^2$ measures regression fit quality across analyzed levels:

$$R^2 = 1 - \frac{SS_{\text{res}}}{SS_{\text{tot}}} = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$

If all occupied cell counts across levels are identical (zero variance $\text{Var}(y) = 0$), $R^2$ evaluates to `NaN` to signal a degenerate regression state rather than overstating quality.

### Occupancy Percentage
For each grid level with $C$ columns and $R$ rows ($N_{\text{total}} = C \times R$):

$$\text{Fill Ratio} = \frac{N_{\text{filled}}}{N_{\text{total}}}, \quad \text{Occupancy \%} = \text{Fill Ratio} \times 100\%$$

---

## Computational Geometry Pipeline

### SVG Element & Styling Resolution
The SVG Loader (`svg_loader.py`) parses elements (`path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`) and resolves inherited styles across presentation attributes, inline `style="..."` attributes, and `<style>` CSS class definitions (`.classname`).

**Visibility & Opacity Filtering**:
An element is excluded from geometry analysis if:
- `display` evaluates to `none`
- `visibility` evaluates to `hidden` or `collapse`
- `opacity` evaluates to `0.0`
- `effective_fill_alpha` ($=\text{fill\_opacity} \times \text{opacity}$) and `effective_stroke_alpha` ($=\text{stroke\_opacity} \times \text{opacity}$) both evaluate to `0.0`

### CSS Unit Conversions
Length parameters are converted to absolute floating-point pixels ($px$) using physical unit scale factors:

| Unit | Definition | Scale Factor to Pixels ($px$) |
|:---|:---|:---|
| `px` | Pixels | $1.0$ |
| `pt` | Points | $1.33333$ ($4/3$) |
| `pc` | Picas | $16.0$ |
| `mm` | Millimeters | $3.77953$ |
| `cm` | Centimeters | $37.7953$ |
| `in` | Inches | $96.0$ |
| `em`, `rem` | Font relative units | $16.0$ (Default font base) |
| `%` | ViewBox percentage | Relative to ViewBox dimension |

### 2D Affine Transformation Matrix Stack
SVG elements inherit coordinate transformations from parent `<g>` groups and element `transform="..."` attributes. The engine builds a 3x3 homogeneous transformation matrix $M$ for each element:

$$M_{\text{cumulative}} = \prod_{k=1}^{m} T_k$$

Supported transformation functions:
- `matrix(a, b, c, d, e, f)` $\rightarrow \begin{bmatrix} a & c & e \\ b & d & f \\ 0 & 0 & 1 \end{bmatrix}$
- `translate(tx, ty)` $\rightarrow \begin{bmatrix} 1 & 0 & t_x \\ 0 & 1 & t_y \\ 0 & 0 & 1 \end{bmatrix}$
- `scale(sx, sy)` $\rightarrow \begin{bmatrix} s_x & 0 & 0 \\ 0 & s_y & 0 \\ 0 & 0 & 1 \end{bmatrix}$
- `rotate(angle, cx, cy)` $\rightarrow T(c_x, c_y) \cdot R(\theta) \cdot T(-c_x, -c_y)$
- `skewX(angle)` $\rightarrow \begin{bmatrix} 1 & \tan\alpha & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$
- `skewY(angle)` $\rightarrow \begin{bmatrix} 1 & 0 & 0 \\ \tan\alpha & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$

**Stroke Width Transformation Scaling**:
Stroke widths are scaled by the local transformation scale factor:
$$w_{\text{effective}} = w_{\text{stroke}} \cdot \sqrt{|\det(M_{2\times 2})|} = w_{\text{stroke}} \cdot \sqrt{|a \cdot d - b \cdot c|}$$

### Curve & Arc Vector Flattening
SVG paths contain parametric curves that are adaptively sampled into linear segments based on tolerance configuration (`high`: 24 steps, `medium`: 12 steps, `low`: 6 steps):

- **Cubic Bézier ($C, S$)**: $B(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + 3(1-t) t^2 P_2 + t^3 P_3, \quad t \in [0, 1]$
- **Quadratic Bézier ($Q, T$)**: $B(t) = (1-t)^2 P_0 + 2(1-t) t P_1 + t^2 P_2, \quad t \in [0, 1]$
- **Elliptical Arcs ($A$)**: Converted from SVG endpoint parameterization $(x_1, y_1, r_x, r_y, \phi, f_A, f_S, x_2, y_2)$ to center parameterization $(c_x, c_y, \theta_1, \Delta\theta)$ before trigonometric evaluation.

### Fill Rule Topology Resolution
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
4. Emergency fallback box $[0, 0, 100, 100]$

Given analysis dimensions $W_{\text{analysis}}$ and $H_{	ext{analysis}}$, aspect ratio is $AR = \frac{W_{\text{analysis}}}{H_{\text{analysis}}}$.

At Level 01, base grid dimensions $(C_1, R_1)$ are calculated to make cells as square as possible ($W_{\text{cell}} \approx H_{	ext{cell}}$):
$$\text{If } AR \ge 1.0: \quad R_1 = N_{\text{base}}, \quad C_1 = \max(1, \text{round}(R_1 \cdot AR))$$
$$\text{If } AR < 1.0: \quad C_1 = N_{\text{base}}, \quad R_1 = \max(1, \text{round}(C_1 / AR))$$

For all subsequent levels $i \ge 1$, resolution doubles strictly:
$$C_i = C_1 \cdot 2^{i-1}, \quad R_i = R_1 \cdot 2^{i-1}$$

This **strict $2^i$ doubling** guarantees quadtree parent-child cell alignment across levels without aspect-ratio rounding drift.

---

## Performance Optimization & Complexity Analysis

### Unlimited Level Depth & Workload Scaling
There is **no hard limit** on the number of requested grid levels (`--levels N`, $N \ge 1$). However, because resolution doubles along both axes at every level, total grid cell count scales quadratically (approximately **$4\times$ cell expansion per level**):

| Level | Grid Resolution | Total Cells ($N_{\text{total}}$) | Memory & STRtree Workload Scale |
|:---|:---|:---|:---|
| **L01** | $4 \times 8$ | 32 | $1\times$ (Base) |
| **L02** | $8 \times 16$ | 128 | $\approx 4\times$ |
| **L03** | $16 \times 32$ | 512 | $\approx 16\times$ |
| **L04** | $32 \times 64$ | 2,048 | $\approx 64\times$ |
| **L05** | $64 \times 128$ | 8,192 | $\approx 256\times$ |
| **L06** | $128 \times 256$ | 32,768 | $\approx 1,024\times$ |
| **L07** | $256 \times 512$ | 131,072 | $\approx 4,096\times$ (Default CLI Depth) |
| **L08** | $512 \times 1024$ | 524,288 | $\approx 16,384\times$ |
| **L09** | $1024 \times 2048$ | 2,097,152 | $\approx 65,536\times$ |
| **L10** | $2048 \times 4096$ | 8,388,608 | $\approx 262,144\times$ |

### Complementary Empty Cell Accounting
For a grid with $N_{\text{total}}$ cells, testing every cell individually against geometry would require $O(N_{	ext{total}})$ evaluations.
`intersection_cpu.py` uses vectorized NumPy grid bounding boxes queried against a C++ GEOS `STRtree` spatial index:
1. `cell_boxes` are queried in bulk: `tree.query(cell_boxes, predicate='intersects')`.
2. Occupied cell indices are collected: `matched_indices = np.unique(matches[0])`.
3. Filled cell count is $N_{\text{filled}} = |\text{matched\_indices}|$.
4. Empty cell count is calculated by complementary subtraction: $N_{\text{empty}} = N_{	ext{total}} - N_{	ext{filled}}$.

This avoids allocating or storing empty cell geometry objects, keeping performance fast even for grids with millions of cells.

### RLE Compression & Spatial Indexing
Per-level cell occupancy datasets are stored using Run-Length Encoding (RLE) JSON structures (`tables/*_rle.json`):
```json
{
  "level": 1, "cols": 4, "rows": 8, "total_cells": 32, "filled_cells": 32,
  "rle_runs": [[1, 32]]
}
```
This compresses sparse or solid grid maps by orders of magnitude compared to uncompressed 2D boolean arrays.

### High-Level XLSX Export Policy
Microsoft Excel worksheets support up to 1,048,576 rows. Full per-cell XLSX exports for levels $L08$ ($524,288$ cells) and $L09$ ($2,097,152$ cells) can lead to massive file sizes or exceed worksheet bounds.

**Export Policy**:
- **L01--L07**: Full per-cell XLSX tables are generated by default.
- **L08**: Per-cell XLSX tables are omitted by default; enabled via `--export-high-level-tables`.
- **L09+**: Per-cell XLSX tables are skipped. Summary metrics, PDF/HTML reports, SVG maps, and manifest metadata remain fully generated.

---

## Output Profiles & Execution Modes

The engine supports four export profiles managed by `output_profiles.py`:

| Profile | Target Audience | Generated Artifacts |
|:---|:---|:---|
| `lean` *(Default)* | Large batch processing & fast runs | PDF report, HTML report, Markdown summary, master Excel workbook, SVG maps, terminal log. |
| `reproducible` | Academic publication submission | Full audit trail, `manifest.json` with SHA-256 hash, per-level CSV/XLSX datasets, RLE JSON files. |
| `debug` | Geometry engine verification | Includes `CellDebugInfo` collection, cell bounding box dumps, raw CSV files, and detailed execution timings. |
| `presentation` | Visual design showcase | High-resolution pure vector SVG grid maps and formatted PDF publication reports. |

---

## Academic Output Package Specifications

Each analyzed SVG file produces an isolated research output package:

```text
outputs/[motif_name]/
├── report/
│   ├── report.pdf      # Publication PDF research report compiled via PyMuPDF
│   ├── report.html     # Interactive HTML report with image-free first screen
│   └── report.md       # Clean Markdown report for documentation
├── excel/
│   └── workbook.xlsx   # Multi-sheet Excel workbook with summary metrics & validation
├── tables/
│   ├── 01_4x8_cells.xlsx
│   ├── 01_4x8_rle.json # Run-Length Encoded dataset
│   ├── 01_4x8_ascii.txt# Aligned ASCII grid map book
│   └── tables.html     # Interactive cell data table viewer with search filter
├── figures/
│   ├── 01_4x8_map.svg  # Pure vector SVG grid occupancy map
│   └── ...
├── terminal/
│   └── terminal.txt    # Plain-text execution log with step timings
└── manifest/
    └── manifest.json   # Reproducibility metadata with SHA-256 checksum
```

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
| `--measure` | String | `area` | Measurement mode (`area`: evaluates fill area & stroke width). |
| `--engine` | String | `cpu` | Computational engine (`cpu`: CPU Exact GEOS Engine). |
| `--profile` | String | `lean` | Export profile: `lean`, `reproducible`, `debug`, or `presentation`. |
| `--output-dir` | Path | `outputs/` | Root directory for exported research packages. |
| `--export-high-level-tables` | Flag | `False` | Forces per-cell XLSX dataset generation for Level 08. |

---

---

## Automated Validation & Quality Assurance Pipeline

RASH-HIT Fractal Studio integrates specialized verification modules to ensure data integrity, PDF stream validity, and cross-format dataset consistency:

1. **Output Slug Sanitization (`sanitize_output_slug`)**:
   Input SVG filenames and motif names are sanitized using regex filtering (`[^A-Za-z0-9._-]+`) to prevent path traversal vulnerabilities (`../`) and generate safe, cross-platform filesystem directory names.

2. **Boundary Cell & Degeneracy Detector (`backend/suspicious_detector.py`)**:
   `verify_boundary_cells()` inspects grid boundary cell occupancy ratios across levels. It flags potential bounding-box clipping, zero-area vector degenerate paths, or misaligned ViewBox boundaries.

3. **PDF Structural Validator (`backend/pdf_validator.py`)**:
   `validate_pdf_file()` uses PyMuPDF to inspect compiled `report.pdf` files. It verifies page count integrity, font text stream extraction, vector drawing primitives, and checks for stream corruption.

4. **Multi-Source Artifact Cross-Validator (`backend/artifact_validator.py`)**:
   `validate_and_generate_real_diff_reports()` performs a 4-way cross-verification matrix between ASCII grid books (`*_ascii.txt`), Run-Length Encoded JSON files (`*_rle.json`), SVG coordinate maps (`*_map.svg`), and optional PNG renderings to guarantee $100\%$ cell occupancy consistency across all export formats.


---

## Reproducibility & Validation Controls

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
